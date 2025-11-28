-- 第6章：索引和性能优化 - 高级索引策略演示

-- 1. 自定义索引类型

-- 1.1 GiST索引 - 几何数据类型
-- 创建包含几何数据的表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    coordinates POINT,  -- PostGIS点类型
    description TEXT
);

-- 插入测试数据
INSERT INTO locations (name, coordinates, description) VALUES
('City Center', POINT(0, 0), 'Main city center'),
('Airport', POINT(5, 3), 'International airport'),
('University', POINT(-2, 4), 'State university'),
('Shopping Mall', POINT(3, -1), 'Largest mall in the city');

-- 创建GiST索引用于空间查询
CREATE INDEX idx_locations_gist ON locations USING GIST (coordinates);

-- 测试空间查询
EXPLAIN ANALYZE
SELECT name, coordinates 
FROM locations 
WHERE coordinates <@ circle(POINT(0, 0), 2.5);  -- 距离(0,0)点2.5单位半径内的点

-- 1.2 GIN索引 - 全文搜索和数组类型
-- 创建包含文本搜索数据的表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入测试数据
INSERT INTO documents (title, content, tags) VALUES
('PostgreSQL Tutorial', 'PostgreSQL is a powerful, open source object-relational database system.', ARRAY['database', 'postgresql', 'tutorial']),
('Python Data Analysis', 'Python provides excellent libraries for data analysis and visualization.', ARRAY['python', 'data', 'analysis']),
('Database Design Principles', 'Good database design involves normalization and careful planning.', ARRAY['database', 'design', 'theory']),
('Web Development with Django', 'Django is a high-level Python web framework.', ARRAY['python', 'web', 'django']);

-- 创建GIN索引用于全文搜索
CREATE INDEX idx_documents_gin ON documents USING GIN (to_tsvector('english', title || ' ' || content));

-- 创建GIN索引用于标签数组
CREATE INDEX idx_documents_tags_gin ON documents USING GIN (tags);

-- 测试全文搜索
EXPLAIN ANALYZE
SELECT title, ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', 'database')) as rank
FROM documents
WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'database')
ORDER BY rank DESC;

-- 测试标签数组查询
EXPLAIN ANALYZE
SELECT title, tags
FROM documents
WHERE tags @> ARRAY['python'];

-- 2. 条件索引和部分索引

-- 2.1 基于条件的索引
-- 只为活跃记录创建索引
CREATE INDEX idx_documents_active ON documents (created_at) WHERE created_at >= CURRENT_DATE - INTERVAL '1 year';

-- 2.2 函数索引
-- 对计算结果建立索引
CREATE INDEX idx_documents_title_length ON documents (LENGTH(title));
CREATE INDEX idx_documents_word_count ON documents ((array_length(tags, 1)));

-- 3. 唯一性索引和约束

-- 3.1 复合唯一索引
-- 确保同一部门内员工姓名的唯一性
ALTER TABLE employees ADD CONSTRAINT uk_employee_dept_name UNIQUE (department_id, name);

-- 3.2 条件唯一约束
-- 每个部门的经理
CREATE TABLE managers (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    department_id INTEGER REFERENCES departments(id),
    title VARCHAR(50) DEFAULT 'Manager',
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    is_active BOOLEAN GENERATED ALWAYS AS (end_date IS NULL) STORED
);

-- 创建部分唯一索引
CREATE UNIQUE INDEX idx_managers_active_dept ON managers (department_id) 
WHERE is_active = true;

-- 4. 索引性能测试和比较

-- 4.1 创建测试表和数据
CREATE TABLE performance_test (
    id SERIAL PRIMARY KEY,
    random_data VARCHAR(100),
    integer_data INTEGER,
    timestamp_data TIMESTAMP,
    text_data TEXT
);

-- 插入大量测试数据
INSERT INTO performance_test (random_data, integer_data, timestamp_data, text_data)
SELECT 
    'Data_' || i,
    (RANDOM() * 1000000)::INTEGER,
    CURRENT_TIMESTAMP + (RANDOM() * 365 || ' days')::INTERVAL,
    'This is text data for record ' || i || ' with some random content to test full text search capabilities.'
FROM generate_series(1, 50000);

-- 4.2 测试不同索引类型的效果

-- 无索引查询
EXPLAIN ANALYZE
SELECT COUNT(*) FROM performance_test 
WHERE integer_data > 500000;

-- 创建B-Tree索引
CREATE INDEX idx_perf_int_btree ON performance_test (integer_data);
EXPLAIN ANALYZE
SELECT COUNT(*) FROM performance_test 
WHERE integer_data > 500000;

-- 创建Hash索引
CREATE INDEX idx_perf_int_hash ON performance_test USING HASH (integer_data);
EXPLAIN ANALYZE
SELECT COUNT(*) FROM performance_test 
WHERE integer_data = 500000;

-- 5. 索引维护和监控

-- 5.1 查看索引使用统计
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'performance_test'
ORDER BY idx_scan DESC;

-- 5.2 检查索引膨胀
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as current_size,
    pg_size_pretty(pg_relation_size(indexrelid) + pg_relation_size('pg_class')::BIGINT) as estimated_total
FROM pg_stat_user_indexes
WHERE tablename = 'performance_test';

-- 6. 分区表索引策略

-- 6.1 创建分区表
CREATE TABLE partitioned_sales (
    id SERIAL PRIMARY KEY,
    sale_date DATE,
    region VARCHAR(50),
    amount DECIMAL(10,2),
    salesperson VARCHAR(100)
) PARTITION BY RANGE (sale_date);

-- 创建月度分区
CREATE TABLE sales_2023_01 PARTITION OF partitioned_sales
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');
CREATE TABLE sales_2023_02 PARTITION OF partitioned_sales
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

-- 6.2 在分区上创建索引
CREATE INDEX idx_sales_2023_01 ON sales_2023_01 (region, amount);
CREATE INDEX idx_sales_2023_02 ON sales_2023_02 (region, amount);

-- 7. 全文搜索索引

-- 7.1 创建搜索配置
ALTER TEXT SEARCH CONFIGURATION english_search 
    ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word
    WITH pg_catalog.simple;

-- 7.2 高级全文搜索查询
-- 使用全文搜索和排名
EXPLAIN ANALYZE
SELECT 
    title,
    ts_rank(to_tsvector('english', content), 
            plainto_tsquery('english', 'database tutorial')) as rank,
    ts_headline('english', content, 
                plainto_tsquery('english', 'database tutorial'),
                'MaxWords=50, MinWords=10') as excerpt
FROM documents
WHERE to_tsvector('english', title || ' ' || content) 
      @@ plainto_tsquery('english', 'database tutorial')
ORDER BY rank DESC;

-- 8. 表达式索引的高级应用

-- 8.1 对JSON数据建立索引
-- 创建包含JSON数据的表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    specifications JSONB,
    price DECIMAL(10,2),
    category VARCHAR(50)
);

-- 插入JSON数据
INSERT INTO products (name, specifications, price, category) VALUES
('Laptop', '{"processor": "Intel i7", "memory": "16GB", "storage": "512GB SSD"}', 1299.99, 'Electronics'),
('Phone', '{"processor": "Snapdragon 888", "memory": "8GB", "storage": "128GB"}', 899.99, 'Electronics'),
('Desk', '{"material": "Oak", "dimensions": "120x60x75", "color": "Brown"}', 299.99, 'Furniture'),
('Chair', '{"material": "Leather", "type": "Office", "color": "Black"}', 199.99, 'Furniture');

-- 对JSON路径建立索引
CREATE INDEX idx_products_processor ON products ((specifications->>'processor'));
CREATE INDEX idx_products_memory ON products ((specifications->>'memory'));

-- 8.2 条件表达式索引
CREATE INDEX idx_products_electronics_price ON products (price) WHERE category = 'Electronics';

-- 测试JSON索引
EXPLAIN ANALYZE
SELECT name, specifications->>'processor' as processor, price
FROM products
WHERE specifications->>'processor' = 'Intel i7'
  AND price < 1500;

-- 9. 索引重构和优化

-- 9.1 删除无效索引
-- 查找从未被使用的索引
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0 
  AND schemaname = 'public';

-- 9.2 重建索引
-- 重建单个索引
REINDEX INDEX idx_perf_int_btree;

-- 重建表的所有索引
REINDEX TABLE performance_test;

-- 10. 自定义索引方法

-- 10.1 创建包含索引建议的视图
CREATE OR REPLACE VIEW index_recommendations AS
SELECT 
    schemaname,
    tablename,
    'Consider creating index on ' || attname as recommendation,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename IN ('employees', 'sales', 'documents')
  AND schemaname = 'public'
  AND n_distinct > 10
  AND attname IN ('salary', 'department_id', 'amount', 'title');

-- 10.2 索引性能监控视图
CREATE OR REPLACE VIEW index_performance AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE 
        WHEN idx_scan = 0 THEN 'Never Used'
        WHEN idx_scan < 100 THEN 'Low Usage'
        WHEN idx_scan < 1000 THEN 'Medium Usage'
        ELSE 'High Usage'
    END as usage_category,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;