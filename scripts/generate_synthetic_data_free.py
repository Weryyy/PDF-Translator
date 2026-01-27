#!/usr/bin/env python3
"""
Free Synthetic Data Generator for Translation Model Training
Generates synthetic translation pairs WITHOUT using paid APIs

Supported Methods:
1. Ollama (Local LLM) - Completely free, runs locally
2. Hugging Face (Free tier) - Free with rate limits
3. Rule-based templates - No API needed, fully offline
4. Back-translation - Using free MarianMT models
5. Open Source Models (GPT-2, BLOOM, etc.) - Free, run locally
6. Corpus-based - Uses public domain books from Project Gutenberg

Usage examples:
  # Using Ollama (recommended - free and unlimited)
  python scripts/generate_synthetic_data_free.py -n 1000 -m ollama --ollama-model llama2

  # Using open source models (GPT-2, BLOOM, etc.)
  python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model gpt2

  # Using Hugging Face free tier
  python scripts/generate_synthetic_data_free.py -n 1000 -m huggingface

  # Using rule-based (fastest, no setup needed)
  python scripts/generate_synthetic_data_free.py -n 10000 -m rulebased

  # Using back-translation
  python scripts/generate_synthetic_data_free.py -n 5000 -m backtranslation
  
  # Using public domain corpus (high quality literature)
  python scripts/generate_synthetic_data_free.py -n 2000 -m corpus
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import random
from datetime import datetime

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)


class OllamaGenerator:
    """Generate synthetic data using Ollama (local, free LLM)"""
    
    def __init__(self, model_name: str = "llama2"):
        """Initialize Ollama generator"""
        self.model_name = model_name
        try:
            import requests
            self.requests = requests
            # Test connection
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                raise ConnectionError("Ollama not responding")
        except Exception as e:
            print("\n" + "="*60)
            print("ERROR: Ollama is not running!")
            print("="*60)
            print("\nOllama is a FREE tool to run LLMs locally.")
            print("\nTo install and use Ollama:")
            print("1. Install Ollama from: https://ollama.ai/")
            print("2. Run: ollama pull llama2")
            print("3. Start Ollama: ollama serve")
            print("4. Run this script again")
            print("\nAvailable models: llama2, mistral, codellama, etc.")
            print("="*60)
            sys.exit(1)
    
    def generate_with_ollama(self, prompt: str, temperature: float = 0.8) -> str:
        """Generate text using Ollama API"""
        try:
            response = self.requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"].strip()
            else:
                print(f"Ollama error: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    def generate_pair(self, source_lang: str, target_lang: str, 
                     domain: str, text_type: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a translation pair"""
        
        # Generate source text
        source_prompt = f"""Generate 2-3 sentences in {source_lang} about {domain}. 
Style: {text_type}. 
Output only the text, no explanations or quotes."""
        
        source_text = self.generate_with_ollama(source_prompt, temperature=0.8)
        if not source_text:
            return None, None
        
        # Generate translation
        translation_prompt = f"""Translate this {source_lang} text to {target_lang}:

{source_text}

Output only the translation, no explanations."""
        
        target_text = self.generate_with_ollama(translation_prompt, temperature=0.3)
        if not target_text:
            return None, None
        
        return source_text, target_text


class OpenSourceModelGenerator:
    """Generate synthetic data using open source models (GPT-2, BLOOM, etc.)"""
    
    AVAILABLE_MODELS = {
        "gpt2": {
            "name": "gpt2",
            "description": "OpenAI's GPT-2 (open source)",
            "size": "~500MB",
            "quality": "good"
        },
        "gpt2-medium": {
            "name": "gpt2-medium",
            "description": "GPT-2 Medium (better quality)",
            "size": "~1.5GB",
            "quality": "very good"
        },
        "gpt2-large": {
            "name": "gpt2-large",
            "description": "GPT-2 Large (best quality)",
            "size": "~3GB",
            "quality": "excellent"
        },
        "bloom-560m": {
            "name": "bigscience/bloom-560m",
            "description": "BLOOM 560M (multilingual)",
            "size": "~1GB",
            "quality": "good"
        },
        "bloom-1b7": {
            "name": "bigscience/bloom-1b7",
            "description": "BLOOM 1.7B (better multilingual)",
            "size": "~3.5GB",
            "quality": "very good"
        },
        "distilgpt2": {
            "name": "distilgpt2",
            "description": "Distilled GPT-2 (faster, smaller)",
            "size": "~350MB",
            "quality": "good"
        }
    }
    
    def __init__(self, model_name: str = "gpt2"):
        """Initialize open source model generator"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, MarianMTModel, MarianTokenizer
            import torch
            
            print(f"\nLoading open source model: {model_name}")
            print("This may take a few minutes on first run (downloading model)...")
            
            # Get full model name
            if model_name in self.AVAILABLE_MODELS:
                full_model_name = self.AVAILABLE_MODELS[model_name]["name"]
                print(f"Model: {self.AVAILABLE_MODELS[model_name]['description']}")
                print(f"Size: {self.AVAILABLE_MODELS[model_name]['size']}")
            else:
                full_model_name = model_name
                print(f"Using custom model: {model_name}")
            
            # Load text generation model
            self.tokenizer = AutoTokenizer.from_pretrained(full_model_name)
            self.model = AutoModelForCausalLM.from_pretrained(full_model_name)
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load translation model
            print("Loading translation model...")
            self.trans_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            self.trans_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            
            # Move to GPU if available
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
            self.trans_model = self.trans_model.to(self.device)
            
            print(f"Models loaded successfully! Using device: {self.device}")
            print()
            
        except ImportError as e:
            print(f"\nError: Required libraries not found: {e}")
            print("Please install: pip install transformers torch")
            sys.exit(1)
        except Exception as e:
            print(f"\nError loading model: {e}")
            print("\nTry a different model or check your internet connection.")
            print("Available models: gpt2, gpt2-medium, gpt2-large, bloom-560m, distilgpt2")
            sys.exit(1)
    
    def generate_text(self, prompt: str, max_length: int = 100, temperature: float = 0.8) -> str:
        """Generate text using the open source model"""
        try:
            import torch
            
            inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the generated text
            generated_text = generated_text.replace(prompt, "").strip()
            
            return generated_text
            
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""
    
    def translate_text(self, text: str) -> str:
        """Translate text to Spanish"""
        try:
            import torch
            
            inputs = self.trans_tokenizer([text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                translated = self.trans_model.generate(**inputs, max_length=512)
            
            translation = self.trans_tokenizer.decode(translated[0], skip_special_tokens=True)
            return translation
            
        except Exception as e:
            print(f"Error translating: {e}")
            return ""
    
    def generate_pair(self, source_lang: str, target_lang: str,
                     domain: str, text_type: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a translation pair"""
        
        # Create prompt for text generation
        prompt = f"Write about {domain} as a {text_type}: "
        
        # Generate source text
        source_text = self.generate_text(prompt, max_length=150, temperature=0.8)
        
        if not source_text or len(source_text) < 10:
            return None, None
        
        # Clean up the text (take first few sentences)
        sentences = source_text.split('.')[:3]  # Take max 3 sentences
        source_text = '.'.join(sentences).strip() + '.'
        
        # Translate to target language
        target_text = self.translate_text(source_text)
        
        if not target_text or len(target_text) < 5:
            return None, None
        
        return source_text, target_text


class HuggingFaceGenerator:
    """Generate synthetic data using Hugging Face free API"""
    
    # Available models for text generation (all free on HuggingFace)
    TEXT_MODELS = {
        "mistral": "mistralai/Mistral-7B-Instruct-v0.1",
        "flan-t5": "google/flan-t5-large",
        "flan-t5-xl": "google/flan-t5-xl",
        "bloom": "bigscience/bloom-560m",
        "gpt2": "gpt2",
        "gpt2-large": "gpt2-large",
    }
    
    # Available translation models (all free)
    TRANSLATION_MODELS = {
        "en-es": "Helsinki-NLP/opus-mt-en-es",
        "en-fr": "Helsinki-NLP/opus-mt-en-fr",
        "en-de": "Helsinki-NLP/opus-mt-en-de",
        "en-it": "Helsinki-NLP/opus-mt-en-it",
        "en-pt": "Helsinki-NLP/opus-mt-en-pt",
        "en-ru": "Helsinki-NLP/opus-mt-en-ru",
        "en-zh": "Helsinki-NLP/opus-mt-en-zh",
    }
    
    def __init__(self, api_token: Optional[str] = None, text_model: str = "flan-t5"):
        """Initialize HuggingFace generator"""
        try:
            import requests
            self.requests = requests
        except ImportError:
            print("Error: requests library required")
            sys.exit(1)
        
        # Get HF token (free tier available)
        self.api_token = api_token or os.getenv("HUGGINGFACE_TOKEN")
        
        print("\n" + "="*60)
        print("🤗 HUGGING FACE FREE TIER")
        print("="*60)
        
        if not self.api_token:
            print("⚠️  Token no encontrado - usando límites públicos")
            print("\nPara obtener GRATIS más límites:")
            print("1. Crear cuenta gratuita: https://huggingface.co/join")
            print("2. Obtener token gratis: https://huggingface.co/settings/tokens")
            print("3. Exportar: export HUGGINGFACE_TOKEN=tu_token")
            print("\nVentajas del token gratuito:")
            print("  ✅ Más requests por hora")
            print("  ✅ Acceso prioritario a modelos")
            print("  ✅ Sin límite de tiempo")
            print("  ✅ 100% GRATIS (no requiere tarjeta)")
        else:
            print("✅ Token detectado - usando límites mejorados")
            print("📊 Límites aproximados: ~1000 requests/hora")
            print("💰 Costo: $0.00 (tier gratuito)")
        
        print("="*60 + "\n")
        
        self.headers = {}
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"
        
        # Select text generation model
        self.text_model = self.TEXT_MODELS.get(text_model, text_model)
        print(f"📝 Modelo de texto: {self.text_model}")
        print(f"🔄 Modelo de traducción: Helsinki-NLP/opus-mt-en-es")
        print()
    
    def generate_with_hf(self, prompt: str, model: Optional[str] = None, max_tokens: int = 250) -> Optional[str]:
        """Generate text using HuggingFace Inference API"""
        if model is None:
            model = self.text_model
        
        try:
            # Use text generation API (usando nuevo endpoint de HuggingFace)
            response = self.requests.post(
                f"https://router.huggingface.co/models/{model}",
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "do_sample": True,
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        text = result[0]["generated_text"]
                        # Remove prompt from response
                        text = text.replace(prompt, "").strip()
                        return text
                    return str(result[0]).strip()
                elif isinstance(result, dict) and "generated_text" in result:
                    text = result["generated_text"]
                    text = text.replace(prompt, "").strip()
                    return text
                
                return str(result).strip()
                
            elif response.status_code == 401:
                print(f"❌ Error 401: Token inválido o no autenticado")
                print(f"⚠️  Sin token válido, cambiando a generador basado en reglas...")
                return None
                
            elif response.status_code == 503:
                print(f"⏳ Modelo cargándose... (primera vez puede tardar ~20 segundos)")
                # Wait and retry
                import time
                time.sleep(20)
                return self.generate_with_hf(prompt, model, max_tokens)
                
            elif response.status_code == 429:
                print(f"⚠️  Rate limit alcanzado. Esperando 60 segundos...")
                import time
                time.sleep(60)
                return self.generate_with_hf(prompt, model, max_tokens)
                
            else:
                print(f"❌ Error API: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Detalle: {error_detail}")
                except Exception:
                    pass
                return None
                
        except self.requests.exceptions.Timeout:
            print(f"⏱️  Timeout - reintentando...")
            return None
        except Exception as e:
            print(f"❌ Error llamando a HuggingFace: {e}")
            return None
    
    def translate_with_hf(self, text: str, source_lang: str = "English", target_lang: str = "Spanish") -> Optional[str]:
        """Translate text using HuggingFace translation models"""
        
        # Map language pairs to models
        if source_lang.lower() == "english" and target_lang.lower() == "spanish":
            model = self.TRANSLATION_MODELS["en-es"]
        elif source_lang.lower() == "english" and target_lang.lower() == "french":
            model = self.TRANSLATION_MODELS["en-fr"]
        elif source_lang.lower() == "english" and target_lang.lower() == "german":
            model = self.TRANSLATION_MODELS["en-de"]
        else:
            model = self.TRANSLATION_MODELS["en-es"]  # Default
        
        try:
            response = self.requests.post(
                f"https://router.huggingface.co/models/{model}",
                headers=self.headers,
                json={"inputs": text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    if "translation_text" in result[0]:
                        return result[0]["translation_text"]
                return None
                
            elif response.status_code == 503:
                print(f"⏳ Modelo de traducción cargándose...")
                import time
                time.sleep(15)
                return self.translate_with_hf(text, source_lang, target_lang)
                
            elif response.status_code == 429:
                print(f"⚠️  Rate limit - esperando...")
                import time
                time.sleep(60)
                return self.translate_with_hf(text, source_lang, target_lang)
            else:
                print(f"❌ Error de traducción: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error traduciendo: {e}")
            return None
    
    def generate_pair(self, source_lang: str, target_lang: str,
                     domain: str, text_type: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a translation pair"""
        
        # Create a more detailed prompt for better quality
        prompt = f"""Write 2-3 sentences in English about {domain}.
Style: {text_type}
Topic: {domain}

Text:"""
        
        # Generate source text
        source_text = self.generate_with_hf(prompt, max_tokens=200)
        
        if not source_text or len(source_text) < 20:
            print(f"⚠️  Texto generado muy corto o vacío")
            return None, None
        
        # Clean up source text (take first few sentences)
        sentences = source_text.split('.')[:3]
        source_text = '.'.join(sentences).strip()
        if not source_text.endswith('.'):
            source_text += '.'
        
        # Translate to target language
        target_text = self.translate_with_hf(source_text, source_lang, target_lang)
        
        if not target_text or len(target_text) < 10:
            print(f"⚠️  Traducción vacía o muy corta")
            return None, None
        
        return source_text, target_text


class RuleBasedGenerator:
    """Generate synthetic data using rule-based templates (completely offline)"""
    
    # Template sentences for different domains
    TEMPLATES = {
        "technology": [
            "The {device} runs on {os} and has {feature}.",
            "New {product} released with improved {aspect}.",
            "Software update {version} includes {improvement}.",
            "{company} announces {innovation} for {market}.",
            "The {application} allows users to {action}.",
        ],
        "science": [
            "Research shows that {subject} affects {outcome}.",
            "Scientists discovered {finding} in {location}.",
            "The study of {field} reveals {insight}.",
            "Experiments demonstrate {phenomenon} under {condition}.",
            "New theory explains {concept} through {mechanism}.",
        ],
        "business": [
            "The company reported {metric} in the {period}.",
            "{business} expands operations to {market}.",
            "Sales increased by {percentage} due to {reason}.",
            "New {strategy} improves {aspect} significantly.",
            "Partnership between {company1} and {company2} announced.",
        ],
        "general": [
            "Today {subject} is {description}.",
            "Many people believe that {statement}.",
            "It is important to {action} when {condition}.",
            "The {item} provides {benefit} for {user}.",
            "According to {source}, {fact}.",
        ],
    }
    
    VOCABULARY = {
        "device": ["smartphone", "laptop", "tablet", "computer", "server"],
        "os": ["Android", "iOS", "Windows", "Linux", "macOS"],
        "feature": ["advanced security", "long battery life", "high performance", "AI capabilities"],
        "product": ["software", "hardware", "application", "service", "platform"],
        "aspect": ["performance", "security", "usability", "efficiency", "design"],
        "company": ["Microsoft", "Google", "Apple", "Amazon", "Meta"],
        "subject": ["weather", "economy", "technology", "health", "education"],
        "finding": ["a new species", "a cure", "evidence", "a correlation", "patterns"],
        "metric": ["strong growth", "increased revenue", "record profits", "positive results"],
        "percentage": ["15%", "20%", "30%", "50%", "75%"],
    }
    
    # Simple translation dictionary (for demonstration)
    TRANSLATIONS = {
        "English_Spanish": {
            "The": "El", "is": "es", "and": "y", "has": "tiene",
            "New": "Nuevo", "with": "con", "for": "para",
            "Many": "Muchos", "people": "personas", "believe": "creen",
            "that": "que", "important": "importante", "to": "a",
        }
    }
    
    def __init__(self):
        """Initialize rule-based generator"""
        # Load translation model for better quality
        try:
            from transformers import MarianMTModel, MarianTokenizer
            self.use_model = True
            print("Loading translation model for rule-based generation...")
            model_name = "Helsinki-NLP/opus-mt-en-es"
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
            print("Translation model loaded successfully!")
        except Exception as e:
            print(f"Note: Using simple templates (translation model not available: {e})")
            self.use_model = False
    
    def fill_template(self, template: str) -> str:
        """Fill template with random vocabulary"""
        result = template
        for key, values in self.VOCABULARY.items():
            if f"{{{key}}}" in result:
                result = result.replace(f"{{{key}}}", random.choice(values))
        
        # Fill any remaining placeholders with generic terms
        import re
        placeholders = re.findall(r'\{(\w+)\}', result)
        for ph in placeholders:
            result = result.replace(f"{{{ph}}}", f"[{ph}]")
        
        return result
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using model or simple dictionary"""
        if self.use_model and source_lang == "English" and target_lang == "Spanish":
            try:
                inputs = self.tokenizer([text], return_tensors="pt", padding=True)
                translated = self.model.generate(**inputs)
                return self.tokenizer.decode(translated[0], skip_special_tokens=True)
            except Exception as e:
                print(f"Translation error: {e}")
        
        # Fallback to simple word replacement
        words = text.split()
        trans_key = f"{source_lang}_{target_lang}"
        trans_dict = self.TRANSLATIONS.get(trans_key, {})
        
        translated_words = [trans_dict.get(word, word) for word in words]
        return " ".join(translated_words)
    
    def generate_pair(self, source_lang: str, target_lang: str,
                     domain: str, text_type: str) -> Tuple[str, str]:
        """Generate a translation pair using templates"""
        
        # Select template domain
        template_domain = domain if domain in self.TEMPLATES else "general"
        
        # Generate 1-3 sentences
        num_sentences = random.randint(1, 3)
        sentences = []
        
        for _ in range(num_sentences):
            template = random.choice(self.TEMPLATES[template_domain])
            sentence = self.fill_template(template)
            sentences.append(sentence)
        
        source_text = " ".join(sentences)
        target_text = self.translate_text(source_text, source_lang, target_lang)
        
        return source_text, target_text


class BackTranslationGenerator:
    """Generate synthetic data using back-translation technique"""
    
    def __init__(self):
        """Initialize back-translation generator"""
        print("Loading MarianMT translation models...")
        print("This might take a moment on first run...")
        
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            # English -> Spanish
            self.en_es_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            self.en_es_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            
            # Spanish -> English
            self.es_en_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-en")
            self.es_en_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-en")
            
            print("✓ Models loaded successfully")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            print("Install transformers: pip install transformers")
            sys.exit(1)
        
        # Base sentences for back-translation
        self.base_sentences = [
            "The rapid advancement of technology has transformed modern society.",
            "Climate change poses significant challenges to global ecosystems.",
            "Effective communication is essential for successful collaboration.",
            "Innovation drives economic growth and competitiveness.",
            "Education plays a crucial role in personal development.",
            "Data analysis helps organizations make informed decisions.",
            "Quality assurance ensures product reliability and customer satisfaction.",
            "Research and development accelerate scientific progress.",
            "Digital transformation changes how businesses operate.",
            "Sustainable practices protect environmental resources.",
        ]


class CorpusBasedGenerator:
    """Generate synthetic data from public domain corpus"""
    
    def __init__(self, corpus_file: str = None):
        """Initialize corpus-based generator"""
        if corpus_file and os.path.exists(corpus_file):
            self.corpus_file = corpus_file
            print(f"Loading corpus from {corpus_file}...")
            with open(corpus_file, 'r', encoding='utf-8') as f:
                corpus_data = json.load(f)
            self.pairs = [(p["source"], p["target"]) for p in corpus_data.get("pairs", [])]
            print(f"✓ Loaded {len(self.pairs)} translation pairs from corpus")
        else:
            print("No corpus file provided or file not found.")
            print("Building corpus from public domain books...")
            # Import and use public domain corpus builder
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            try:
                from public_domain_corpus import PublicDomainCorpus
                corpus = PublicDomainCorpus()
                # Build a small corpus with one book
                corpus_file = corpus.build_corpus_dataset(
                    output_dir="./corpus_data",
                    books=["alice_wonderland"],  # Start with Alice in Wonderland
                    pairs_per_book=500
                )
                self.corpus_file = corpus_file
                # Reload the pairs
                with open(corpus_file, 'r', encoding='utf-8') as f:
                    corpus_data = json.load(f)
                self.pairs = [(p["source"], p["target"]) for p in corpus_data.get("pairs", [])]
            except Exception as e:
                print(f"Error building corpus: {e}")
                print("Falling back to empty corpus")
                self.pairs = []
    
    def generate_pair(self, source_lang: str, target_lang: str,
                     domain: str, text_type: str) -> Tuple[str, str]:
        """Generate pair from corpus"""
        if not self.pairs:
            return "", ""
        
        # Return a random pair from corpus
        return random.choice(self.pairs)


class BackTranslationGenerator:
    """Generate synthetic data using back-translation technique"""
    
    def __init__(self):
        """Initialize back-translation generator"""
        try:
            from transformers import MarianMTModel, MarianTokenizer
            
            print("Loading translation models for back-translation...")
            # Load both directions
            self.en_es_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            self.en_es_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-es")
            
            self.es_en_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-en")
            self.es_en_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-en")
            
            print("Models loaded successfully!")
            
        except Exception as e:
            print(f"Error loading translation models: {e}")
            print("Please install transformers: pip install transformers")
            sys.exit(1)
        
        # Load base sentences from common sources
        self.base_sentences = self._load_base_sentences()
    
    def _load_base_sentences(self) -> List[str]:
        """Load or generate base sentences"""
        # Common English sentences for back-translation
        return [
            "The weather is beautiful today.",
            "Technology continues to advance rapidly.",
            "Education is essential for personal development.",
            "Healthcare systems face many challenges.",
            "Climate change affects everyone globally.",
            "Artificial intelligence transforms industries.",
            "Renewable energy becomes more affordable.",
            "Global trade connects distant markets.",
            "Scientific research drives innovation.",
            "Cultural diversity enriches society.",
            # Add more base sentences...
        ] * 10  # Repeat to get more variations
    
    def translate_en_to_es(self, text: str) -> str:
        """Translate English to Spanish"""
        try:
            inputs = self.en_es_tokenizer([text], return_tensors="pt", padding=True)
            translated = self.en_es_model.generate(**inputs, max_length=512)
            return self.en_es_tokenizer.decode(translated[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Translation error: {e}")
            return ""
    
    def translate_es_to_en(self, text: str) -> str:
        """Translate Spanish to English"""
        try:
            inputs = self.es_en_tokenizer([text], return_tensors="pt", padding=True)
            translated = self.es_en_model.generate(**inputs, max_length=512)
            return self.es_en_tokenizer.decode(translated[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Translation error: {e}")
            return ""
    
    def generate_pair(self, source_lang: str, target_lang: str,
                     domain: str, text_type: str) -> Tuple[str, str]:
        """Generate pair using back-translation"""
        
        # Get random base sentence
        base_text = random.choice(self.base_sentences)
        
        if source_lang == "English" and target_lang == "Spanish":
            # Forward translation
            target_text = self.translate_en_to_es(base_text)
            # Back translation creates variation
            source_text = self.translate_es_to_en(target_text)
            
            # Use back-translated as source for variety
            return source_text if source_text else base_text, target_text
        else:
            # For other language pairs, use base directly
            return base_text, self.translate_en_to_es(base_text)


class FreeSyntheticDataGenerator:
    """Main generator supporting multiple free methods"""
    
    DOMAINS = [
        "technology", "science", "medicine", "business", "literature",
        "history", "law", "education", "engineering", "philosophy",
        "psychology", "economics", "politics", "sports", "entertainment",
    ]
    
    TEXT_TYPES = [
        "technical document", "news article", "academic paper",
        "blog post", "email", "product description",
        "instruction manual", "research abstract",
    ]
    
    def __init__(self, method: str = "rulebased", **kwargs):
        """Initialize generator with specified method"""
        self.method = method
        self.output_dir = Path("synthetic_data")
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"\nInitializing {method} generator...")
        
        if method == "ollama":
            self.generator = OllamaGenerator(kwargs.get("ollama_model", "llama2"))
        elif method == "opensource":
            self.generator = OpenSourceModelGenerator(kwargs.get("os_model", "gpt2"))
        elif method == "huggingface":
            self.generator = HuggingFaceGenerator(
                api_token=kwargs.get("hf_token"),
                text_model=kwargs.get("hf_text_model", "flan-t5")
            )
        elif method == "rulebased":
            self.generator = RuleBasedGenerator()
        elif method == "backtranslation":
            self.generator = BackTranslationGenerator()
        elif method == "corpus":
            self.generator = CorpusBasedGenerator(kwargs.get("corpus_file"))
        else:
            raise ValueError(f"Unknown method: {method}")
        
        print(f"Generator initialized successfully!\n")
    
    def generate_batch(self, num_pairs: int, source_lang: str, target_lang: str,
                      batch_id: int) -> pd.DataFrame:
        """Generate a batch of translation pairs"""
        
        data = []
        
        print(f"\nGenerating batch {batch_id} with {num_pairs} pairs using {self.method}...")
        
        for i in range(num_pairs):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{num_pairs} pairs...")
            
            domain = random.choice(self.DOMAINS)
            text_type = random.choice(self.TEXT_TYPES)
            
            try:
                source_text, target_text = self.generator.generate_pair(
                    source_lang, target_lang, domain, text_type
                )
                
                if source_text and target_text:
                    data.append({
                        "id": f"batch{batch_id}_{i}",
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "source_text": source_text,
                        "target_text": target_text,
                        "domain": domain,
                        "text_type": text_type,
                        "method": self.method,
                        "source_length": len(source_text),
                        "target_length": len(target_text),
                        "timestamp": datetime.utcnow().isoformat()
                    })
            except Exception as e:
                print(f"  Error generating pair {i}: {e}")
                continue
        
        print(f"  Completed batch {batch_id}: {len(data)} pairs generated")
        
        return pd.DataFrame(data)
    
    def save_batch_parquet(self, df: pd.DataFrame, batch_id: int):
        """Save batch to Parquet format"""
        table = pa.Table.from_pandas(df)
        output_file = self.output_dir / f"batch_{batch_id:04d}.parquet"
        
        pq.write_table(
            table,
            output_file,
            compression='snappy',
            use_dictionary=True,
            write_statistics=True,
        )
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"  Saved to {output_file} ({file_size:.2f} MB, {len(df)} rows)")
    
    def generate_dataset(self, total_pairs: int, batch_size: int,
                        source_lang: str = "English",
                        target_lang: str = "Spanish"):
        """Generate complete dataset"""
        
        print("="*60)
        print(f"FREE Synthetic Data Generator - {self.method.upper()}")
        print("="*60)
        print(f"Target pairs: {total_pairs}")
        print(f"Batch size: {batch_size}")
        print(f"Language pair: {source_lang} → {target_lang}")
        print(f"Output directory: {self.output_dir}")
        print(f"Cost: $0.00 (completely FREE!)")
        print("="*60)
        
        num_batches = (total_pairs + batch_size - 1) // batch_size
        total_generated = 0
        
        for batch_id in range(num_batches):
            pairs_in_batch = min(batch_size, total_pairs - total_generated)
            
            df = self.generate_batch(
                pairs_in_batch, source_lang, target_lang, batch_id
            )
            
            if len(df) > 0:
                self.save_batch_parquet(df, batch_id)
                total_generated += len(df)
            
            print(f"Overall progress: {total_generated}/{total_pairs} "
                  f"({100*total_generated/total_pairs:.1f}%)")
        
        print("\n" + "="*60)
        print(f"Dataset generation complete!")
        print(f"Total pairs generated: {total_generated}")
        print(f"Files saved in: {self.output_dir}")
        print(f"Total cost: $0.00 💰")
        
        metadata = {
            "total_pairs": total_generated,
            "num_batches": num_batches,
            "batch_size": batch_size,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "method": self.method,
            "format": "parquet",
            "cost": 0.0,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Metadata saved to: {metadata_file}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic translation data using FREE methods (no API costs)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using open source models (GPT-2, BLOOM, etc.)
  python scripts/generate_synthetic_data_free.py -n 1000 -m opensource --os-model gpt2
  
  # Using Ollama (best quality, free, unlimited)
  python scripts/generate_synthetic_data_free.py -n 1000 -m ollama --ollama-model llama2
  
  # Using rule-based (fastest, no setup needed)
  python scripts/generate_synthetic_data_free.py -n 10000 -m rulebased
  
  # Using back-translation (good quality)
  python scripts/generate_synthetic_data_free.py -n 5000 -m backtranslation
  
  # Using HuggingFace (free tier with rate limits)
  python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-token YOUR_TOKEN
  
  # Using HuggingFace with specific text model
  python scripts/generate_synthetic_data_free.py -n 500 -m huggingface --hf-text-model flan-t5-xl

Methods comparison:
  - corpus: High-quality from public domain books (Don Quixote, Bible, etc.)
  - opensource: OpenAI's GPT-2 and other open models, good quality, runs locally
  - ollama: Best quality, requires local installation, unlimited
  - rulebased: Fastest, works offline, good for large datasets
  - backtranslation: Good quality, works offline, medium speed
  - huggingface: Good quality, requires internet, rate limited (100% FREE)
        """
    )
    
    parser.add_argument(
        '-n', '--num-pairs',
        type=int,
        default=1000,
        help='Total number of translation pairs to generate (default: 1000)'
    )
    
    parser.add_argument(
        '-b', '--batch-size',
        type=int,
        default=100,
        help='Number of pairs per batch (default: 100)'
    )
    
    parser.add_argument(
        '-m', '--method',
        choices=['ollama', 'opensource', 'huggingface', 'rulebased', 'backtranslation', 'corpus'],
        default='rulebased',
        help='Generation method (default: rulebased)'
    )
    
    parser.add_argument(
        '-s', '--source-lang',
        default='English',
        help='Source language (default: English)'
    )
    
    parser.add_argument(
        '-t', '--target-lang',
        default='Spanish',
        help='Target language (default: Spanish)'
    )
    
    parser.add_argument(
        '--ollama-model',
        default='llama2',
        help='Ollama model to use (default: llama2)'
    )
    
    parser.add_argument(
        '--os-model',
        default='gpt2',
        help='Open source model to use: gpt2, gpt2-medium, gpt2-large, bloom-560m, bloom-1b7, distilgpt2 (default: gpt2)'
    )
    
    parser.add_argument(
        '--hf-token',
        help='HuggingFace API token (optional, get FREE at https://huggingface.co/settings/tokens)'
    )
    
    parser.add_argument(
        '--hf-text-model',
        choices=['mistral', 'flan-t5', 'flan-t5-xl', 'bloom', 'gpt2', 'gpt2-large'],
        default='flan-t5',
        help='HuggingFace text generation model (default: flan-t5). Recommended: flan-t5-xl for best quality'
    )
    
    parser.add_argument(
        '--corpus-file',
        help='Path to public domain corpus file for corpus-based generation'
    )
    
    args = parser.parse_args()
    
    try:
        generator = FreeSyntheticDataGenerator(
            method=args.method,
            ollama_model=args.ollama_model,
            os_model=args.os_model,
            hf_token=args.hf_token,
            hf_text_model=args.hf_text_model,
            corpus_file=args.corpus_file
        )
        
        generator.generate_dataset(
            total_pairs=args.num_pairs,
            batch_size=args.batch_size,
            source_lang=args.source_lang,
            target_lang=args.target_lang
        )
        
        print("\n✅ SUCCESS! Synthetic data generated without any API costs!")
        
    except KeyboardInterrupt:
        print("\n\nGeneration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
