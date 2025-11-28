#!/usr/bin/env python3
"""
Chapter 3: Basic SQL Syntax - Python Examples
This script demonstrates how to perform basic SQL operations using Python and psycopg2
"""

import psycopg2
from psycopg2 import sql
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

def create_sample_tables(cursor):
    """Create sample tables for demonstration"""
    # Create employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(50),
            salary DECIMAL(10, 2),
            hire_date DATE DEFAULT CURRENT_DATE
        )
    """)
    
    # Insert sample data
    cursor.execute("""
        INSERT INTO employees (name, department, salary, hire_date) 
        VALUES 
            ('John Doe', 'Engineering', 75000.00, '2022-01-15'),
            ('Jane Smith', 'Marketing', 65000.00, '2022-03-20'),
            ('Bob Johnson', 'Sales', 70000.00, '2021-11-10')
        ON CONFLICT DO NOTHING
    """)

def select_examples(cursor):
    """Demonstrate SELECT operations"""
    print("=== SELECT Examples ===")
    
    # Select all employees
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    print("All employees:")
    for emp in employees:
        print(f"  {emp}")
    
    # Select with WHERE clause
    cursor.execute("SELECT name, salary FROM employees WHERE salary > %s", (70000,))
    high_earners = cursor.fetchall()
    print("\nEmployees with salary > 70000:")
    for emp in high_earners:
        print(f"  {emp[0]}: ${emp[1]}")
    
    # Select with ORDER BY
    cursor.execute("SELECT name, department FROM employees ORDER BY name")
    sorted_employees = cursor.fetchall()
    print("\nEmployees sorted by name:")
    for emp in sorted_employees:
        print(f"  {emp[0]} - {emp[1]}")

def insert_examples(cursor):
    """Demonstrate INSERT operations"""
    print("\n=== INSERT Examples ===")
    
    # Insert single row
    cursor.execute("""
        INSERT INTO employees (name, department, salary) 
        VALUES (%s, %s, %s)
        RETURNING id, name
    """, ('Alice Johnson', 'HR', 62000.00))
    
    new_employee = cursor.fetchone()
    print(f"Inserted new employee: ID {new_employee[0]}, Name {new_employee[1]}")
    
    # Insert multiple rows
    employees_data = [
        ('Charlie Brown', 'Finance', 68000.00),
        ('Diana Prince', 'Engineering', 80000.00)
    ]
    
    cursor.executemany("""
        INSERT INTO employees (name, department, salary) 
        VALUES (%s, %s, %s)
    """, employees_data)
    
    print(f"Inserted {len(employees_data)} new employees")

def update_examples(cursor):
    """Demonstrate UPDATE operations"""
    print("\n=== UPDATE Examples ===")
    
    # Update single row
    cursor.execute("""
        UPDATE employees 
        SET salary = %s 
        WHERE name = %s
        RETURNING id, name, salary
    """, (65000.00, 'Alice Johnson'))
    
    updated_employee = cursor.fetchone()
    print(f"Updated employee: ID {updated_employee[0]}, Name {updated_employee[1]}, New Salary ${updated_employee[2]}")
    
    # Update multiple rows
    cursor.execute("""
        UPDATE employees 
        SET salary = salary * 1.05 
        WHERE department = %s
    """, ('Engineering',))
    
    print(f"Updated salaries for {cursor.rowcount} Engineering employees")

def delete_examples(cursor):
    """Demonstrate DELETE operations"""
    print("\n=== DELETE Examples ===")
    
    # Delete specific employee
    cursor.execute("""
        DELETE FROM employees 
        WHERE name = %s
        RETURNING id, name
    """, ('Bob Johnson',))
    
    deleted_employee = cursor.fetchone()
    if deleted_employee:
        print(f"Deleted employee: ID {deleted_employee[0]}, Name {deleted_employee[1]}")
    else:
        print("No employee found to delete")

def main():
    """Main function to demonstrate SQL operations"""
    conn = create_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Create sample tables
        create_sample_tables(cursor)
        conn.commit()
        
        # Demonstrate SELECT operations
        select_examples(cursor)
        
        # Demonstrate INSERT operations
        insert_examples(cursor)
        conn.commit()
        
        # Demonstrate UPDATE operations
        update_examples(cursor)
        conn.commit()
        
        # Demonstrate DELETE operations
        delete_examples(cursor)
        conn.commit()
        
        # Final query to show results
        print("\n=== Final Employee List ===")
        cursor.execute("SELECT name, department, salary FROM employees ORDER BY name")
        employees = cursor.fetchall()
        for emp in employees:
            print(f"  {emp[0]} - {emp[1]} - ${emp[2]}")
        
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