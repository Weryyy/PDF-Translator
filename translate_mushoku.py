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

from transformers import MarianTokenizer, MarianMTModel, AutoModelForCausalLM, AutoTokenizer as LLMTokenizer
import gc

def main():
    model_path = "./models/translation_model"
    refiner_model_id = "Qwen/Qwen2-1.5B-Instruct"
    input_pdf = "Mushoku Tensei Redundant Reincarnation Vol. 3.pdf"
    output_pdf = "output/Mushoku_Tensei_ES_Refined.pdf"
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # --- PASO 1: TRADUCCIÓN ---
    print(f"Loading translation model from {model_path}...")
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path).to(device)
    model.eval()
    
    # ... (Glosario y extracción igual)
    glossary = {
        "Rudeus": "Rudeus", "Greyrat": "Greyrat", "Eris": "Eris", 
        "Roxy": "Roxy", "Sylphiette": "Sylphiette", "Paul": "Paul",
        "Zenith": "Zenith", "Ghislaine": "Ghislaine", "Fittoa": "Fittoa"
    }

    def apply_glossary(text, reverse=False):
        for key, value in glossary.items():
            if not reverse: text = text.replace(key, f" {key} ")
            else: text = text.replace(f" {key} ", key)
        return text

    print(f"Extracting text...")
    text_chunks = []
    with open(input_pdf, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_chunks.append(page.extract_text())
    
    print(f"Phase 1: Translating...")
    raw_translations = []
    for chunk in tqdm(text_chunks, desc="Translating"):
        if not chunk.strip():
            raw_translations.append("")
            continue
        
        paragraphs = [p for p in chunk.split('\n\n') if p.strip()]
        translated_paragraphs = []
        for para in paragraphs:
            processed_para = apply_glossary(para.replace('\n', ' '))
            inputs = tokenizer(processed_para, return_tensors="pt", truncation=True, max_length=256).to(device)
            with torch.no_grad():
                outputs = model.generate(**inputs, num_beams=4)
            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            translated_paragraphs.append(apply_glossary(result, reverse=True))
        raw_translations.append("\n\n".join(translated_paragraphs))

    # --- LIBERAR MEMORIA ---
    print("Freeing memory for Refiner model...")
    del model
    del tokenizer
    gc.collect()
    torch.cuda.empty_cache()

    # --- PASO 2: REFINAMIENTO CON LLM ---
    print(f"Loading refiner model {refiner_model_id}...")
    refiner_tokenizer = LLMTokenizer.from_pretrained(refiner_model_id)
    refiner_model = AutoModelForCausalLM.from_pretrained(
        refiner_model_id, 
        torch_dtype=torch.float16, 
        device_map="auto"
    )

    print("Phase 2: Refining gender and consistency...")
    final_text = []
    for translated_page in tqdm(raw_translations, desc="Refining"):
        if not translated_page.strip():
            final_text.append("")
            continue
            
        # Refinamos por bloques para que el LLM tenga contexto
        prompt = f"Eres un editor experto en novelas ligeras. Corrige el género gramatical (especialmente Eris es mujer, Rudeus es hombre) y mejora la fluidez de esta traducción al español. Devuelve SOLO el texto corregido:\n\n{translated_page}"
        
        messages = [{"role": "user", "content": prompt}]
        text = refiner_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = refiner_tokenizer([text], return_tensors="pt").to(device)

        with torch.no_grad():
            generated_ids = refiner_model.generate(
                model_inputs.input_ids,
                max_new_tokens=1024,
                temperature=0.3
            )
            # Cortar el prompt de la respuesta
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = refiner_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        final_text.append(response.strip())

    # --- GENERAR PDF ---
    print(f"Creating PDF: {output_pdf}...")
    os.makedirs("output", exist_ok=True)
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for page_text in final_text:
        for p in page_text.split('\n'):
            if p.strip(): story.append(Paragraph(p, styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    print("Complete!")

if __name__ == "__main__":
    main()
