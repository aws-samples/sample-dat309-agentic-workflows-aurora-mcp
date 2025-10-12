#!/bin/bash
# ClickShop Complete Setup Script
# Sets up all three demos end-to-end

set -e

# Change to script's parent directory (clickshop-demo)
cd "$(dirname "$0")/.."

echo "🛍️  ClickShop Complete Setup"
echo "================================"
echo "Working directory: $(pwd)"
echo ""

# Check Python version
echo "[1/10] Checking Python version..."
python3 --version
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[2/10] Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "[2/10] ✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/10] Activating virtual environment..."
source venv/bin/activate
echo "✅ Activated"
echo ""

# Upgrade pip
echo "[4/10] Upgrading pip..."
pip install --upgrade pip -q
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "[5/10] Installing dependencies..."
pip install -r requirements.txt -q --upgrade
echo "✅ Dependencies installed/updated"
echo ""

# Check if database is already initialized
DB_INITIALIZED=false
if python -c "from lib.aurora_db import get_database_stats; stats = get_database_stats(); exit(0 if stats['total_products'] > 0 else 1)" 2>/dev/null; then
    DB_INITIALIZED=true
fi

# Verify installation
echo "[6/10] Verifying installation..."
python scripts/verify_installation.py
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "[7/10] ⚠️  .env file not found"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your AWS credentials before proceeding!"
    echo ""
    read -p "Press Enter after updating .env file..."
else
    echo "[7/10] ✅ .env file exists"
fi
echo ""

# Test Aurora connection
echo "[8/10] Testing Aurora connection..."
if python scripts/test_aurora_connection.py; then
    echo "✅ Aurora connection successful"
    echo ""
    
    # Initialize database (only if not already initialized)
    if [ "$DB_INITIALIZED" = true ]; then
        echo "[9/10] ✅ Database already initialized (skipping)"
        echo ""
        echo "[10/10] ✅ Embeddings already exist (skipping)"
        echo ""
    else
        echo "[9/10] Initializing database schema..."
        python scripts/init_aurora_schema.py
        echo ""
        
        echo "[10/10] Generating vector embeddings for semantic search..."
        python scripts/generate_embeddings.py
        echo ""
    fi
    
    echo "================================"
    echo "✅ ✅ ✅ Setup Complete! ✅ ✅ ✅"
    echo "================================"
    echo ""
    echo "🎉 All three demos are ready:"
    echo ""
    echo "  • Month 1: Single Agent (50 orders/day)"
    echo "  • Month 3: MCP-Powered (200 orders/day)"
    echo "  • Month 6: Multi-Agent (50K orders/day)"
    echo ""
    echo "Run demos:"
    echo "  python run_demo.py"
    echo ""
    echo "Or run individually:"
    echo "  python -m demos.month_1_single_agent"
    echo "  python -m demos.month_3_agent_mcp"
    echo "  python -m demos.month_6_multi_agent"
    echo ""
else
    echo ""
    echo "❌ Aurora connection failed"
    echo ""
    echo "Troubleshooting:"
    echo "1. Verify Aurora cluster is running"
    echo "2. Check security group allows your IP"
    echo "3. Confirm credentials in .env are correct"
    echo "4. Test with: aws rds describe-db-clusters"
    echo ""
    exit 1
fi
