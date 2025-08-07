-- Data Quality Demo Checks
-- Example SQL queries for data quality checks

-- 1. Completeness Check - Null values
SELECT 
    'users' as table_name,
    'null_check' as check_type,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN user_id IS NULL THEN 1 END) as null_count,
    CASE WHEN COUNT(CASE WHEN user_id IS NULL THEN 1 END) > 0 THEN 'FAIL' ELSE 'PASS' END as check_result
FROM default.users
WHERE created_date >= today() - 30;

-- 2. Accuracy Check - Range validation
SELECT 
    'users' as table_name,
    'range_check' as check_type,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN age < 0 OR age > 120 THEN 1 END) as out_of_range_count,
    CASE WHEN COUNT(CASE WHEN age < 0 OR age > 120 THEN 1 END) > 0 THEN 'FAIL' ELSE 'PASS' END as check_result
FROM default.users
WHERE created_date >= today() - 30 AND age IS NOT NULL;

-- 3. Consistency Check - Referential integrity
SELECT 
    'orders' as table_name,
    'referential_integrity' as check_type,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN customer_id IS NOT NULL AND customer_id NOT IN (
        SELECT customer_id FROM default.customers
    ) THEN 1 END) as invalid_reference_count,
    CASE WHEN COUNT(CASE WHEN customer_id IS NOT NULL AND customer_id NOT IN (
        SELECT customer_id FROM default.customers
    ) THEN 1 END) > 0 THEN 'FAIL' ELSE 'PASS' END as check_result
FROM default.orders
WHERE created_date >= today() - 30;

-- 4. Case Sensitivity Check
SELECT 
    'users' as table_name,
    'case_sensitivity' as check_type,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN email != LOWER(email) THEN 1 END) as not_lowercase_count,
    COUNT(CASE WHEN email REGEXP '[A-Z].*[a-z]|[a-z].*[A-Z]' THEN 1 END) as mixed_case_count,
    CASE WHEN COUNT(CASE WHEN email != LOWER(email) THEN 1 END) > 0 THEN 'FAIL' ELSE 'PASS' END as check_result
FROM default.users
WHERE created_date >= today() - 30;

-- 5. Data Range Check - Enhanced
SELECT 
    'products' as table_name,
    'data_range' as check_type,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN price < 0 THEN 1 END) as negative_price_count,
    COUNT(CASE WHEN price > 10000 THEN 1 END) as excessive_price_count,
    COUNT(CASE WHEN stock_quantity < 0 THEN 1 END) as negative_stock_count,
    CASE WHEN COUNT(CASE WHEN price < 0 OR price > 10000 OR stock_quantity < 0 THEN 1 END) > 0 THEN 'FAIL' ELSE 'PASS' END as check_result
FROM default.products
WHERE updated_date >= today() - 30;

-- 6. Timeliness Check - Data freshness
SELECT 
    'users' as table_name,
    'data_freshness' as check_type,
    COUNT(*) as total_rows,
    MAX(created_date) as latest_record_date,
    DATEDIFF('day', MAX(created_date), today()) as days_since_last_update,
    CASE WHEN DATEDIFF('day', MAX(created_date), today()) > 7 THEN 'FAIL' ELSE 'PASS' END as check_result
FROM default.users; 