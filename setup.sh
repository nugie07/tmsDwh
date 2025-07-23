#!/bin/bash

# Data Warehouse TMS Synchronization System - Setup Script
# This script helps you set up the system quickly

echo "=== Data Warehouse TMS Synchronization System Setup ==="
echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip."
    exit 1
fi

echo "✓ pip3 found: $(pip3 --version)"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo ""
    echo "config.env file not found. Creating from template..."
    cp config.env.example config.env
    echo "✓ config.env created from template"
    echo ""
    echo "IMPORTANT: Please edit config.env with your actual database configuration!"
    echo "You can use any text editor to modify the file."
    echo ""
    echo "Example:"
    echo "  nano config.env"
    echo "  vim config.env"
    echo "  code config.env"
else
    echo "✓ config.env already exists"
fi

# Make scripts executable
chmod +x run_example.sh
chmod +x test_connection.py

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit config.env with your database configuration"
echo "2. Test your database connections:"
echo "   python3 test_connection.py"
echo "3. Run the synchronization:"
echo "   ./run_example.sh"
echo "   or"
echo "   python3 sync_manager.py --sync-type both"
echo ""
echo "For more information, see README.md" 