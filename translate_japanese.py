import torch
from transformers import MarianTokenizer, MarianMTModel
import PyPDF2
from tqdm import tqdm
import os

class JAToESTranslator:
    def __init__(self, model_name="Helsinki-NLP/opus-mt-ja-es"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading Japanese-Spanish model {model_name} on {self.device}...")
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name).to(self.device).eval()

    def translate(self, text, max_length=128):
        if not text.strip(): return ""
        
        # Split into smaller sentences for Japanese (Japanese uses '。' or '！' or '？')
        import re
        sentences = re.split('([。！？])', text.replace('\n', ''))
        # Rejoin separators
        sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
        
        translated = []
        for sent in sentences:
            if not sent.strip(): continue
            inputs = self.tokenizer(sent, return_tensors="pt", truncation=True, max_length=max_length).to(self.device)
            with torch.no_grad():
                outputs = self.model.generate(**inputs, num_beams=4)
            translated.append(self.tokenizer.decode(outputs[0], skip_special_tokens=True))
            
        return " ".join(translated)

def translate_japanese_file(file_path):
    translator = JAToESTranslator()
    
    # Simple text file loading
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Process by paragraphs
    paragraphs = content.split('\n\n')
    print(f"Translating {len(paragraphs)} paragraphs from Japanese...")
    
    final_translation = []
    for p in tqdm(paragraphs):
        final_translation.append(translator.translate(p))
        
    output_path = file_path.replace('.txt', '_ES.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(final_translation))
    print(f"Complete! Saved to {output_path}")

if __name__ == "__main__":
    # If the user has a japenese source as text
    # translate_japanese_file("source_ja.txt")
    print("Japanese-Spanish translator ready. Use translate_japanese_file('your_file.txt') to begin.")
