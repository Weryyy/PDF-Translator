#!/usr/bin/env python3
import os
import sys
import torch
import PyPDF2
from pathlib import Path
from transformers import MarianTokenizer, MarianMTModel
from tqdm import tqdm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def main():
    model_path = "./models/translation_model"
    input_pdf = "Mushoku Tensei Redundant Reincarnation Vol. 3.pdf"
    output_pdf = "output/Mushoku_Tensei_ES.pdf"
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    print(f"Loading model from {model_path}...")
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path).to(device)
    model.eval()
    
    print(f"Extracting text from {input_pdf}...")
    text_chunks = []
    with open(input_pdf, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in tqdm(reader.pages, desc="Extracting"):
            text_chunks.append(page.extract_text())
    
    print(f"Translating {len(text_chunks)} pages...")
    translated_text = []
    for chunk in tqdm(text_chunks, desc="Translating"):
        if not chunk.strip():
            translated_text.append("")
            continue
            
        # Split chunk into smaller parts if too long (max 128 chars for this model's config)
        # But we'll try full paragraphs
        lines = chunk.split('\n')
        translated_lines = []
        for line in lines:
            if not line.strip(): 
                translated_lines.append("")
                continue
            
            inputs = tokenizer(line, return_tensors="pt", truncation=True, max_length=128).to(device)
            with torch.no_grad():
                outputs = model.generate(**inputs)
            translated_lines.append(tokenizer.decode(outputs[0], skip_special_tokens=True))
        
        translated_text.append("\n".join(translated_lines))
    
    print(f"Creating PDF: {output_pdf}...")
    os.makedirs("output", exist_ok=True)
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    for page_text in translated_text:
        paragraphs = page_text.split('\n')
        for p in paragraphs:
            if p.strip():
                story.append(Paragraph(p, styles["Normal"]))
        story.append(Spacer(1, 12))
        
    doc.build(story)
    print("Complete!")

if __name__ == "__main__":
    main()
