#!/usr/bin/env python3
"""
Show Table Structure Program
This program shows the structure of tables in Database B
"""

import sys
import logging
from database_utils import DatabaseManager, logger

def get_table_structure(db_manager, table_name):
    """Get the structure of a table"""
    try:
        engine = db_manager.get_db_b_engine()
        
        # Get column information
        column_query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = %s
        ORDER BY ordinal_position;
        """
        
        # Get index information
        index_query = """
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE tablename = %s
        ORDER BY indexname;
        """
        
        # Get constraint information
        constraint_query = """
        SELECT 
            conname,
            contype,
            pg_get_constraintdef(oid) as constraint_definition
        FROM pg_constraint 
        WHERE conrelid = %s::regclass
        ORDER BY conname;
        """
        
        with engine.connect() as conn:
            # Get table OID for constraint query
            oid_query = "SELECT oid FROM pg_class WHERE relname = %s AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');"
            oid_result = conn.execute(oid_query, (table_name,))
            oid_row = oid_result.fetchone()
            
            if not oid_row:
                logger.error(f"Table {table_name} not found")
                return None
            
            table_oid = oid_row[0]
            
            # Get columns
            columns_result = conn.execute(column_query, (table_name,))
            columns = columns_result.fetchall()
            
            # Get indexes
            indexes_result = conn.execute(index_query, (table_name,))
            indexes = indexes_result.fetchall()
            
            # Get constraints
            constraints_result = conn.execute(constraint_query, (table_oid,))
            constraints = constraints_result.fetchall()
        
        return {
            'columns': columns,
            'indexes': indexes,
            'constraints': constraints
        }
        
    except Exception as e:
        logger.error(f"Error getting table structure for {table_name}: {e}")
        return None

def format_column_info(column):
    """Format column information for display"""
    column_name, data_type, is_nullable, column_default, char_max_length, numeric_precision, numeric_scale = column
    
    # Format data type
    if data_type == 'character varying' and char_max_length:
        formatted_type = f"VARCHAR({char_max_length})"
    elif data_type == 'numeric' and numeric_precision and numeric_scale:
        formatted_type = f"NUMERIC({numeric_precision},{numeric_scale})"
    elif data_type == 'numeric' and numeric_precision:
        formatted_type = f"NUMERIC({numeric_precision})"
    else:
        formatted_type = data_type.upper()
    
    # Format nullable
    nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
    
    # Format default
    default = f"DEFAULT {column_default}" if column_default else ""
    
    return f"{column_name:<30} {formatted_type:<20} {nullable:<10} {default}"

def show_table_structure(db_manager, table_name):
    """Show the structure of a specific table"""
    logger.info(f"Table Structure: {table_name}")
    logger.info("=" * 80)
    
    structure = get_table_structure(db_manager, table_name)
    if not structure:
        return False
    
    # Show columns
    logger.info("COLUMNS:")
    logger.info("-" * 80)
    logger.info(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default'}")
    logger.info("-" * 80)
    
    for column in structure['columns']:
        logger.info(format_column_info(column))
    
    # Show constraints
    if structure['constraints']:
        logger.info("")
        logger.info("CONSTRAINTS:")
        logger.info("-" * 80)
        for constraint in structure['constraints']:
            conname, contype, definition = constraint
            constraint_type = {
                'p': 'PRIMARY KEY',
                'f': 'FOREIGN KEY',
                'u': 'UNIQUE',
                'c': 'CHECK'
            }.get(contype, contype.upper())
            
            logger.info(f"{conname:<30} {constraint_type:<15} {definition}")
    
    # Show indexes
    if structure['indexes']:
        logger.info("")
        logger.info("INDEXES:")
        logger.info("-" * 80)
        for index in structure['indexes']:
            indexname, indexdef = index
            logger.info(f"{indexname:<30} {indexdef}")
    
    logger.info("=" * 80)
    return True

def list_tables(db_manager):
    """List all tables in Database B"""
    try:
        engine = db_manager.get_db_b_engine()
        
        list_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        with engine.connect() as conn:
            result = conn.execute(list_query)
            tables = result.fetchall()
        
        if tables:
            logger.info("Available tables in Database B:")
            logger.info("-" * 40)
            for table in tables:
                logger.info(f"  - {table[0]}")
        else:
            logger.info("No tables found in Database B")
        
        return [table[0] for table in tables]
        
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return []

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Show table structure in Database B')
    parser.add_argument('--table',
                       help='Specific table to show structure (default: list all tables)')
    parser.add_argument('--list',
                       action='store_true',
                       help='List all tables')
    
    args = parser.parse_args()
    
    try:
        logger.info("Connecting to Database B...")
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        if args.list or not args.table:
            # List all tables
            tables = list_tables(db_manager)
            
            if args.table:
                # Show specific table structure
                if args.table in tables:
                    show_table_structure(db_manager, args.table)
                else:
                    logger.error(f"Table '{args.table}' not found")
                    logger.info("Available tables:")
                    for table in tables:
                        logger.info(f"  - {table}")
        else:
            # Show specific table structure
            show_table_structure(db_manager, args.table)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 