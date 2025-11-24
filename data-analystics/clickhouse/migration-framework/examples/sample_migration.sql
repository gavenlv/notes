-- Sample Migration File
-- Version: V1__create_users_table
-- Description: Create initial users table

-- Create users table
CREATE TABLE users (
    id UInt64,
    name String,
    email String,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (id);

-- Insert sample data
INSERT INTO users (id, name, email) VALUES
(1, 'John Doe', 'john.doe@example.com'),
(2, 'Jane Smith', 'jane.smith@example.com');

-- Create index on email
ALTER TABLE users ADD INDEX idx_email email TYPE minmax GRANULARITY 1;