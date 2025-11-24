-- PostgreSQL Database Initialization Script
-- Creates sample tables and views for data quality testing

-- Drop existing objects if they exist (with CASCADE to handle dependencies)
DROP VIEW IF EXISTS active_users_view CASCADE;
DROP VIEW IF EXISTS recent_orders_view CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table (constraints removed for data quality testing)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table (constraints removed for data quality testing)
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    product_name VARCHAR(255),
    quantity INTEGER,
    price DECIMAL(10,2),
    order_status VARCHAR(20) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert valid sample data into users first
INSERT INTO users (name, email, status, created_at) VALUES
    ('John Doe', 'john.doe@example.com', 'active', NOW() - INTERVAL '1 day'),
    ('Jane Smith', 'jane.smith@example.com', 'active', NOW() - INTERVAL '2 days'),
    ('Bob Johnson', 'bob.johnson@example.com', 'inactive', NOW() - INTERVAL '5 days'),
    ('Alice Brown', 'alice.brown@example.com', 'pending', NOW() - INTERVAL '1 hour'),
    ('Charlie Wilson', 'charlie.wilson@example.com', 'active', NOW() - INTERVAL '3 days'),
    ('Diana Davis', 'diana.davis@example.com', 'active', NOW() - INTERVAL '6 hours'),
    ('Eva Martinez', 'eva.martinez@example.com', 'pending', NOW() - INTERVAL '2 hours'),
    ('Frank Garcia', 'frank.garcia@example.com', 'active', NOW() - INTERVAL '4 days'),
    ('Grace Lee', 'grace.lee@example.com', 'active', NOW() - INTERVAL '12 hours'),
    ('Henry Taylor', 'henry.taylor@example.com', 'inactive', NOW() - INTERVAL '7 days'),
    ('Future User', 'future.user@example.com', 'active', NOW() + INTERVAL '1 day'); -- Future registration date

-- Insert data quality test cases (these will now succeed but be caught by Soda checks)
INSERT INTO users (name, email, status, created_at) VALUES
    (NULL, 'missing.name@example.com', 'active', NOW() - INTERVAL '1 day'), -- NULL name - will be caught by NOT NULL checks
    ('Duplicate Email', 'john.doe@example.com', 'active', NOW() - INTERVAL '1 day'), -- Duplicate email - will be caught by uniqueness checks
    ('Test Invalid Email', 'invalid-email-format', 'active', NOW() - INTERVAL '1 day'), -- Invalid email format - will be caught by pattern checks
    ('Invalid Status User', 'invalid.status@example.com', 'unknown', NOW() - INTERVAL '1 day'), -- Invalid status value
    ('Future User', 'future.user@example.com', 'active', NOW() + INTERVAL '1 day'), -- Future registration date
    ('', 'empty.name@example.com', 'active', NOW() - INTERVAL '1 day'), -- Empty name
    ('Very Long Name', 'long.name@example.com', 'active', NOW() - INTERVAL '1 day'), -- Shortened but still for length validation
    ('Test User', '', 'active', NOW() - INTERVAL '1 day'), -- Empty email
    ('Test User', NULL, 'active', NOW() - INTERVAL '1 day'), -- NULL email
    ('Old User', 'old.user@example.com', 'active', NOW() - INTERVAL '365 days'); -- Very old registration

-- Insert valid sample data into orders
INSERT INTO orders (user_id, product_name, quantity, price, order_status, order_date) VALUES
    (1, 'Laptop Computer', 1, 999.99, 'delivered', NOW() - INTERVAL '1 day'),
    (1, 'Wireless Mouse', 2, 29.99, 'delivered', NOW() - INTERVAL '1 day'),
    (2, 'Smartphone', 1, 599.99, 'shipped', NOW() - INTERVAL '2 days'),
    (3, 'Tablet', 1, 299.99, 'cancelled', NOW() - INTERVAL '5 days'),
    (4, 'Headphones', 1, 79.99, 'pending', NOW() - INTERVAL '1 hour'),
    (5, 'Keyboard', 1, 49.99, 'processing', NOW() - INTERVAL '3 days'),
    (6, 'Monitor', 1, 249.99, 'shipped', NOW() - INTERVAL '6 hours'),
    (7, 'USB Cable', 3, 12.99, 'pending', NOW() - INTERVAL '2 hours'),
    (8, 'External Hard Drive', 1, 89.99, 'delivered', NOW() - INTERVAL '4 days'),
    (9, 'Webcam', 1, 39.99, 'processing', NOW() - INTERVAL '12 hours'),
    (1, 'Phone Case', 1, 19.99, 'delivered', NOW() - INTERVAL '3 hours'),
    (2, 'Screen Protector', 2, 9.99, 'shipped', NOW() - INTERVAL '1 day'),
    (5, 'Power Bank', 1, 34.99, 'pending', NOW() - INTERVAL '30 minutes'),
    (6, 'Bluetooth Speaker', 1, 59.99, 'processing', NOW() - INTERVAL '4 hours'),
    (9, 'Gaming Mouse', 1, 69.99, 'delivered', NOW() - INTERVAL '2 days');

-- Insert data quality test cases for orders (these will now succeed but be caught by Soda checks)
INSERT INTO orders (user_id, product_name, quantity, price, order_status, order_date) VALUES
    (999, 'Invalid User Order', 1, 10.00, 'pending', NOW()), -- Invalid user_id - referential integrity check
    (1, NULL, 1, 25.00, 'delivered', NOW()), -- Missing product name - NULL check
    (NULL, 'No User Product', 1, 15.00, 'pending', NOW()), -- NULL user_id
    (1, 'Zero Quantity Item', 0, 10.00, 'pending', NOW()), -- Zero quantity - range check
    (1, 'Negative Quantity Item', -5, 10.00, 'pending', NOW()), -- Negative quantity
    (1, 'Negative Price Item', 1, -5.00, 'pending', NOW()), -- Negative price - range check
    (1, 'Zero Price Item', 1, 0.00, 'pending', NOW()), -- Zero price
    (1, 'Very Expensive Item', 1, 999999.99, 'pending', NOW()), -- Extremely high price
    (1, 'Invalid Status Order', 1, 25.00, 'unknown_status', NOW()), -- Invalid order status
    (1, '', 1, 25.00, 'pending', NOW()), -- Empty product name
    (1, 'Test Product With Long Name', 1, 0.01, 'pending', NOW()), -- Shortened but still for length validation
    (2, 'Future Order', 1, 50.00, 'pending', NOW() + INTERVAL '1 day'), -- Future order date
    (1, 'Old Order', 1, 25.00, 'delivered', NOW() - INTERVAL '365 days'), -- Very old order
    (1, 'High Quantity Order', 9999, 1.00, 'pending', NOW()), -- Extremely high quantity
    (1, 'Product with Special Chars !@#$%^&*()', 1, 25.00, 'pending', NOW()); -- Special characters in product name

-- Create view for active users
CREATE VIEW active_users_view AS
SELECT 
    id,
    name,
    email,
    created_at,
    EXTRACT(days FROM (NOW() - created_at)) as days_since_registration
FROM users 
WHERE status = 'active';

-- Create view for recent orders (last 7 days)
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
WHERE o.order_date >= NOW() - INTERVAL '7 days'
ORDER BY o.order_date DESC;

-- Create indexes for better performance
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(order_status);

-- Display summary
SELECT 'PostgreSQL Database Initialized Successfully' as status;
SELECT 'Users created: ' || COUNT(*) as summary FROM users;
SELECT 'Orders created: ' || COUNT(*) as summary FROM orders;
SELECT 'Views created: 2 (active_users_view, recent_orders_view)' as summary;
