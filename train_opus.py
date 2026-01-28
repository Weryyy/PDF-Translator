#!/usr/bin/env python3
import sys
import os
import torch
import pandas
import time
from pathlib import Path
from torch.utils.data import Dataset, DataLoader

# CRITICAL FIX: Lazy import to avoid sklearn issues during initialization
# MarianMT doesn't need sklearn metrics by default
from transformers import MarianTokenizer, MarianMTModel
from torch.optim import AdamW
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm

print("All imports successful.")

# HYPER-OPTIMIZED FOR 6GB GPU
BATCH_SIZE = 1
EPOCHS = 3
LEARNING_RATE = 5e-5
MODEL_NAME = "Helsinki-NLP/opus-mt-en-es"
OUTPUT_DIR = "./models/translation_model"
MAX_LENGTH = 64

def main():
    print(f"CUDA: {torch.cuda.is_available()}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("Loading samples...")
    all_samples = []
    for f in Path("synthetic_data").glob("*.parquet"):
        df = pandas.read_parquet(f)
        for _, row in df.iterrows():
            all_samples.append({"src": str(row['source_text']), "tgt": str(row['target_text'])})
    
    print(f"Total: {len(all_samples)}")
    
    tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
    model = MarianMTModel.from_pretrained(MODEL_NAME).to(device)
    
    class SimpleDataset(Dataset):
        def __init__(self, s): self.s = s
        def __len__(self): return len(self.s)
        def __getitem__(self, i):
            # Correct tokenization for MarianMT
            src = tokenizer(self.s[i]["src"], max_length=MAX_LENGTH, truncation=True, padding="max_length", return_tensors="pt")
            tgt = tokenizer(text_target=self.s[i]["tgt"], max_length=MAX_LENGTH, truncation=True, padding="max_length", return_tensors="pt")
            return {"input_ids": src["input_ids"].squeeze(), "attention_mask": src["attention_mask"].squeeze(), "labels": tgt["input_ids"].squeeze()}

    loader = DataLoader(SimpleDataset(all_samples), batch_size=BATCH_SIZE, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    scaler = torch.amp.GradScaler('cuda')
    
    print("Training...")
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        pbar = tqdm(loader, desc=f"Epoch {epoch+1}")
        for batch in pbar:
            for k in batch: batch[k] = batch[k].to(device)
            optimizer.zero_grad()
            with torch.amp.autocast('cuda'):
                loss = model(**batch).loss
            
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total_loss += loss.item()
            pbar.set_postfix(loss=f"{loss.item():.4f}")
        print(f"Epoch {epoch+1} Avg Loss: {total_loss/len(loader):.4f}")

    print("Saving...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Done!")

if __name__ == "__main__": main()
