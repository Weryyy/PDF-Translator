import os
import PyPDF2
from tqdm import tqdm

def extract_all_spanish_prose(folder_path="pdfs"):
    output_file = "mushoku_es_corpus.txt"
    es_files = [f for f in os.listdir(folder_path) if "Español" in f and f.endswith(".pdf")]
    
    all_text = ""
    print(f"Extracting prose from {len(es_files)} Spanish volumes...")
    
    for es_file in tqdm(es_files):
        path = os.path.join(folder_path, es_file)
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                # Skip the first 10 pages and last 10 (usually covers/indexes)
                start = 10
                end = len(reader.pages) - 10
                for i in range(start, end):
                    all_text += reader.pages[i].extract_text() + "\n"
        except Exception as e:
            print(f"Error reading {es_file}: {e}")
            
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_text)
    
    print(f"Grand Spanish Corpus created: {output_file} ({len(all_text)} chars)")

if __name__ == "__main__":
    extract_all_spanish_prose()
