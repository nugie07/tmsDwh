#!/usr/bin/env python3
"""
Fact Order Data Processing Program
This program executes the fact_order query from Database A and upserts the results to Database B
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def get_fact_order_query():
    """Return the fact_order query"""
    return """
    SELECT
      a.status,
      c.manifest_reference,
      a.order_id,
      c.manifest_integration_id,
      c.external_expedition_type,
      d.driver_name,
      e.code,
      a.faktur_date,
      a.created_date AS tms_created,
      DATE(c.created_date) AS route_created,
      a.delivery_date,
      c.route_id,
      a.updated_date AS tms_complete,
      DATE(g.location_confirmation_timestamp) as location_confirmation,
      SUM(od.quantity_faktur) AS faktur_total_quantity,
      SUM(od.quantity_delivery) AS tms_total_quantity,
      SUM(od.quantity_delivery) - SUM(od.quantity_unloading) AS total_return,
      SUM(od.net_price) AS total_net_value
    FROM
      "public"."order" AS a
    LEFT JOIN
      "public"."route_detail" AS b
    ON
      b.order_id = a.order_id
    LEFT JOIN
      "public"."route" AS c
    ON
      c.route_id = b.route_id
    LEFT JOIN
      "public"."dma_driver" AS d
    ON
      d.driver_id = c.driver_id
    LEFT JOIN
      "public"."mst_vehicle" AS e
    ON
      e.mst_vehicle_id = c.vehicle_id
    LEFT JOIN
      "public"."driver_tasks" AS f
    ON
      f.order_id = a.order_id
    LEFT JOIN
      "public"."driver_task_confirmations" AS g
    ON
      g.driver_task_id = f.driver_task_id
    LEFT JOIN
      "public"."order_detail" AS od
    ON
      od.order_id = a.order_id
    WHERE
      a.faktur_date >= '2024-12-01'
      AND a.faktur_date <= CURRENT_DATE
    GROUP BY
      a.status,
      c.manifest_reference,
      a.order_id,
      c.manifest_integration_id,
      c.external_expedition_type,
      d.driver_name,
      e.code,
      a.faktur_date,
      a.created_date,
      c.created_date,
      a.delivery_date,
      c.route_id,
      a.updated_date,
      g.location_confirmation_timestamp
    ORDER BY
      a.faktur_date DESC
    """

def create_fact_order_table_schema_b(db_manager):
    """Create fact_order table in Database B if it doesn't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS tms_fact_order (
        status VARCHAR(50),
        manifest_reference VARCHAR(100),
        order_id VARCHAR(50) PRIMARY KEY,
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
        last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        engine = db_manager.get_db_b_engine()
        with engine.connect() as conn:
            conn.execute(create_table_query)
            conn.commit()
        logger.info("tms_fact_order table created/verified in Database B")
    except Exception as e:
        logger.error(f"Error creating fact_order table: {e}")
        raise

def process_fact_order():
    """Main function to process fact_order data"""
    try:
        logger.info("Starting fact_order data processing...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Create table in Database B if not exists
        create_fact_order_table_schema_b(db_manager)
        
        # Execute query on Database A
        logger.info("Executing fact_order query on Database A...")
        query = get_fact_order_query()
        df = db_manager.execute_query_to_dataframe(query, 'A')
        
        if df.empty:
            logger.warning("No data retrieved from fact_order query")
            return
        
        logger.info(f"Retrieved {len(df)} rows from fact_order query")
        
        # Define unique columns for upsert
        unique_columns = ['order_id']
        
        # Upsert data to Database B
        logger.info("Upserting fact_order data to Database B...")
        db_manager.upsert_dataframe_to_db(df, 'tms_fact_order', unique_columns, 'B')
        
        logger.info("fact_order data processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in fact_order processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_fact_order() 