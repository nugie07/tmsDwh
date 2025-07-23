#!/usr/bin/env python3
"""
Create Tables Program
This program creates tables in Database B based on the queries from fact_order and fact_delivery programs
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def get_fact_order_table_structure():
    """Get the table structure for fact_order based on the query"""
    return """
    CREATE TABLE IF NOT EXISTS fact_order (
        -- Columns from the fact_order query
        status VARCHAR(50),
        manifest_reference VARCHAR(100),
        order_id VARCHAR(50),
        manifest_integration_id VARCHAR(100),
        external_expedition_type VARCHAR(50),
        driver_name VARCHAR(100),
        code VARCHAR(50),
        faktur_date DATE,
        tms_created TIMESTAMP,
        route_created DATE,
        delivery_date DATE,
        route_id VARCHAR(50),
        tms_complete TIMESTAMP,
        location_confirmation DATE,
        faktur_total_quantity NUMERIC(15,2),
        tms_total_quantity NUMERIC(15,2),
        total_return NUMERIC(15,2),
        total_net_value NUMERIC(15,2),
        
        -- Additional tracking columns
        last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        -- Primary key
        PRIMARY KEY (order_id)
    );
    
    -- Create index for better performance
    CREATE INDEX IF NOT EXISTS idx_fact_order_faktur_date ON fact_order(faktur_date);
    CREATE INDEX IF NOT EXISTS idx_fact_order_route_id ON fact_order(route_id);
    CREATE INDEX IF NOT EXISTS idx_fact_order_last_synced ON fact_order(last_synced);
    
    -- Create trigger to update updated_at column
    CREATE OR REPLACE FUNCTION update_fact_order_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS trigger_fact_order_updated_at ON fact_order;
    CREATE TRIGGER trigger_fact_order_updated_at
        BEFORE UPDATE ON fact_order
        FOR EACH ROW
        EXECUTE FUNCTION update_fact_order_updated_at();
    """

def get_fact_delivery_table_structure():
    """Get the table structure for fact_delivery based on the query"""
    return """
    CREATE TABLE IF NOT EXISTS fact_delivery (
        -- Columns from the fact_delivery query
        route_id VARCHAR(50),
        manifest_reference VARCHAR(100),
        route_detail_id VARCHAR(50),
        order_id VARCHAR(50),
        do_number VARCHAR(100),
        faktur_date DATE,
        created_date_only DATE,
        waktu TIME,
        delivery_date DATE,
        status VARCHAR(50),
        client_id VARCHAR(50),
        warehouse_id VARCHAR(50),
        origin_name VARCHAR(200),
        origin_city VARCHAR(100),
        customer_id VARCHAR(50),
        code VARCHAR(50),
        name VARCHAR(200),
        address TEXT,
        address_text TEXT,
        external_expedition_type VARCHAR(50),
        vehicle_id VARCHAR(50),
        driver_id VARCHAR(50),
        plate_number VARCHAR(20),
        driver_name VARCHAR(100),
        kenek_id VARCHAR(50),
        kenek_name VARCHAR(100),
        driver_status VARCHAR(50),
        manifest_integration_id VARCHAR(100),
        complete_time TIMESTAMP,
        net_price NUMERIC(15,2),
        quantity_delivery NUMERIC(15,2),
        quantity_faktur NUMERIC(15,2),
        
        -- Additional tracking columns
        last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        -- Composite primary key
        PRIMARY KEY (route_id, route_detail_id, order_id)
    );
    
    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_route_id ON fact_delivery(route_id);
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_order_id ON fact_delivery(order_id);
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_faktur_date ON fact_delivery(faktur_date);
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_delivery_date ON fact_delivery(delivery_date);
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_last_synced ON fact_delivery(last_synced);
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_driver_id ON fact_delivery(driver_id);
    CREATE INDEX IF NOT EXISTS idx_fact_delivery_vehicle_id ON fact_delivery(vehicle_id);
    
    -- Create trigger to update updated_at column
    CREATE OR REPLACE FUNCTION update_fact_delivery_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS trigger_fact_delivery_updated_at ON fact_delivery;
    CREATE TRIGGER trigger_fact_delivery_updated_at
        BEFORE UPDATE ON fact_delivery
        FOR EACH ROW
        EXECUTE FUNCTION update_fact_delivery_updated_at();
    """

def get_sync_log_table_structure():
    """Get the table structure for sync_log"""
    return """
    CREATE TABLE IF NOT EXISTS sync_log (
        id SERIAL PRIMARY KEY,
        sync_type VARCHAR(50) NOT NULL,
        start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP WITH TIME ZONE,
        status VARCHAR(20) NOT NULL,
        records_processed INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create indexes for sync_log
    CREATE INDEX IF NOT EXISTS idx_sync_log_sync_type ON sync_log(sync_type);
    CREATE INDEX IF NOT EXISTS idx_sync_log_start_time ON sync_log(start_time);
    CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);
    
    -- Create trigger to update updated_at column
    CREATE OR REPLACE FUNCTION update_sync_log_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    DROP TRIGGER IF EXISTS trigger_sync_log_updated_at ON sync_log;
    CREATE TRIGGER trigger_sync_log_updated_at
        BEFORE UPDATE ON sync_log
        FOR EACH ROW
        EXECUTE FUNCTION update_sync_log_updated_at();
    """

def create_table(db_manager, table_name, create_sql):
    """Create a table in Database B"""
    try:
        logger.info(f"Creating table: {table_name}")
        
        engine = db_manager.get_db_b_engine()
        with engine.connect() as conn:
            # Split the SQL into individual statements
            statements = create_sql.split(';')
            
            for statement in statements:
                statement = statement.strip()
                if statement:  # Skip empty statements
                    conn.execute(statement)
            
            conn.commit()
        
        logger.info(f"✓ Table {table_name} created successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error creating table {table_name}: {e}")
        return False

def drop_table_if_exists(db_manager, table_name):
    """Drop table if it exists"""
    try:
        logger.info(f"Dropping table if exists: {table_name}")
        
        engine = db_manager.get_db_b_engine()
        drop_sql = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
        
        with engine.connect() as conn:
            conn.execute(drop_sql)
            conn.commit()
        
        logger.info(f"✓ Table {table_name} dropped successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error dropping table {table_name}: {e}")
        return False

def check_table_exists(db_manager, table_name):
    """Check if table exists in Database B"""
    try:
        engine = db_manager.get_db_b_engine()
        check_sql = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        
        with engine.connect() as conn:
            result = conn.execute(check_sql, (table_name,))
            exists = result.fetchone()[0]
        
        return exists
        
    except Exception as e:
        logger.error(f"Error checking if table {table_name} exists: {e}")
        return False

def create_all_tables(db_manager, force_recreate=False):
    """Create all tables in Database B"""
    tables_config = [
        {
            'name': 'fact_order',
            'create_sql': get_fact_order_table_structure()
        },
        {
            'name': 'fact_delivery',
            'create_sql': get_fact_delivery_table_structure()
        },
        {
            'name': 'sync_log',
            'create_sql': get_sync_log_table_structure()
        }
    ]
    
    success_count = 0
    total_count = len(tables_config)
    
    for table_config in tables_config:
        table_name = table_config['name']
        create_sql = table_config['create_sql']
        
        # Check if table exists
        if check_table_exists(db_manager, table_name):
            if force_recreate:
                logger.info(f"Table {table_name} exists. Dropping and recreating...")
                if not drop_table_if_exists(db_manager, table_name):
                    continue
            else:
                logger.info(f"Table {table_name} already exists. Skipping...")
                success_count += 1
                continue
        
        # Create table
        if create_table(db_manager, table_name, create_sql):
            success_count += 1
    
    return success_count, total_count

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create tables in Database B')
    parser.add_argument('--force', 
                       action='store_true',
                       help='Force recreate tables if they exist')
    parser.add_argument('--table',
                       choices=['fact_order', 'fact_delivery', 'sync_log', 'all'],
                       default='all',
                       help='Specific table to create (default: all)')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting table creation process...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        if args.table == 'all':
            # Create all tables
            success_count, total_count = create_all_tables(db_manager, args.force)
            
            if success_count == total_count:
                logger.info(f"✓ All {total_count} tables created successfully!")
            else:
                logger.warning(f"⚠ {success_count}/{total_count} tables created successfully")
                sys.exit(1)
        else:
            # Create specific table
            table_configs = {
                'fact_order': {
                    'name': 'fact_order',
                    'create_sql': get_fact_order_table_structure()
                },
                'fact_delivery': {
                    'name': 'fact_delivery',
                    'create_sql': get_fact_delivery_table_structure()
                },
                'sync_log': {
                    'name': 'sync_log',
                    'create_sql': get_sync_log_table_structure()
                }
            }
            
            table_config = table_configs[args.table]
            table_name = table_config['name']
            create_sql = table_config['create_sql']
            
            # Check if table exists
            if check_table_exists(db_manager, table_name):
                if args.force:
                    logger.info(f"Table {table_name} exists. Dropping and recreating...")
                    if not drop_table_if_exists(db_manager, table_name):
                        sys.exit(1)
                else:
                    logger.info(f"Table {table_name} already exists. Use --force to recreate.")
                    return
            
            # Create table
            if create_table(db_manager, table_name, create_sql):
                logger.info(f"✓ Table {table_name} created successfully!")
            else:
                sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error in table creation process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 