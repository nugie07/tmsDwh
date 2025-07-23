#!/usr/bin/env python3
"""
Sync Manager Program
This program manages the synchronization of both fact_order and fact_delivery data
"""

import sys
import logging
import argparse
from datetime import datetime
from database_utils import DatabaseManager, logger
from fact_order import process_fact_order
from fact_delivery import process_fact_delivery

def create_sync_log_table(db_manager):
    """Create sync_log table in Database B to track synchronization history"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sync_log (
        id SERIAL PRIMARY KEY,
        sync_type VARCHAR(50) NOT NULL,
        start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP WITH TIME ZONE,
        status VARCHAR(20) NOT NULL,
        records_processed INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        engine = db_manager.get_db_b_engine()
        with engine.connect() as conn:
            conn.execute(create_table_query)
            conn.commit()
        logger.info("sync_log table created/verified in Database B")
    except Exception as e:
        logger.error(f"Error creating sync_log table: {e}")
        raise

def log_sync_start(db_manager, sync_type):
    """Log the start of synchronization"""
    try:
        engine = db_manager.get_db_b_engine()
        insert_query = """
        INSERT INTO sync_log (sync_type, status, start_time)
        VALUES (%s, 'RUNNING', CURRENT_TIMESTAMP)
        RETURNING id;
        """
        
        with engine.connect() as conn:
            result = conn.execute(insert_query, (sync_type,))
            sync_id = result.fetchone()[0]
            conn.commit()
        
        logger.info(f"Sync started for {sync_type} with ID: {sync_id}")
        return sync_id
    except Exception as e:
        logger.error(f"Error logging sync start: {e}")
        return None

def log_sync_complete(db_manager, sync_id, status, records_processed=0, error_message=None):
    """Log the completion of synchronization"""
    try:
        engine = db_manager.get_db_b_engine()
        update_query = """
        UPDATE sync_log 
        SET end_time = CURRENT_TIMESTAMP,
            status = %s,
            records_processed = %s,
            error_message = %s
        WHERE id = %s;
        """
        
        with engine.connect() as conn:
            conn.execute(update_query, (status, records_processed, error_message, sync_id))
            conn.commit()
        
        logger.info(f"Sync completed with status: {status}")
    except Exception as e:
        logger.error(f"Error logging sync completion: {e}")

def get_sync_status(db_manager, sync_type=None, limit=10):
    """Get recent sync status"""
    try:
        engine = db_manager.get_db_b_engine()
        
        if sync_type:
            query = """
            SELECT sync_type, start_time, end_time, status, records_processed, error_message
            FROM sync_log 
            WHERE sync_type = %s
            ORDER BY start_time DESC 
            LIMIT %s;
            """
            params = (sync_type, limit)
        else:
            query = """
            SELECT sync_type, start_time, end_time, status, records_processed, error_message
            FROM sync_log 
            ORDER BY start_time DESC 
            LIMIT %s;
            """
            params = (limit,)
        
        with engine.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()
        
        return rows
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return []

def run_sync(sync_type):
    """Run synchronization for specified type"""
    db_manager = DatabaseManager()
    
    # Create sync_log table if not exists
    create_sync_log_table(db_manager)
    
    # Log sync start
    sync_id = log_sync_start(db_manager, sync_type)
    
    try:
        if sync_type == 'fact_order':
            process_fact_order()
            log_sync_complete(db_manager, sync_id, 'SUCCESS')
        elif sync_type == 'fact_delivery':
            process_fact_delivery()
            log_sync_complete(db_manager, sync_id, 'SUCCESS')
        elif sync_type == 'both':
            # Run both synchronizations
            logger.info("Starting fact_order sync...")
            process_fact_order()
            logger.info("Starting fact_delivery sync...")
            process_fact_delivery()
            log_sync_complete(db_manager, sync_id, 'SUCCESS')
        else:
            raise ValueError(f"Invalid sync_type: {sync_type}")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Sync failed: {error_msg}")
        log_sync_complete(db_manager, sync_id, 'FAILED', error_message=error_msg)
        raise

def main():
    parser = argparse.ArgumentParser(description='Data Synchronization Manager')
    parser.add_argument('--sync-type', 
                       choices=['fact_order', 'fact_delivery', 'both'],
                       default='both',
                       help='Type of synchronization to run')
    parser.add_argument('--status', 
                       action='store_true',
                       help='Show recent sync status')
    parser.add_argument('--status-type',
                       choices=['fact_order', 'fact_delivery'],
                       help='Show status for specific sync type')
    parser.add_argument('--limit',
                       type=int,
                       default=10,
                       help='Number of status records to show (default: 10)')
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    if args.status:
        # Show sync status
        status_rows = get_sync_status(db_manager, args.status_type, args.limit)
        
        if not status_rows:
            print("No sync history found.")
            return
        
        print(f"\n{'Sync Type':<15} {'Start Time':<20} {'End Time':<20} {'Status':<10} {'Records':<8} {'Error'}")
        print("-" * 100)
        
        for row in status_rows:
            sync_type, start_time, end_time, status, records, error = row
            start_str = start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else 'N/A'
            end_str = end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else 'N/A'
            error_str = error[:30] + '...' if error and len(error) > 30 else error or ''
            
            print(f"{sync_type:<15} {start_str:<20} {end_str:<20} {status:<10} {records or 0:<8} {error_str}")
    else:
        # Run synchronization
        logger.info(f"Starting {args.sync_type} synchronization...")
        run_sync(args.sync_type)
        logger.info("Synchronization completed successfully!")

if __name__ == "__main__":
    main() 