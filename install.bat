@echo off
REM PDF Translator - Automated Installation Script for Windows
REM This script sets up the environment and installs all dependencies

echo ========================================
echo PDF Translator - Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not installed or not in PATH
    pause
    exit /b 1
)

echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [4/5] Installing dependencies...
echo Installing base requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install base requirements
    pause
    exit /b 1
)
echo.

REM Ask user if they want to install GPU optimizations
echo [5/5] GPU Optimizations (Optional)
echo.
set /p install_gpu="Do you have an NVIDIA GPU and want to install GPU optimizations? (y/n): "
if /i "%install_gpu%"=="y" (
    echo Installing GPU requirements...
    pip install -r requirements-gpu.txt
    if %errorlevel% neq 0 (
        echo WARNING: Failed to install GPU requirements
        echo You can continue without GPU support
    ) else (
        echo GPU requirements installed successfully
    )
)
echo.

REM Create config.json from example if it doesn't exist
if not exist "config\config.json" (
    echo Creating config.json from example...
    copy config\config.example.json config\config.json
    echo.
    echo IMPORTANT: Please edit config\config.json and add your OpenAI API key
    echo or set use_local_model to true to use a local model.
)
echo.

REM Create necessary directories
if not exist "models" mkdir models
if not exist "synthetic_data" mkdir synthetic_data
if not exist "output" mkdir output
if not exist "translations" mkdir translations
if not exist "pdfs" mkdir pdfs

REM Check optimizations while still in virtual environment
echo.
echo Checking installed optimizations...
python scripts\check_optimizations.py
echo.

echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config\config.json with your settings
echo 2. Run: venv\Scripts\activate.bat (to activate virtual environment)
echo 3. Run: python src\translate_pdf.py your-file.pdf (to translate a PDF)
echo.
echo For more information, see README.md
echo.

pause
