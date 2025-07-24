#!/usr/bin/env python3
"""
Automatic Monthly Sync Script
This script runs sync from 1st of current month to current date
Can be registered to crontab to run daily at 12:00
"""

import sys
import logging
from datetime import datetime, date
from database_utils import DatabaseManager, logger
from sync_manager import sync_fact_order, sync_fact_delivery

def get_monthly_date_range():
    """Get date range from 1st of current month to current date"""
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today
    
    logger.info(f"Monthly sync range: {start_date} to {end_date}")
    return start_date, end_date

def cleanup_temp_tables():
    """Clean up temporary tables that might be left behind"""
    try:
        logger.info("Starting cleanup of temporary tables...")
        db_manager = DatabaseManager()
        engine = db_manager.get_db_b_engine()
        
        with engine.connect() as conn:
            from sqlalchemy import text
            
            # Find all temporary tables
            find_temp_tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'temp_tms_%'
            """
            
            result = conn.execute(text(find_temp_tables_query))
            temp_tables = [row[0] for row in result.fetchall()]
            
            if temp_tables:
                logger.info(f"Found {len(temp_tables)} temporary tables to clean up")
                
                for table_name in temp_tables:
                    try:
                        drop_query = f"DROP TABLE IF EXISTS public.{table_name}"
                        conn.execute(text(drop_query))
                        logger.info(f"Dropped temporary table: {table_name}")
                    except Exception as e:
                        logger.warning(f"Failed to drop {table_name}: {e}")
                
                conn.commit()
                logger.info("Temporary tables cleanup completed")
            else:
                logger.info("No temporary tables found to clean up")
                
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def run_monthly_sync():
    """Run monthly sync for both fact_order and fact_delivery"""
    try:
        logger.info("=== Starting Monthly Auto Sync ===")
        
        # Get date range
        start_date, end_date = get_monthly_date_range()
        
        # Clean up temporary tables first
        cleanup_temp_tables()
        
        # Run sync for fact_order
        logger.info("Starting fact_order sync...")
        sync_fact_order(start_date, end_date)
        
        # Run sync for fact_delivery
        logger.info("Starting fact_delivery sync...")
        sync_fact_delivery(start_date, end_date)
        
        # Clean up temporary tables after sync
        cleanup_temp_tables()
        
        logger.info("=== Monthly Auto Sync Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Error in monthly sync: {e}")
        # Clean up temporary tables even if sync fails
        cleanup_temp_tables()
        sys.exit(1)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('auto_sync_monthly.log'),
            logging.StreamHandler()
        ]
    )
    
    run_monthly_sync() 