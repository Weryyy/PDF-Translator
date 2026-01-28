import torch
from transformers import MarianTokenizer, MarianMTModel

def translate_test():
    model_path = "./models/translation_model"
    print(f"Loading local model from {model_path}...")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = MarianTokenizer.from_pretrained(model_path)
    model = MarianMTModel.from_pretrained(model_path).to(device)
    
    test_sentences = [
        "This is a technical document about artificial intelligence.",
        "The model was trained on synthetic data successfully.",
        "Deep learning requires significant GPU resources for large models.",
        "The translation process is now optimized for performance."
    ]
    
    print("\nStarting Translation Test:\n" + "="*50)
    
    model.eval()
    for text in test_sentences:
        # Tokenize
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
        
        # Generate
        with torch.no_grad():
            translated_tokens = model.generate(**inputs)
        
        # Decode
        result = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        
        print(f"English: {text}")
        print(f"Spanish: {result}")
        print("-" * 50)

if __name__ == "__main__":
    translate_test()
