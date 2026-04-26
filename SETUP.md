# 🔧 Setup Guide - Document AI System

> Complete installation and configuration guide for Document AI System

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Tesseract OCR Setup](#tesseract-ocr-setup)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Setup](#advanced-setup)

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 5GB free space
- **CPU**: 2 cores minimum (4+ cores recommended)

### Recommended Setup
- **OS**: Ubuntu 20.04 LTS or Windows Server 2019+
- **Python**: 3.11+
- **RAM**: 8GB+
- **Disk**: 20GB+ SSD
- **CPU**: 8 cores+
- **GPU**: NVIDIA (optional, for faster processing)

### Check Python Version
```bash
python --version
# Should be 3.9 or higher

python -m pip --version
# pip 21.0 or higher
```

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
# HTTPS
git clone https://github.com/vineet-5581/ne.git
cd ne

# Or SSH
git clone git@github.com:vineet-5581/ne.git
cd ne
```

### Step 2: Create Virtual Environment

#### On macOS/Linux:
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Verify activation (should show venv prefix)
which python
```

#### On Windows (PowerShell):
```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# If restricted, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation
where python
```

#### On Windows (CMD):
```cmd
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate.bat

# Verify activation
where python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 4: Create Configuration Files

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional)
# nano .env  # or use your editor
```

---

## 🔍 Tesseract OCR Setup

### Windows Installation

#### Method 1: Direct Download
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (latest version, e.g., `tesseract-ocr-w64-setup-v5.x.exe`)
3. Choose installation path (default: `C:\Program Files\Tesseract-OCR`)
4. Complete installation

#### Method 2: Chocolatey
```powershell
# Install Chocolatey first (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; 
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Tesseract
choco install tesseract
```

#### Verify Installation (Windows):
```powershell
# Find Tesseract
where tesseract

# Test Tesseract
tesseract --version

# Set environment variable (optional)
[Environment]::SetEnvironmentVariable('TESSERACT_CMD', 'C:\Program Files\Tesseract-OCR\tesseract.exe', 'User')
```

### macOS Installation

#### Method 1: Homebrew
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Tesseract
brew install tesseract

# Verify installation
tesseract --version
which tesseract
```

### Linux Installation

#### Ubuntu/Debian:
```bash
# Update package manager
sudo apt-get update

# Install Tesseract
sudo apt-get install -y tesseract-ocr

# Install language packs (optional)
sudo apt-get install -y tesseract-ocr-eng
sudo apt-get install -y tesseract-ocr-fra
sudo apt-get install -y tesseract-ocr-deu

# Verify installation
tesseract --version
which tesseract
```

#### CentOS/RHEL:
```bash
# Install Tesseract
sudo yum install -y tesseract

# Install language packs
sudo yum install -y tesseract-langpack-eng

# Verify installation
tesseract --version
```

### Configure Tesseract in Python

Add to your `.env` file or set in code:

```python
# .env file
TESSERACT_PATH=/usr/bin/tesseract          # Linux/macOS
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe  # Windows

# Or in Python code
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## ⚙️ Configuration

### Step 1: Environment Variables (.env)

Create `.env` file in project root:

```env
# ============================================
# LOGGING
# ============================================
LOG_LEVEL=INFO
FILE_LOGGING=true
CONSOLE_LOGGING=true

# ============================================
# PDF PROCESSING
# ============================================
MAX_PDF_SIZE=100
PDF_DPI=300
EXTRACT_IMAGES=true
PRESERVE_FORMATTING=true
DETECT_TABLES=true

# ============================================
# OCR
# ============================================
ENABLE_OCR=true
OCR_ENGINE=tesseract
TESSERACT_PATH=/usr/bin/tesseract
OCR_LANGUAGE=eng
OCR_CONFIDENCE=0.5
OCR_DESKEW=true
OCR_DENOISE=true

# ============================================
# COMPUTER VISION
# ============================================
USE_DETECTRON2=true
CV_DEVICE=cpu
CV_BATCH_SIZE=1

# ============================================
# NLP
# ============================================
ENABLE_NLP=true
NLP_MODEL=bert-base-uncased
NLP_DEVICE=cpu
NLP_BATCH_SIZE=32

# ============================================
# WORD GENERATION
# ============================================
PRESERVE_IMAGES=true
PRESERVE_FONTS=true
DEFAULT_FONT=Calibri
DEFAULT_FONT_SIZE=11

# ============================================
# PROCESSING
# ============================================
PARALLEL_PROCESSING=true
NUM_WORKERS=4
TIMEOUT_SECONDS=300
ENABLE_CACHING=true

# ============================================
# API
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
MAX_UPLOAD_SIZE=100
ALLOW_ORIGINS=*

# ============================================
# PATHS
# ============================================
BASE_DIR=.
INPUT_DIR=./inputs
OUTPUT_DIR=./outputs
LOG_DIR=./logs
```

### Step 2: Create Directories

```bash
# Create input/output directories
mkdir -p inputs outputs logs temp

# Or in Python
from pathlib import Path
Path("inputs").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
Path("temp").mkdir(exist_ok=True)
```

### Step 3: Verify Configuration

```bash
# Validate setup
python cli.py validate

# Get system information
python cli.py info

# Or in Python
from config import settings
print(settings.get_summary())
```

---

## ✅ Verification

### Test Installation

#### 1. Test Imports
```bash
python -c "
import pymupdf
import pdfplumber
import cv2
import transformers
import torch
from docx import Document
print('✅ All core imports successful')
"
```

#### 2. Test Tesseract
```bash
python -c "
import pytesseract
from PIL import Image
import numpy as np
# Create test image
img = Image.fromarray(np.zeros((100, 100)), 'L')
result = pytesseract.image_to_string(img)
print('✅ Tesseract working')
"
```

#### 3. Test CLI
```bash
# Show help
python cli.py --help

# Validate system
python cli.py validate

# Show system info
python cli.py info
```

#### 4. Test with Sample PDF
```bash
# Create test PDF first
python examples.py create_test_pdf

# Convert it
python cli.py convert test_sample.pdf test_output.docx --verbose

# Check output
ls -la test_output.docx
```

### Run Complete Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_layer1.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

**Problem:**
```
ModuleNotFoundError: No module named 'pymupdf'
```

**Solution:**
```bash
# Reinstall requirements
pip install --force-reinstall -r requirements.txt

# Or install specific package
pip install PyMuPDF==1.23.8
```

### Issue: Tesseract Not Found

**Problem:**
```
TesseractNotFoundError: tesseract is not installed or it's not in your path
```

**Solution:**
```python
# Set path in Python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Or set environment variable
import os
os.environ['TESSERACT_CMD'] = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: Out of Memory

**Problem:**
```
MemoryError: Unable to allocate 2GB
```

**Solution:**
```bash
# Reduce workers
NUM_WORKERS=1 python cli.py convert input.pdf output.docx

# Or in .env
NUM_WORKERS=2
BATCH_SIZE=1
```

### Issue: PDF File Not Found

**Problem:**
```
FileNotFoundError: input.pdf not found
```

**Solution:**
```bash
# Use absolute path
python cli.py convert /absolute/path/to/input.pdf /absolute/path/to/output.docx

# Or put file in inputs directory
cp input.pdf inputs/
python cli.py convert inputs/input.pdf outputs/output.docx
```

### Issue: Slow Processing

**Problem:**
```
Processing taking too long
```

**Solution:**
```bash
# Enable parallel processing
PARALLEL_PROCESSING=true python cli.py convert input.pdf output.docx

# Use GPU if available
NLP_DEVICE=cuda CV_DEVICE=cuda python cli.py convert input.pdf output.docx

# Reduce DPI for faster processing
PDF_DPI=150 python cli.py convert input.pdf output.docx
```

### Issue: API Port Already in Use

**Problem:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Use different port
python -m uvicorn api:app --port 8001

# Or kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 🔧 Advanced Setup

### GPU Support (CUDA)

#### Check NVIDIA GPU
```bash
# Linux/macOS
nvidia-smi

# Windows
"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
```

#### Install CUDA Support
```bash
# Uninstall CPU torch
pip uninstall torch torchvision torchaudio -y

# Install GPU torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify
python -c "import torch; print(torch.cuda.is_available())"
```

#### Configure for GPU
```env
# .env file
NLP_DEVICE=cuda
CV_DEVICE=cuda
NUM_WORKERS=8
```

### Docker Setup

#### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose API port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run Docker
```bash
# Build image
docker build -t document-ai:latest .

# Run container
docker run -p 8000:8000 -v $(pwd)/inputs:/app/inputs -v $(pwd)/outputs:/app/outputs document-ai:latest

# Or with docker-compose
docker-compose up
```

### Development Setup

#### Install Development Tools
```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

#### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .

# Run tests
pytest --cov=.
```

---

## 📚 Next Steps

1. ✅ **Verify Installation**: Run `python cli.py validate`
2. ✅ **Test with Sample**: Run `python examples.py`
3. ✅ **Try CLI**: Convert a PDF using `python cli.py convert`
4. ✅ **Start API**: Run `python -m uvicorn api:app --reload`
5. ✅ **Launch GUI**: Run `streamlit run gui.py`

---

## 📞 Getting Help

- **Issues**: https://github.com/vineet-5581/ne/issues
- **Documentation**: See [README.md](README.md)
- **Examples**: See [examples.py](examples.py)

---

**✨ Setup complete! Start converting PDFs!** 🚀
