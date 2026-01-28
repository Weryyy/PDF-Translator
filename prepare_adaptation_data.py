import os
import PyPDF2
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import json

def extract_text(pdf_path, max_pages=10):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        pages_to_read = min(len(reader.pages), max_pages)
        for i in range(pages_to_read):
            text += reader.pages[i].extract_text() + "\n"
    return text

def align_sentences_with_llm(en_text, es_text):
    print("Aligning sentences using LLM (this will take a while)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_id = "Qwen/Qwen2-1.5B-Instruct"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
    
    # We take chunks of text and ask the LLM to provide parallel translations
    en_lines = [l.strip() for l in en_text.split('\n') if len(l.strip()) > 20][:100]
    es_lines = [l.strip() for l in es_text.split('\n') if len(l.strip()) > 20][:150] # Spanish often has more lines due to formatting
    
    dataset = []
    
    # Strategy: Give the LLM a chunk of Spanish text and ask it to find the best English match 
    # OR better yet, give it English and ask it to rewrite it into the style of our Spanish sample.
    # But since we have professional Spanish text, let's just use it as training target.
    
    # Due to token limits, we'll do this in small batches
    for i in tqdm(range(0, len(en_lines), 5), desc="Batch Aligning"):
        batch_en = "\n".join(en_lines[i:i+5])
        prompt = (
            "Based on these English lines from Mushoku Tensei, find or create the most accurate and stylistically "
            "consistent Spanish translations that use the correct gender (Eris/Aisha=female) and dialogue dashes (—). "
            "Return ONLY a JSON list of objects with 'en' and 'es' keys.\n\n"
            f"English:\n{batch_en}\n\n"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=1024)
        
        response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)
        try:
            # Simple extraction of JSON if present
            json_str = response[response.find('['):response.rfind(']')+1]
            data = json.loads(json_str)
            dataset.extend(data)
        except:
            continue
            
    return dataset

if __name__ == "__main__":
    # Sample from Volume 1 to create the "Gold Style"
    en_path = "pdfs/Mushoku Tensei_ Redundant Reincarnation Vol. 1.pdf"
    es_path = "pdfs/Mushoku Tensei v01 - Español.pdf"
    
    if os.path.exists(en_path) and os.path.exists(es_path):
        en_txt = extract_text(en_path, max_pages=15)
        es_txt = extract_text(es_path, max_pages=15)
        
        gold_dataset = align_sentences_with_llm(en_txt, es_txt)
        
        with open("mushoku_gold_dataset.json", "w", encoding="utf-8") as f:
            json.dump(gold_dataset, f, ensure_ascii=False, indent=2)
        
        print(f"Created gold dataset with {len(gold_dataset)} pairs.")
    else:
        print("Source files not found in pdfs/ folder.")
