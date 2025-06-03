#!/bin/bash

# UK Government Scraper Setup Script

echo "🇬🇧 UK Government Members Scraper Setup"
echo "========================================"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Anaconda or Miniconda first."
    echo "   Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda found"

# Check if environment already exists
if conda env list | grep -q "uk-pep-scraper"; then
    echo "📦 Environment 'uk-pep-scraper' already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        conda env remove -n uk-pep-scraper -y
    else
        echo "🚀 Using existing environment"
        conda activate uk-pep-scraper
        python app.py
        exit 0
    fi
fi

echo "📦 Creating conda environment from environment.yml..."
conda env create -f environment.yml

if [ $? -eq 0 ]; then
    echo "✅ Environment created successfully"
    
    echo "🔧 Activating environment..."
    conda activate uk-pep-scraper
    
    echo "🚀 Starting Flask application..."
    echo "   The service will be available at: http://localhost:5000"
    echo "   Press Ctrl+C to stop the service"
    echo ""
    
    python app.py
else
    echo "❌ Failed to create conda environment"
    exit 1
fi
