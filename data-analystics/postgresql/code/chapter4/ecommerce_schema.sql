-- Chapter 4: Complete E-commerce Schema Example
-- This script creates a complete schema for an e-commerce system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- 2. User Addresses Table
CREATE TABLE user_addresses (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_type VARCHAR(20) DEFAULT 'shipping' CHECK (address_type IN ('shipping', 'billing')),
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Categories Table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Products Table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    sku VARCHAR(50) UNIQUE NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    compare_at_price NUMERIC(10,2) CHECK (compare_at_price >= 0),
    cost_per_item NUMERIC(10,2) CHECK (cost_per_item >= 0),
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    inventory_quantity INTEGER DEFAULT 0 CHECK (inventory_quantity >= 0),
    inventory_policy VARCHAR(20) DEFAULT 'deny' CHECK (inventory_policy IN ('allow', 'deny')),
    weight DECIMAL(8,2),
    weight_unit VARCHAR(10) DEFAULT 'kg' CHECK (weight_unit IN ('g', 'kg', 'lb', 'oz')),
    specifications JSONB,
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Product Images Table
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded')),
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal NUMERIC(12,2) NOT NULL,
    tax_amount NUMERIC(12,2) DEFAULT 0,
    shipping_amount NUMERIC(12,2) DEFAULT 0,
    discount_amount NUMERIC(12,2) DEFAULT 0,
    total_amount NUMERIC(12,2) NOT NULL,
    shipping_address JSONB,
    billing_address JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. Order Items Table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. Shopping Cart Table
CREATE TABLE shopping_cart (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- 9. Indexes for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_tags ON products USING GIN(tags);
CREATE INDEX idx_products_specs ON products USING GIN(specifications);
CREATE INDEX idx_product_images_product ON product_images(product_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_shopping_cart_user ON shopping_cart(user_id);
CREATE INDEX idx_shopping_cart_product ON shopping_cart(product_id);

-- 10. Sample Data Insertion

-- Insert categories
INSERT INTO categories (name, description, slug) VALUES
('Electronics', 'Electronic devices and gadgets', 'electronics'),
('Computers', 'Desktops, laptops, and computer components', 'computers'),
('Smartphones', 'Mobile phones and accessories', 'smartphones'),
('Books', 'Physical and digital books', 'books');

-- Insert subcategories
INSERT INTO categories (name, description, slug, parent_id) VALUES
('Laptops', 'Portable computers', 'laptops', 2),
('Desktops', 'Personal computers', 'desktops', 2),
('Android Phones', 'Android-based smartphones', 'android-phones', 3),
('iOS Phones', 'Apple iPhones', 'ios-phones', 3);

-- Insert products
INSERT INTO products (name, description, short_description, sku, price, category_id, inventory_quantity, specifications, tags) VALUES
('Gaming Laptop Pro', 'High-performance gaming laptop with RTX graphics', 'Powerful gaming laptop for enthusiasts', 'GLP-001', 1499.99, 5, 25, 
'{"processor": "Intel i7", "memory": "16GB", "storage": "1TB SSD", "graphics": "RTX 3070"}', 
ARRAY['gaming', 'laptop', 'electronics']),

('Business Desktop', 'Reliable desktop computer for office work', 'Professional desktop for productivity', 'BDC-001', 899.99, 6, 15,
'{"processor": "AMD Ryzen 5", "memory": "8GB", "storage": "512GB SSD", "os": "Windows 11"}',
ARRAY['business', 'desktop', 'office']),

('Smartphone X', 'Latest Android smartphone with excellent camera', 'Flagship Android phone with premium features', 'SPX-001', 799.99, 7, 50,
'{"display": "6.7 inch", "camera": "108MP", "battery": "5000mAh", "os": "Android 13"}',
ARRAY['android', 'smartphone', 'camera']);

-- Insert users
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('john_doe', 'john.doe@example.com', 'hashed_password_123', 'John', 'Doe'),
('jane_smith', 'jane.smith@example.com', 'hashed_password_456', 'Jane', 'Smith');

-- Insert addresses
INSERT INTO user_addresses (user_id, address_type, street_address, city, state, postal_code, country, is_default) VALUES
((SELECT id FROM users WHERE username = 'john_doe'), 'shipping', '123 Main St', 'New York', 'NY', '10001', 'USA', TRUE),
((SELECT id FROM users WHERE username = 'jane_smith'), 'shipping', '456 Oak Ave', 'Los Angeles', 'CA', '90210', 'USA', TRUE);

-- Clean up function (optional)
/*
DROP TABLE IF EXISTS shopping_cart;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS product_images;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS user_addresses;
DROP TABLE IF EXISTS users;
*/