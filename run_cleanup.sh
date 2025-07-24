#!/bin/bash

# Cleanup Temporary Tables Script
# This script cleans up temporary tables that might be left behind
# Can be scheduled in crontab to run periodically

# Set working directory
cd "$(dirname "$0")"

# Load environment variables
if [ -f "config.env" ]; then
    export $(cat config.env | grep -v '^#' | xargs)
fi

# Log file
LOG_FILE="cleanup_temp_tables.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting Temporary Tables Cleanup..." >> "$LOG_FILE"

# Run the cleanup script
python3 cleanup_temp_tables.py >> "$LOG_FILE" 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Cleanup completed successfully" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] Cleanup failed with exit code $?" >> "$LOG_FILE"
    exit 1
fi

echo "[$TIMESTAMP] Cleanup process finished" >> "$LOG_FILE" 