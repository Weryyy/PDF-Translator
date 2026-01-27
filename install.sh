#!/bin/bash
# PDF Translator - Automated Installation Script for Linux/Mac
# This script sets up the environment and installs all dependencies

set -e

echo "========================================"
echo "PDF Translator - Installation Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "[1/5] Python found:"
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip is not installed"
    exit 1
fi

echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi
echo ""

echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo ""

echo "[4/5] Installing dependencies..."
echo "Installing base requirements..."
pip install -r requirements.txt
echo ""

# Ask user if they want to install GPU optimizations
echo "[5/5] GPU Optimizations (Optional)"
echo ""
read -p "Do you have an NVIDIA GPU and want to install GPU optimizations? (y/n): " install_gpu
if [[ "$install_gpu" =~ ^[Yy]$ ]]; then
    echo "Installing GPU requirements..."
    if pip install -r requirements-gpu.txt; then
        echo "GPU requirements installed successfully"
    else
        echo "WARNING: Failed to install GPU requirements"
        echo "You can continue without GPU support"
    fi
fi
echo ""

# Create config.json from example if it doesn't exist
if [ ! -f "config/config.json" ]; then
    echo "Creating config.json from example..."
    cp config/config.example.json config/config.json
    echo ""
    echo "IMPORTANT: Please edit config/config.json and add your OpenAI API key"
    echo "or set use_local_model to true to use a local model."
fi
echo ""

# Create necessary directories
mkdir -p models synthetic_data output translations pdfs

echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit config/config.json with your settings"
echo "2. Run: source venv/bin/activate (to activate virtual environment)"
echo "3. Run: python src/translate_pdf.py your-file.pdf (to translate a PDF)"
echo ""
echo "For more information, see README.md"
echo ""

# Check optimizations
echo "Checking installed optimizations..."
python scripts/check_optimizations.py
echo ""

echo "Installation script completed. Virtual environment is active."
echo "To deactivate, run: deactivate"
