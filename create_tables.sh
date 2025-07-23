#!/bin/bash

# Create Tables Script
# This script helps you create tables in Database B

echo "=== Create Tables in Database B ==="
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

echo "Available options:"
echo "1. Create all tables (fact_order, fact_delivery, sync_log)"
echo "2. Create fact_order table only"
echo "3. Create fact_delivery table only"
echo "4. Create sync_log table only"
echo "5. Force recreate all tables (drop if exists)"
echo "6. Show table structure"
echo "7. List all tables"
echo ""

read -p "What would you like to do? (1-7, or 'q' to quit): " choice

case $choice in
    1)
        echo "Creating all tables..."
        python3 create_tables.py --table all
        ;;
    2)
        echo "Creating fact_order table..."
        python3 create_tables.py --table fact_order
        ;;
    3)
        echo "Creating fact_delivery table..."
        python3 create_tables.py --table fact_delivery
        ;;
    4)
        echo "Creating sync_log table..."
        python3 create_tables.py --table sync_log
        ;;
    5)
        echo "Force recreating all tables..."
        python3 create_tables.py --table all --force
        ;;
    6)
        echo "Showing table structure..."
        echo "Available tables:"
        python3 show_table_structure.py --list
        echo ""
        read -p "Enter table name to show structure (or press Enter to skip): " table_name
        if [ ! -z "$table_name" ]; then
            python3 show_table_structure.py --table "$table_name"
        fi
        ;;
    7)
        echo "Listing all tables..."
        python3 show_table_structure.py --list
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