-- Sample Rollback File
-- Version: V1__create_users_table
-- Description: Rollback for creating initial users table

-- Drop index on email
ALTER TABLE users DROP INDEX idx_email;

-- Drop users table
DROP TABLE users;