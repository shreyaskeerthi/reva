#!/bin/bash
# Setup script for CRE Deal Voice Agent

echo "🏢 CRE Deal Voice Agent - Setup"
echo "================================"

# Check Python version
echo ""
echo "1. Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "2. Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo ""
    echo "2. Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "3. Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "4. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "5. Creating .env file from template..."
    cp .env.example .env
    echo "   ✅ .env created - edit this file to add your API keys"
else
    echo ""
    echo "5. .env file already exists"
fi

# Create runs directory
mkdir -p runs
mkdir -p static

echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys (optional - works in demo mode without keys)"
echo "  2. Activate virtual environment: source venv/bin/activate"
echo "  3. Run the app: streamlit run app.py"
echo "  4. Or test first: python3 test_demo.py"
echo ""
