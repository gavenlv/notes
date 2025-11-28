-- Chapter 4: Table Design Best Practices Examples
-- This script demonstrates proper table design with constraints and relationships

-- 1. Primary Key Design Examples

-- Good: Using SERIAL for auto-incrementing primary key
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alternative: Using UUID for distributed systems
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE distributed_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Foreign Key Constraints Examples

-- Parent table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Child table with foreign key
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0),
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Various Constraint Examples

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_amount NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Index Examples for Performance

-- Create indexes on frequently queried columns
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_date ON orders(order_date);

-- 5. Insert Sample Data

INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and gadgets'),
('Books', 'Physical and digital books'),
('Clothing', 'Apparel and accessories');

INSERT INTO users (username, email) VALUES
('john_doe', 'john@example.com'),
('jane_smith', 'jane@example.com');

INSERT INTO products (name, price, category_id) VALUES
('Laptop', 999.99, 1),
('Smartphone', 699.99, 1),
('Novel', 19.99, 2),
('T-shirt', 29.99, 3);

INSERT INTO orders (user_id, total_amount, shipping_address) VALUES
(1, 1019.98, '123 Main St, City, Country'),
(2, 49.98, '456 Oak Ave, Town, Country');

-- 6. Query Examples to Demonstrate Relationships

-- Join users and orders
SELECT u.username, o.total_amount, o.order_date 
FROM users u 
JOIN orders o ON u.id = o.user_id;

-- Join products and categories
SELECT p.name, p.price, c.name as category 
FROM products p 
LEFT JOIN categories c ON p.category_id = c.id;

-- Clean up (optional)
-- DROP TABLE orders;
-- DROP TABLE products;
-- DROP TABLE categories;
-- DROP TABLE users;
-- DROP TABLE distributed_users;