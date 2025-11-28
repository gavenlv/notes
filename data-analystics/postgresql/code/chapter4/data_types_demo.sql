-- Chapter 4: Data Types Demonstration
-- This script demonstrates various PostgreSQL data types and their usage

-- 1. Numeric Types Examples
CREATE TABLE numeric_examples (
    id SERIAL PRIMARY KEY,
    small_int_col SMALLINT,
    int_col INTEGER,
    big_int_col BIGINT,
    decimal_col DECIMAL(10,2),
    numeric_col NUMERIC(12,3),
    real_col REAL,
    double_col DOUBLE PRECISION
);

INSERT INTO numeric_examples (small_int_col, int_col, big_int_col, decimal_col, numeric_col, real_col, double_col) VALUES
(32767, 2147483647, 9223372036854775807, 99999999.99, 999999999.999, 3.14159, 3.141592653589793);

SELECT * FROM numeric_examples;

-- 2. String Types Examples
CREATE TABLE string_examples (
    id SERIAL PRIMARY KEY,
    char_col CHAR(10),
    varchar_col VARCHAR(50),
    text_col TEXT
);

INSERT INTO string_examples (char_col, varchar_col, text_col) VALUES
('Fixed', 'Variable length string', 'This is a very long text that can contain multiple lines and lots of characters without any specific limit.');

SELECT * FROM string_examples;

-- 3. Date/Time Types Examples
CREATE TABLE datetime_examples (
    id SERIAL PRIMARY KEY,
    date_col DATE,
    time_col TIME,
    timestamp_col TIMESTAMP,
    timestamptz_col TIMESTAMPTZ,
    interval_col INTERVAL
);

INSERT INTO datetime_examples (date_col, time_col, timestamp_col, timestamptz_col, interval_col) VALUES
(CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP, NOW(), '1 year 2 months 3 days');

SELECT * FROM datetime_examples;

-- 4. JSON Types Examples
CREATE TABLE json_examples (
    id SERIAL PRIMARY KEY,
    json_col JSON,
    jsonb_col JSONB
);

INSERT INTO json_examples (json_col, jsonb_col) VALUES
('{"name": "John", "age": 30, "city": "New York"}', 
'{"name": "John", "age": 30, "city": "New York"}');

-- JSONB allows for more efficient querying
INSERT INTO json_examples (json_col, jsonb_col) VALUES
('{"name": "Jane", "age": 25, "hobbies": ["reading", "swimming"]}', 
'{"name": "Jane", "age": 25, "hobbies": ["reading", "swimming"]}');

-- Querying JSON data
SELECT id, jsonb_col->>'name' AS name, jsonb_col->>'age' AS age FROM json_examples;
SELECT id, jsonb_col->'hobbies' AS hobbies FROM json_examples WHERE jsonb_col ? 'hobbies';

-- 5. Array Types Examples
CREATE TABLE array_examples (
    id SERIAL PRIMARY KEY,
    int_array INTEGER[],
    text_array TEXT[]
);

INSERT INTO array_examples (int_array, text_array) VALUES
(ARRAY[1, 2, 3, 4, 5], ARRAY['apple', 'banana', 'cherry']);
INSERT INTO array_examples (int_array, text_array) VALUES
('{10, 20, 30}', '{"dog", "cat", "bird"}');

SELECT * FROM array_examples;
SELECT id, int_array[2] AS second_element FROM array_examples;

-- 6. Boolean Type Examples
CREATE TABLE boolean_examples (
    id SERIAL PRIMARY KEY,
    is_active BOOLEAN,
    is_verified BOOLEAN DEFAULT FALSE
);

INSERT INTO boolean_examples (is_active, is_verified) VALUES
(TRUE, TRUE), (FALSE, TRUE), (TRUE, FALSE);

SELECT * FROM boolean_examples WHERE is_active = TRUE;

-- Clean up (optional)
-- DROP TABLE numeric_examples;
-- DROP TABLE string_examples;
-- DROP TABLE datetime_examples;
-- DROP TABLE json_examples;
-- DROP TABLE array_examples;
-- DROP TABLE boolean_examples;