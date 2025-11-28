-- PostgreSQL教程第8章：高级函数和存储过程

-- 创建测试表
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales_data (
    sale_id SERIAL PRIMARY KEY,
    product_id INTEGER,
    sale_date DATE,
    quantity_sold INTEGER,
    revenue DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 清空表并插入测试数据
TRUNCATE order_items CASCADE;
TRUNCATE orders CASCADE;
TRUNCATE sales_data CASCADE;
TRUNCATE products CASCADE;

INSERT INTO products (product_name, category, price, stock_quantity) VALUES
('Laptop Pro', 'Electronics', 2999.99, 50),
('Gaming Mouse', 'Electronics', 199.99, 200),
('Office Chair', 'Furniture', 899.99, 75),
('Desk Lamp', 'Furniture', 79.99, 150),
('Coffee Maker', 'Appliances', 299.99, 100),
('Blender', 'Appliances', 149.99, 80),
('Wireless Headphones', 'Electronics', 399.99, 120),
('Smartphone', 'Electronics', 1299.99, 60);

INSERT INTO orders (customer_id, status, total_amount) VALUES
(1, 'completed', 3199.98),
(2, 'processing', 999.98),
(1, 'pending', 599.97),
(3, 'completed', 1799.97),
(2, 'cancelled', 1499.99);

INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES
(1, 1, 1, 2999.99, 0.00),
(1, 2, 1, 199.99, 0.00),
(2, 3, 1, 899.99, 0.00),
(2, 4, 2, 79.99, 0.05),
(3, 5, 2, 299.99, 0.00),
(4, 6, 1, 149.99, 0.10),
(4, 7, 1, 399.99, 0.00),
(4, 8, 1, 1299.99, 0.00);

INSERT INTO sales_data (product_id, sale_date, quantity_sold, revenue) VALUES
(1, '2024-01-01', 5, 14999.95),
(2, '2024-01-01', 15, 2998.50),
(1, '2024-01-02', 3, 8999.97),
(5, '2024-01-02', 8, 2399.92),
(8, '2024-01-03', 2, 2599.98);

-- 1. 高级函数特性

-- 1.1 变长参数函数
CREATE OR REPLACE FUNCTION calculate_average_multiple(values NUMERIC[])
RETURNS NUMERIC AS $$
DECLARE
    total NUMERIC := 0;
    count INTEGER := 0;
    value NUMERIC;
BEGIN
    FOREACH value IN ARRAY values LOOP
        total := total + value;
        count := count + 1;
    END LOOP;
    
    IF count = 0 THEN
        RETURN NULL;
    END IF;
    
    RETURN total / count;
END;
$$ LANGUAGE plpgsql;

-- 1.2 可变参数函数 (VARARGS)
CREATE OR REPLACE FUNCTION format_message(prefix TEXT, message TEXT, VARIADIC additional_info TEXT[])
RETURNS TEXT AS $$
BEGIN
    IF array_length(additional_info, 1) IS NULL THEN
        RETURN prefix || ': ' || message;
    ELSE
        RETURN prefix || ': ' || message || ' [' || array_to_string(additional_info, ', ') || ']';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 1.3 多态函数
CREATE OR REPLACE FUNCTION get_max_value(value1 ANYELEMENT, value2 ANYELEMENT)
RETURNS ANYELEMENT AS $$
BEGIN
    IF value1 > value2 THEN
        RETURN value1;
    ELSE
        RETURN value2;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 测试多态函数
SELECT 
    get_max_value(10, 20) as max_int,
    get_max_value('apple', 'banana') as max_string,
    get_max_value(3.14, 2.71) as max_float;

-- 1.4 数组处理函数
CREATE OR REPLACE FUNCTION merge_arrays(arr1 ANYARRAY, arr2 ANYARRAY)
RETURNS ANYARRAY AS $$
BEGIN
    RETURN array_cat(arr1, arr2);
END;
$$ LANGUAGE plpgsql;

-- 2. 复杂的业务逻辑函数

-- 2.1 订单处理函数
CREATE OR REPLACE FUNCTION process_order(
    p_customer_id INTEGER,
    p_product_items JSONB
)
RETURNS TABLE (
    order_id INTEGER,
    status VARCHAR(50),
    total_amount DECIMAL(10,2),
    processing_message TEXT
) AS $$
DECLARE
    new_order_id INTEGER;
    total DECIMAL(10,2) := 0;
    item JSONB;
    product_price DECIMAL(10,2);
    stock_available INTEGER;
    item_total DECIMAL(10,2);
BEGIN
    -- 开始事务
    BEGIN
        -- 创建订单
        INSERT INTO orders (customer_id, status, total_amount)
        VALUES (p_customer_id, 'processing', 0)
        RETURNING order_id INTO new_order_id;
        
        -- 处理订单项
        FOR item IN SELECT * FROM jsonb_array_elements(p_product_items)
        LOOP
            -- 检查产品存在性和库存
            SELECT price, stock_quantity 
            INTO product_price, stock_available
            FROM products 
            WHERE product_id = (item->>'product_id')::INTEGER;
            
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Product with ID % not found', item->>'product_id';
            END IF;
            
            -- 检查库存
            IF stock_available < (item->>'quantity')::INTEGER THEN
                RAISE EXCEPTION 'Insufficient stock for product %. Available: %, Requested: %', 
                    item->>'product_id', stock_available, item->>'quantity';
            END IF;
            
            -- 计算小计
            item_total := product_price * (item->>'quantity')::INTEGER;
            total := total + item_total;
            
            -- 添加订单项
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (
                new_order_id, 
                (item->>'product_id')::INTEGER,
                (item->>'quantity')::INTEGER,
                product_price
            );
            
            -- 更新库存
            UPDATE products 
            SET stock_quantity = stock_quantity - (item->>'quantity')::INTEGER,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = (item->>'product_id')::INTEGER;
        END LOOP;
        
        -- 更新订单总金额
        UPDATE orders 
        SET total_amount = total,
            updated_at = CURRENT_TIMESTAMP
        WHERE order_id = new_order_id;
        
        -- 返回结果
        RETURN QUERY SELECT 
            new_order_id,
            'completed'::VARCHAR(50),
            total,
            format_message('SUCCESS', 'Order processed successfully', 
                          'Order ID: ' || new_order_id::TEXT, 'Total: ' || total::TEXT);
        
    EXCEPTION WHEN OTHERS THEN
        -- 回滚并返回错误信息
        RAISE NOTICE 'Order processing failed: %', SQLERRM;
        RETURN QUERY SELECT 
            0::INTEGER,
            'failed'::VARCHAR(50),
            0::DECIMAL(10,2),
            'ERROR: ' || SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql;

-- 测试订单处理函数
SELECT * FROM process_order(1, '[{"product_id": 1, "quantity": 1}, {"product_id": 2, "quantity": 2}]'::JSONB);

-- 2.2 库存管理函数
CREATE OR REPLACE FUNCTION update_stock(
    p_product_id INTEGER,
    p_quantity_change INTEGER,
    p_reason VARCHAR(100) DEFAULT 'Manual adjustment'
)
RETURNS TABLE (
    product_id INTEGER,
    old_stock INTEGER,
    new_stock INTEGER,
    change_amount INTEGER,
    status VARCHAR(50)
) AS $$
DECLARE
    current_stock INTEGER;
    new_stock INTEGER;
BEGIN
    -- 获取当前库存
    SELECT stock_quantity INTO current_stock
    FROM products
    WHERE product_id = p_product_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product with ID % not found', p_product_id;
    END IF;
    
    -- 计算新库存
    new_stock := current_stock + p_quantity_change;
    
    -- 检查库存不能为负数
    IF new_stock < 0 THEN
        RAISE EXCEPTION 'Insufficient stock. Current: %, Requested reduction: %', 
            current_stock, ABS(p_quantity_change);
    END IF;
    
    -- 更新库存
    UPDATE products
    SET stock_quantity = new_stock,
        updated_at = CURRENT_TIMESTAMP
    WHERE product_id = p_product_id;
    
    -- 返回结果
    RETURN QUERY SELECT 
        p_product_id,
        current_stock,
        new_stock,
        p_quantity_change,
        'updated'::VARCHAR(50);
END;
$$ LANGUAGE plpgsql;

-- 2.3 销售分析函数
CREATE OR REPLACE FUNCTION get_product_performance(
    p_start_date DATE,
    p_end_date DATE,
    p_min_revenue DECIMAL DEFAULT 0
)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR,
    category VARCHAR,
    total_quantity_sold BIGINT,
    total_revenue DECIMAL,
    avg_daily_sales DECIMAL,
    performance_rank INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH sales_summary AS (
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            COALESCE(SUM(sd.quantity_sold), 0) as total_qty,
            COALESCE(SUM(sd.revenue), 0) as total_rev
        FROM products p
        LEFT JOIN sales_data sd ON p.product_id = sd.product_id
            AND sd.sale_date BETWEEN p_start_date AND p_end_date
        GROUP BY p.product_id, p.product_name, p.category
    )
    SELECT 
        ss.product_id,
        ss.product_name,
        ss.category,
        ss.total_qty,
        ss.total_rev,
        ROUND(ss.total_rev / GREATEST((p_end_date - p_start_date + 1), 1), 2) as avg_daily_sales,
        RANK() OVER (ORDER BY ss.total_rev DESC) as performance_rank
    FROM sales_summary ss
    WHERE ss.total_rev >= p_min_revenue
    ORDER BY ss.total_rev DESC;
END;
$$ LANGUAGE plpgsql;

-- 3. 数据验证和清理函数

-- 3.1 邮箱验证函数
CREATE OR REPLACE FUNCTION is_valid_email(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- 简单的邮箱格式验证
    IF email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        RETURN FALSE;
    END IF;
    
    -- 检查长度
    IF LENGTH(email) > 254 THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 3.2 数据清理函数
CREATE OR REPLACE FUNCTION clean_product_name(product_name TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 移除前后空格
    product_name := TRIM(product_name);
    
    -- 将多个空格替换为单个空格
    product_name := regexp_replace(product_name, '\s+', ' ', 'g');
    
    -- 首字母大写
    product_name := INITCAP(product_name);
    
    RETURN product_name;
END;
$$ LANGUAGE plpgsql;

-- 3.3 批量数据验证函数
CREATE OR REPLACE FUNCTION validate_product_data(
    p_product_name TEXT,
    p_price DECIMAL,
    p_stock_quantity INTEGER
)
RETURNS TABLE (
    field_name VARCHAR,
    is_valid BOOLEAN,
    error_message TEXT
) AS $$
BEGIN
    -- 验证产品名称
    IF p_product_name IS NULL OR TRIM(p_product_name) = '' THEN
        RETURN QUERY SELECT 
            'product_name'::VARCHAR,
            FALSE::BOOLEAN,
            'Product name cannot be empty'::TEXT;
    ELSEIF LENGTH(TRIM(p_product_name)) < 3 THEN
        RETURN QUERY SELECT 
            'product_name'::VARCHAR,
            FALSE::BOOLEAN,
            'Product name must be at least 3 characters'::TEXT;
    ELSE
        RETURN QUERY SELECT 
            'product_name'::VARCHAR,
            TRUE::BOOLEAN,
            NULL::TEXT;
    END IF;
    
    -- 验证价格
    IF p_price IS NULL THEN
        RETURN QUERY SELECT 
            'price'::VARCHAR,
            FALSE::BOOLEAN,
            'Price cannot be NULL'::TEXT;
    ELSEIF p_price <= 0 THEN
        RETURN QUERY SELECT 
            'price'::VARCHAR,
            FALSE::BOOLEAN,
            'Price must be greater than 0'::TEXT;
    ELSEIF p_price > 999999.99 THEN
        RETURN QUERY SELECT 
            'price'::VARCHAR,
            FALSE::BOOLEAN,
            'Price cannot exceed 999999.99'::TEXT;
    ELSE
        RETURN QUERY SELECT 
            'price'::VARCHAR,
            TRUE::BOOLEAN,
            NULL::TEXT;
    END IF;
    
    -- 验证库存数量
    IF p_stock_quantity IS NULL THEN
        RETURN QUERY SELECT 
            'stock_quantity'::VARCHAR,
            FALSE::BOOLEAN,
            'Stock quantity cannot be NULL'::TEXT;
    ELSEIF p_stock_quantity < 0 THEN
        RETURN QUERY SELECT 
            'stock_quantity'::VARCHAR,
            FALSE::BOOLEAN,
            'Stock quantity cannot be negative'::TEXT;
    ELSEIF p_stock_quantity > 999999 THEN
        RETURN QUERY SELECT 
            'stock_quantity'::VARCHAR,
            FALSE::BOOLEAN,
            'Stock quantity cannot exceed 999999'::TEXT;
    ELSE
        RETURN QUERY SELECT 
            'stock_quantity'::VARCHAR,
            TRUE::BOOLEAN,
            NULL::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 4. 报表和聚合函数

-- 4.1 自定义聚合函数
CREATE OR REPLACE FUNCTION weighted_average(final_value NUMERIC, weight NUMERIC, variance NUMERIC)
RETURNS NUMERIC AS $$
DECLARE
    total_weight NUMERIC := 0;
    weighted_sum NUMERIC := 0;
BEGIN
    -- 这是一个聚合函数的内部函数，需要与聚合函数定义一起使用
    weighted_sum := weighted_sum + (final_value * weight);
    total_weight := total_weight + weight;
    
    IF total_weight = 0 THEN
        RETURN NULL;
    END IF;
    
    RETURN weighted_sum / total_weight;
END;
$$ LANGUAGE plpgsql;

-- 创建聚合函数
CREATE AGGREGATE weighted_avg(NUMERIC, NUMERIC) (
    SFUNC = weighted_average,
    STYPE = NUMERIC,
    INITCOND = 0
);

-- 4.2 字符串聚合函数
CREATE OR REPLACE FUNCTION list_product_names(category_filter VARCHAR DEFAULT NULL)
RETURNS TEXT AS $$
DECLARE
    result TEXT := '';
    product_name TEXT;
BEGIN
    FOR product_name IN 
        SELECT product_name 
        FROM products 
        WHERE (category_filter IS NULL OR category = category_filter)
        ORDER BY product_name
    LOOP
        IF result = '' THEN
            result := product_name;
        ELSE
            result := result || ', ' || product_name;
        END IF;
    END LOOP;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 5. 窗口函数和OLAP

-- 5.1 使用窗口函数的函数
CREATE OR REPLACE FUNCTION get_product_rankings(p_category VARCHAR DEFAULT NULL)
RETURNS TABLE (
    product_id INTEGER,
    product_name VARCHAR,
    price DECIMAL,
    category VARCHAR,
    price_rank INTEGER,
    price_percentile DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.product_id,
        p.product_name,
        p.price,
        p.category,
        RANK() OVER (ORDER BY p.price DESC) as price_rank,
        PERCENT_RANK() OVER (ORDER BY p.price) as price_percentile
    FROM products p
    WHERE (p_category IS NULL OR p.category = p_category)
    ORDER BY p.price DESC;
END;
$$ LANGUAGE plpgsql;

-- 5.2 移动平均函数
CREATE OR REPLACE FUNCTION calculate_moving_average(
    p_product_id INTEGER,
    p_days_window INTEGER DEFAULT 7
)
RETURNS TABLE (
    sale_date DATE,
    daily_revenue DECIMAL,
    moving_average DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH daily_sales AS (
        SELECT 
            sale_date,
            COALESCE(SUM(revenue), 0) as daily_rev
        FROM sales_data
        WHERE product_id = p_product_id
        GROUP BY sale_date
    )
    SELECT 
        ds.sale_date,
        ds.daily_rev,
        AVG(ds.daily_rev) OVER (
            ORDER BY ds.sale_date 
            ROWS BETWEEN (p_days_window - 1) PRECEDING AND CURRENT ROW
        ) as moving_average
    FROM daily_sales ds
    ORDER BY ds.sale_date;
END;
$$ LANGUAGE plpgsql;

-- 6. 复杂的业务场景函数

-- 6.1 价格计算函数（考虑折扣、税费等）
CREATE OR REPLACE FUNCTION calculate_final_price(
    p_product_id INTEGER,
    p_quantity INTEGER,
    p_discount_percent DECIMAL DEFAULT 0,
    p_tax_rate DECIMAL DEFAULT 0.13,
    p_apply_loyalty_discount BOOLEAN DEFAULT FALSE,
    p_customer_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    product_id INTEGER,
    quantity INTEGER,
    base_price DECIMAL,
    subtotal DECIMAL,
    discount_amount DECIMAL,
    tax_amount DECIMAL,
    loyalty_discount DECIMAL,
    final_price DECIMAL
) AS $$
DECLARE
    base_price DECIMAL;
    subtotal DECIMAL;
    discount_amount DECIMAL;
    tax_amount DECIMAL;
    loyalty_discount DECIMAL := 0;
    loyalty_points INTEGER := 0;
BEGIN
    -- 获取基础价格
    SELECT price INTO base_price
    FROM products
    WHERE product_id = p_product_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Product with ID % not found', p_product_id;
    END IF;
    
    -- 计算小计
    subtotal := base_price * p_quantity;
    
    -- 计算折扣
    discount_amount := subtotal * (p_discount_percent / 100);
    
    -- 计算loyalty折扣
    IF p_apply_loyalty_discount AND p_customer_id IS NOT NULL THEN
        SELECT loyalty_points INTO loyalty_points
        FROM customer_loyalty  -- 假设存在这样的表
        WHERE customer_id = p_customer_id;
        
        IF FOUND THEN
            loyalty_discount := subtotal * LEAST(loyalty_points / 1000.0, 0.05); -- 最多5%折扣
        END IF;
    END IF;
    
    -- 计算税费
    tax_amount := (subtotal - discount_amount - loyalty_discount) * p_tax_rate;
    
    -- 计算最终价格
    RETURN QUERY SELECT 
        p_product_id,
        p_quantity,
        base_price,
        subtotal,
        discount_amount,
        tax_amount,
        loyalty_discount,
        subtotal - discount_amount - loyalty_discount + tax_amount;
END;
$$ LANGUAGE plpgsql;

-- 7. 错误处理和调试

-- 7.1 详细的错误处理函数
CREATE OR REPLACE FUNCTION safe_divide(numerator NUMERIC, denominator NUMERIC)
RETURNS TABLE (
    result NUMERIC,
    status VARCHAR(50),
    error_details TEXT,
    input_info TEXT
) AS $$
BEGIN
    -- 输入验证
    IF numerator IS NULL OR denominator IS NULL THEN
        RETURN QUERY SELECT 
            NULL::NUMERIC,
            'invalid_input'::VARCHAR(50),
            'Numerator or denominator cannot be NULL'::TEXT,
            'Numerator: ' || COALESCE(numerator::TEXT, 'NULL') || 
            ', Denominator: ' || COALESCE(denominator::TEXT, 'NULL');
        RETURN;
    END IF;
    
    -- 除零检查
    IF denominator = 0 THEN
        RETURN QUERY SELECT 
            NULL::NUMERIC,
            'division_by_zero'::VARCHAR(50),
            'Division by zero is not allowed'::TEXT,
            'Numerator: ' || numerator::TEXT || 
            ', Denominator: ' || denominator::TEXT;
        RETURN;
    END IF;
    
    -- 范围检查
    IF ABS(numerator) > 1e15 OR ABS(denominator) > 1e15 THEN
        RETURN QUERY SELECT 
            NULL::NUMERIC,
            'overflow_risk'::VARCHAR(50),
            'Input values are too large, potential overflow'::TEXT,
            'Numerator: ' || numerator::TEXT || 
            ', Denominator: ' || denominator::TEXT;
        RETURN;
    END IF;
    
    -- 执行计算
    RETURN QUERY SELECT 
        numerator / denominator,
        'success'::VARCHAR(50),
        'Calculation completed successfully'::TEXT,
        'Result: ' || (numerator / denominator)::TEXT;
END;
$$ LANGUAGE plpgsql;

-- 7.2 日志记录函数
CREATE OR REPLACE FUNCTION log_function_call(
    function_name TEXT,
    input_params TEXT,
    execution_time_ms INTEGER,
    result_status VARCHAR(50)
)
RETURNS VOID AS $$
BEGIN
    -- 这里可以将日志写入到专门的日志表
    RAISE NOTICE '[%] Function: %, Params: %, Time: %ms, Status: %', 
        CURRENT_TIMESTAMP, function_name, input_params, execution_time_ms, result_status;
END;
$$ LANGUAGE plpgsql;

-- 8. 测试所有高级函数
SELECT '=== 测试高级函数 ===' as test_section;

-- 测试变长参数函数
SELECT calculate_average_multiple(ARRAY[10, 20, 30, 40, 50]) as avg_array;
SELECT format_message('INFO', 'System started', 'Version 1.0', 'Environment: Production') as formatted_message;

-- 测试业务逻辑函数
SELECT * FROM update_stock(1, 5, 'Stock replenishment');
SELECT * FROM get_product_performance('2024-01-01', '2024-01-31', 1000);

-- 测试验证函数
SELECT * FROM validate_product_data('Valid Product', 99.99, 100);
SELECT is_valid_email('user@example.com') as is_valid_email_test;

-- 测试排名函数
SELECT * FROM get_product_rankings('Electronics');

-- 测试价格计算函数
SELECT * FROM calculate_final_price(1, 2, 10.0, 0.13, true, 1);

-- 测试安全除法函数
SELECT * FROM safe_divide(10, 3);
SELECT * FROM safe_divide(10, 0);

SELECT '=== 高级函数测试完成 ===' as test_section;