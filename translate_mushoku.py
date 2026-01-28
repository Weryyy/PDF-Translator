from transformers import MarianTokenizer, MarianMTModel, AutoModelForCausalLM, AutoTokenizer as LLMTokenizer
import gc
import time
import re
import torch
import PyPDF2
import os
from pathlib import Path
from tqdm import tqdm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def clean_text(text):
    # Eliminar repeticiones de guiones o puntos
    text = re.sub(r'([-\._\s]){4,}', r'\1\1\1', text)
    # Limpiar restos de meta-comentarios comunes de la IA
    meta_trash = [
        r"Aquí tienes la edición revisada.*",
        r"Entonces, aquí tienes.*",
        r"Resumen:.*",
        r"Aristotle dijo.*",
        r"Edición revisada:.*",
        r"Este es el texto corregido:.*"
    ]
    for pattern in meta_trash:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
    
    return text.strip()

def main():
    model_path = "./models/translation_model"
    refiner_model_id = "Qwen/Qwen2-1.5B-Instruct"
    input_pdf = "Mushoku Tensei Redundant Reincarnation Vol. 3.pdf"
    
    # Nombre con timestamp para evitar sobreescribir
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_pdf = f"output/Mushoku_Tensei_ES_{timestamp}.pdf"
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # --- PASO 1: TRADUCCIÓN ---
    print(f"Loading translation model from {model_path}...")
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path).to(device)
    model.eval()
    
    # --- CONFIGURACIÓN DE MEJORAS ---
    glossary = {
        "Rudeus": "Rudeus", "Arus": "Rudeus", "Greyrat": "Greyrat", 
        "Eris": "Eris", "Roxy": "Roxy", "Sylphiette": "Sylphiette",
        "Paul": "Paul", "Zenith": "Zenith", "Lilia": "Lilia", 
        "Ghislaine": "Ghislaine", "Fittoa": "Fittoa", "Asura": "Asura",
        "Lucie": "Lucy", "Aisha": "Aisha", "Norn": "Norn"
    }

    def apply_glossary(text, reverse=False):
        # Ordenar por longitud descendente para evitar reemplazar partes de nombres
        sorted_keys = sorted(glossary.keys(), key=len, reverse=True)
        for key in sorted_keys:
            value = glossary[key]
            if not reverse: text = text.replace(key, f" {key} ")
            else: text = text.replace(f" {key} ", value)
        return text

    print(f"Extracting text...")
    text_chunks = []
    with open(input_pdf, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            raw_text = page.extract_text()
            text_chunks.append(clean_text(raw_text))
    
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
                outputs = model.generate(**inputs, num_beams=4, repetition_penalty=1.5)
            result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            result = apply_glossary(result, reverse=True)
            translated_paragraphs.append(clean_text(result))
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

    print("Phase 2: Refining gender, consistency and dialogues...")
    final_text = []
    prev_paragraph = "" # Memoria de corto plazo para el refinador
    
    for page_idx, translated_page in enumerate(tqdm(raw_translations, desc="Refining")):
        if not translated_page.strip():
            final_text.append("")
            continue
            
        paragraphs = [p for p in translated_page.split('\n\n') if p.strip()]
        refined_paragraphs = []
        
        for para in paragraphs:
            # Contexto previo simplificado pero eficaz
            context_header = f"[Contexto: Escena con {', '.join(glossary.keys())[:50]}]"
            
            prompt = (
                "Eres un transcriptor profesional de Novelas Ligeras Japonesas. "
                "Convierte este borrador de traducción en prosa impecable.\n\n"
                "REGLAS DE ORO DE DIÁLOGO:\n"
                "- CUALQUER habla debe ir en su PROPIA LÍNEA.\n"
                "- Usa el guion largo (—) en lugar de comillas. Ejemplo: —Hola, Rudeus —dijo Eris—, ¿cómo estás?\n"
                "- Si el párrafo contiene una descripción y un diálogo, SE PÁRALOS en dos líneas distintas.\n\n"
                "ESTILO Y PERSONAJES:\n"
                "- Género: Eris/Aisha/Zenith (Femenino), Rudeus/Paul (Masculino).\n"
                "- NO traduzcas nombres propios (Rudeus, Eris, Aisha, Zenith).\n"
                "- Prohibido añadir comentarios como 'Aquí tienes' o 'He editado'. Devuelve solo narrativa.\n\n"
                f"{context_header}\n"
                f"BORRADOR A LIMPIAR: {para}"
            )
            
            messages = [{"role": "user", "content": prompt}]
            text = refiner_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            model_inputs = refiner_tokenizer([text], return_tensors="pt").to(device)

            with torch.no_grad():
                generated_ids = refiner_model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=768, 
                    temperature=0.1, # Muy baja para evitar alucinaciones como Aristotle
                    repetition_penalty=1.4, # Más fuerte para evitar bucles de guiones
                    do_sample=False, # Determinista para consistencia
                    top_p=0.9
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]
                response = refiner_tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            refined_para = response.strip()
            
            # Post-procesado manual de seguridad
            refined_para = refined_para.replace("Arus", "Rudeus")
            refined_para = clean_text(refined_para)
            
            # Si el modelo alucina y el output es demasiado corto o vacío, usamos el original
            if len(refined_para) < 10 and len(para) > 15:
                refined_para = para
                
            refined_paragraphs.append(refined_para)
            prev_paragraph = refined_para 
        
        final_text.append("\n\n".join(refined_paragraphs))
        
        # Guardado de seguridad cada 5 páginas
        if (page_idx + 1) % 5 == 0:
            with open(f"output/progress_backup_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write("\n\n=== PAGINA ===\n\n".join(final_text))

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
