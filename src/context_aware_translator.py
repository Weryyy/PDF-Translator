#!/usr/bin/env python3
"""
Context-Aware Translation Module

This module provides context-aware translation capabilities that consider
sentence context and use translation memory from public domain books.

Features:
- Maintains context across multiple sentences
- Uses translation memory from public domain corpus
- Provides contextual examples to improve translation quality
- Supports both API-based and local model translation with context
"""

import os
import json
from typing import List, Tuple, Optional, Dict
from pathlib import Path


class ContextAwareTranslator:
    """
    Translator that maintains context and uses translation memory
    """
    
    def __init__(
        self,
        corpus_file: Optional[str] = None,
        context_window: int = 3
    ):
        """
        Initialize context-aware translator
        
        Args:
            corpus_file: Path to public domain corpus JSON file
            context_window: Number of previous sentences to maintain as context
        """
        self.corpus_file = corpus_file
        self.context_window = context_window
        self.translation_memory = []
        self.context_history = []
        
        # Load corpus if provided
        if corpus_file and os.path.exists(corpus_file):
            self._load_corpus(corpus_file)
    
    def _load_corpus(self, corpus_file: str):
        """Load translation memory from corpus"""
        print(f"Loading translation corpus from {corpus_file}...")
        try:
            with open(corpus_file, 'r', encoding='utf-8') as f:
                corpus_data = json.load(f)
            
            self.translation_memory = [
                (p["source"], p["target"])
                for p in corpus_data.get("pairs", [])
            ]
            
            print(f"✓ Loaded {len(self.translation_memory)} translation pairs")
        except Exception as e:
            print(f"Warning: Could not load corpus: {e}")
            self.translation_memory = []
    
    def add_to_context(self, source: str, translation: str):
        """
        Add a sentence pair to context history
        
        Args:
            source: Source language sentence
            translation: Translated sentence
        """
        self.context_history.append((source, translation))
        
        # Keep only last N sentences
        if len(self.context_history) > self.context_window:
            self.context_history = self.context_history[-self.context_window:]
    
    def get_context_prompt(self) -> str:
        """
        Build context prompt from history
        
        Returns:
            Context string to prepend to translation request
        """
        if not self.context_history:
            return ""
        
        context_parts = []
        context_parts.append("Previous context:")
        
        for i, (src, tgt) in enumerate(self.context_history[-3:], 1):
            context_parts.append(f"{i}. Source: {src[:100]}...")
            context_parts.append(f"   Translation: {tgt[:100]}...")
        
        return "\n".join(context_parts)
    
    def find_similar_examples(
        self,
        query: str,
        n_examples: int = 3
    ) -> List[Tuple[str, str]]:
        """
        Find similar translation examples from corpus
        
        Args:
            query: Query text to find similar examples
            n_examples: Number of examples to return
            
        Returns:
            List of (source, target) tuples
        """
        if not self.translation_memory:
            return []
        
        # Simple keyword-based similarity
        query_words = set(query.lower().split())
        
        scored_pairs = []
        for src, tgt in self.translation_memory:
            src_words = set(src.lower().split())
            
            # Calculate word overlap
            overlap = len(query_words & src_words)
            
            if overlap > 0:
                # Bonus for similar length
                len_similarity = 1.0 - abs(len(src) - len(query)) / max(len(src), len(query))
                score = overlap * (1 + len_similarity)
                scored_pairs.append((score, src, tgt))
        
        # Sort by score
        scored_pairs.sort(reverse=True, key=lambda x: x[0])
        
        # Return top N
        return [(src, tgt) for _, src, tgt in scored_pairs[:n_examples]]
    
    def build_enhanced_prompt(
        self,
        text: str,
        target_language: str,
        use_examples: bool = True
    ) -> str:
        """
        Build an enhanced translation prompt with context and examples
        
        Args:
            text: Text to translate
            target_language: Target language
            use_examples: Whether to include similar examples
            
        Returns:
            Enhanced prompt for translation
        """
        prompt_parts = []
        
        # Add system instruction
        prompt_parts.append(
            f"Translate the following text to {target_language}. "
            "Maintain natural flow and consider context."
        )
        
        # Add context from previous translations
        context = self.get_context_prompt()
        if context:
            prompt_parts.append("\n" + context)
        
        # Add similar examples from corpus
        if use_examples and self.translation_memory:
            examples = self.find_similar_examples(text, n_examples=2)
            if examples:
                prompt_parts.append("\nSimilar translation examples:")
                for i, (src, tgt) in enumerate(examples, 1):
                    prompt_parts.append(f"{i}. '{src}' -> '{tgt}'")
        
        # Add the actual text to translate
        prompt_parts.append(f"\nNow translate:\n{text}")
        
        return "\n".join(prompt_parts)
    
    def clear_context(self):
        """Clear context history"""
        self.context_history = []


class ContextAwareTranslationSession:
    """
    Manages a context-aware translation session for a document
    """
    
    def __init__(
        self,
        translator_func,
        corpus_file: Optional[str] = None,
        context_window: int = 3,
        enable_context: bool = True
    ):
        """
        Initialize translation session
        
        Args:
            translator_func: Function that performs actual translation
            corpus_file: Path to public domain corpus
            context_window: Number of sentences to keep in context
            enable_context: Whether to use context-aware features
        """
        self.translator_func = translator_func
        self.enable_context = enable_context
        
        if enable_context:
            self.context_translator = ContextAwareTranslator(
                corpus_file=corpus_file,
                context_window=context_window
            )
        else:
            self.context_translator = None
    
    def translate_with_context(
        self,
        text: str,
        target_language: str
    ) -> str:
        """
        Translate text with context awareness
        
        Args:
            text: Text to translate
            target_language: Target language
            
        Returns:
            Translated text
        """
        if not self.enable_context or not self.context_translator:
            # Fall back to regular translation
            return self.translator_func(text, target_language)
        
        # Build enhanced prompt with context
        enhanced_prompt = self.context_translator.build_enhanced_prompt(
            text,
            target_language,
            use_examples=True
        )
        
        # Perform translation
        translation = self.translator_func(enhanced_prompt, target_language)
        
        # Add to context history
        self.context_translator.add_to_context(text, translation)
        
        return translation
    
    def translate_sentences(
        self,
        sentences: List[str],
        target_language: str,
        show_progress: bool = True
    ) -> List[str]:
        """
        Translate multiple sentences with context preservation
        
        Args:
            sentences: List of sentences to translate
            target_language: Target language
            show_progress: Whether to show progress
            
        Returns:
            List of translated sentences
        """
        translations = []
        
        for i, sentence in enumerate(sentences, 1):
            if show_progress:
                print(f"Translating sentence {i}/{len(sentences)}...")
            
            translation = self.translate_with_context(sentence, target_language)
            translations.append(translation)
        
        return translations
    
    def finish_session(self):
        """Clean up and finish translation session"""
        if self.context_translator:
            self.context_translator.clear_context()


def create_context_aware_wrapper(
    base_translator,
    corpus_file: Optional[str] = None,
    enable_context: bool = True
):
    """
    Create a context-aware wrapper around an existing translator
    
    Args:
        base_translator: Base translator instance with translate_text method
        corpus_file: Path to corpus file
        enable_context: Whether to enable context features
        
    Returns:
        Wrapped translator with context-aware capabilities
    """
    
    def translator_func(text: str, target_lang: str) -> str:
        """Wrapper function for base translator"""
        return base_translator._translate_with_openai(text, target_lang) \
               if hasattr(base_translator, '_translate_with_openai') \
               else base_translator.translate_text(text, target_lang)
    
    return ContextAwareTranslationSession(
        translator_func=translator_func,
        corpus_file=corpus_file,
        enable_context=enable_context
    )


if __name__ == "__main__":
    # Example usage
    print("Context-Aware Translator Module")
    print("="*60)
    print("\nThis module provides context-aware translation using")
    print("translation memory from public domain books.")
    print("\nUsage:")
    print("1. First build a corpus: python src/public_domain_corpus.py")
    print("2. Enable context in config.json: 'use_context_aware': true")
    print("3. Translate PDFs with enhanced context understanding")
