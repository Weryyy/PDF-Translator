import torch
from transformers import MarianTokenizer, MarianMTModel, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import Dataset, DataLoader
import json
import os
from tqdm import tqdm

class GoldDataset(Dataset):
    def __init__(self, json_file, tokenizer, max_length=128):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        inputs = self.tokenizer(item['en'], truncation=True, padding='max_length', max_length=self.max_length, return_tensors="pt")
        targets = self.tokenizer(text_target=item['es'], truncation=True, padding='max_length', max_length=self.max_length, return_tensors="pt")
        
        return {
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze(),
            'labels': targets['input_ids'].squeeze()
        }

def fine_tune_marian():
    model_name = "Helsinki-NLP/opus-mt-en-es"
    output_dir = "./models/mushoku_trained_model"
    dataset_path = "mushoku_gold_dataset.json"
    
    if not os.path.exists(dataset_path):
        print("Gold dataset not found. Run prepare_adaptation_data.py first.")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Fine-tuning on {device}...")

    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name).to(device)

    dataset = GoldDataset(dataset_path, tokenizer)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

    optimizer = AdamW(model.parameters(), lr=5e-5)
    
    model.train()
    epochs = 5
    scaler = torch.amp.GradScaler()

    for epoch in range(epochs):
        loop = tqdm(dataloader, leave=True)
        epoch_loss = 0
        for batch in loop:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            with torch.amp.autocast('cuda'):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            epoch_loss += loss.item()
            loop.set_description(f"Epoch {epoch+1}")
            loop.set_postfix(loss=loss.item())

        print(f"Epoch {epoch+1} Average Loss: {epoch_loss/len(dataloader)}")

    # Save the adapted model
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Adapted model saved to {output_dir}")

if __name__ == "__main__":
    fine_tune_marian()
