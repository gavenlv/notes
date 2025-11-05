-- Database Schema for MyApp

-- Create database
CREATE DATABASE myapp;

-- Connect to database
\c myapp;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    author_id INTEGER REFERENCES users(id),
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_published ON posts(published);

-- Permissions
GRANT ALL PRIVILEGES ON TABLE users TO myapp_user;
GRANT ALL PRIVILEGES ON TABLE posts TO myapp_user;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO myapp_user;
GRANT USAGE, SELECT ON SEQUENCE posts_id_seq TO myapp_user;