#!/usr/bin/env python3
"""
Example: Context-Aware Translation with Public Domain Books

This script demonstrates how to use context-aware translation
with public domain book corpus.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demonstrate_corpus_building():
    """Demonstrate building a corpus from public domain books"""
    print("="*70)
    print("EXAMPLE 1: Building Public Domain Corpus")
    print("="*70)
    print()
    
    from public_domain_corpus import PublicDomainCorpus
    
    print("This example shows how to build a translation corpus from")
    print("free public domain books available on Project Gutenberg.")
    print()
    
    # Initialize corpus
    corpus = PublicDomainCorpus(cache_dir="./demo_corpus_cache")
    
    # Show available books
    print("Available bilingual books:")
    for book_name, info in corpus.BILINGUAL_BOOKS.items():
        print(f"  - {book_name}: English ID={info['en']}, Spanish ID={info['es']}")
    
    print()
    print("To build a corpus, you would run:")
    print("  corpus.build_corpus_dataset(")
    print("      output_dir='./corpus_data',")
    print("      books=['alice_wonderland'],  # Start with one book")
    print("      pairs_per_book=100")
    print("  )")
    print()
    print("Note: This requires internet connection to download books")
    print()


def demonstrate_context_aware_translation():
    """Demonstrate context-aware translation"""
    print("="*70)
    print("EXAMPLE 2: Context-Aware Translation")
    print("="*70)
    print()
    
    from context_aware_translator import ContextAwareTranslator
    
    print("This example shows how context improves translation quality.")
    print()
    
    # Initialize translator without corpus (just context window)
    translator = ContextAwareTranslator(
        corpus_file=None,
        context_window=3
    )
    
    # Simulate translating a short story
    sentences = [
        "John went to the store.",
        "He bought some milk.",
        "Then he went home."
    ]
    
    translations = [
        "Juan fue a la tienda.",
        "Él compró algo de leche.",
        "Luego se fue a casa."
    ]
    
    print("Translating with context awareness:")
    print()
    
    for i, (src, tgt) in enumerate(zip(sentences, translations), 1):
        # Add to context
        translator.add_to_context(src, tgt)
        
        print(f"Sentence {i}:")
        print(f"  Source: {src}")
        print(f"  Translation: {tgt}")
        print()
    
    # Show context
    context = translator.get_context_prompt()
    print("Current context maintained:")
    print(context)
    print()
    print("This context is used to improve subsequent translations!")
    print()


def demonstrate_synthetic_data_generation():
    """Demonstrate generating synthetic data from corpus"""
    print("="*70)
    print("EXAMPLE 3: Generating Training Data from Corpus")
    print("="*70)
    print()
    
    print("Once you have a corpus, you can generate synthetic training data:")
    print()
    print("Method 1: Directly from corpus")
    print("  $ python scripts/generate_synthetic_data_free.py -n 1000 -m corpus")
    print()
    print("Method 2: Combine with other free methods")
    print("  $ python scripts/generate_synthetic_data_free.py -n 2000 -m corpus")
    print("  $ python scripts/generate_synthetic_data_free.py -n 3000 -m rulebased")
    print("  $ python scripts/generate_synthetic_data_free.py -n 2000 -m backtranslation")
    print()
    print("Result: 7000 high-quality training pairs at $0.00 cost!")
    print()


def demonstrate_full_workflow():
    """Demonstrate complete workflow"""
    print("="*70)
    print("EXAMPLE 4: Complete Workflow")
    print("="*70)
    print()
    
    print("Complete workflow from corpus building to translation:")
    print()
    print("Step 1: Build corpus from public domain books")
    print("  $ python src/public_domain_corpus.py -o corpus_data -n 1000")
    print()
    print("Step 2: Enable context-aware mode in config.json")
    print('  {')
    print('    "use_context_aware": true,')
    print('    "corpus_file": "./corpus_data/public_domain_corpus.json",')
    print('    "context_window": 3')
    print('  }')
    print()
    print("Step 3: Translate PDFs with enhanced context")
    print("  $ python src/translate_pdf.py document.pdf")
    print()
    print("Benefits:")
    print("  ✓ Better translation coherence")
    print("  ✓ Context-aware pronoun resolution")
    print("  ✓ Improved handling of ambiguous words")
    print("  ✓ More natural sentence flow")
    print()


def main():
    """Run all demonstrations"""
    print()
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "Context-Aware Translation Demo" + " "*23 + "║")
    print("║" + " "*13 + "Using Public Domain Books Corpus" + " "*21 + "║")
    print("╚" + "═"*68 + "╝")
    print()
    
    try:
        demonstrate_corpus_building()
        demonstrate_context_aware_translation()
        demonstrate_synthetic_data_generation()
        demonstrate_full_workflow()
        
        print("="*70)
        print("✅ All demonstrations completed!")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Read the full guide: docs/CONTEXT_AWARE_TRANSLATION.md")
        print("2. Build your corpus: python src/public_domain_corpus.py")
        print("3. Try translating: python src/translate_pdf.py your_file.pdf")
        print()
        
    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure all required modules are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
