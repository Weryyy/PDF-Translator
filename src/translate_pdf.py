#!/usr/bin/env python3
"""
PDF Translator - Translate PDF documents using language models
"""

import sys
import os
import json
import argparse
import re
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import PyPDF2
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from openai import OpenAI
    from dotenv import load_dotenv
    
    # Optional: for local model inference
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        LOCAL_MODEL_AVAILABLE = True
    except ImportError:
        LOCAL_MODEL_AVAILABLE = False
        
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)


class PDFTranslator:
    """Main class for PDF translation functionality"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the PDF translator with configuration"""
        self.config = self._load_config(config_path)
        self.use_local_model = self.config.get("use_local_model", False)
        
        if self.use_local_model:
            self._setup_local_model()
        else:
            self._setup_openai()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file or environment variables"""
        config = {
            "model": "gpt-3.5-turbo",
            "source_language": "auto",
            "target_language": "es",
            "max_tokens": 2000,
            "use_local_model": False,
            "local_model_path": "./models/translation_model"
        }
        
        # Try to load from config file
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Load environment variables
        load_dotenv()
        
        # Get API key from config or environment (only if not using local model)
        if not config.get("use_local_model", False):
            api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your-api-key-here":
                print("Error: OpenAI API key not found!")
                print("Please set OPENAI_API_KEY environment variable or add it to config/config.json")
                print("Or set 'use_local_model': true in config/config.json to use a local model")
                sys.exit(1)
            config["openai_api_key"] = api_key
        
        return config
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        self.client = OpenAI(api_key=self.config["openai_api_key"])
        print("Using OpenAI API for translation")
    
    def _setup_local_model(self):
        """Setup local translation model with automatic optimizations"""
        if not LOCAL_MODEL_AVAILABLE:
            print("Error: Local model support requires torch and transformers")
            print("Install with: pip install torch transformers")
            sys.exit(1)
        
        model_path = self.config.get("local_model_path", "./models/translation_model")
        
        if not os.path.exists(model_path):
            print(f"Error: Local model not found at {model_path}")
            print("Please train a model first using train_model_hpc.py")
            sys.exit(1)
        
        print("="*60)
        print("Loading Local Translation Model")
        print("="*60)
        print(f"Model path: {model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()
        
        print(f"✓ Device: {self.device}")
        
        # Enable all GPU optimizations
        if self.device == "cuda":
            try:
                self.model = self.model.half()
                print("✓ Mixed precision (FP16) enabled - 2x speedup")
            except:
                print("⚠ Mixed precision not supported")
            
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.enabled = True
            print("✓ CuDNN optimizations enabled")
            
            # TF32 for Ampere GPUs
            if torch.cuda.get_device_capability()[0] >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                print("✓ TensorFloat-32 enabled")
            
            print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
        
        print("="*60)
        print()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        print(f"Extracting text from {pdf_path}...")
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"Total pages: {total_pages}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    print(f"Processing page {page_num}/{total_pages}...")
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise
    
    def translate_text(self, text: str, target_language: str = None) -> str:
        """Translate text using OpenAI API or local model"""
        if not text.strip():
            return ""
        
        target_lang = target_language or self.config["target_language"]
        
        print(f"Translating text to {target_lang}...")
        
        # Split text into chunks if it's too long
        max_chunk_size = 3000  # characters
        chunks = self._split_text(text, max_chunk_size)
        
        translated_chunks = []
        
        for i, chunk in enumerate(chunks, 1):
            print(f"Translating chunk {i}/{len(chunks)}...")
            
            if self.use_local_model:
                translated_text = self._translate_with_local_model(chunk)
            else:
                translated_text = self._translate_with_openai(chunk, target_lang)
            
            if translated_text:
                translated_chunks.append(translated_text)
        
        return "\n\n".join(translated_chunks)
    
    def _translate_with_openai(self, chunk: str, target_lang: str) -> str:
        """Translate using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=[
                    {"role": "system", "content": f"You are a professional translator. Translate the following text to {target_lang}. Maintain the original formatting and structure."},
                    {"role": "user", "content": chunk}
                ],
                max_tokens=self.config["max_tokens"],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error translating with OpenAI: {e}")
            return f"[Translation error: {str(e)}]"
    
    def _translate_with_local_model(self, chunk: str) -> str:
        """Translate using local model"""
        try:
            # Tokenize
            inputs = self.tokenizer(
                chunk,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode
            translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translation
            
        except Exception as e:
            print(f"Error translating with local model: {e}")
            return f"[Translation error: {str(e)}]"
    
    def _split_text(self, text: str, max_size: int) -> list:
        """Split text into smaller chunks"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If single paragraph is too long, split by sentences
                if len(para) > max_size:
                    # Simple sentence boundary detection
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    temp_chunk = ""
                    for sent in sentences:
                        if len(temp_chunk) + len(sent) + 1 <= max_size:
                            if temp_chunk:
                                temp_chunk += " " + sent
                            else:
                                temp_chunk = sent
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = sent
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def save_as_pdf(self, text: str, output_path: str):
        """Save translated text as PDF"""
        print(f"Saving translated PDF to {output_path}...")
        
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Split text into paragraphs
            paragraphs = text.split('\n\n')
            
            for para in paragraphs:
                if para.strip():
                    p = Paragraph(para.strip(), styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 0.2*inch))
            
            doc.build(story)
            print(f"Successfully saved translated PDF!")
        except Exception as e:
            print(f"Error saving PDF: {e}")
            raise
    
    def translate_pdf(self, input_pdf: str, output_pdf: Optional[str] = None, 
                     target_language: Optional[str] = None) -> str:
        """Main method to translate a PDF file"""
        # Generate output filename if not provided
        if not output_pdf:
            input_path = Path(input_pdf)
            output_pdf = str(input_path.parent / f"{input_path.stem}_translated.pdf")
        
        print(f"Starting PDF translation...")
        print(f"Input: {input_pdf}")
        print(f"Output: {output_pdf}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(input_pdf)
        
        if not text:
            print("Warning: No text extracted from PDF!")
            return output_pdf
        
        print(f"Extracted {len(text)} characters")
        
        # Translate text
        translated_text = self.translate_text(text, target_language)
        
        # Save as new PDF
        self.save_as_pdf(translated_text, output_pdf)
        
        print(f"\n✓ Translation complete!")
        print(f"Output file: {output_pdf}")
        
        return output_pdf


def main():
    """Main entry point for the command-line interface"""
    parser = argparse.ArgumentParser(
        description="Translate PDF documents using language models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python translate_pdf.py document.pdf
  python translate_pdf.py document.pdf -o output.pdf
  python translate_pdf.py document.pdf -l en
  python translate_pdf.py document.pdf -l es -c custom_config.json
        """
    )
    
    parser.add_argument(
        'input_pdf',
        help='Path to the input PDF file to translate'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Path to the output PDF file (default: input_translated.pdf)',
        default=None
    )
    
    parser.add_argument(
        '-l', '--language',
        help='Target language for translation (default: from config)',
        default=None
    )
    
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (default: config/config.json)',
        default='config/config.json'
    )
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file not found: {args.input_pdf}")
        sys.exit(1)
    
    try:
        # Initialize translator
        translator = PDFTranslator(config_path=args.config)
        
        # Translate PDF
        translator.translate_pdf(
            input_pdf=args.input_pdf,
            output_pdf=args.output,
            target_language=args.language
        )
        
    except KeyboardInterrupt:
        print("\n\nTranslation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
