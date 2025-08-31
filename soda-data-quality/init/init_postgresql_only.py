#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script
Initializes only PostgreSQL database with sample data
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, 'config', 'environment.env')
load_dotenv(env_path)

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
        sql_file = Path(os.path.join(project_root, 'init', 'scripts', 'init_postgresql.sql'))
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

def main():
    """Main initialization function"""
    logger.info("🚀 Starting PostgreSQL database initialization...")
    
    # Check environment variables
    required_vars = [
        'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_DATABASE', 
        'POSTGRES_USERNAME', 'POSTGRES_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Initialize PostgreSQL
    postgres_success = init_postgresql()
    
    if postgres_success:
        logger.info("✅ PostgreSQL database initialized successfully!")
        logger.info("Ready to run data quality checks!")
        sys.exit(0)
    else:
        logger.error("❌ PostgreSQL database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

