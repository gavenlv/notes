#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL索引与性能优化示例代码
本章代码演示了MySQL中各种索引类型的使用方法、索引设计策略、查询优化技巧
以及性能监控和分析方法。
"""

import mysql.connector
import time
import statistics
import concurrent.futures
import json
import random
import logging
from typing import Dict, List, Tuple, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MySQL索引与性能优化")

class IndexManager:
    """MySQL索引管理示例"""
    
    def __init__(self, host='localhost', user='root', password='password', database='mysql_tutorial'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logger.info("成功连接到MySQL数据库")
            return True
        except mysql.connector.Error as err:
            logger.error(f"连接失败: {err}")
            return False
    
    def setup_tables(self):
        """创建示例表和测试数据"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 删除已存在的表
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS categories")
            cursor.execute("DROP TABLE IF EXISTS brands")
            cursor.execute("DROP TABLE IF EXISTS sales")
            
            # 创建分类表
            cursor.execute("""
                CREATE TABLE categories (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建品牌表
            cursor.execute("""
                CREATE TABLE brands (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(50) NOT NULL,
                    country VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建产品表
            cursor.execute("""
                CREATE TABLE products (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    category_id INT NOT NULL,
                    brand_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    stock_quantity INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id),
                    FOREIGN KEY (brand_id) REFERENCES brands(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建销售表
            cursor.execute("""
                CREATE TABLE sales (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    sale_date DATE NOT NULL,
                    customer_id INT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 插入分类数据
            categories_data = [
                ('电子产品', '各类电子设备和配件'),
                ('家用电器', '家庭使用的电器产品'),
                ('服装鞋帽', '各类服装、鞋子和帽子')
            ]
            
            cursor.executemany(
                "INSERT INTO categories (name, description) VALUES (%s, %s)",
                categories_data
            )
            
            # 插入品牌数据
            brands_data = [
                ('华为', '中国'),
                ('苹果', '美国'),
                ('小米', '中国'),
                ('三星', '韩国'),
                ('索尼', '日本')
            ]
            
            cursor.executemany(
                "INSERT INTO brands (name, country) VALUES (%s, %s)",
                brands_data
            )
            
            # 插入产品数据
            products_data = []
            for category_id in range(1, 4):
                for brand_id in range(1, 6):
                    for i in range(10):
                        product_name = f"产品{category_id}{brand_id}{i+1}"
                        price = random.uniform(100, 5000)
                        stock = random.randint(10, 1000)
                        products_data.append((category_id, brand_id, product_name, f"{product_name}的描述", price, stock))
            
            cursor.executemany(
                """INSERT INTO products (category_id, brand_id, name, description, price, stock_quantity) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                products_data
            )
            
            # 插入销售数据
            sales_data = []
            for product_id in range(1, 151):
                for _ in range(random.randint(1, 20)):
                    sale_date = f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
                    quantity = random.randint(1, 10)
                    cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
                    unit_price = cursor.fetchone()[0]
                    total_price = quantity * unit_price
                    customer_id = random.randint(1, 1000)
                    sales_data.append((product_id, quantity, unit_price, total_price, sale_date, customer_id))
            
            cursor.executemany(
                """INSERT INTO sales (product_id, quantity, unit_price, total_price, sale_date, customer_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                sales_data
            )
            
            self.connection.commit()
            cursor.close()
            logger.info("成功创建示例表和插入测试数据")
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"创建表失败: {err}")
            return False
    
    def demonstrate_index_types(self):
        """演示各种索引类型"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 1. 创建单列索引
            cursor.execute("CREATE INDEX idx_product_name ON products(name)")
            logger.info("创建了产品名称的单列索引")
            
            # 2. 创建复合索引
            cursor.execute("CREATE INDEX idx_category_brand ON products(category_id, brand_id)")
            logger.info("创建了分类和品牌的复合索引")
            
            # 3. 创建覆盖索引
            cursor.execute("CREATE INDEX idx_category_price_name ON products(category_id, price, name)")
            logger.info("创建了分类、价格和名称的覆盖索引")
            
            # 4. 创建唯一索引
            cursor.execute("CREATE UNIQUE INDEX idx_product_unique ON products(category_id, brand_id, name)")
            logger.info("创建了产品的唯一索引")
            
            # 5. 创建前缀索引
            cursor.execute("CREATE INDEX idx_product_name_prefix ON products(name(20))")
            logger.info("创建了产品名称的前缀索引")
            
            # 查看表的索引
            cursor.execute("SHOW INDEX FROM products")
            indexes = cursor.fetchall()
            
            logger.info("products表的索引信息:")
            for index in indexes:
                logger.info(f"  索引名: {index[2]}, 列名: {index[4]}, 唯一性: {index[1]}")
            
            self.connection.commit()
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"创建索引失败: {err}")
            return False
    
    def demonstrate_index_usage(self):
        """演示索引的使用情况"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 测试查询1：使用单列索引
            query1 = "SELECT * FROM products WHERE name LIKE '产品12%'"
            explain1 = self.explain_query(query1)
            logger.info(f"查询1的执行计划: {json.dumps(explain1, indent=2, default=str)}")
            
            # 测试查询2：使用复合索引
            query2 = "SELECT * FROM products WHERE category_id = 1 AND brand_id = 2"
            explain2 = self.explain_query(query2)
            logger.info(f"查询2的执行计划: {json.dumps(explain2, indent=2, default=str)}")
            
            # 测试查询3：使用覆盖索引
            query3 = "SELECT category_id, price, name FROM products WHERE category_id = 1 AND price > 1000"
            explain3 = self.explain_query(query3)
            logger.info(f"查询3的执行计划: {json.dumps(explain3, indent=2, default=str)}")
            
            # 测试查询4：索引失效的情况
            query4 = "SELECT * FROM products WHERE UPPER(name) LIKE 'PRODUCT12%'"
            explain4 = self.explain_query(query4)
            logger.info(f"查询4的执行计划(索引失效): {json.dumps(explain4, indent=2, default=str)}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示索引使用失败: {err}")
            return False
    
    def explain_query(self, query):
        """解释查询执行计划"""
        if not self.connection:
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(f"EXPLAIN FORMAT=JSON {query}")
            result = cursor.fetchone()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            logger.error(f"解释查询失败: {err}")
            return None
    
    def demonstrate_query_optimization(self):
        """演示查询优化技巧"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 测试不同查询的性能
            queries = {
                'select_all': "SELECT * FROM products WHERE category_id = 1",
                'select_columns': "SELECT id, name, price FROM products WHERE category_id = 1",
                'with_limit': "SELECT id, name, price FROM products WHERE category_id = 1 LIMIT 10",
                'order_by': "SELECT id, name, price FROM products WHERE category_id = 1 ORDER BY price DESC",
                'join_with_subquery': """
                    SELECT p.name, p.price, c.name AS category_name 
                    FROM products p 
                    WHERE p.category_id IN (SELECT id FROM categories WHERE name LIKE '电子%')
                """,
                'join_with_join': """
                    SELECT p.name, p.price, c.name AS category_name 
                    FROM products p 
                    JOIN categories c ON p.category_id = c.id 
                    WHERE c.name LIKE '电子%'
                """
            }
            
            results = {}
            for name, query in queries.items():
                start_time = time.time()
                cursor.execute(query)
                result = cursor.fetchall()
                end_time = time.time()
                
                results[name] = {
                    'duration': end_time - start_time,
                    'rows': len(result)
                }
                
                logger.info(f"查询 {name}: 耗时 {results[name]['duration']:.6f} 秒, 返回 {results[name]['rows']} 行")
            
            cursor.close()
            return results
            
        except mysql.connector.Error as err:
            logger.error(f"演示查询优化失败: {err}")
            return False
    
    def demonstrate_performance_monitoring(self):
        """演示性能监控"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 1. 查看服务器状态
            cursor.execute("SHOW STATUS LIKE 'Handler_%'")
            handler_status = cursor.fetchall()
            
            logger.info("Handler状态:")
            for status in handler_status[:10]:  # 只显示前10个
                logger.info(f"  {status['Variable_name']}: {status['Value']}")
            
            # 2. 查看InnoDB状态
            cursor.execute("SHOW ENGINE INNODB STATUS")
            innodb_status = cursor.fetchone()
            # InnoDB状态太长，只显示部分内容
            status_text = innodb_status['Status']
            logger.info("InnoDB状态摘要:")
            
            # 提取一些关键信息
            if "Buffer pool size" in status_text:
                buffer_pool_start = status_text.find("Buffer pool size")
                buffer_pool_end = status_text.find("\n", buffer_pool_start)
                logger.info(f"  {status_text[buffer_pool_start:buffer_pool_end]}")
            
            # 3. 查看慢查询配置
            cursor.execute("SHOW VARIABLES LIKE 'slow_query%'")
            slow_query_vars = cursor.fetchall()
            
            logger.info("慢查询配置:")
            for var in slow_query_vars:
                logger.info(f"  {var['Variable_name']}: {var['Value']}")
            
            # 4. 查看查询缓存配置
            cursor.execute("SHOW VARIABLES LIKE 'query_cache%'")
            query_cache_vars = cursor.fetchall()
            
            logger.info("查询缓存配置:")
            for var in query_cache_vars:
                logger.info(f"  {var['Variable_name']}: {var['Value']}")
            
            # 5. 查看锁等待情况
            cursor.execute("SELECT * FROM sys.innodb_lock_waits")
            lock_waits = cursor.fetchall()
            
            if lock_waits:
                logger.info("当前锁等待情况:")
                for wait in lock_waits:
                    logger.info(f"  等待中的事务ID: {wait['waiting_trx_id']}, 阻塞的事务ID: {wait['blocking_trx_id']}")
            else:
                logger.info("当前没有锁等待")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示性能监控失败: {err}")
            return False
    
    def run_performance_test(self, num_threads=10, num_queries=100):
        """运行性能测试"""
        if not self.connection:
            logger.error("未连接到数据库")
            return None
            
        queries = [
            "SELECT * FROM products WHERE category_id = 1",
            "SELECT * FROM products WHERE name LIKE '产品12%'",
            "SELECT p.name, p.price, c.name AS category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE c.id = 1",
            "SELECT category_id, AVG(price) AS avg_price FROM products GROUP BY category_id"
        ]
        
        results = []
        
        def worker(query):
            """工作线程函数"""
            connection = None
            try:
                connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                cursor = connection.cursor()
                durations = []
                
                for _ in range(num_queries):
                    start_time = time.time()
                    cursor.execute(query)
                    cursor.fetchall()
                    end_time = time.time()
                    durations.append(end_time - start_time)
                
                cursor.close()
                return durations
            except mysql.connector.Error as err:
                logger.error(f"性能测试失败: {err}")
                return []
            finally:
                if connection:
                    connection.close()
        
        # 为每个查询运行测试
        for i, query in enumerate(queries):
            logger.info(f"测试查询 {i+1}: {query[:50]}...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker, query) for _ in range(num_threads)]
                all_durations = []
                
                for future in concurrent.futures.as_completed(futures):
                    thread_durations = future.result()
                    all_durations.extend(thread_durations)
            
            # 计算统计信息
            avg_duration = statistics.mean(all_durations)
            min_duration = min(all_durations)
            max_duration = max(all_durations)
            median_duration = statistics.median(all_durations)
            total_duration = sum(all_durations)
            
            result = {
                'query': query,
                'avg_duration': avg_duration,
                'min_duration': min_duration,
                'max_duration': max_duration,
                'median_duration': median_duration,
                'total_duration': total_duration,
                'total_queries': len(all_durations)
            }
            
            results.append(result)
            
            logger.info(f"  平均耗时: {avg_duration:.6f} 秒")
            logger.info(f"  最小耗时: {min_duration:.6f} 秒")
            logger.info(f"  最大耗时: {max_duration:.6f} 秒")
            logger.info(f"  中位数耗时: {median_duration:.6f} 秒")
            logger.info(f"  总耗时: {total_duration:.6f} 秒")
            logger.info(f"  查询总数: {len(all_durations)}")
        
        return results
    
    def demonstrate_partitioning(self):
        """演示分区表"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 创建分区表
            cursor.execute("""
                CREATE TABLE sales_partitioned (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10, 2) NOT NULL,
                    total_price DECIMAL(10, 2) NOT NULL,
                    sale_date DATE NOT NULL,
                    customer_id INT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                PARTITION BY RANGE (YEAR(sale_date)) (
                    PARTITION p2022 VALUES LESS THAN (2023),
                    PARTITION p2023 VALUES LESS THAN (2024),
                    PARTITION p2024 VALUES LESS THAN (2025),
                    PARTITION pmax VALUES LESS THAN MAXVALUE
                )
            """)
            
            # 插入数据到分区表
            sales_data = []
            for product_id in range(1, 11):  # 只插入10个产品的数据
                for year in [2022, 2023, 2024]:
                    for month in range(1, 13):
                        for _ in range(random.randint(1, 5)):
                            day = random.randint(1, 28)
                            sale_date = f"{year}-{month:02d}-{day:02d}"
                            quantity = random.randint(1, 10)
                            cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
                            unit_price = cursor.fetchone()[0]
                            total_price = quantity * unit_price
                            customer_id = random.randint(1, 1000)
                            sales_data.append((product_id, quantity, unit_price, total_price, sale_date, customer_id))
            
            cursor.executemany(
                """INSERT INTO sales_partitioned (product_id, quantity, unit_price, total_price, sale_date, customer_id) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                sales_data
            )
            
            # 测试分区查询
            test_queries = [
                "SELECT COUNT(*) FROM sales_partitioned WHERE YEAR(sale_date) = 2023",
                "SELECT COUNT(*) FROM sales_partitioned WHERE sale_date BETWEEN '2023-01-01' AND '2023-12-31'",
                "SELECT YEAR(sale_date) AS year, SUM(total_price) AS total_sales FROM sales_partitioned GROUP BY YEAR(sale_date)"
            ]
            
            for query in test_queries:
                logger.info(f"执行查询: {query}")
                start_time = time.time()
                cursor.execute(query)
                result = cursor.fetchall()
                end_time = time.time()
                logger.info(f"  结果: {result}, 耗时: {end_time - start_time:.6f} 秒")
            
            # 查看分区信息
            cursor.execute("SELECT PARTITION_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = 'sales_partitioned'")
            partitions = cursor.fetchall()
            
            logger.info("分区信息:")
            for partition in partitions:
                logger.info(f"  分区名: {partition[0]}, 行数: {partition[1]}")
            
            self.connection.commit()
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示分区表失败: {err}")
            return False
    
    def demonstrate_index_maintenance(self):
        """演示索引维护"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor()
            
            # 1. 分析表
            cursor.execute("ANALYZE TABLE products")
            logger.info("已分析products表")
            
            # 2. 检查表
            cursor.execute("CHECK TABLE products")
            result = cursor.fetchone()
            logger.info(f"检查products表结果: {result}")
            
            # 3. 优化表（注意：这会锁表，生产环境慎用）
            cursor.execute("OPTIMIZE TABLE products")
            logger.info("已优化products表")
            
            # 4. 查看索引基数
            cursor.execute("SHOW INDEX FROM products")
            indexes = cursor.fetchall()
            
            logger.info("索引信息:")
            for index in indexes:
                logger.info(f"  索引名: {index[2]}, 列名: {index[4]}, 基数: {index[6]}")
            
            # 5. 查看未使用的索引
            cursor.execute("""
                SELECT OBJECT_SCHEMA, OBJECT_NAME, INDEX_NAME
                FROM performance_schema.table_io_waits_summary_by_index_usage
                WHERE OBJECT_SCHEMA = %s
                AND OBJECT_NAME = 'products'
                AND INDEX_NAME IS NOT NULL
                AND COUNT_FETCH = 0
            """, (self.database,))
            
            unused_indexes = cursor.fetchall()
            
            if unused_indexes:
                logger.info("未使用的索引:")
                for index in unused_indexes:
                    logger.info(f"  数据库: {index[0]}, 表: {index[1]}, 索引: {index[2]}")
            else:
                logger.info("没有发现未使用的索引")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示索引维护失败: {err}")
            return False
    
    def demonstrate_server_config(self):
        """演示服务器配置"""
        if not self.connection:
            logger.error("未连接到数据库")
            return False
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # 1. 查看内存相关配置
            memory_vars = [
                'innodb_buffer_pool_size',
                'innodb_buffer_pool_instances',
                'innodb_log_buffer_size',
                'key_buffer_size',
                'query_cache_size',
                'tmp_table_size',
                'max_heap_table_size'
            ]
            
            logger.info("内存相关配置:")
            for var in memory_vars:
                cursor.execute(f"SHOW VARIABLES LIKE '{var}'")
                result = cursor.fetchone()
                if result:
                    value = int(result['Value'])
                    value_mb = value / (1024 * 1024) if value > 1048576 else value / 1024
                    unit = 'MB' if value > 1048576 else 'KB'
                    logger.info(f"  {var}: {value_mb:.2f} {unit}")
            
            # 2. 查看I/O相关配置
            io_vars = [
                'innodb_flush_log_at_trx_commit',
                'innodb_flush_method',
                'innodb_log_file_size',
                'innodb_log_files_in_group',
                'innodb_io_capacity',
                'innodb_io_capacity_max',
                'innodb_read_io_threads',
                'innodb_write_io_threads'
            ]
            
            logger.info("I/O相关配置:")
            for var in io_vars:
                cursor.execute(f"SHOW VARIABLES LIKE '{var}'")
                result = cursor.fetchone()
                if result:
                    logger.info(f"  {var}: {result['Value']}")
            
            # 3. 查看并发相关配置
            concurrency_vars = [
                'max_connections',
                'thread_cache_size',
                'innodb_thread_concurrency',
                'innodb_read_ahead_threshold',
                'innodb_lock_wait_timeout',
                'wait_timeout'
            ]
            
            logger.info("并发相关配置:")
            for var in concurrency_vars:
                cursor.execute(f"SHOW VARIABLES LIKE '{var}'")
                result = cursor.fetchone()
                if result:
                    logger.info(f"  {var}: {result['Value']}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            logger.error(f"演示服务器配置失败: {err}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("已关闭数据库连接")


class QueryOptimizer:
    """查询优化器示例"""
    
    def __init__(self, index_manager):
        self.index_manager = index_manager
    
    def compare_query_plans(self, queries):
        """比较不同查询的执行计划"""
        if not self.index_manager.connection:
            logger.error("未连接到数据库")
            return None
            
        results = {}
        cursor = self.index_manager.connection.cursor(dictionary=True)
        
        for name, query in queries.items():
            logger.info(f"分析查询: {name}")
            logger.info(f"SQL: {query}")
            
            # 获取执行计划
            cursor.execute(f"EXPLAIN FORMAT=JSON {query}")
            explain_result = cursor.fetchone()
            
            # 获取实际执行时间和行数
            start_time = time.time()
            cursor.execute(query)
            cursor.fetchall()
            end_time = time.time()
            
            actual_time = end_time - start_time
            
            results[name] = {
                'query': query,
                'explain': explain_result,
                'actual_time': actual_time
            }
            
            # 打印关键信息
            try:
                explain_json = json.loads(explain_result['EXPLAIN'])
                query_block = explain_json['query_block']
                table_info = query_block.get('table', {})
                
                if 'access_type' in table_info:
                    access_type = table_info['access_type']
                    logger.info(f"  访问类型: {access_type}")
                
                if 'possible_keys' in table_info:
                    possible_keys = table_info['possible_keys']
                    logger.info(f"  可能的索引: {possible_keys}")
                
                if 'key' in table_info:
                    key = table_info['key']
                    logger.info(f"  使用的索引: {key}")
                
                if 'rows_examined_per_scan' in table_info:
                    rows_examined = table_info['rows_examined_per_scan']
                    logger.info(f"  扫描行数: {rows_examined}")
                
                if 'using_index' in table_info:
                    using_index = table_info['using_index']
                    logger.info(f"  使用覆盖索引: {using_index}")
                
            except json.JSONDecodeError:
                logger.error("无法解析执行计划JSON")
            
            logger.info(f"  实际执行时间: {actual_time:.6f} 秒")
            logger.info("")
        
        cursor.close()
        return results
    
    def suggest_indexes(self, table, where_conditions=None, join_conditions=None, order_by=None, group_by=None):
        """为表建议索引"""
        if not self.index_manager.connection:
            logger.error("未连接到数据库")
            return None
            
        suggestions = []
        
        # 基于WHERE条件的索引建议
        if where_conditions:
            # 单列条件
            for condition in where_conditions:
                if ' = ' in condition:
                    column = condition.split(' = ')[0].strip()
                    suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
                elif ' IN ' in condition:
                    column = condition.split(' IN ')[0].strip()
                    suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
                elif ' LIKE ' in condition and condition.endswith("'%'') == False:
                    column = condition.split(' LIKE ')[0].strip()
                    suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
                elif ' > ' in condition or ' < ' in condition or ' BETWEEN ' in condition:
                    column = condition.split(' ')[0].strip()
                    suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
        
        # 基于连接条件的索引建议
        if join_conditions:
            for condition in join_conditions:
                # 连接条件通常格式为 table1.column = table2.column
                parts = condition.split(' = ')
                if len(parts) == 2:
                    column = parts[0].split('.')[-1].strip()
                    suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
        
        # 基于ORDER BY的索引建议
        if order_by:
            columns = [col.strip() for col in order_by.split(',')]
            if len(columns) == 1:
                column = columns[0]
                if ' DESC' in column:
                    column = column.replace(' DESC', '')
                elif ' ASC' in column:
                    column = column.replace(' ASC', '')
                suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
            else:
                # 多列排序
                columns_clean = [col.replace(' DESC', '').replace(' ASC', '') for col in columns]
                columns_str = ', '.join(columns_clean)
                suggestions.append(f"CREATE INDEX idx_{table}_order ON {table}({columns_str})")
        
        # 基于GROUP BY的索引建议
        if group_by:
            columns = [col.strip() for col in group_by.split(',')]
            if len(columns) == 1:
                column = columns[0]
                suggestions.append(f"CREATE INDEX idx_{table}_{column} ON {table}({column})")
            else:
                columns_str = ', '.join(columns)
                suggestions.append(f"CREATE INDEX idx_{table}_group ON {table}({columns_str})")
        
        # 去重
        unique_suggestions = list(set(suggestions))
        
        logger.info(f"为表 {table} 的索引建议:")
        for i, suggestion in enumerate(unique_suggestions, 1):
            logger.info(f"  {i}. {suggestion}")
        
        return unique_suggestions
    
    def analyze_slow_queries(self, limit=10):
        """分析慢查询"""
        if not self.index_manager.connection:
            logger.error("未连接到数据库")
            return None
            
        # 注意：需要启用慢查询日志才能使用
        cursor = self.index_manager.connection.cursor(dictionary=True)
        
        try:
            cursor.execute(f"SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT {limit}")
            slow_queries = cursor.fetchall()
            
            if not slow_queries:
                logger.info("没有找到慢查询记录")
                return []
            
            logger.info(f"找到 {len(slow_queries)} 个慢查询:")
            for query in slow_queries:
                logger.info(f"  执行时间: {query['query_time']}, 锁定时间: {query['lock_time']}")
                logger.info(f"  发送行数: {query['rows_sent']}, 检查行数: {query['rows_examined']}")
                logger.info(f"  SQL: {query['sql_text']}")
                logger.info("")
            
            return slow_queries
            
        except mysql.connector.Error as err:
            logger.error(f"分析慢查询失败: {err}")
            return None
        finally:
            cursor.close()


def main():
    """主函数"""
    # 创建索引管理器
    index_manager = IndexManager()
    
    # 连接到数据库
    if not index_manager.connect():
        logger.error("无法连接到数据库，退出程序")
        return
    
    try:
        # 1. 设置示例表和数据
        logger.info("=== 设置示例表和数据 ===")
        index_manager.setup_tables()
        
        # 2. 演示各种索引类型
        logger.info("\n=== 演示各种索引类型 ===")
        index_manager.demonstrate_index_types()
        
        # 3. 演示索引使用情况
        logger.info("\n=== 演示索引使用情况 ===")
        index_manager.demonstrate_index_usage()
        
        # 4. 演示查询优化技巧
        logger.info("\n=== 演示查询优化技巧 ===")
        index_manager.demonstrate_query_optimization()
        
        # 5. 演示性能监控
        logger.info("\n=== 演示性能监控 ===")
        index_manager.demonstrate_performance_monitoring()
        
        # 6. 运行性能测试
        logger.info("\n=== 运行性能测试 ===")
        test_results = index_manager.run_performance_test(num_threads=5, num_queries=20)
        
        # 7. 演示分区表
        logger.info("\n=== 演示分区表 ===")
        index_manager.demonstrate_partitioning()
        
        # 8. 演示索引维护
        logger.info("\n=== 演示索引维护 ===")
        index_manager.demonstrate_index_maintenance()
        
        # 9. 演示服务器配置
        logger.info("\n=== 演示服务器配置 ===")
        index_manager.demonstrate_server_config()
        
        # 10. 查询优化示例
        logger.info("\n=== 查询优化示例 ===")
        optimizer = QueryOptimizer(index_manager)
        
        # 比较查询执行计划
        queries = {
            'select_star': "SELECT * FROM products WHERE category_id = 1",
            'select_columns': "SELECT id, name, price FROM products WHERE category_id = 1",
            'join_subquery': """
                SELECT p.name, p.price, c.name AS category_name 
                FROM products p 
                WHERE p.category_id IN (SELECT id FROM categories WHERE name LIKE '电子%')
            """,
            'join_direct': """
                SELECT p.name, p.price, c.name AS category_name 
                FROM products p 
                JOIN categories c ON p.category_id = c.id 
                WHERE c.name LIKE '电子%'
            """
        }
        
        optimizer.compare_query_plans(queries)
        
        # 索引建议
        optimizer.suggest_indexes(
            table='products',
            where_conditions=['category_id = 1', 'price > 1000'],
            join_conditions=['products.category_id = categories.id'],
            order_by='price DESC',
            group_by='category_id'
        )
        
        # 分析慢查询
        optimizer.analyze_slow_queries()
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")
    finally:
        # 关闭连接
        index_manager.close()


if __name__ == "__main__":
    main()