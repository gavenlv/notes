#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script
Chapter 2: Installation and Configuration
"""

import psycopg2
from psycopg2 import Error
import sys

def test_connection():
    """Test connection to PostgreSQL database"""
    try:
        # Connect to PostgreSQL database
        connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="mypassword",  # Change this to your actual password
            port="5432"
        )
        
        # Create a cursor object
        cursor = connection.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        
        # Create a test table
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(50),
            salary DECIMAL(10, 2),
            hire_date DATE DEFAULT CURRENT_DATE
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'employees' created successfully")
        
        # Insert sample data
        insert_query = '''
        INSERT INTO employees (name, department, salary) VALUES 
        ('John Doe', 'Engineering', 75000.00),
        ('Jane Smith', 'Marketing', 65000.00),
        ('Bob Johnson', 'Sales', 70000.00);
        '''
        cursor.execute(insert_query)
        connection.commit()
        print("Sample data inserted successfully")
        
        # Query the data
        cursor.execute("SELECT * FROM employees;")
        records = cursor.fetchall()
        print("Employee Records:")
        for row in records:
            print(f"ID: {row[0]}, Name: {row[1]}, Department: {row[2]}, Salary: {row[3]}, Hire Date: {row[4]}")
            
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        
    finally:
        # Close database connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    test_connection()