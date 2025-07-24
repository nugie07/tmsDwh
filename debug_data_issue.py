#!/usr/bin/env python3
"""
Debug script to find problematic date/timestamp data in the database
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def check_table_structure():
    """Check the structure of problematic tables"""
    
    db_manager = DatabaseManager()
    
    # Check driver_task_confirmations table structure
    check_driver_task_confirmations_structure = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'driver_task_confirmations' 
    AND table_schema = 'public'
    ORDER BY ordinal_position;
    """
    
    # Check driver_tasks table structure
    check_driver_tasks_structure = """
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'driver_tasks' 
    AND table_schema = 'public'
    ORDER BY ordinal_position;
    """
    
    try:
        print("=== Checking driver_task_confirmations table structure ===")
        df1 = db_manager.execute_query_to_dataframe(check_driver_task_confirmations_structure, 'A')
        print(df1.to_string())
        
        print("\n=== Checking driver_tasks table structure ===")
        df2 = db_manager.execute_query_to_dataframe(check_driver_tasks_structure, 'A')
        print(df2.to_string())
        
    except Exception as e:
        logger.error(f"Error checking table structure: {e}")
        raise

def check_problematic_dates():
    """Check for problematic date/timestamp values in the database"""
    
    db_manager = DatabaseManager()
    
    # Query to check for problematic location_confirmation_timestamp values
    check_location_confirmation_query = """
    SELECT 
        driver_task_id,
        location_confirmation_timestamp,
        location_confirmation_timestamp::TEXT as timestamp_text
    FROM "public"."driver_task_confirmations" 
    WHERE location_confirmation_timestamp IS NOT NULL
    ORDER BY location_confirmation_timestamp DESC
    LIMIT 10;
    """
    
    # Query to check for problematic created_date values in route table
    check_route_created_date_query = """
    SELECT 
        route_id,
        created_date,
        created_date::TEXT as created_date_text
    FROM "public"."route" 
    WHERE created_date IS NOT NULL
    ORDER BY created_date DESC
    LIMIT 10;
    """
    
    # Query to check for problematic faktur_date values
    check_faktur_date_query = """
    SELECT 
        order_id,
        faktur_date,
        faktur_date::TEXT as faktur_date_text
    FROM "public"."order" 
    WHERE faktur_date IS NOT NULL
    ORDER BY faktur_date DESC
    LIMIT 10;
    """
    
    try:
        print("=== Checking location_confirmation_timestamp values ===")
        df1 = db_manager.execute_query_to_dataframe(check_location_confirmation_query, 'A')
        print(df1.to_string())
        
        print("\n=== Checking route created_date values ===")
        df2 = db_manager.execute_query_to_dataframe(check_route_created_date_query, 'A')
        print(df2.to_string())
        
        print("\n=== Checking faktur_date values ===")
        df3 = db_manager.execute_query_to_dataframe(check_faktur_date_query, 'A')
        print(df3.to_string())
        
    except Exception as e:
        logger.error(f"Error checking problematic dates: {e}")
        raise

def test_simple_query():
    """Test a simple query without problematic fields"""
    
    db_manager = DatabaseManager()
    
    # Simple query without location_confirmation_timestamp
    simple_query = """
    SELECT DISTINCT ON (a.order_id)
      a.status,
      c.manifest_reference,
      a.order_id,
      c.manifest_integration_id,
      c.external_expedition_type,
      d.driver_name,
      e.code,
      a.faktur_date,
      a.created_date AS tms_created,
      CASE 
        WHEN c.created_date IS NOT NULL 
        THEN c.created_date::DATE 
        ELSE NULL 
      END AS route_created,
      a.delivery_date,
      c.route_id,
      a.updated_date AS tms_complete,
      SUM(od.quantity_faktur)::NUMERIC(15,2) AS faktur_total_quantity,
      SUM(od.quantity_delivery)::NUMERIC(15,2) AS tms_total_quantity,
      (SUM(od.quantity_delivery) - SUM(od.quantity_unloading))::NUMERIC(15,2) AS total_return,
      SUM(od.net_price)::NUMERIC(15,2) AS total_net_value
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
      "public"."order_detail" AS od
    ON
      od.order_id = a.order_id
    WHERE 1=1 AND a.faktur_date >= '2025-04-01' AND a.faktur_date <= '2025-05-31'
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
      a.updated_date
    ORDER BY
      a.order_id, a.faktur_date DESC
    LIMIT 5;
    """
    
    try:
        print("=== Testing simple query without problematic fields ===")
        df = db_manager.execute_query_to_dataframe(simple_query, 'A')
        print(f"Query successful! Retrieved {len(df)} rows")
        print(df.to_string())
        
    except Exception as e:
        logger.error(f"Error in simple query: {e}")
        raise

if __name__ == "__main__":
    print("Debugging data issues in TMS database...")
    
    # First check table structure
    check_table_structure()
    
    print("\n" + "="*50)
    
    # Then check for problematic data
    check_problematic_dates()
    
    print("\n" + "="*50)
    
    # Then test simple query
    test_simple_query() 