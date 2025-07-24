#!/usr/bin/env python3
"""
Cleanup Temporary Tables Script
This script cleans up temporary tables that might be left behind from sync operations
Can be run independently or scheduled via crontab
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def cleanup_temp_tables():
    """Clean up temporary tables that might be left behind"""
    try:
        logger.info("=== Starting Temporary Tables Cleanup ===")
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
            ORDER BY table_name
            """
            
            result = conn.execute(text(find_temp_tables_query))
            temp_tables = [row[0] for row in result.fetchall()]
            
            if temp_tables:
                logger.info(f"Found {len(temp_tables)} temporary tables to clean up:")
                for table in temp_tables:
                    logger.info(f"  - {table}")
                
                dropped_count = 0
                for table_name in temp_tables:
                    try:
                        drop_query = f"DROP TABLE IF EXISTS public.{table_name}"
                        conn.execute(text(drop_query))
                        logger.info(f"✓ Dropped temporary table: {table_name}")
                        dropped_count += 1
                    except Exception as e:
                        logger.warning(f"✗ Failed to drop {table_name}: {e}")
                
                conn.commit()
                logger.info(f"=== Cleanup completed: {dropped_count}/{len(temp_tables)} tables dropped ===")
            else:
                logger.info("No temporary tables found to clean up")
                
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cleanup_temp_tables.log'),
            logging.StreamHandler()
        ]
    )
    
    cleanup_temp_tables() 