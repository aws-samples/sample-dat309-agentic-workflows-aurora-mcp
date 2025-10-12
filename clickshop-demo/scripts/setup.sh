#!/bin/bash
# ClickShop Setup Script

set -e

echo "🛍️  ClickShop Setup"
echo "===================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify installation
echo ""
echo "Verifying installation..."
python scripts/verify_installation.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Configure .env file with your AWS credentials"
echo "3. Test Aurora connection: python scripts/test_aurora_connection.py"
echo "4. Initialize database: python scripts/init_aurora_schema.py"
echo "5. Run demos: python run_demo.py"
echo ""
