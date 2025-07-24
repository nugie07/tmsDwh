#!/bin/bash

# Data Warehouse TMS Synchronization System - Run Examples
# This script provides examples of how to run the synchronization programs

echo "=== Data Warehouse TMS Synchronization System ==="
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
python3 -c "import psycopg2, pandas, sqlalchemy, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Available commands:"
echo "1. Run both synchronizations:"
echo "   python3 sync_manager.py --sync both"
echo ""
echo "2. Run fact_order only:"
echo "   python3 sync_manager.py --sync fact_order"
echo ""
echo "3. Run fact_delivery only:"
echo "   python3 sync_manager.py --sync fact_delivery"
echo ""
echo "4. Run with date filter (e.g., 2025-07-01 to 2025-07-07):"
echo "   python3 sync_manager.py --sync both --date-from 2025-07-01 --date-to 2025-07-07"
echo ""
echo "5. Check sync status:"
echo "   python3 sync_manager.py --status"
echo ""
echo "6. Run individual programs:"
echo "   python3 fact_order.py"
echo "   python3 fact_delivery.py"
echo ""

# Ask user what to do
read -p "What would you like to do? (1-6, or 'q' to quit): " choice

case $choice in
    1)
        echo "Running both synchronizations..."
        python3 sync_manager.py --sync both
        ;;
    2)
        echo "Running fact_order synchronization..."
        python3 sync_manager.py --sync fact_order
        ;;
    3)
        echo "Running fact_delivery synchronization..."
        python3 sync_manager.py --sync fact_delivery
        ;;
    4)
        echo "Running with date filter..."
        read -p "Enter start date (YYYY-MM-DD): " date_from
        read -p "Enter end date (YYYY-MM-DD): " date_to
        echo "Running both synchronizations with date filter..."
        python3 sync_manager.py --sync both --date-from "$date_from" --date-to "$date_to"
        ;;
    5)
        echo "Checking sync status..."
        python3 sync_manager.py --status
        ;;
    6)
        echo "Running individual programs..."
        echo "1. fact_order.py"
        echo "2. fact_delivery.py"
        read -p "Which program? (1 or 2): " subchoice
        case $subchoice in
            1)
                python3 fact_order.py
                ;;
            2)
                python3 fact_delivery.py
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
    q|Q)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "Done!" 