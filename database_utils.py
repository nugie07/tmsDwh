import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging
from datetime import datetime
import pytz

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_a_config = {
            'host': os.getenv('DB_A_HOST'),
            'port': os.getenv('DB_A_PORT'),
            'database': os.getenv('DB_A_NAME'),
            'user': os.getenv('DB_A_USER'),
            'password': os.getenv('DB_A_PASSWORD'),
            'schema': os.getenv('DB_A_SCHEMA')
        }
        
        self.db_b_config = {
            'host': os.getenv('DB_B_HOST'),
            'port': os.getenv('DB_B_PORT'),
            'database': os.getenv('DB_B_NAME'),
            'user': os.getenv('DB_B_USER'),
            'password': os.getenv('DB_B_PASSWORD'),
            'schema': os.getenv('DB_B_SCHEMA')
        }
        
        self.batch_size = int(os.getenv('BATCH_SIZE', 1000))
    
    def get_db_a_connection(self):
        """Get connection to Database A (Source)"""
        try:
            conn = psycopg2.connect(
                host=self.db_a_config['host'],
                port=self.db_a_config['port'],
                database=self.db_a_config['database'],
                user=self.db_a_config['user'],
                password=self.db_a_config['password']
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to Database A: {e}")
            raise
    
    def get_db_b_connection(self):
        """Get connection to Database B (Target)"""
        try:
            conn = psycopg2.connect(
                host=self.db_b_config['host'],
                port=self.db_b_config['port'],
                database=self.db_b_config['database'],
                user=self.db_b_config['user'],
                password=self.db_b_config['password']
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to Database B: {e}")
            raise
    
    def get_db_a_engine(self):
        """Get SQLAlchemy engine for Database A"""
        try:
            connection_string = f"postgresql://{self.db_a_config['user']}:{self.db_a_config['password']}@{self.db_a_config['host']}:{self.db_a_config['port']}/{self.db_a_config['database']}"
            engine = create_engine(connection_string)
            return engine
        except Exception as e:
            logger.error(f"Error creating engine for Database A: {e}")
            raise
    
    def get_db_b_engine(self):
        """Get SQLAlchemy engine for Database B"""
        try:
            connection_string = f"postgresql://{self.db_b_config['user']}:{self.db_b_config['password']}@{self.db_b_config['host']}:{self.db_b_config['port']}/{self.db_b_config['database']}"
            engine = create_engine(connection_string)
            return engine
        except Exception as e:
            logger.error(f"Error creating engine for Database B: {e}")
            raise
    
    def execute_query_to_dataframe(self, query, db_type='A'):
        """Execute query and return results as DataFrame"""
        try:
            if db_type.upper() == 'A':
                engine = self.get_db_a_engine()
            else:
                engine = self.get_db_b_engine()
            
            df = pd.read_sql(query, engine)
            logger.info(f"Query executed successfully. Retrieved {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def upsert_dataframe_to_db(self, df, table_name, unique_columns, db_type='B'):
        """Upsert DataFrame to database table"""
        try:
            if db_type.upper() == 'A':
                engine = self.get_db_a_engine()
                schema = self.db_a_config['schema']
            else:
                engine = self.get_db_b_engine()
                schema = self.db_b_config['schema']
            
            # Add last_synced column if not exists
            if 'last_synced' not in df.columns:
                df['last_synced'] = datetime.now(pytz.UTC)
            
            # Create temporary table for upsert
            temp_table_name = f"temp_{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Insert data to temporary table
            df.to_sql(temp_table_name, engine, schema=schema, if_exists='replace', index=False)
            
            # Build upsert query
            columns = df.columns.tolist()
            columns_str = ', '.join(columns)
            placeholders = ', '.join([f'%s' for _ in columns])
            
            # Build ON CONFLICT clause
            conflict_columns = ', '.join(unique_columns)
            update_columns = ', '.join([f'{col} = EXCLUDED.{col}' for col in columns if col not in unique_columns])
            
            upsert_query = f"""
                INSERT INTO {schema}.{table_name} ({columns_str})
                SELECT {columns_str} FROM {schema}.{temp_table_name}
                ON CONFLICT ({conflict_columns})
                DO UPDATE SET {update_columns}
            """
            
            # Execute upsert
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text(upsert_query))
                conn.commit()
            
            # Drop temporary table
            drop_query = f"DROP TABLE IF EXISTS {schema}.{temp_table_name}"
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text(drop_query))
                conn.commit()
            
            logger.info(f"Successfully upserted {len(df)} rows to {schema}.{table_name}")
            
        except Exception as e:
            logger.error(f"Error upserting data: {e}")
            raise 