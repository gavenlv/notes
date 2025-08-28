#!/usr/bin/env python3
"""
Simple database connection test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('environment.env')

def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        conn_params = {
            'host': os.getenv('POSTGRES_HOST'),
            'port': int(os.getenv('POSTGRES_PORT')),
            'database': os.getenv('POSTGRES_DATABASE'),
            'user': os.getenv('POSTGRES_USERNAME'),
            'password': os.getenv('POSTGRES_PASSWORD')
        }
        
        print(f"Testing PostgreSQL connection to {conn_params['host']}:{conn_params['port']}")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"✅ PostgreSQL connected: {result[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {str(e)}")
        return False

def test_clickhouse():
    """Test ClickHouse connection"""
    try:
        from clickhouse_driver import Client
        client = Client(
            host=os.getenv('CLICKHOUSE_HOST'),
            port=int(os.getenv('CLICKHOUSE_PORT')),
            user=os.getenv('CLICKHOUSE_USERNAME'),
            password=os.getenv('CLICKHOUSE_PASSWORD'),
            database=os.getenv('CLICKHOUSE_DATABASE')
        )
        
        print(f"Testing ClickHouse connection to {os.getenv('CLICKHOUSE_HOST')}:{os.getenv('CLICKHOUSE_PORT')}")
        result = client.execute("SELECT version()")
        print(f"✅ ClickHouse connected: {result[0][0]}")
        return True
    except Exception as e:
        print(f"❌ ClickHouse connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔌 Testing database connections...")
    pg_ok = test_postgresql()
    ch_ok = test_clickhouse()
    
    if pg_ok and ch_ok:
        print("\n✅ All database connections successful!")
    else:
        print("\n❌ Some database connections failed!")
        print("Please check your database configurations and ensure the servers are running.")
