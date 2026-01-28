import os
import torch
from transformers import MarianMTModel, MarianTokenizer, AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

# Rutas de los modelos entrenados
JA_ES_REFINED = "./models/mushoku_mt_ja_es_refined"
EN_ES_REFINED = "./models/mushoku_mt_en_es_refined"
LLM_MODEL = "Qwen/Qwen2-1.5B-Instruct"

class MushokuTranslatorV2:
    def __init__(self, mode="ja2es"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.mode = mode
        
        model_path = JA_ES_REFINED if mode == "ja2es" else EN_ES_REFINED
        print(f"Cargando modelo REFINADO: {model_path}")
        self.tokenizer = MarianTokenizer.from_pretrained(model_path)
        self.model = MarianMTModel.from_pretrained(model_path).to(self.device).to(torch.float16)
        
        print("Cargando LLM para refinamiento final...")
        self.llm_tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL, 
            torch_dtype=torch.float16, 
            device_map="auto"
        )

    def translate(self, text):
        # Paso 1: Traducción con modelo adaptado (Base)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            translated = self.model.generate(**inputs, max_new_tokens=256)
        base_es = self.tokenizer.decode(translated[0], skip_special_tokens=True)
        
        # Si la traducción base es muy corta o vacía, la devolvemos tal cual para no confundir al LLM
        if len(base_es.strip()) < 2:
            return base_es

        # Paso 2: Refinamiento con LLM (Estricto)
        system_prompt = (
            "Eres un traductor literario experto. Tu única tarea es pulir el estilo de la traducción al español. "
            "REGLAS CRÍTICAS:\n"
            "1. Usa rayas largas (—) para diálogos.\n"
            "2. Mantén coherencia de nombres (Rudeus, Eris, Roxy, Sylphiette).\n"
            "3. NO devuelvas NADA que no sea la historia traducida.\n"
            "4. Prohibido usar prefijos como 'Refinado:', 'Traducción:' o explicar lo que hiciste."
        )
        
        user_prompt = f"Traduce/Pule este texto de Mushoku Tensei:\n{base_es}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        text_input = self.llm_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.llm_tokenizer(text_input, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.llm_model.generate(
                **inputs, 
                max_new_tokens=256, 
                temperature=0.01, # Casi determinista
                repetition_penalty=1.2, # Evitar bucles
                do_sample=False
            )
        
        refined = self.llm_tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True).strip()
        
        # Limpieza agresiva de "coletillas" del modelo
        prefixes_to_clean = [
            "Refinada:", "Refinado:", "Traducción:", "Traducción refinada:", 
            "Texto corregido:", "Refinamiento:", "Nota:", "PROLOGO:", "Prólogo:"
        ]
        for prefix in prefixes_to_clean:
            if refined.startswith(prefix):
                refined = refined[len(prefix):].strip()
        
        # Eliminar comillas innecesarias que a veces añade el modelo al principio y final
        if refined.startswith('"') and refined.endswith('"'):
            refined = refined[1:-1]
            
        return refined

def translate_chapter(file_path, output_path, mode="ja2es"):
    translator = MushokuTranslatorV2(mode=mode)
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    translated_lines = []
    print(f"Traduciendo {file_path} con el modelo de adaptación...")
    for line in tqdm(lines):
        if line.strip():
            translated_lines.append(translator.translate(line.strip()))
        else:
            translated_lines.append("")
            
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(translated_lines))
    
    print(f"Capítulo guardado en {output_path}")

if __name__ == "__main__":
    import sys
    
    # Directorio de salida
    os.makedirs("translations_es", exist_ok=True)
    
    # Traducir los primeros 5 capítulos como prueba de fuego
    for i in range(1, 6):
        input_ch = f"novels/n9669bk/chapter_{i:03d}.txt"
        output_ch = f"translations_es/chapter_{i:03d}_ES.txt"
        
        if os.path.exists(input_ch):
            if os.path.exists(output_ch):
                print(f"Capítulo {i} ya existe, saltando...")
                continue
            translate_chapter(input_ch, output_ch, mode="ja2es")
        else:
            print(f"Capítulo {input_ch} no encontrado.")
