#!/bin/bash

# Auto Sync Monthly Script
# This script runs the monthly sync from 1st of current month to current date
# Can be scheduled in crontab to run daily at 12:00

# Set working directory
cd "$(dirname "$0")"

# Load environment variables
if [ -f "config.env" ]; then
    export $(cat config.env | grep -v '^#' | xargs)
fi

# Log file
LOG_FILE="auto_sync_monthly.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting Auto Sync Monthly..." >> "$LOG_FILE"

# Run the auto sync script
python3 auto_sync_monthly.py >> "$LOG_FILE" 2>&1

# Check exit status
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Auto Sync completed successfully" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] Auto Sync failed with exit code $?" >> "$LOG_FILE"
    exit 1
fi

echo "[$TIMESTAMP] Auto Sync process finished" >> "$LOG_FILE" 