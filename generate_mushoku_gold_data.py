import os
import json
import torch
import random
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

def get_random_chunks(corpus_path, n_chunks=50, chunk_size=2000):
    if not os.path.exists(corpus_path):
        return []
    
    with open(corpus_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    chunks = []
    total_len = len(text)
    for _ in range(n_chunks):
        start = random.randint(0, max(0, total_len - chunk_size))
        chunks.append(text[start:start + chunk_size])
    return chunks

def generate_parallel_synthetic_data(corpus_path, output_file, mode="en2es", n_samples=300):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_id = "Qwen/Qwen2-1.5B-Instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
    
    # We want roughly n_samples, and each prompt generates ~5 samples
    chunks = get_random_chunks(corpus_path, n_chunks=max(1, n_samples // 5))
    dataset = []
    
    source_lang = "INGLÉS" if mode == "en2es" else "JAPONÉS"
    source_key = "en" if mode == "en2es" else "ja"
    
    print(f"\nGenerando datos sintéticos {mode} usando estilo de {corpus_path}...")
    
    for chunk in tqdm(chunks):
        prompt = (
            f"Basándote en el ESTILO de este fragmento de la novela 'Mushoku Tensei' en español:\n\n"
            f"--- Fragmento ---\n{chunk}\n-----------------\n\n"
            f"TAREA: Genera 5 pares de frases u oraciones (narración y diálogo). "
            f"El primer elemento de cada par debe estar en {source_lang} y el segundo debe ser su traducción al "
            f"ESPAÑOL conservando el estilo literario, los nombres exactos (Rudeus, Eris, Roxy, Sylphiette) y el uso de rayas de diálogo (—).\n"
            f"Regla de oro: El español debe sonar natural y profesional, no traducido por IA.\n"
            f"Devuelve estrictamente una LISTA JSON: [{{'{source_key}': '...', 'es': '...'}}, ...]"
        )

        messages = [
            {"role": "system", "content": "Eres un experto traductor literario de novelas ligeras japonesas."},
            {"role": "user", "content": prompt}
        ]
        
        text_input = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text_input, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=1000, temperature=0.8, repetition_penalty=1.1)
        
        response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
        
        try:
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                data = json.loads(response[json_start:json_end])
                dataset.extend(data)
        except Exception:
            continue
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
        
    print(f"Finalizado: {len(dataset)} pares guardados en {output_file}")

if __name__ == "__main__":
    corpus = "mushoku_es_corpus.txt"
    
    if os.path.exists(corpus):
        # Generar para EN-ES (para la versión traducida de Seven Seas)
        generate_parallel_synthetic_data(corpus, "mushoku_gold_en_es.json", mode="en2es", n_samples=300)
        # Generar para JA-ES (para la Web Novel original)
        generate_parallel_synthetic_data(corpus, "mushoku_gold_ja_es.json", mode="ja2es", n_samples=300)
    else:
        print(f"Error: {corpus} no encontrado. Ejecuta primero create_es_corpus.py")
