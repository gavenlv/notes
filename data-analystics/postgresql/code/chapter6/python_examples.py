#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第6章：PostgreSQL索引和性能优化 - Python演示脚本

这个脚本演示了如何:
1. 使用psycopg2连接PostgreSQL数据库
2. 执行索引创建和优化
3. 分析查询执行计划
4. 监控数据库性能
5. 应用查询优化技巧

运行前请确保：
1. PostgreSQL服务正在运行
2. 创建了测试数据库
3. 安装了requirements.txt中的依赖包
4. 配置了正确的数据库连接信息
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import time
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import json

# 加载环境变量
load_dotenv()


class DatabaseOptimizer:
    """数据库性能优化工具类"""
    
    def __init__(self):
        """初始化数据库连接"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password')
            )
            self.conn.autocommit = False
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """执行SQL查询并返回结果"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ 查询执行失败: {e}")
            print(f"SQL: {query}")
            return []
    
    def execute_command(self, command: str, params: tuple = None) -> bool:
        """执行SQL命令"""
        try:
            self.cursor.execute(command, params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 命令执行失败: {e}")
            print(f"SQL: {command}")
            return False
    
    def create_performance_test_tables(self):
        """创建性能测试表"""
        print("\n📊 创建性能测试表...")
        
        # 创建基础表结构
        create_tables_sql = """
        -- 删除已存在的表
        DROP TABLE IF EXISTS sales CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;
        
        -- 创建客户表
        CREATE TABLE customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            city VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 创建产品表
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            price DECIMAL(10,2),
            stock_quantity INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- 创建销售表
        CREATE TABLE sales (
            id SERIAL PRIMARY KEY,
            customer_id INTEGER REFERENCES customers(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            sale_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        if self.execute_command(create_tables_sql):
            print("✅ 基础表结构创建成功")
            
            # 插入测试数据
            self._insert_test_data()
        else:
            print("❌ 基础表结构创建失败")
    
    def _insert_test_data(self):
        """插入测试数据"""
        print("📈 插入测试数据...")
        
        # 插入客户数据
        customers_sql = """
        INSERT INTO customers (name, email, city) VALUES
        ('张伟', 'zhangwei@email.com', '北京'),
        ('李娜', 'lina@email.com', '上海'),
        ('王强', 'wangqiang@email.com', '广州'),
        ('赵丽', 'zhaoli@email.com', '深圳'),
        ('刘洋', 'liuyang@email.com', '杭州')
        """
        self.execute_command(customers_sql)
        
        # 插入产品数据
        products_sql = """
        INSERT INTO products (name, category, price, stock_quantity) VALUES
        ('iPhone 14', '手机', 7999.00, 100),
        ('MacBook Pro', '电脑', 19999.00, 50),
        ('iPad Air', '平板', 4399.00, 80),
        ('AirPods Pro', '耳机', 1999.00, 200),
        ('小米手机', '手机', 2999.00, 150)
        """
        self.execute_command(products_sql)
        
        # 插入销售数据（生成1000条记录）
        sales_sql = """
        INSERT INTO sales (customer_id, product_id, quantity, unit_price, sale_date)
        SELECT 
            (RANDOM() * 4)::INTEGER + 1,
            (RANDOM() * 4)::INTEGER + 1,
            (RANDOM() * 3)::INTEGER + 1,
            p.price,
            CURRENT_DATE - (RANDOM() * 365)::INTEGER
        FROM products p, generate_series(1, 1000)
        """
        self.execute_command(sales_sql)
        print("✅ 测试数据插入完成")
    
    def create_indexes(self):
        """创建各种类型的索引"""
        print("\n🔧 创建索引...")
        
        indexes = [
            # B-Tree索引
            "CREATE INDEX idx_sales_customer_id ON sales (customer_id)",
            "CREATE INDEX idx_sales_product_id ON sales (product_id)",
            "CREATE INDEX idx_sales_date ON sales (sale_date)",
            "CREATE INDEX idx_sales_customer_date ON sales (customer_id, sale_date)",
            
            # 复合索引
            "CREATE INDEX idx_products_category_price ON products (category, price)",
            
            # 部分索引
            "CREATE INDEX idx_sales_high_value ON sales (unit_price, quantity) WHERE unit_price > 1000",
            
            # 表达式索引
            "CREATE INDEX idx_customers_email_lower ON customers (LOWER(email))",
            "CREATE INDEX idx_products_name_upper ON products ((UPPER(name)))",
        ]
        
        for index_sql in indexes:
            if self.execute_command(index_sql):
                print(f"✅ 索引创建成功: {index_sql[:50]}...")
            else:
                print(f"❌ 索引创建失败: {index_sql[:50]}...")
    
    def analyze_query_performance(self):
        """分析查询性能"""
        print("\n📊 分析查询性能...")
        
        # 测试查询列表
        test_queries = [
            ("简单查询", "SELECT * FROM sales WHERE customer_id = 1"),
            ("范围查询", "SELECT * FROM sales WHERE sale_date BETWEEN '2023-01-01' AND '2023-12-31'"),
            ("连接查询", "SELECT c.name, p.name, s.quantity FROM sales s JOIN customers c ON s.customer_id = c.id JOIN products p ON s.product_id = p.id"),
            ("聚合查询", "SELECT customer_id, COUNT(*), SUM(quantity * unit_price) as total FROM sales GROUP BY customer_id"),
            ("复杂查询", """
                SELECT c.city, p.category, 
                       COUNT(*) as sales_count,
                       SUM(s.quantity * s.unit_price) as total_revenue
                FROM sales s 
                JOIN customers c ON s.customer_id = c.id 
                JOIN products p ON s.product_id = p.id
                WHERE s.sale_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY c.city, p.category
                ORDER BY total_revenue DESC
            """)
        ]
        
        for query_name, query_sql in test_queries:
            print(f"\n🔍 测试查询: {query_name}")
            
            # 获取执行计划
            explain_query = f"EXPLAIN ANALYZE {query_sql}"
            start_time = time.time()
            
            try:
                self.cursor.execute(explain_query)
                execution_plan = self.cursor.fetchall()
                
                execution_time = time.time() - start_time
                
                print(f"⏱️  执行时间: {execution_time:.3f}秒")
                print("📋 执行计划:")
                
                for row in execution_plan:
                    plan_text = row['QUERY PLAN']
                    print(f"   {plan_text}")
                    
                    # 提取关键信息
                    if 'actual time=' in plan_text:
                        try:
                            # 解析执行时间
                            parts = plan_text.split('actual time=')
                            if len(parts) > 1:
                                time_info = parts[1].split()[0].split('..')[1]
                                print(f"   💡 实际执行时间: {time_info}ms")
                        except:
                            pass
                    
                    if 'rows=' in plan_text:
                        try:
                            # 解析返回行数
                            parts = plan_text.split('rows=')
                            if len(parts) > 1:
                                rows = parts[1].split()[0]
                                print(f"   📊 预期返回行数: {rows}")
                        except:
                            pass
                
            except Exception as e:
                print(f"❌ 查询分析失败: {e}")
    
    def test_index_performance(self):
        """测试索引性能"""
        print("\n⚡ 测试索引性能...")
        
        # 测试不同查询的性能对比
        performance_tests = [
            ("无索引查询", "DROP INDEX IF EXISTS idx_sales_test; SELECT * FROM sales WHERE unit_price = 5000;"),
            ("有索引查询", "CREATE INDEX idx_sales_test ON sales (unit_price); SELECT * FROM sales WHERE unit_price = 5000;"),
        ]
        
        for test_name, test_sql in performance_tests:
            start_time = time.time()
            try:
                # 执行测试SQL
                statements = test_sql.split(';')
                for stmt in statements:
                    if stmt.strip():
                        self.execute_command(stmt.strip())
                
                execution_time = time.time() - start_time
                print(f"🧪 {test_name}: {execution_time:.3f}秒")
            except Exception as e:
                print(f"❌ {test_name} 失败: {e}")
    
    def check_index_usage(self):
        """检查索引使用情况"""
        print("\n📈 检查索引使用情况...")
        
        usage_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            CASE 
                WHEN idx_scan = 0 THEN 'Never Used'
                WHEN idx_scan < 10 THEN 'Low Usage'
                WHEN idx_scan < 100 THEN 'Medium Usage'
                ELSE 'High Usage'
            END as usage_category
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY idx_scan DESC
        """
        
        results = self.execute_query(usage_query)
        
        if results:
            print("📊 索引使用统计:")
            print(f"{'索引名':<30} {'使用次数':<10} {'大小':<15} {'使用情况':<15}")
            print("-" * 80)
            
            for row in results:
                print(f"{row['indexname']:<30} {row['idx_scan']:<10} {row['index_size']:<15} {row['usage_category']:<15}")
        else:
            print("❌ 无法获取索引使用统计")
    
    def optimize_queries(self):
        """演示查询优化"""
        print("\n🎯 演示查询优化...")
        
        # 优化示例1: 使用EXISTS替代IN
        print("\n📝 优化示例1: EXISTS vs IN")
        
        # 原始查询（使用IN）
        slow_query = """
        SELECT * FROM customers 
        WHERE id IN (SELECT DISTINCT customer_id FROM sales WHERE unit_price > 5000)
        """
        
        # 优化后查询（使用EXISTS）
        fast_query = """
        SELECT * FROM customers c
        WHERE EXISTS (SELECT 1 FROM sales s WHERE s.customer_id = c.id AND s.unit_price > 5000)
        """
        
        # 测试性能
        for query_name, query_sql in [("IN查询", slow_query), ("EXISTS查询", fast_query)]:
            start_time = time.time()
            self.execute_query(query_sql)
            execution_time = time.time() - start_time
            print(f"⏱️  {query_name}: {execution_time:.3f}秒")
        
        # 优化示例2: 使用UNION ALL替代UNION
        print("\n📝 优化示例2: UNION vs UNION ALL")
        
        # 原始查询（使用UNION）
        union_query = """
        SELECT name FROM customers WHERE city = '北京'
        UNION
        SELECT name FROM customers WHERE city = '上海'
        """
        
        # 优化后查询（使用UNION ALL）
        union_all_query = """
        SELECT name FROM customers WHERE city = '北京'
        UNION ALL
        SELECT name FROM customers WHERE city = '上海'
        """
        
        for query_name, query_sql in [("UNION查询", union_query), ("UNION ALL查询", union_all_query)]:
            start_time = time.time()
            self.execute_query(query_sql)
            execution_time = time.time() - start_time
            print(f"⏱️  {query_name}: {execution_time:.3f}秒")
    
    def monitor_database_stats(self):
        """监控数据库统计信息"""
        print("\n📊 监控数据库统计信息...")
        
        # 表统计信息
        table_stats_query = """
        SELECT 
            schemaname,
            tablename,
            n_tup_ins,
            n_tup_upd,
            n_tup_del,
            n_live_tup,
            n_dead_tup,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_tup_ins DESC
        """
        
        results = self.execute_query(table_stats_query)
        
        if results:
            print("📋 表统计信息:")
            for row in results:
                print(f"表: {row['tablename']}")
                print(f"  活跃记录: {row['n_live_tup']}")
                print(f"  死亡记录: {row['n_dead_tup']}")
                print(f"  总插入: {row['n_tup_ins']}")
                print(f"  最后ANALYZE: {row['last_analyze']}")
                print("-" * 40)
    
    def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        
        cleanup_sql = """
        DROP TABLE IF EXISTS sales CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;
        """
        
        if self.execute_command(cleanup_sql):
            print("✅ 测试数据清理完成")
        else:
            print("❌ 测试数据清理失败")
    
    def close_connection(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔒 数据库连接已关闭")


def main():
    """主函数"""
    print("🚀 PostgreSQL 索引和性能优化演示")
    print("=" * 50)
    
    optimizer = None
    
    try:
        # 创建优化器实例
        optimizer = DatabaseOptimizer()
        
        # 创建测试表和数据
        optimizer.create_performance_test_tables()
        
        # 创建索引
        optimizer.create_indexes()
        
        # 分析查询性能
        optimizer.analyze_query_performance()
        
        # 测试索引性能
        optimizer.test_index_performance()
        
        # 检查索引使用情况
        optimizer.check_index_usage()
        
        # 演示查询优化
        optimizer.optimize_queries()
        
        # 监控数据库统计信息
        optimizer.monitor_database_stats()
        
        print("\n🎉 演示完成！")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        
    finally:
        # 清理资源
        if optimizer:
            optimizer.close_connection()


if __name__ == "__main__":
    main()