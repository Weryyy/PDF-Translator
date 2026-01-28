import os
import json
import torch
from transformers import (
    MarianMTModel, 
    MarianTokenizer, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer, 
    DataCollatorForSeq2Seq
)
from datasets import Dataset

def train_adaptation(base_model_name, train_files, output_dir, epochs=5):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Iniciando entrenamiento de adaptación para {base_model_name}...")
    
    # 1. Cargar datos
    all_data = []
    for f_path in train_files:
        if os.path.exists(f_path):
            with open(f_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Normalizar claves a 'src' y 'tgt'
                for item in data:
                    if 'ja' in item: src = item['ja']
                    elif 'en' in item: src = item['en']
                    else: continue
                    all_data.append({"src": src, "tgt": item['es']})
    
    if not all_data:
        print("Error: No hay datos para entrenar.")
        return

    # Convertir a Dataset de HuggingFace
    raw_dataset = Dataset.from_list(all_data)
    
    # 2. Tokenizador y Modelo
    tokenizer = MarianTokenizer.from_pretrained(base_model_name)
    model = MarianMTModel.from_pretrained(base_model_name)
    
    def preprocess_function(examples):
        inputs = examples["src"]
        targets = examples["tgt"]
        # Nueva forma recomendada para Seq2Seq en Transformers
        model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
        labels = tokenizer(text_target=targets, max_length=128, truncation=True, padding="max_length")

        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_dataset = raw_dataset.map(preprocess_function, batched=True)
    
    # 3. Configuración de Entrenamiento (Optimizado para 6GB VRAM)
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        eval_strategy="no",
        learning_rate=5e-5,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8, # Batch efectivo de 16
        weight_decay=0.01,
        save_total_limit=1,
        num_train_epochs=epochs,
        predict_with_generate=True,
        fp16=True, # Obligatorio para ahorrar VRAM
        push_to_hub=False,
        logging_steps=10,
        report_to="none"
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        processing_class=tokenizer,
    )

    # 4. Ejecutar
    print("Entrenando...")
    trainer.train()
    
    # 5. Guardar modelo refinado
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Modelo guardado en {output_dir}")

if __name__ == "__main__":
    # Entrenar el modelo JAPONÉS -> ESPAÑOL
    train_adaptation(
        "Helsinki-NLP/opus-mt-ja-es", 
        ["mushoku_training_dataset_ja_es.json", "mushoku_gold_ja_es.json"],
        "./models/mushoku_mt_ja_es_refined"
    )
    
    # Opcional: Entrenar el modelo INGLÉS -> ESPAÑOL (si tienes los datos)
    if os.path.exists("mushoku_gold_en_es.json"):
        train_adaptation(
            "Helsinki-NLP/opus-mt-en-es", 
            ["mushoku_gold_en_es.json"],
            "./models/mushoku_mt_en_es_refined"
        )
