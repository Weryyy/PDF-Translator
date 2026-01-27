#!/usr/bin/env python3
"""
Example script demonstrating how to use the PDF Translator
This script shows basic usage without requiring an API key
"""

import sys
import os

# Add parent directory to path to import the translator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("PDF Translator - Example Usage")
print("="*60)
print()

print("This example demonstrates how to use the PDF Translator.")
print()

print("1. Basic Usage:")
print("   python translate_pdf.py 'document.pdf'")
print()

print("2. Specify output file:")
print("   python translate_pdf.py 'document.pdf' -o 'output.pdf'")
print()

print("3. Specify target language:")
print("   python translate_pdf.py 'document.pdf' -l en")
print()

print("4. Full example with all options:")
print("   python translate_pdf.py 'Mushoku Tensei Redundant Reincarnation Vol. 3.pdf' \\")
print("       -o 'translated_output.pdf' \\")
print("       -l es \\")
print("       -c config.json")
print()

print("="*60)
print("Configuration Setup")
print("="*60)
print()

print("Before using the translator, you need to set up your OpenAI API key:")
print()
print("Option A - Environment Variable:")
print("   export OPENAI_API_KEY='your-api-key-here'")
print()
print("Option B - Configuration File:")
print("   1. Copy the example config: cp config.example.json config.json")
print("   2. Edit config.json and add your API key")
print()

print("="*60)
print("Installation")
print("="*60)
print()
print("To install dependencies, run:")
print("   pip install -r requirements.txt")
print()

print("="*60)
print()
print("For more information, see README.md")
print()
