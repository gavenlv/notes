#!/usr/bin/env python3
"""
Soda Core Demo with Mock Data
Demonstrates data quality checks using in-memory SQLite databases
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import tempfile

from dotenv import load_dotenv

# Load environment variables
load_dotenv('environment.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockDataQualityDemo:
    """Demo class using SQLite to simulate PostgreSQL data quality checks"""
    
    def __init__(self):
        self.reports_path = Path('./reports')
        self.reports_path.mkdir(exist_ok=True)
        
        # Create temporary SQLite databases
        self.pg_db_path = tempfile.mktemp(suffix='.db')
        self.ch_db_path = tempfile.mktemp(suffix='.db')
        
        logger.info("Initializing mock databases...")
        self.init_mock_postgresql()
        logger.info("Mock databases initialized successfully!")
    
    def init_mock_postgresql(self):
        """Initialize mock PostgreSQL data using SQLite"""
        conn = sqlite3.connect(self.pg_db_path)
        cursor = conn.cursor()
        
        # Create users table (without constraints for demo purposes)
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create orders table (without constraints for demo purposes)
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price DECIMAL(10,2),
                order_status TEXT DEFAULT 'pending',
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample users data with some data quality issues for testing
        users_data = [
            ('John Doe', 'john.doe@example.com', 'active', (datetime.now() - timedelta(days=1)).isoformat()),
            ('Jane Smith', 'jane.smith@example.com', 'active', (datetime.now() - timedelta(days=2)).isoformat()),
            ('Bob Johnson', 'bob.johnson@example.com', 'inactive', (datetime.now() - timedelta(days=5)).isoformat()),
            ('Alice Brown', 'alice.brown@example.com', 'pending', (datetime.now() - timedelta(hours=1)).isoformat()),
            ('Charlie Wilson', 'charlie.wilson@example.com', 'active', (datetime.now() - timedelta(days=3)).isoformat()),
            ('', 'empty.name@example.com', 'active', (datetime.now() - timedelta(days=1)).isoformat()),  # Data quality issue: empty name
            ('Test User', 'invalid-email', 'active', (datetime.now() - timedelta(days=1)).isoformat()),  # Data quality issue: invalid email
            ('Future User', 'future@example.com', 'active', (datetime.now() + timedelta(days=1)).isoformat()),  # Data quality issue: future date
        ]
        
        cursor.executemany(
            "INSERT INTO users (name, email, status, created_at) VALUES (?, ?, ?, ?)",
            users_data
        )
        
        # Insert sample orders data (including problematic data for testing)
        orders_data = [
            (1, 'Laptop Computer', 1, 999.99, 'delivered', (datetime.now() - timedelta(days=1)).isoformat()),
            (1, 'Wireless Mouse', 2, 29.99, 'delivered', (datetime.now() - timedelta(days=1)).isoformat()),
            (2, 'Smartphone', 1, 599.99, 'shipped', (datetime.now() - timedelta(days=2)).isoformat()),
            (3, 'Tablet', 1, 299.99, 'cancelled', (datetime.now() - timedelta(days=5)).isoformat()),
            (4, 'Headphones', 1, 79.99, 'pending', (datetime.now() - timedelta(hours=1)).isoformat()),
            (99, 'Invalid Product', 1, 99.99, 'pending', (datetime.now() - timedelta(hours=1)).isoformat()),  # Data quality issue: invalid user_id
            (1, '', 1, 49.99, 'pending', (datetime.now() - timedelta(hours=1)).isoformat()),  # Data quality issue: empty product name
            (2, 'Negative Quantity', -1, 29.99, 'pending', (datetime.now() - timedelta(hours=1)).isoformat()),  # Data quality issue: negative quantity
            (3, 'Negative Price', 1, -19.99, 'pending', (datetime.now() - timedelta(hours=1)).isoformat()),  # Data quality issue: negative price
        ]
        
        cursor.executemany(
            "INSERT INTO orders (user_id, product_name, quantity, price, order_status, order_date) VALUES (?, ?, ?, ?, ?, ?)",
            orders_data
        )
        
        # Create views
        cursor.execute("""
            CREATE VIEW active_users_view AS
            SELECT 
                id,
                name,
                email,
                created_at,
                CAST((julianday('now') - julianday(created_at)) as INTEGER) as days_since_registration
            FROM users 
            WHERE status = 'active'
        """)
        
        cursor.execute("""
            CREATE VIEW recent_orders_view AS
            SELECT 
                o.id,
                o.user_id,
                u.name as user_name,
                u.email as user_email,
                o.product_name,
                o.quantity,
                o.price,
                o.order_status,
                o.order_date,
                (o.quantity * o.price) as total_amount
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE datetime(o.order_date) >= datetime('now', '-7 days')
            ORDER BY o.order_date DESC
        """)
        
        conn.commit()
        conn.close()
    
    def run_manual_data_quality_checks(self):
        """Run manual data quality checks to simulate soda-core functionality"""
        logger.info("Running manual data quality checks...")
        
        conn = sqlite3.connect(self.pg_db_path)
        cursor = conn.cursor()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'checks': []
        }
        
        # Check 1: Users table has data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Users table has data',
            'table': 'users',
            'type': 'row_count',
            'result': 'PASS' if user_count > 0 else 'FAIL',
            'value': user_count,
            'details': f"Found {user_count} users"
        })
        
        # Check 2: No duplicate emails
        cursor.execute("SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1")
        duplicate_emails = cursor.fetchall()
        results['checks'].append({
            'name': 'No duplicate emails',
            'table': 'users',
            'type': 'duplicate_check',
            'result': 'PASS' if not duplicate_emails else 'FAIL',
            'value': len(duplicate_emails),
            'details': f"Found {len(duplicate_emails)} duplicate emails: {duplicate_emails}"
        })
        
        # Check 3: Name is required
        cursor.execute("SELECT COUNT(*) FROM users WHERE name IS NULL OR name = ''")
        missing_names = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Name is required',
            'table': 'users',
            'type': 'missing_check',
            'result': 'PASS' if missing_names == 0 else 'FAIL',
            'value': missing_names,
            'details': f"Found {missing_names} users with missing names"
        })
        
        # Check 4: Valid email format (simplified check)
        cursor.execute("SELECT COUNT(*) FROM users WHERE email NOT LIKE '%@%' OR email NOT LIKE '%.%'")
        invalid_emails = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Valid email format',
            'table': 'users',
            'type': 'format_check',
            'result': 'PASS' if invalid_emails == 0 else 'FAIL',
            'value': invalid_emails,
            'details': f"Found {invalid_emails} users with invalid email format"
        })
        
        # Check 5: No future registration dates
        cursor.execute("SELECT COUNT(*) FROM users WHERE created_at > datetime('now')")
        future_dates = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'No future registration dates',
            'table': 'users',
            'type': 'date_check',
            'result': 'PASS' if future_dates == 0 else 'FAIL',
            'value': future_dates,
            'details': f"Found {future_dates} users with future registration dates"
        })
        
        # Check 6: Orders table has data
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Orders table has data',
            'table': 'orders',
            'type': 'row_count',
            'result': 'PASS' if order_count > 0 else 'FAIL',
            'value': order_count,
            'details': f"Found {order_count} orders"
        })
        
        # Check 7: Valid user references
        cursor.execute("""
            SELECT COUNT(*) FROM orders o 
            LEFT JOIN users u ON o.user_id = u.id 
            WHERE u.id IS NULL
        """)
        invalid_refs = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Valid user references',
            'table': 'orders',
            'type': 'referential_integrity',
            'result': 'PASS' if invalid_refs == 0 else 'FAIL',
            'value': invalid_refs,
            'details': f"Found {invalid_refs} orders with invalid user references"
        })
        
        # Check 8: Positive quantity
        cursor.execute("SELECT COUNT(*) FROM orders WHERE quantity <= 0")
        negative_qty = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Positive quantity',
            'table': 'orders',
            'type': 'value_check',
            'result': 'PASS' if negative_qty == 0 else 'FAIL',
            'value': negative_qty,
            'details': f"Found {negative_qty} orders with non-positive quantity"
        })
        
        # Check 9: Non-negative price
        cursor.execute("SELECT COUNT(*) FROM orders WHERE price < 0")
        negative_price = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Non-negative price',
            'table': 'orders',
            'type': 'value_check',
            'result': 'PASS' if negative_price == 0 else 'FAIL',
            'value': negative_price,
            'details': f"Found {negative_price} orders with negative price"
        })
        
        # Check 10: Product name is required
        cursor.execute("SELECT COUNT(*) FROM orders WHERE product_name IS NULL OR product_name = ''")
        missing_products = cursor.fetchone()[0]
        results['checks'].append({
            'name': 'Product name is required',
            'table': 'orders',
            'type': 'missing_check',
            'result': 'PASS' if missing_products == 0 else 'FAIL',
            'value': missing_products,
            'details': f"Found {missing_products} orders with missing product names"
        })
        
        conn.close()
        return results
    
    def print_results(self, results):
        """Print formatted results"""
        print("\n" + "="*80)
        print("DATA QUALITY CHECK RESULTS")
        print("="*80)
        print(f"Timestamp: {results['timestamp']}")
        print(f"Total Checks: {len(results['checks'])}")
        
        passed = sum(1 for check in results['checks'] if check['result'] == 'PASS')
        failed = len(results['checks']) - passed
        
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print("-"*80)
        
        for i, check in enumerate(results['checks'], 1):
            status_icon = "✅" if check['result'] == 'PASS' else "❌"
            print(f"{i:2d}. {status_icon} {check['name']}")
            print(f"    Table: {check['table']} | Type: {check['type']} | Result: {check['result']}")
            print(f"    Details: {check['details']}")
            print()
        
        overall_status = "✅ HEALTHY" if failed == 0 else "⚠️  ISSUES FOUND"
        print(f"Overall Status: {overall_status}")
        print("="*80)
    
    def save_report(self, results):
        """Save results to JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_path / f"data_quality_demo_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Report saved to: {report_path}")
        return report_path
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.pg_db_path):
                os.remove(self.pg_db_path)
            if os.path.exists(self.ch_db_path):
                os.remove(self.ch_db_path)
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

def main():
    """Main demo function"""
    print("🚀 Starting Soda Core Data Quality Demo")
    print("Using mock SQLite databases to simulate PostgreSQL checks")
    
    demo = MockDataQualityDemo()
    
    try:
        # Run checks
        results = demo.run_manual_data_quality_checks()
        
        # Display results
        demo.print_results(results)
        
        # Save report
        report_path = demo.save_report(results)
        
        print(f"\n📊 Report saved to: {report_path}")
        print("\n💡 This demo shows how soda-core would work with real databases.")
        print("   To use with actual PostgreSQL/ClickHouse, ensure databases are running")
        print("   and update the configuration in environment.env")
        
        # Exit with appropriate code
        failed_checks = sum(1 for check in results['checks'] if check['result'] == 'FAIL')
        exit_code = 0 if failed_checks == 0 else 1
        
        return exit_code
        
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        return 1
    
    finally:
        demo.cleanup()

if __name__ == "__main__":
    sys.exit(main())
