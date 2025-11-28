#!/usr/bin/env python3
"""
Chapter 4: Data Types and Table Design - Python Examples
This script demonstrates how to work with various PostgreSQL data types using Python and psycopg2
"""

import psycopg2
from psycopg2 import sql
import json
import uuid
from datetime import datetime, date, time
import os

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'mypassword',  # Change this to your actual password
    'port': '5432'
}

def create_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def demonstrate_data_types(cursor):
    """Demonstrate working with various PostgreSQL data types"""
    print("=== Working with PostgreSQL Data Types ===")
    
    # Create table for demonstration
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS python_data_types (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INTEGER,
            salary NUMERIC(10,2),
            birth_date DATE,
            start_time TIME,
            created_at TIMESTAMP,
            metadata JSONB,
            tags TEXT[]
        )
    """)
    
    # Insert data with various types
    sample_data = {
        'name': 'John Doe',
        'age': 30,
        'salary': 75000.50,
        'birth_date': date(1993, 5, 15),
        'start_time': time(9, 30, 0),
        'created_at': datetime.now(),
        'metadata': json.dumps({
            'department': 'Engineering',
            'skills': ['Python', 'SQL', 'Docker'],
            'experience_years': 5
        }),
        'tags': ['developer', 'backend', 'python']
    }
    
    cursor.execute("""
        INSERT INTO python_data_types 
        (name, age, salary, birth_date, start_time, created_at, metadata, tags)
        VALUES (%(name)s, %(age)s, %(salary)s, %(birth_date)s, %(start_time)s, 
                %(created_at)s, %(metadata)s, %(tags)s)
    """, sample_data)
    
    # Query and display the data
    cursor.execute("SELECT * FROM python_data_types")
    result = cursor.fetchone()
    print(f"Inserted record: {result}")

def demonstrate_json_operations(cursor):
    """Demonstrate JSON/JSONB operations"""
    print("\n=== Working with JSON Data ===")
    
    # Create table for JSON examples
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS json_examples (
            id SERIAL PRIMARY KEY,
            user_data JSONB
        )
    """)
    
    # Insert JSON data
    user_profile = {
        'name': 'Jane Smith',
        'age': 28,
        'preferences': {
            'theme': 'dark',
            'notifications': True,
            'language': 'en'
        },
        'hobbies': ['reading', 'hiking', 'photography']
    }
    
    cursor.execute("""
        INSERT INTO json_examples (user_data) VALUES (%s)
    """, (json.dumps(user_profile),))
    
    # Query JSON data
    cursor.execute("""
        SELECT 
            user_data->>'name' as name,
            (user_data->'preferences'->>'theme') as theme,
            user_data->'hobbies' as hobbies
        FROM json_examples
    """)
    
    result = cursor.fetchone()
    print(f"Extracted JSON data: Name={result[0]}, Theme={result[1]}, Hobbies={result[2]}")
    
    # Query with JSON conditions
    cursor.execute("""
        SELECT user_data FROM json_examples 
        WHERE user_data->'preferences'->>'theme' = 'dark'
    """)
    
    result = cursor.fetchone()
    print(f"Users with dark theme: {result[0] if result else 'None'}")

def demonstrate_array_operations(cursor):
    """Demonstrate array operations"""
    print("\n=== Working with Arrays ===")
    
    # Create table for array examples
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS array_examples (
            id SERIAL PRIMARY KEY,
            numbers INTEGER[],
            tags TEXT[]
        )
    """)
    
    # Insert array data
    cursor.execute("""
        INSERT INTO array_examples (numbers, tags) VALUES (%s, %s)
    """, ([1, 2, 3, 4, 5], ['python', 'database', 'tutorial']))
    
    # Query arrays
    cursor.execute("SELECT * FROM array_examples")
    result = cursor.fetchone()
    print(f"Array data: Numbers={result[1]}, Tags={result[2]}")
    
    # Query with array conditions
    cursor.execute("""
        SELECT * FROM array_examples 
        WHERE %s = ANY(tags)
    """, ('python',))
    
    result = cursor.fetchone()
    print(f"Records with 'python' tag: {result is not None}")

def demonstrate_uuid_operations(cursor):
    """Demonstrate UUID operations"""
    print("\n=== Working with UUIDs ===")
    
    # Create extension if not exists
    cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    
    # Create table with UUID
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uuid_examples (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            name VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Insert data (UUID will be auto-generated)
    cursor.execute("""
        INSERT INTO uuid_examples (name) VALUES (%s) RETURNING id
    """, ('Test Record',))
    
    result = cursor.fetchone()
    print(f"Generated UUID: {result[0]}")

def main():
    """Main function to demonstrate data type operations"""
    conn = create_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Demonstrate various data types
        demonstrate_data_types(cursor)
        conn.commit()
        
        # Demonstrate JSON operations
        demonstrate_json_operations(cursor)
        conn.commit()
        
        # Demonstrate array operations
        demonstrate_array_operations(cursor)
        conn.commit()
        
        # Demonstrate UUID operations
        demonstrate_uuid_operations(cursor)
        conn.commit()
        
        print("\n=== All demonstrations completed successfully ===")
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()