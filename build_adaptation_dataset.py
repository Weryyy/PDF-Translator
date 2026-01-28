import os
import json
import torch
from transformers import MarianMTModel, MarianTokenizer, AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import glob

# Configuración de modelos
JA_ES_MODEL = "Helsinki-NLP/opus-mt-ja-es"
LLM_MODEL = "Qwen/Qwen2-1.5B-Instruct"

class TrainingDataGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("Cargando modelo de traducción base (JA-ES)...")
        self.ja_es_tokenizer = MarianTokenizer.from_pretrained(JA_ES_MODEL)
        self.ja_es_model = MarianMTModel.from_pretrained(JA_ES_MODEL).to(self.device).to(torch.float16)
        
        print("Cargando modelo de refinamiento (LLM)...")
        self.llm_tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL, 
            torch_dtype=torch.float16, 
            device_map="auto"
        )
        
        # Cargar corpus de estilo para el prompt
        with open("mushoku_es_corpus.txt", "r", encoding="utf-8") as f:
            self.style_sample = f.read(5000)

    def translate_base(self, text):
        inputs = self.ja_es_tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            translated = self.ja_es_model.generate(**inputs)
        return self.ja_es_tokenizer.decode(translated[0], skip_special_tokens=True)

    def refine_style(self, original_ja, base_es):
        prompt = (
            f"Eres un experto editor de novelas ligeras. Refina la siguiente traducción del JAPONÉS al ESPAÑOL.\n"
            f"Usa este ESTILO DE REFERENCIA:\n{self.style_sample[:1000]}\n\n"
            f"ORIGINAL JAPONÉS: {original_ja}\n"
            f"TRADUCCIÓN BASE: {base_es}\n\n"
            f"TAREA: Devuelve la traducción refinada en un español natural, literario, "
            f"respetando los nombres (Rudeus, Eris, etc.) y usando rayas de diálogo (—).\n"
            f"SOLO devuelve el texto traducido, nada de explicaciones."
        )

        messages = [{"role": "user", "content": prompt}]
        text_input = self.llm_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.llm_tokenizer(text_input, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.llm_model.generate(**inputs, max_new_tokens=512, temperature=0.1)
        
        return self.llm_tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True).strip()

    def process_chapters(self, chapters_dir, output_file, max_pairs=1000):
        chapter_files = sorted(glob.glob(os.path.join(chapters_dir, "chapter_*.txt")))
        dataset = []
        
        print(f"Procesando capítulos para generar {max_pairs} pares de alta calidad...")
        
        pbar = tqdm(total=max_pairs)
        for cf in chapter_files:
            if len(dataset) >= max_pairs:
                break
                
            with open(cf, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines() if l.strip() and len(l.strip()) > 10]
            
            # Tomamos una muestra aleatoria o secuencial de líneas
            for line in lines:
                if len(dataset) >= max_pairs:
                    break
                
                try:
                    base_es = self.translate_base(line)
                    refined_es = self.refine_style(line, base_es)
                    
                    dataset.append({
                        "ja": line,
                        "es": refined_es
                    })
                    pbar.update(1)
                except Exception as e:
                    continue
        
        pbar.close()
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"Dataset de entrenamiento generado: {output_file} ({len(dataset)} pares)")

if __name__ == "__main__":
    generator = TrainingDataGenerator()
    generator.process_chapters("novels/n9669bk", "mushoku_training_dataset_ja_es.json", max_pairs=500)
