#!/usr/bin/env python3
"""
Fact Delivery Data Processing Program
This program executes the fact_delivery query from Database A and upserts the results to Database B
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def get_fact_delivery_query():
    """Return the fact_delivery query"""
    return """
    SELECT
        a.route_id,
        a.manifest_reference,
        b.route_detail_id,
        b.order_id,
        c.do_number,
        c.faktur_date,
        DATE(a.created_date) AS created_date_only,
        a.created_date::TIMESTAMP::TIME as waktu,
        c.delivery_date,
        a.status,
        c.client_id,
        c.warehouse_id,
        c.origin_name,
        c.origin_city,
        c.customer_id,
        e.code,
        e."name",
        d.address,
        d.address_text,
        a.external_expedition_type,
        a.vehicle_id,
        a.driver_id,
        f.plate_number,
        g.driver_name,
        a.kenek_id,
        h.kenek_name,
        a.driver_status,
        a.manifest_integration_id,
        i.complete_time,
        j.net_price,
        j.quantity_delivery,
        j.quantity_faktur
    FROM
        PUBLIC.route AS a
    LEFT JOIN
        PUBLIC.route_detail AS b ON b.route_id = a.route_id
    LEFT JOIN
        PUBLIC."order" AS c ON c.order_id = b.order_id
    LEFT JOIN 
        PUBLIC.mst_location_child as d ON d.mst_location_child_id = c.customer_id
    LEFT JOIN
        PUBLIC.mst_location_parent as e ON e.mst_location_parent_id = d.mst_location_parent_id
    LEFT JOIN 
        PUBLIC.mst_vehicle as f ON f.mst_vehicle_id = a.vehicle_id
    LEFT JOIN 
        PUBLIC.dma_driver as g ON g.driver_id = a.driver_id
    LEFT JOIN 
        PUBLIC.dma_kenek as h ON h.kenek_id = a.kenek_id
    LEFT JOIN 
        PUBLIC.driver_tasks as i on i.order_id = b.order_id
    LEFT JOIN 
        PUBLIC.order_detail as j on j.order_id = b.order_id
    """

def create_fact_delivery_table_schema_b(db_manager):
    """Create fact_delivery table in Database B if it doesn't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS fact_delivery (
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
        last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (route_id, route_detail_id, order_id)
    );
    """
    
    try:
        engine = db_manager.get_db_b_engine()
        with engine.connect() as conn:
            conn.execute(create_table_query)
            conn.commit()
        logger.info("fact_delivery table created/verified in Database B")
    except Exception as e:
        logger.error(f"Error creating fact_delivery table: {e}")
        raise

def process_fact_delivery():
    """Main function to process fact_delivery data"""
    try:
        logger.info("Starting fact_delivery data processing...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Create table in Database B if not exists
        create_fact_delivery_table_schema_b(db_manager)
        
        # Execute query on Database A
        logger.info("Executing fact_delivery query on Database A...")
        query = get_fact_delivery_query()
        df = db_manager.execute_query_to_dataframe(query, 'A')
        
        if df.empty:
            logger.warning("No data retrieved from fact_delivery query")
            return
        
        logger.info(f"Retrieved {len(df)} rows from fact_delivery query")
        
        # Define unique columns for upsert (composite primary key)
        unique_columns = ['route_id', 'route_detail_id', 'order_id']
        
        # Upsert data to Database B
        logger.info("Upserting fact_delivery data to Database B...")
        db_manager.upsert_dataframe_to_db(df, 'fact_delivery', unique_columns, 'B')
        
        logger.info("fact_delivery data processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in fact_delivery processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_fact_delivery() 