#!/bin/bash

# TMS Data Warehouse Web Dashboard Starter
# This script starts the web dashboard for monitoring sync status

echo "=== TMS Data Warehouse Web Dashboard ==="
echo ""

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "Error: config.env file not found!"
    echo "Please create config.env with your database configuration."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing Flask..."
    pip3 install flask==3.0.0
fi

# Set default web configuration
export WEB_HOST=${WEB_HOST:-"0.0.0.0"}
export WEB_PORT=${WEB_PORT:-"5000"}

echo ""
echo "🚀 Starting TMS Data Warehouse Web Dashboard..."
echo "📊 Dashboard will be available at: http://$WEB_HOST:$WEB_PORT"
echo "🔄 Auto-refresh every 30 seconds"
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Start the web dashboard
python3 web_dashboard.py 