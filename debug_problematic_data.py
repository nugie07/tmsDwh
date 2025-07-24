#!/usr/bin/env python3
"""
Debug script to identify problematic data causing "year 252025" error
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def check_problematic_timestamp_data():
    """Check for problematic timestamp data in driver_task_confirmations"""
    
    db_manager = DatabaseManager()
    
    # Check for problematic location_confirmation_timestamp values
    check_location_confirmation_query = """
    SELECT 
        driver_task_id,
        location_confirmation_timestamp,
        location_confirmation_timestamp::TEXT as timestamp_text,
        EXTRACT(YEAR FROM location_confirmation_timestamp) as year_extracted
    FROM "public"."driver_task_confirmations" 
    WHERE location_confirmation_timestamp IS NOT NULL
    ORDER BY location_confirmation_timestamp DESC
    LIMIT 20;
    """
    
    try:
        print("=== Checking location_confirmation_timestamp values ===")
        df1 = db_manager.execute_query_to_dataframe(check_location_confirmation_query, 'A')
        print(df1.to_string())
        
        # Check for any problematic years
        if 'year_extracted' in df1.columns:
            problematic_years = df1[df1['year_extracted'] > 2100]
            if not problematic_years.empty:
                print(f"\n=== PROBLEMATIC YEARS FOUND ===")
                print(problematic_years.to_string())
            else:
                print(f"\n=== No problematic years found in sample ===")
        
    except Exception as e:
        logger.error(f"Error checking location_confirmation_timestamp: {e}")
        print(f"Error: {e}")

def check_problematic_created_date_data():
    """Check for problematic created_date data in route table"""
    
    db_manager = DatabaseManager()
    
    # Check for problematic created_date values
    check_created_date_query = """
    SELECT 
        route_id,
        created_date,
        created_date::TEXT as created_date_text,
        EXTRACT(YEAR FROM created_date) as year_extracted
    FROM "public"."route" 
    WHERE created_date IS NOT NULL
    ORDER BY created_date DESC
    LIMIT 20;
    """
    
    try:
        print("\n=== Checking route created_date values ===")
        df2 = db_manager.execute_query_to_dataframe(check_created_date_query, 'A')
        print(df2.to_string())
        
        # Check for any problematic years
        if 'year_extracted' in df2.columns:
            problematic_years = df2[df2['year_extracted'] > 2100]
            if not problematic_years.empty:
                print(f"\n=== PROBLEMATIC YEARS FOUND ===")
                print(problematic_years.to_string())
            else:
                print(f"\n=== No problematic years found in sample ===")
        
    except Exception as e:
        logger.error(f"Error checking created_date: {e}")
        print(f"Error: {e}")

def find_problematic_data_in_date_range():
    """Find problematic data specifically in the date range that's causing issues"""
    
    db_manager = DatabaseManager()
    
    # Check for problematic data in the specific date range
    problematic_data_query = """
    SELECT 
        dtc.driver_task_id,
        dtc.location_confirmation_timestamp,
        dtc.location_confirmation_timestamp::TEXT as timestamp_text,
        EXTRACT(YEAR FROM dtc.location_confirmation_timestamp) as year_extracted,
        o.order_id,
        o.faktur_date
    FROM "public"."driver_task_confirmations" dtc
    JOIN "public"."driver_tasks" dt ON dt.driver_task_id = dtc.driver_task_id
    JOIN "public"."order" o ON o.order_id = dt.order_id
    WHERE dtc.location_confirmation_timestamp IS NOT NULL
    AND o.faktur_date >= '2025-04-01' 
    AND o.faktur_date <= '2025-05-31'
    ORDER BY dtc.location_confirmation_timestamp DESC
    LIMIT 50;
    """
    
    try:
        print("\n=== Checking problematic data in date range 2025-04-01 to 2025-05-31 ===")
        df = db_manager.execute_query_to_dataframe(problematic_data_query, 'A')
        print(df.to_string())
        
        # Check for any problematic years
        if 'year_extracted' in df.columns:
            problematic_years = df[df['year_extracted'] > 2100]
            if not problematic_years.empty:
                print(f"\n=== PROBLEMATIC YEARS FOUND IN DATE RANGE ===")
                print(problematic_years.to_string())
            else:
                print(f"\n=== No problematic years found in date range ===")
        
    except Exception as e:
        logger.error(f"Error checking problematic data in date range: {e}")
        print(f"Error: {e}")

def check_all_timestamp_fields():
    """Check all timestamp fields that might be causing the issue"""
    
    db_manager = DatabaseManager()
    
    # Check all timestamp fields in the query
    all_timestamps_query = """
    SELECT 
        o.order_id,
        o.faktur_date,
        o.created_date,
        o.updated_date,
        o.delivery_date,
        c.created_date as route_created_date,
        g.location_confirmation_timestamp,
        EXTRACT(YEAR FROM o.faktur_date) as faktur_year,
        EXTRACT(YEAR FROM o.created_date) as order_created_year,
        EXTRACT(YEAR FROM o.updated_date) as order_updated_year,
        EXTRACT(YEAR FROM o.delivery_date) as delivery_year,
        EXTRACT(YEAR FROM c.created_date) as route_created_year,
        EXTRACT(YEAR FROM g.location_confirmation_timestamp) as location_year
    FROM "public"."order" o
    LEFT JOIN "public"."route_detail" b ON b.order_id = o.order_id
    LEFT JOIN "public"."route" c ON c.route_id = b.route_id
    LEFT JOIN "public"."driver_tasks" f ON f.order_id = o.order_id
    LEFT JOIN "public"."driver_task_confirmations" g ON g.driver_task_id = f.driver_task_id
    WHERE o.faktur_date >= '2025-04-01' 
    AND o.faktur_date <= '2025-05-31'
    AND (
        EXTRACT(YEAR FROM o.faktur_date) > 2100 OR
        EXTRACT(YEAR FROM o.created_date) > 2100 OR
        EXTRACT(YEAR FROM o.updated_date) > 2100 OR
        EXTRACT(YEAR FROM o.delivery_date) > 2100 OR
        EXTRACT(YEAR FROM c.created_date) > 2100 OR
        EXTRACT(YEAR FROM g.location_confirmation_timestamp) > 2100
    )
    LIMIT 20;
    """
    
    try:
        print("\n=== Checking ALL timestamp fields for problematic years ===")
        df = db_manager.execute_query_to_dataframe(all_timestamps_query, 'A')
        if not df.empty:
            print(df.to_string())
        else:
            print("No problematic years found in any timestamp fields")
        
    except Exception as e:
        logger.error(f"Error checking all timestamp fields: {e}")
        print(f"Error: {e}")

def test_query_without_problematic_field():
    """Test query without the problematic field to isolate the issue"""
    
    db_manager = DatabaseManager()
    
    # Query without location_confirmation_timestamp
    safe_query = """
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
        print("\n=== Testing query WITHOUT location_confirmation_timestamp ===")
        df = db_manager.execute_query_to_dataframe(safe_query, 'A')
        print(f"Query successful! Retrieved {len(df)} rows")
        print(df.to_string())
        
    except Exception as e:
        logger.error(f"Error in safe query: {e}")
        print(f"Error: {e}")

def test_query_with_problematic_field():
    """Test query with the problematic field to reproduce the error"""
    
    db_manager = DatabaseManager()
    
    # Query with location_confirmation_timestamp
    problematic_query = """
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
      CASE 
        WHEN g.location_confirmation_timestamp IS NOT NULL 
        AND g.location_confirmation_timestamp >= '1900-01-01'::timestamp
        AND g.location_confirmation_timestamp <= '2100-12-31'::timestamp
        THEN g.location_confirmation_timestamp::DATE 
        ELSE NULL 
      END as location_confirmation,
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
      a.updated_date,
      g.location_confirmation_timestamp
    ORDER BY
      a.order_id, a.faktur_date DESC
    LIMIT 5;
    """
    
    try:
        print("\n=== Testing query WITH location_confirmation_timestamp ===")
        df = db_manager.execute_query_to_dataframe(problematic_query, 'A')
        print(f"Query successful! Retrieved {len(df)} rows")
        print(df.to_string())
        
    except Exception as e:
        logger.error(f"Error in problematic query: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Debugging problematic data causing 'year 252025' error...")
    
    # Check for problematic timestamp data
    check_problematic_timestamp_data()
    
    # Check for problematic created_date data
    check_problematic_created_date_data()
    
    # Find problematic data in specific date range
    find_problematic_data_in_date_range()
    
    # Check all timestamp fields
    check_all_timestamp_fields()
    
    # Test query without problematic field
    test_query_without_problematic_field()
    
    # Test query with problematic field
    test_query_with_problematic_field() 