#!/usr/bin/env python3
"""
Public Domain Book Corpus Loader and Processor

This module loads public domain books from Project Gutenberg and other sources
to create a high-quality translation corpus for context-aware translation.

Features:
- Fetch books from Project Gutenberg (60,000+ free books)
- Extract parallel text from bilingual books
- Build translation memory from public domain content
- Support context-aware sentence extraction
"""

import os
import re
import json
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urljoin
import time


class PublicDomainCorpus:
    """Manages public domain book corpus for translation training"""
    
    # Project Gutenberg mirror URLs
    GUTENBERG_MIRRORS = [
        "https://www.gutenberg.org/",
        "http://aleph.gutenberg.org/"
    ]
    
    # Common bilingual book pairs (English-Spanish)
    BILINGUAL_BOOKS = {
        "don_quixote": {
            "en": 996,   # Don Quixote in English
            "es": 2000,  # Don Quixote in Spanish (original)
        },
        "bible": {
            "en": 10,    # King James Bible
            "es": 1750,  # Spanish Bible
        },
        "alice_wonderland": {
            "en": 11,    # Alice in Wonderland (English)
            "es": 22928, # Alicia en el País de las Maravillas
        }
    }
    
    def __init__(self, cache_dir: str = "./corpus_cache"):
        """Initialize corpus loader"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PDF-Translator/1.0 (Educational Project)'
        })
    
    def fetch_gutenberg_book(self, book_id: int, language: str = "en") -> Optional[str]:
        """
        Fetch a book from Project Gutenberg by ID
        
        Args:
            book_id: Project Gutenberg book ID
            language: Language code (en, es, etc.)
            
        Returns:
            Book text content or None if failed
        """
        cache_file = self.cache_dir / f"gutenberg_{book_id}_{language}.txt"
        
        # Check cache first
        if cache_file.exists():
            print(f"Loading cached book {book_id}...")
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Try to fetch from mirrors
        for mirror in self.GUTENBERG_MIRRORS:
            try:
                # Try different URL patterns
                urls = [
                    f"{mirror}files/{book_id}/{book_id}-0.txt",
                    f"{mirror}files/{book_id}/{book_id}.txt",
                    f"{mirror}ebooks/{book_id}.txt.utf-8"
                ]
                
                for url in urls:
                    print(f"Trying to fetch from {url}...")
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        text = response.text
                        
                        # Remove Project Gutenberg header/footer
                        text = self._clean_gutenberg_text(text)
                        
                        # Cache the result
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            f.write(text)
                        
                        print(f"✓ Successfully fetched book {book_id}")
                        return text
                
                # Rate limiting - be nice to Gutenberg servers
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching from {mirror}: {e}")
                continue
        
        print(f"Failed to fetch book {book_id}")
        return None
    
    def _clean_gutenberg_text(self, text: str) -> str:
        """Remove Project Gutenberg headers and footers"""
        # Find start marker
        start_patterns = [
            r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG.*?\*\*\*",
            r"START OF THE PROJECT GUTENBERG",
        ]
        
        for pattern in start_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                text = text[match.end():]
                break
        
        # Find end marker
        end_patterns = [
            r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG.*?\*\*\*",
            r"END OF THE PROJECT GUTENBERG",
        ]
        
        for pattern in end_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                text = text[:match.start()]
                break
        
        return text.strip()
    
    def extract_parallel_sentences(
        self, 
        book_name: str,
        max_pairs: int = 1000
    ) -> List[Tuple[str, str]]:
        """
        Extract parallel sentence pairs from bilingual books
        
        Args:
            book_name: Name of the bilingual book pair
            max_pairs: Maximum number of sentence pairs to extract
            
        Returns:
            List of (source_sentence, target_sentence) tuples
        """
        if book_name not in self.BILINGUAL_BOOKS:
            print(f"Unknown book: {book_name}")
            print(f"Available books: {list(self.BILINGUAL_BOOKS.keys())}")
            return []
        
        book_info = self.BILINGUAL_BOOKS[book_name]
        
        # Fetch both versions
        print(f"\nFetching bilingual book pair: {book_name}")
        en_text = self.fetch_gutenberg_book(book_info["en"], "en")
        es_text = self.fetch_gutenberg_book(book_info["es"], "es")
        
        if not en_text or not es_text:
            print("Failed to fetch one or both versions")
            return []
        
        # Extract sentences
        en_sentences = self._extract_sentences(en_text)
        es_sentences = self._extract_sentences(es_text)
        
        print(f"Extracted {len(en_sentences)} English sentences")
        print(f"Extracted {len(es_sentences)} Spanish sentences")
        
        # Align sentences (simple alignment based on position)
        pairs = self._align_sentences(en_sentences, es_sentences, max_pairs)
        
        print(f"✓ Created {len(pairs)} parallel sentence pairs")
        return pairs
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract clean sentences from text"""
        # Split by sentence boundaries
        sentences = re.split(r'[.!?]+\s+', text)
        
        # Clean and filter
        clean_sentences = []
        for sent in sentences:
            # Remove extra whitespace
            sent = ' '.join(sent.split())
            
            # Filter out short sentences and chapter headers
            if len(sent) >= 20 and len(sent) <= 500:
                # Skip all-caps headers
                if not sent.isupper():
                    clean_sentences.append(sent)
        
        return clean_sentences
    
    def _align_sentences(
        self,
        source_sents: List[str],
        target_sents: List[str],
        max_pairs: int
    ) -> List[Tuple[str, str]]:
        """
        Align parallel sentences from two texts
        
        Simple alignment based on relative position in text.
        For better quality, could use sentence embeddings or other alignment methods.
        """
        pairs = []
        
        # Calculate alignment ratio
        src_len = len(source_sents)
        tgt_len = len(target_sents)
        
        if src_len == 0 or tgt_len == 0:
            return pairs
        
        ratio = tgt_len / src_len
        
        # Sample evenly distributed pairs
        step = max(1, src_len // max_pairs)
        
        for i in range(0, src_len, step):
            if len(pairs) >= max_pairs:
                break
            
            # Calculate corresponding target index
            j = int(i * ratio)
            
            if j < tgt_len:
                pairs.append((source_sents[i], target_sents[j]))
        
        return pairs
    
    def build_corpus_dataset(
        self,
        output_dir: str = "./corpus_data",
        books: List[str] = None,
        pairs_per_book: int = 1000
    ) -> str:
        """
        Build a complete corpus dataset from multiple books
        
        Args:
            output_dir: Directory to save the corpus
            books: List of book names to use (None = use all available)
            pairs_per_book: Number of pairs to extract per book
            
        Returns:
            Path to the saved corpus file
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        if books is None:
            books = list(self.BILINGUAL_BOOKS.keys())
        
        all_pairs = []
        
        print("\n" + "="*60)
        print("Building Public Domain Translation Corpus")
        print("="*60)
        
        for book_name in books:
            print(f"\nProcessing book: {book_name}")
            pairs = self.extract_parallel_sentences(book_name, pairs_per_book)
            all_pairs.extend(pairs)
            print(f"Total pairs collected: {len(all_pairs)}")
        
        # Save as JSON
        corpus_file = output_path / "public_domain_corpus.json"
        corpus_data = {
            "metadata": {
                "source": "Project Gutenberg",
                "created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "books": books,
                "total_pairs": len(all_pairs)
            },
            "pairs": [
                {"source": src, "target": tgt}
                for src, tgt in all_pairs
            ]
        }
        
        with open(corpus_file, 'w', encoding='utf-8') as f:
            json.dump(corpus_data, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print(f"✓ Corpus built successfully!")
        print(f"✓ Total pairs: {len(all_pairs)}")
        print(f"✓ Saved to: {corpus_file}")
        print("="*60)
        
        return str(corpus_file)
    
    def get_contextual_examples(
        self,
        query: str,
        corpus_file: str,
        n_examples: int = 5
    ) -> List[Tuple[str, str]]:
        """
        Get contextually similar translation examples from corpus
        
        Args:
            query: Query text to find similar examples
            corpus_file: Path to corpus JSON file
            n_examples: Number of examples to return
            
        Returns:
            List of similar (source, target) pairs
        """
        if not os.path.exists(corpus_file):
            return []
        
        with open(corpus_file, 'r', encoding='utf-8') as f:
            corpus_data = json.load(f)
        
        pairs = [(p["source"], p["target"]) for p in corpus_data["pairs"]]
        
        # Simple similarity based on word overlap
        # For production, use sentence embeddings (sentence-transformers)
        query_words = set(query.lower().split())
        
        scored_pairs = []
        for src, tgt in pairs:
            src_words = set(src.lower().split())
            overlap = len(query_words & src_words)
            if overlap > 0:
                scored_pairs.append((overlap, src, tgt))
        
        # Sort by similarity score
        scored_pairs.sort(reverse=True, key=lambda x: x[0])
        
        # Return top N
        return [(src, tgt) for _, src, tgt in scored_pairs[:n_examples]]


def main():
    """Command-line interface for corpus building"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Build translation corpus from public domain books"
    )
    parser.add_argument(
        "-o", "--output",
        default="./corpus_data",
        help="Output directory for corpus"
    )
    parser.add_argument(
        "-n", "--pairs-per-book",
        type=int,
        default=1000,
        help="Number of pairs to extract per book"
    )
    parser.add_argument(
        "--books",
        nargs="+",
        help="Specific books to process (default: all)"
    )
    
    args = parser.parse_args()
    
    corpus = PublicDomainCorpus()
    corpus.build_corpus_dataset(
        output_dir=args.output,
        books=args.books,
        pairs_per_book=args.pairs_per_book
    )


if __name__ == "__main__":
    main()
