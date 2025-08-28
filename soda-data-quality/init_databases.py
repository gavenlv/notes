#!/usr/bin/env python3
"""
Database Initialization Script
Initializes PostgreSQL and ClickHouse databases with sample data
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from clickhouse_driver import Client

# Load environment variables
load_dotenv('environment.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_postgresql():
    """Initialize PostgreSQL database"""
    logger.info("Initializing PostgreSQL database...")
    
    try:
        # Database connection parameters
        conn_params = {
            'host': os.getenv('POSTGRES_HOST'),
            'port': int(os.getenv('POSTGRES_PORT')),
            'database': os.getenv('POSTGRES_DATABASE'),
            'user': os.getenv('POSTGRES_USERNAME'),
            'password': os.getenv('POSTGRES_PASSWORD')
        }
        
        logger.info(f"Connecting to PostgreSQL at {conn_params['host']}:{conn_params['port']}")
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Read and execute SQL script
        sql_file = Path('scripts/init_postgresql.sql')
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL script not found: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Execute script
        cursor.execute(sql_script)
        
        # Get summary
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        
        logger.info(f"PostgreSQL initialization completed successfully!")
        logger.info(f"Created {user_count} users and {order_count} orders")
        logger.info(f"Created 2 views: active_users_view, recent_orders_view")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL: {str(e)}")
        return False

def init_clickhouse():
    """Initialize ClickHouse database"""
    logger.info("Initializing ClickHouse database...")
    
    try:
        # Database connection parameters
        client = Client(
            host=os.getenv('CLICKHOUSE_HOST'),
            port=int(os.getenv('CLICKHOUSE_PORT')),
            user=os.getenv('CLICKHOUSE_USERNAME'),
            password=os.getenv('CLICKHOUSE_PASSWORD'),
            database=os.getenv('CLICKHOUSE_DATABASE')
        )
        
        logger.info(f"Connecting to ClickHouse at {os.getenv('CLICKHOUSE_HOST')}:{os.getenv('CLICKHOUSE_PORT')}")
        
        # Read and execute SQL script
        sql_file = Path('scripts/init_clickhouse.sql')
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL script not found: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        # Split script into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement.strip():
                try:
                    client.execute(statement)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        logger.warning(f"Warning executing statement: {str(e)}")
        
        # Get summary
        event_count = client.execute("SELECT COUNT(*) FROM events")[0][0]
        session_count = client.execute("SELECT COUNT(*) FROM user_sessions")[0][0]
        
        logger.info(f"ClickHouse initialization completed successfully!")
        logger.info(f"Created {event_count} events and {session_count} sessions")
        logger.info(f"Created 2 views: daily_events_summary, user_activity_view")
        
        return True
        
    except Exception as e:
        logger.error(f"Error initializing ClickHouse: {str(e)}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Starting database initialization...")
    
    # Check environment variables
    required_vars = [
        'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DATABASE', 'POSTGRES_USERNAME', 'POSTGRES_PASSWORD',
        'CLICKHOUSE_HOST', 'CLICKHOUSE_PORT', 'CLICKHOUSE_DATABASE', 'CLICKHOUSE_USERNAME', 'CLICKHOUSE_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        sys.exit(1)
    
    # Initialize databases
    postgres_success = init_postgresql()
    clickhouse_success = init_clickhouse()
    
    if postgres_success and clickhouse_success:
        logger.info("✅ All databases initialized successfully!")
        logger.info("Ready to run data quality checks!")
        sys.exit(0)
    else:
        logger.error("❌ Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
