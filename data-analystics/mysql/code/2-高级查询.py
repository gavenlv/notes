#!/usr/bin/env python3
"""
MySQL第2章：高级查询代码示例

这个文件包含了第2章"高级查询"的所有代码示例，包括：
- 高级SELECT语句
- 连接查询（内连接、外连接、自连接等）
- 子查询（相关子查询、非相关子查询）
- 聚合函数与分组
- 窗口函数
- 高级过滤条件
- 查询优化

使用方法：
1. 确保MySQL服务器已安装并运行
2. 修改配置信息（主机、用户名、密码等）
3. 运行脚本：python 2-高级查询.py

注意：在生产环境中使用时，请确保数据库凭据的安全。
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime, date, timedelta
import random
import string
import time
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'password',  # 修改为你的MySQL密码
    'charset': 'utf8mb4',
    'autocommit': True
}

class MySQLConnection:
    """MySQL连接管理类"""
    
    def __init__(self, config=None):
        """初始化连接"""
        self.config = config or DB_CONFIG
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """连接到MySQL服务器"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            logger.info(f"成功连接到MySQL服务器: {self.config['host']}:{self.config['port']}")
            return True
        except Error as e:
            logger.error(f"连接MySQL失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL连接已关闭")
    
    def execute_query(self, query, params=None):
        """执行查询（SELECT）"""
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"执行查询失败: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """执行更新（INSERT, UPDATE, DELETE）"""
        try:
            self.cursor.execute(query, params or ())
            affected_rows = self.cursor.rowcount
            if not self.config.get('autocommit', False):
                self.connection.commit()
            logger.info(f"执行更新成功，影响行数: {affected_rows}")
            return affected_rows
        except Error as e:
            logger.error(f"执行更新失败: {e}")
            if not self.config.get('autocommit', False):
                self.connection.rollback()
            return None
    
    def execute_many(self, query, params_list):
        """批量执行更新"""
        try:
            self.cursor.executemany(query, params_list)
            affected_rows = self.cursor.rowcount
            if not self.config.get('autocommit', False):
                self.connection.commit()
            logger.info(f"批量执行成功，影响行数: {affected_rows}")
            return affected_rows
        except Error as e:
            logger.error(f"批量执行失败: {e}")
            if not self.config.get('autocommit', False):
                self.connection.rollback()
            return None
    
    def explain_query(self, query, params=None):
        """分析查询执行计划"""
        try:
            explain_query = f"EXPLAIN FORMAT=JSON {query}"
            self.cursor.execute(explain_query, params or ())
            result = self.cursor.fetchone()
            return result
        except Error as e:
            logger.error(f"分析查询执行计划失败: {e}")
            return None

class AdvancedQueryDemo:
    """高级查询演示"""
    
    def __init__(self, config=None):
        self.db_conn = MySQLConnection(config)
        self.demo_db = "mysql_advanced_demo"
        
    def run_all_demos(self):
        """运行所有演示"""
        logger.info("开始运行MySQL高级查询演示")
        
        if not self.db_conn.connect():
            logger.error("无法连接到MySQL服务器，停止演示")
            return
        
        try:
            # 1. 准备测试数据
            self.prepare_test_data()
            
            # 2. 高级SELECT语句
            self.advanced_select_demo()
            
            # 3. 连接查询
            self.join_queries_demo()
            
            # 4. 子查询
            self.subquery_demo()
            
            # 5. 聚合函数与分组
            self.aggregation_demo()
            
            # 6. 窗口函数
            self.window_function_demo()
            
            # 7. 高级过滤条件
            self.advanced_filter_demo()
            
            # 8. 查询优化
            self.query_optimization_demo()
            
            logger.info("所有演示运行完成")
            
        except Exception as e:
            logger.error(f"运行演示时发生错误: {e}")
        finally:
            self.db_conn.disconnect()
    
    def prepare_test_data(self):
        """准备测试数据"""
        logger.info("\n" + "="*50)
        logger.info("准备测试数据")
        logger.info("="*50)
        
        # 创建演示数据库
        self.db_conn.execute_update(f"CREATE DATABASE IF NOT EXISTS {self.demo_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # 创建部门表
        logger.info("创建部门表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT AUTO_INCREMENT PRIMARY KEY,
                department_name VARCHAR(100) NOT NULL,
                location_id INT,
                manager_id INT
            )
        """)
        
        # 创建员工表
        logger.info("创建员工表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(20),
                hire_date DATE NOT NULL,
                job_id VARCHAR(10) NOT NULL,
                salary DECIMAL(10, 2) NOT NULL,
                commission_pct DECIMAL(5, 2),
                manager_id INT,
                department_id INT,
                INDEX idx_department (department_id),
                INDEX idx_salary (salary),
                INDEX idx_hire_date (hire_date)
            )
        """)
        
        # 创建工作表
        logger.info("创建工作表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id VARCHAR(10) PRIMARY KEY,
                job_title VARCHAR(100) NOT NULL,
                min_salary DECIMAL(10, 2),
                max_salary DECIMAL(10, 2)
            )
        """)
        
        # 创建位置表
        logger.info("创建位置表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id INT AUTO_INCREMENT PRIMARY KEY,
                street_address VARCHAR(100),
                postal_code VARCHAR(20),
                city VARCHAR(50),
                state_province VARCHAR(50),
                country_id VARCHAR(2)
            )
        """)
        
        # 创建薪资等级表
        logger.info("创建薪资等级表")
        self.db_conn.execute_update("""
            CREATE TABLE IF NOT EXISTS job_grades (
                grade_level VARCHAR(3) PRIMARY KEY,
                lowest_sal DECIMAL(10, 2),
                highest_sal DECIMAL(10, 2)
            )
        """)
        
        # 清空表
        logger.info("清空表数据")
        tables = ['employees', 'departments', 'jobs', 'locations', 'job_grades']
        for table in tables:
            self.db_conn.execute_update(f"DELETE FROM {table}")
        
        # 插入位置数据
        logger.info("插入位置数据")
        locations_data = [
            (1700, '1400 40th Ave', '94061', 'South San Francisco', 'California', 'US'),
            (1800, '460 Bloor St. W', 'M5V 2Y5', 'Toronto', 'Ontario', 'CA'),
            (2500, 'Magdalen Centre, The Oxford Science Park', 'OX9 9ZB', 'Oxford', 'Oxford', 'UK')
        ]
        self.db_conn.execute_many("""
            INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, locations_data)
        
        # 插入部门数据
        logger.info("插入部门数据")
        departments_data = [
            (10, '行政部', 1700, 200),
            (20, '市场部', 1800, 201),
            (30, '销售部', 2500, 202),
            (40, '人力资源部', 1700, 203),
            (50, '技术部', 1800, 204),
            (60, '财务部', 2500, 205)
        ]
        self.db_conn.execute_many("""
            INSERT INTO departments (department_id, department_name, location_id, manager_id)
            VALUES (%s, %s, %s, %s)
        """, departments_data)
        
        # 插入工作数据
        logger.info("插入工作数据")
        jobs_data = [
            ('AD_PRES', '总裁', 20000, 40000),
            ('AD_VP', '副总裁', 15000, 30000),
            ('AD_ASST', '行政助理', 3000, 6000),
            ('FI_MGR', '财务经理', 8200, 16000),
            ('FI_ACCOUNT', '财务会计', 4200, 9000),
            ('AC_MGR', '会计经理', 8200, 16000),
            ('AC_ACCOUNT', '会计', 4200, 9000),
            ('SA_MAN', '销售经理', 10000, 20000),
            ('SA_REP', '销售代表', 6000, 12000),
            ('PU_MAN', '采购经理', 8000, 15000),
            ('PU_CLERK', '采购员', 2500, 5500),
            ('ST_MAN', '库房经理', 5600, 11500),
            ('ST_CLERK', '库房员', 2100, 4100),
            ('SH_CLERK', '发货员', 2000, 4000),
            ('IT_PROG', '程序员', 4000, 10000),
            ('MK_MAN', '市场经理', 9000, 15000),
            ('MK_REP', '市场代表', 4000, 9000)
        ]
        self.db_conn.execute_many("""
            INSERT INTO jobs (job_id, job_title, min_salary, max_salary)
            VALUES (%s, %s, %s, %s)
        """, jobs_data)
        
        # 插入薪资等级数据
        logger.info("插入薪资等级数据")
        grades_data = [
            ('A', 1000, 2999),
            ('B', 3000, 5999),
            ('C', 6000, 9999),
            ('D', 10000, 14999),
            ('E', 15000, 24999),
            ('F', 25000, 40000)
        ]
        self.db_conn.execute_many("""
            INSERT INTO job_grades (grade_level, lowest_sal, highest_sal)
            VALUES (%s, %s, %s)
        """, grades_data)
        
        # 生成员工数据
        logger.info("生成员工数据")
        first_names = ['张', '李', '王', '赵', '钱', '孙', '周', '吴', '郑', '冯', 
                      '陈', '楚', '魏', '蒋', '沈', '韩', '杨', '朱', '秦', '尤',
                      '许', '何', '吕', '施', '张', '孔', '曹', '严', '华', '金',
                      '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦']
        last_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '洋', '艳',
                      '勇', '军', '杰', '娟', '涛', '明', '超', '秀英', '霞', '平',
                      '刚', '桂英', '玉兰', '萍', '飞', '淑兰', '秀兰', '秀珍', '华',
                      '慧', '巧', '美', '红', '春梅', '雪', '琳', '梅', '兰']
        
        job_ids = list(j[0] for j in jobs_data)
        
        employees_data = []
        base_date = date(2000, 1, 1)
        
        for i in range(1, 201):
            first_name = random.choice(first_names) + random.choice(last_names)
            last_name = random.choice(first_names) + random.choice(last_names)
            email = f"user{i}@example.com"
            phone = f"138{random.randint(10000000, 99999999)}"
            
            # 随机生成入职日期
            days_offset = random.randint(0, 20*365)  # 过去20年内
            hire_date = base_date + timedelta(days=days_offset)
            
            job_id = random.choice(job_ids)
            
            # 根据职位生成薪资
            job_info = next((j for j in jobs_data if j[0] == job_id), None)
            if job_info:
                salary = round(random.uniform(float(job_info[2]), float(job_info[3])), 2)
            else:
                salary = round(random.uniform(3000, 15000), 2)
            
            # 随机部门ID
            department_id = random.randint(10, 60)
            
            # 前几个员工设置为主管
            manager_id = None if i <= 6 else random.randint(1, min(i-1, 6))
            
            # 随机佣金比例
            commission_pct = None
            if random.random() < 0.3:  # 30%的员工有佣金
                commission_pct = round(random.uniform(0.05, 0.25), 2)
            
            employees_data.append((
                i, first_name, last_name, email, phone, hire_date,
                job_id, salary, commission_pct, manager_id, department_id
            ))
        
        self.db_conn.execute_many("""
            INSERT INTO employees (
                employee_id, first_name, last_name, email, phone_number,
                hire_date, job_id, salary, commission_pct, manager_id, department_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, employees_data)
        
        # 更新部门的manager_id
        self.db_conn.execute_update("UPDATE departments SET manager_id = 1 WHERE department_id IN (10, 20, 30)")
        self.db_conn.execute_update("UPDATE departments SET manager_id = 2 WHERE department_id IN (40, 50)")
        self.db_conn.execute_update("UPDATE departments SET manager_id = 3 WHERE department_id = 60")
        
        # 创建索引
        logger.info("创建复合索引")
        self.db_conn.execute_update("CREATE INDEX idx_emp_dept_salary ON employees(department_id, salary)")
        
        logger.info("测试数据准备完成")
    
    def advanced_select_demo(self):
        """高级SELECT语句演示"""
        logger.info("\n" + "="*50)
        logger.info("1. 高级SELECT语句演示")
        logger.info("="*50)
        
        # DISTINCT关键字
        logger.info("\n1.1 DISTINCT关键字")
        result = self.db_conn.execute_query("SELECT DISTINCT department_id FROM employees ORDER BY department_id")
        logger.info("不同的部门ID:")
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 别名使用
        logger.info("\n1.2 别名使用")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id AS '员工ID',
                first_name AS '名',
                last_name AS '姓',
                salary AS '薪资',
                salary * 12 AS '年薪'
            FROM employees
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # CASE表达式
        logger.info("\n1.3 CASE表达式")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                department_id,
                salary,
                CASE 
                    WHEN salary < 5000 THEN '低薪资'
                    WHEN salary >= 5000 AND salary < 10000 THEN '中等薪资'
                    WHEN salary >= 10000 AND salary < 20000 THEN '高薪资'
                    ELSE '超高薪资'
                END AS salary_level
            FROM employees
            ORDER BY salary DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 使用表的别名
        logger.info("\n1.4 表的别名")
        result = self.db_conn.execute_query("""
            SELECT 
                e.employee_id,
                e.first_name,
                e.salary,
                d.department_name
            FROM employees AS e
            JOIN departments AS d ON e.department_id = d.department_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def join_queries_demo(self):
        """连接查询演示"""
        logger.info("\n" + "="*50)
        logger.info("2. 连接查询演示")
        logger.info("="*50)
        
        # 内连接
        logger.info("\n2.1 内连接（INNER JOIN）")
        result = self.db_conn.execute_query("""
            SELECT 
                e.employee_id,
                e.first_name,
                e.department_id,
                d.department_name
            FROM employees e
            INNER JOIN departments d ON e.department_id = d.department_id
            ORDER BY e.department_id, e.employee_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 左连接
        logger.info("\n2.2 左连接（LEFT JOIN）")
        result = self.db_conn.execute_query("""
            SELECT 
                e.employee_id,
                e.first_name,
                d.department_name
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.department_id
            ORDER BY e.employee_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 右连接
        logger.info("\n2.3 右连接（RIGHT JOIN）")
        result = self.db_conn.execute_query("""
            SELECT 
                e.employee_id,
                e.first_name,
                d.department_name
            FROM employees e
            RIGHT JOIN departments d ON e.department_id = d.department_id
            ORDER BY d.department_id
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 自连接
        logger.info("\n2.4 自连接")
        result = self.db_conn.execute_query("""
            SELECT 
                e.employee_id AS '员工ID',
                e.first_name AS '员工姓名',
                m.employee_id AS '上级ID',
                m.first_name AS '上级姓名'
            FROM employees e
            LEFT JOIN employees m ON e.manager_id = m.employee_id
            WHERE e.manager_id IS NOT NULL
            ORDER BY e.employee_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 多表连接
        logger.info("\n2.5 多表连接")
        result = self.db_conn.execute_query("""
            SELECT 
                e.employee_id,
                e.first_name,
                d.department_name,
                j.job_title,
                s.grade_level
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            JOIN jobs j ON e.job_id = j.job_id
            JOIN job_grades s ON e.salary BETWEEN s.lowest_sal AND s.highest_sal
            ORDER BY e.employee_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def subquery_demo(self):
        """子查询演示"""
        logger.info("\n" + "="*50)
        logger.info("3. 子查询演示")
        logger.info("="*50)
        
        # 在WHERE子句中使用子查询
        logger.info("\n3.1 在WHERE子句中使用子查询")
        result = self.db_conn.execute_query("""
            SELECT employee_id, first_name, salary
            FROM employees
            WHERE salary > (
                SELECT AVG(salary) FROM employees
            )
            ORDER BY salary DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 在FROM子句中使用子查询（派生表）
        logger.info("\n3.2 在FROM子句中使用子查询（派生表）")
        result = self.db_conn.execute_query("""
            SELECT department_id, avg_salary
            FROM (
                SELECT department_id, AVG(salary) AS avg_salary
                FROM employees
                GROUP BY department_id
            ) dept_avg
            WHERE avg_salary > 10000
            ORDER BY avg_salary DESC
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 相关子查询
        logger.info("\n3.3 相关子查询")
        result = self.db_conn.execute_query("""
            SELECT employee_id, first_name, salary, department_id
            FROM employees e
            WHERE salary > (
                SELECT AVG(salary)
                FROM employees
                WHERE department_id = e.department_id
            )
            ORDER BY department_id, salary DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 使用IN的子查询
        logger.info("\n3.4 使用IN的子查询")
        result = self.db_conn.execute_query("""
            SELECT employee_id, first_name, department_id
            FROM employees
            WHERE department_id IN (
                SELECT department_id
                FROM departments
                WHERE location_id = 1700
            )
            ORDER BY employee_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 使用ANY的子查询
        logger.info("\n3.5 使用ANY的子查询")
        result = self.db_conn.execute_query("""
            SELECT employee_id, first_name, salary
            FROM employees
            WHERE salary > ANY (
                SELECT salary
                FROM employees
                WHERE department_id = 50
            )
            ORDER BY salary DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 使用EXISTS的子查询
        logger.info("\n3.6 使用EXISTS的子查询")
        result = self.db_conn.execute_query("""
            SELECT department_id, department_name
            FROM departments d
            WHERE EXISTS (
                SELECT 1
                FROM employees e
                WHERE e.department_id = d.department_id AND e.salary > 15000
            )
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def aggregation_demo(self):
        """聚合函数与分组演示"""
        logger.info("\n" + "="*50)
        logger.info("4. 聚合函数与分组演示")
        logger.info("="*50)
        
        # 常用聚合函数
        logger.info("\n4.1 常用聚合函数")
        result = self.db_conn.execute_query("""
            SELECT 
                COUNT(*) AS total_employees,
                COUNT(DISTINCT department_id) AS departments,
                AVG(salary) AS avg_salary,
                MAX(salary) AS max_salary,
                MIN(salary) AS min_salary,
                SUM(salary) AS total_salary
            FROM employees
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # GROUP BY基本用法
        logger.info("\n4.2 GROUP BY基本用法")
        result = self.db_conn.execute_query("""
            SELECT 
                department_id,
                COUNT(*) AS employee_count,
                AVG(salary) AS avg_salary,
                MAX(salary) AS max_salary
            FROM employees
            GROUP BY department_id
            ORDER BY department_id
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 多列分组
        logger.info("\n4.3 多列分组")
        result = self.db_conn.execute_query("""
            SELECT 
                department_id,
                job_id,
                COUNT(*) AS employee_count,
                AVG(salary) AS avg_salary
            FROM employees
            GROUP BY department_id, job_id
            ORDER BY department_id, avg_salary DESC
            LIMIT 15
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # GROUP BY与CASE表达式结合
        logger.info("\n4.4 GROUP BY与CASE表达式结合")
        result = self.db_conn.execute_query("""
            SELECT 
                CASE 
                    WHEN salary < 5000 THEN '低薪资'
                    WHEN salary < 10000 THEN '中等薪资'
                    ELSE '高薪资'
                END AS salary_level,
                COUNT(*) AS employee_count,
                AVG(salary) AS avg_salary
            FROM employees
            GROUP BY 
                CASE 
                    WHEN salary < 5000 THEN '低薪资'
                    WHEN salary < 10000 THEN '中等薪资'
                    ELSE '高薪资'
                END
            ORDER BY avg_salary
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # HAVING子句
        logger.info("\n4.5 HAVING子句")
        result = self.db_conn.execute_query("""
            SELECT 
                d.department_name,
                COUNT(e.employee_id) AS employee_count,
                AVG(e.salary) AS avg_salary
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            GROUP BY d.department_name
            HAVING AVG(e.salary) > 10000
            ORDER BY avg_salary DESC
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # WITH ROLLUP
        logger.info("\n4.6 WITH ROLLUP")
        result = self.db_conn.execute_query("""
            SELECT 
                department_id,
                job_id,
                COUNT(*) AS employee_count,
                AVG(salary) AS avg_salary
            FROM employees
            WHERE department_id IN (10, 20, 30)
            GROUP BY department_id, job_id WITH ROLLUP
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # GROUP_CONCAT函数
        logger.info("\n4.7 GROUP_CONCAT函数")
        result = self.db_conn.execute_query("""
            SELECT 
                department_id,
                GROUP_CONCAT(first_name ORDER BY salary DESC SEPARATOR ', ') AS employee_names
            FROM employees
            WHERE department_id IN (10, 20, 30)
            GROUP BY department_id
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def window_function_demo(self):
        """窗口函数演示"""
        logger.info("\n" + "="*50)
        logger.info("5. 窗口函数演示")
        logger.info("="*50)
        
        # 排名函数
        logger.info("\n5.1 排名函数")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                salary,
                ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_number_rank,
                RANK() OVER (ORDER BY salary DESC) AS rank_rank,
                DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank_rank
            FROM employees
            ORDER BY salary DESC
            LIMIT 15
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 分区排名
        logger.info("\n5.2 分区排名")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                department_id,
                salary,
                ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
            FROM employees
            WHERE department_id IN (10, 20, 30)
            ORDER BY department_id, salary DESC
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 聚合窗口函数
        logger.info("\n5.3 聚合窗口函数")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                salary,
                SUM(salary) OVER () AS total_salary,
                SUM(salary) OVER (ORDER BY employee_id) AS running_total,
                AVG(salary) OVER (PARTITION BY department_id) AS dept_avg_salary
            FROM employees
            WHERE department_id IN (10, 20, 30)
            ORDER BY employee_id
            LIMIT 15
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # LAG和LEAD函数
        logger.info("\n5.4 LAG和LEAD函数")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                hire_date,
                LAG(hire_date, 1) OVER (ORDER BY hire_date) AS prev_hire_date,
                LEAD(hire_date, 1) OVER (ORDER BY hire_date) AS next_hire_date
            FROM employees
            WHERE department_id = 10
            ORDER BY hire_date
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # FIRST_VALUE和LAST_VALUE函数
        logger.info("\n5.5 FIRST_VALUE和LAST_VALUE函数")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                department_id,
                salary,
                FIRST_VALUE(salary) OVER (
                    PARTITION BY department_id 
                    ORDER BY salary 
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS dept_min_salary,
                LAST_VALUE(salary) OVER (
                    PARTITION BY department_id 
                    ORDER BY salary 
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                ) AS dept_max_salary
            FROM employees
            WHERE department_id IN (10, 20)
            ORDER BY department_id, salary
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 窗口框架
        logger.info("\n5.6 窗口框架")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                salary,
                SUM(salary) OVER (
                    ORDER BY salary 
                    ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
                ) AS moving_sum,
                AVG(salary) OVER (
                    ORDER BY salary 
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ) AS moving_avg
            FROM employees
            WHERE department_id = 10
            ORDER BY salary
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def advanced_filter_demo(self):
        """高级过滤条件演示"""
        logger.info("\n" + "="*50)
        logger.info("6. 高级过滤条件演示")
        logger.info("="*50)
        
        # LIKE操作符
        logger.info("\n6.1 LIKE操作符")
        result = self.db_conn.execute_query("""
            SELECT employee_id, first_name, last_name
            FROM employees
            WHERE first_name LIKE '张%'
            ORDER BY first_name
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # REGEXP操作符
        logger.info("\n6.2 REGEXP操作符")
        result = self.db_conn.execute_query("""
            SELECT employee_id, first_name, last_name
            FROM employees
            WHERE first_name REGEXP '^(张|李|王)'
            ORDER BY first_name
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # NULL值处理
        logger.info("\n6.3 NULL值处理")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                commission_pct,
                COALESCE(commission_pct, 0) AS commission_pct_not_null
            FROM employees
            WHERE commission_pct IS NOT NULL
            ORDER BY commission_pct DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 类型转换
        logger.info("\n6.4 类型转换")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                salary,
                CAST(salary AS CHAR) AS salary_as_char,
                CAST(salary AS SIGNED) AS salary_as_integer,
                CONCAT('$', FORMAT(salary, 2)) AS formatted_salary
            FROM employees
            ORDER BY salary DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 日期时间函数
        logger.info("\n6.5 日期时间函数")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                hire_date,
                YEAR(hire_date) AS hire_year,
                MONTH(hire_date) AS hire_month,
                DAY(hire_date) AS hire_day,
                DATEDIFF(CURRENT_DATE(), hire_date) AS days_employed,
                DATE_FORMAT(hire_date, '%Y年%m月%d日') AS formatted_hire_date
            FROM employees
            ORDER BY hire_date DESC
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 字符串函数
        logger.info("\n6.6 字符串函数")
        result = self.db_conn.execute_query("""
            SELECT 
                employee_id,
                first_name,
                email,
                CONCAT(first_name, ' ', last_name) AS full_name,
                UPPER(first_name) AS upper_name,
                LENGTH(first_name) AS name_length,
                SUBSTRING(first_name, 1, 3) AS first_three_chars
            FROM employees
            ORDER BY employee_id
            LIMIT 10
        """)
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def query_optimization_demo(self):
        """查询优化演示"""
        logger.info("\n" + "="*50)
        logger.info("7. 查询优化演示")
        logger.info("="*50)
        
        # EXPLAIN分析
        logger.info("\n7.1 EXPLAIN分析")
        
        # 分析简单查询
        query = "SELECT * FROM employees WHERE department_id = 50"
        explain_result = self.db_conn.explain_query(query)
        if explain_result:
            explain_data = explain_result[0][0]
            logger.info(f"查询: {query}")
            logger.info(f"执行计划: {explain_data}")
        
        # 分析连接查询
        query = """
            SELECT e.first_name, d.department_name 
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            WHERE e.salary > 10000
        """
        explain_result = self.db_conn.explain_query(query)
        if explain_result:
            explain_data = explain_result[0][0]
            logger.info(f"查询: {query}")
            logger.info(f"执行计划: {explain_data}")
        
        # 索引使用测试
        logger.info("\n7.2 索引使用测试")
        
        # 使用索引的查询
        query = "SELECT * FROM employees WHERE department_id = 50"
        result = self.db_conn.execute_query(query)
        logger.info(f"使用索引的查询: {query}")
        logger.info(f"返回行数: {len(result) if result else 0}")
        
        # 使用复合索引的查询
        query = "SELECT * FROM employees WHERE department_id = 50 AND salary > 8000"
        result = self.db_conn.execute_query(query)
        logger.info(f"使用复合索引的查询: {query}")
        logger.info(f"返回行数: {len(result) if result else 0}")
        
        # 查询重写示例
        logger.info("\n7.3 查询重写示例")
        
        # 子查询 vs JOIN
        logger.info("子查询 vs JOIN:")
        
        # 使用子查询
        query = """
            SELECT employee_id, first_name
            FROM employees
            WHERE department_id IN (
                SELECT department_id FROM departments WHERE location_id = 1700
            )
        """
        start_time = time.time()
        result = self.db_conn.execute_query(query)
        subquery_time = time.time() - start_time
        logger.info(f"子查询返回行数: {len(result) if result else 0}, 耗时: {subquery_time:.6f}秒")
        
        # 使用JOIN
        query = """
            SELECT e.employee_id, e.first_name
            FROM employees e
            JOIN departments d ON e.department_id = d.department_id
            WHERE d.location_id = 1700
        """
        start_time = time.time()
        result = self.db_conn.execute_query(query)
        join_time = time.time() - start_time
        logger.info(f"JOIN返回行数: {len(result) if result else 0}, 耗时: {join_time:.6f}秒")
        
        logger.info(f"JOIN比子查询快 {((subquery_time - join_time) / subquery_time * 100):.2f}%")
        
        # 分页优化测试
        logger.info("\n7.4 分页优化测试")
        
        # 基本分页
        page = 10
        limit = 10
        offset = (page - 1) * limit
        
        query = f"SELECT * FROM employees ORDER BY employee_id LIMIT {limit} OFFSET {offset}"
        start_time = time.time()
        result = self.db_conn.execute_query(query)
        basic_pagination_time = time.time() - start_time
        logger.info(f"基本分页返回行数: {len(result) if result else 0}, 耗时: {basic_pagination_time:.6f}秒")
        
        # 使用ID优化的分页（假设我们知道上一页的最后一个ID）
        last_id = offset  # 简化示例
        query = f"SELECT * FROM employees WHERE employee_id > {last_id} ORDER BY employee_id LIMIT {limit}"
        start_time = time.time()
        result = self.db_conn.execute_query(query)
        optimized_pagination_time = time.time() - start_time
        logger.info(f"优化分页返回行数: {len(result) if result else 0}, 耗时: {optimized_pagination_time:.6f}秒")
        
        logger.info(f"优化分页比基本分页快 {((basic_pagination_time - optimized_pagination_time) / basic_pagination_time * 100):.2f}%")
    
    def display_query_result(self, result, description):
        """显示查询结果"""
        if not result:
            logger.info("无结果")
            return
        
        # 获取列名
        columns = [desc[0] for desc in description]
        
        # 计算每列的最大宽度
        col_widths = [len(col) for col in columns]
        for row in result:
            for i, value in enumerate(row):
                value_str = str(value) if value is not None else "NULL"
                if len(value_str) > col_widths[i]:
                    col_widths[i] = len(value_str)
        
        # 显示表头
        header = " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(columns))
        logger.info(header)
        logger.info("-" * len(header))
        
        # 显示数据
        for row in result:
            row_str = []
            for i, value in enumerate(row):
                value_str = str(value) if value is not None else "NULL"
                if isinstance(value, datetime):
                    value_str = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    value_str = value.strftime('%Y-%m-%d')
                elif isinstance(value, bytes):
                    value_str = f"[Binary data: {len(value)} bytes]"
                row_str.append(value_str.ljust(col_widths[i]))
            logger.info(" | ".join(row_str))

def main():
    """主函数"""
    logger.info("MySQL第2章：高级查询")
    logger.info("=" * 50)
    
    # 检查MySQL连接
    try:
        conn = MySQLConnection()
        if not conn.connect():
            logger.error("无法连接到MySQL服务器，请检查配置")
            logger.error("请确保MySQL服务器已启动，并修改配置中的连接参数")
            sys.exit(1)
        conn.disconnect()
    except Error as e:
        logger.error(f"MySQL连接测试失败: {e}")
        logger.error("请确保已安装mysql-connector-python库: pip install mysql-connector-python")
        sys.exit(1)
    
    try:
        # 运行高级查询演示
        demo = AdvancedQueryDemo()
        demo.run_all_demos()
        
        logger.info("所有演示运行完成")
        
    except Exception as e:
        logger.error(f"运行演示时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()