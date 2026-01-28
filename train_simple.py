#!/usr/bin/env python3
"""
Simplified training script for opus-mt-en-es
"""
import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

import sys
sys.path.insert(0, '.')

from datasets import Dataset
import json
import torch
from pathlib import Path
import pandas

# Lazy imports to avoid sklearn issues
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq

# Load data
print("Loading data...")
data_dir = Path("synthetic_data")
all_samples = []
for parquet_file in sorted(data_dir.glob("*.parquet")):
    print(f"  Loading {parquet_file.name}...")
    df = pandas.read_parquet(parquet_file)
    for idx, row in df.iterrows():
        all_samples.append({
            "en": str(row['source_text']),
            "es": str(row['target_text'])
        })

print(f"Loaded {len(all_samples)} samples")

# Split data
train_size = max(1, int(0.9 * len(all_samples)))
train_data = all_samples[:train_size]
val_data = all_samples[train_size:]

print(f"Train: {len(train_data)}, Val: {len(val_data)}")

# Create datasets
train_dataset = Dataset.from_dict({
    "en": [s["en"] for s in train_data],
    "es": [s["es"] for s in train_data]
})

if len(val_data) > 0:
    val_dataset = Dataset.from_dict({
        "en": [s["en"] for s in val_data],
        "es": [s["es"] for s in val_data]
    })
else:
    val_dataset = train_dataset

# Load model and tokenizer
print("Loading model: Helsinki-NLP/opus-mt-en-es...")
model_name = "Helsinki-NLP/opus-mt-en-es"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Tokenize
def tokenize_function(examples):
    inputs = tokenizer(examples["en"], max_length=256, truncation=True, padding=True, return_tensors=None)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["es"], max_length=256, truncation=True, padding=True, return_tensors=None)
    inputs["labels"] = labels["input_ids"]
    return inputs

print("Tokenizing...")
train_dataset = train_dataset.map(tokenize_function, batched=True, batch_size=8, remove_columns=["en", "es"])
val_dataset = val_dataset.map(tokenize_function, batched=True, batch_size=8, remove_columns=["en", "es"])

# Training args
training_args = Seq2SeqTrainingArguments(
    output_dir="./models/translation_model",
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    warmup_steps=100,
    weight_decay=0.01,
    fp16=True,
    gradient_accumulation_steps=2,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    push_to_hub=False
)

# Data collator
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator
)

# Train
print("Starting training...")
trainer.train()
print("Training complete!")
