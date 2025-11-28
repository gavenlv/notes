# Chapter 4 Code Examples

This directory contains code examples for Chapter 4: Data Types and Table Design.

## Files Included

1. `data_types_demo.sql` - SQL script demonstrating various PostgreSQL data types
2. `table_design_examples.sql` - SQL script showing best practices in table design
3. `ecommerce_schema.sql` - Complete schema for an e-commerce system
4. `python_examples.py` - Python examples for working with data types
5. `requirements.txt` - Python dependencies

## Running the Examples

1. Make sure you have PostgreSQL running
2. Connect to your database using psql or another client
3. Run the SQL scripts in order:
   ```sql
   \i data_types_demo.sql
   \i table_design_examples.sql
   \i ecommerce_schema.sql
   ```
4. For Python examples:
   ```bash
   pip install -r requirements.txt
   python python_examples.py
   ```

## Contents

The examples cover:
- Numeric, string, date/time, and JSON data types
- Primary key and foreign key design
- Various constraint types (NOT NULL, UNIQUE, CHECK, DEFAULT)
- Complete e-commerce schema design
- Python integration examples