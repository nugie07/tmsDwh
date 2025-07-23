#!/usr/bin/env python3
"""
Database Connection Test Script
This script tests the database connections for both Database A and B
"""

import sys
from database_utils import DatabaseManager, logger

def test_database_connections():
    """Test connections to both databases"""
    try:
        logger.info("Testing database connections...")
        
        db_manager = DatabaseManager()
        
        # Test Database A connection
        logger.info("Testing Database A connection...")
        try:
            conn_a = db_manager.get_db_a_connection()
            cursor_a = conn_a.cursor()
            cursor_a.execute("SELECT version();")
            version_a = cursor_a.fetchone()
            cursor_a.close()
            conn_a.close()
            logger.info(f"✓ Database A connection successful. PostgreSQL version: {version_a[0]}")
        except Exception as e:
            logger.error(f"✗ Database A connection failed: {e}")
            return False
        
        # Test Database B connection
        logger.info("Testing Database B connection...")
        try:
            conn_b = db_manager.get_db_b_connection()
            cursor_b = conn_b.cursor()
            cursor_b.execute("SELECT version();")
            version_b = cursor_b.fetchone()
            cursor_b.close()
            conn_b.close()
            logger.info(f"✓ Database B connection successful. PostgreSQL version: {version_b[0]}")
        except Exception as e:
            logger.error(f"✗ Database B connection failed: {e}")
            return False
        
        # Test SQLAlchemy engines
        logger.info("Testing SQLAlchemy engines...")
        try:
            engine_a = db_manager.get_db_a_engine()
            with engine_a.connect() as conn:
                result = conn.execute("SELECT 1 as test")
                logger.info("✓ Database A SQLAlchemy engine working")
        except Exception as e:
            logger.error(f"✗ Database A SQLAlchemy engine failed: {e}")
            return False
        
        try:
            engine_b = db_manager.get_db_b_engine()
            with engine_b.connect() as conn:
                result = conn.execute("SELECT 1 as test")
                logger.info("✓ Database B SQLAlchemy engine working")
        except Exception as e:
            logger.error(f"✗ Database B SQLAlchemy engine failed: {e}")
            return False
        
        logger.info("✓ All database connections successful!")
        return True
        
    except Exception as e:
        logger.error(f"Error during connection test: {e}")
        return False

def test_table_creation():
    """Test table creation in Database B"""
    try:
        logger.info("Testing table creation in Database B...")
        
        db_manager = DatabaseManager()
        
        # Test creating a simple table
        test_table_query = """
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            test_column VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        engine = db_manager.get_db_b_engine()
        with engine.connect() as conn:
            conn.execute(test_table_query)
            conn.commit()
        
        # Test inserting data
        insert_query = "INSERT INTO test_table (test_column) VALUES ('test_value');"
        with engine.connect() as conn:
            conn.execute(insert_query)
            conn.commit()
        
        # Test querying data
        select_query = "SELECT COUNT(*) FROM test_table;"
        with engine.connect() as conn:
            result = conn.execute(select_query)
            count = result.fetchone()[0]
        
        # Clean up
        drop_query = "DROP TABLE IF EXISTS test_table;"
        with engine.connect() as conn:
            conn.execute(drop_query)
            conn.commit()
        
        logger.info(f"✓ Table creation test successful. Inserted and queried {count} row(s)")
        return True
        
    except Exception as e:
        logger.error(f"✗ Table creation test failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting database connection tests...")
    
    # Test connections
    if not test_database_connections():
        logger.error("Database connection tests failed!")
        sys.exit(1)
    
    # Test table creation
    if not test_table_creation():
        logger.error("Table creation test failed!")
        sys.exit(1)
    
    logger.info("All tests passed! Your database configuration is working correctly.")
    logger.info("You can now run the synchronization programs.")

if __name__ == "__main__":
    main() 