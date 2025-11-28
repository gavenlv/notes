#!/usr/bin/env python3
"""
MySQL第1章：入门与基础概念代码示例

这个文件包含了第1章"MySQL入门与基础概念"的所有代码示例，包括：
- 数据库连接与基本操作
- 创建和管理数据库
- 用户管理
- 创建表和基本CRUD操作
- 数据类型示例
- 最佳实践演示

使用方法：
1. 确保MySQL服务器已安装并运行
2. 修改配置信息（主机、用户名、密码等）
3. 运行脚本：python 1-MySQL入门与基础概念.py

注意：在生产环境中使用时，请确保数据库凭据的安全。
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime, date
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

# 新用户配置（用于演示用户管理）
NEW_USER_CONFIG = {
    'username': 'demo_user',
    'password': 'demo_password',
    'host': 'localhost'
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

class MySQLBasicsDemo:
    """MySQL基础操作演示"""
    
    def __init__(self, config=None):
        self.db_conn = MySQLConnection(config)
        self.demo_db = "mysql_demo"
    
    def run_all_demos(self):
        """运行所有演示"""
        logger.info("开始运行MySQL基础操作演示")
        
        if not self.db_conn.connect():
            logger.error("无法连接到MySQL服务器，停止演示")
            return
        
        try:
            # 1. 连接测试
            self.test_connection()
            
            # 2. 数据库操作
            self.database_operations_demo()
            
            # 3. 用户管理
            self.user_management_demo()
            
            # 4. 数据类型演示
            self.data_types_demo()
            
            # 5. 表操作演示
            self.table_operations_demo()
            
            # 6. CRUD操作演示
            self.crud_operations_demo()
            
            logger.info("所有演示运行完成")
            
        except Exception as e:
            logger.error(f"运行演示时发生错误: {e}")
        finally:
            self.db_conn.disconnect()
    
    def test_connection(self):
        """测试数据库连接"""
        logger.info("\n" + "="*50)
        logger.info("1. 测试数据库连接")
        logger.info("="*50)
        
        # 检查连接状态
        if self.db_conn.connection and self.db_conn.connection.is_connected():
            logger.info("数据库连接正常")
            
            # 获取服务器信息
            server_info = self.db_conn.connection.get_server_info()
            logger.info(f"MySQL服务器版本: {server_info}")
            
            # 获取当前用户
            result = self.db_conn.execute_query("SELECT USER()")
            if result:
                logger.info(f"当前用户: {result[0][0]}")
        else:
            logger.error("数据库连接异常")
    
    def database_operations_demo(self):
        """数据库操作演示"""
        logger.info("\n" + "="*50)
        logger.info("2. 数据库操作演示")
        logger.info("="*50)
        
        # 显示所有数据库
        logger.info("显示所有数据库:")
        result = self.db_conn.execute_query("SHOW DATABASES")
        if result:
            for db in result:
                logger.info(f"  - {db[0]}")
        
        # 创建演示数据库
        logger.info(f"\n创建数据库: {self.demo_db}")
        self.db_conn.execute_update(f"CREATE DATABASE IF NOT EXISTS {self.demo_db} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # 使用演示数据库
        logger.info(f"使用数据库: {self.demo_db}")
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # 显示当前数据库
        result = self.db_conn.execute_query("SELECT DATABASE()")
        if result:
            logger.info(f"当前数据库: {result[0][0]}")
    
    def user_management_demo(self):
        """用户管理演示"""
        logger.info("\n" + "="*50)
        logger.info("3. 用户管理演示")
        logger.info("="*50)
        
        username = NEW_USER_CONFIG['username']
        password = NEW_USER_CONFIG['password']
        host = NEW_USER_CONFIG['host']
        
        # 创建用户
        logger.info(f"创建用户: {username}@{host}")
        create_user_sql = f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY '{password}'"
        self.db_conn.execute_update(create_user_sql)
        
        # 授予权限
        logger.info(f"授予用户权限")
        grant_sql = f"GRANT SELECT, INSERT, UPDATE, DELETE ON {self.demo_db}.* TO '{username}'@'{host}'"
        self.db_conn.execute_update(grant_sql)
        self.db_conn.execute_update("FLUSH PRIVILEGES")
        
        # 显示用户
        logger.info("显示所有用户:")
        result = self.db_conn.execute_query("SELECT User, Host FROM mysql.user")
        if result:
            for user in result:
                logger.info(f"  - {user[0]}@{user[1]}")
        
        # 测试新用户连接
        logger.info(f"测试新用户连接: {username}")
        user_config = {
            'host': DB_CONFIG['host'],
            'port': DB_CONFIG['port'],
            'user': username,
            'password': password,
            'database': self.demo_db,
            'charset': 'utf8mb4'
        }
        
        user_conn = MySQLConnection(user_config)
        if user_conn.connect():
            logger.info("新用户连接成功")
            user_conn.disconnect()
        else:
            logger.warning("新用户连接失败")
        
        # 删除演示用户（可选）
        # logger.info(f"删除用户: {username}")
        # self.db_conn.execute_update(f"DROP USER IF EXISTS '{username}'@'{host}'")
    
    def data_types_demo(self):
        """数据类型演示"""
        logger.info("\n" + "="*50)
        logger.info("4. 数据类型演示")
        logger.info("="*50)
        
        # 确保使用演示数据库
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # 创建数据类型演示表
        logger.info("创建数据类型演示表")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS data_types_demo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tinyint_col TINYINT,
            smallint_col SMALLINT,
            int_col INT,
            bigint_col BIGINT,
            float_col FLOAT,
            double_col DOUBLE,
            decimal_col DECIMAL(10, 2),
            char_col CHAR(10),
            varchar_col VARCHAR(50),
            text_col TEXT,
            date_col DATE,
            datetime_col DATETIME,
            timestamp_col TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            time_col TIME,
            year_col YEAR,
            enum_col ENUM('选项1', '选项2', '选项3'),
            set_col SET('选项A', '选项B', '选项C'),
            binary_col BINARY(10),
            varbinary_col VARBINARY(50)
        )
        """
        self.db_conn.execute_update(create_table_sql)
        
        # 插入各种数据类型的示例
        logger.info("插入各种数据类型的示例数据")
        insert_sql = """
        INSERT INTO data_types_demo (
            tinyint_col, smallint_col, int_col, bigint_col,
            float_col, double_col, decimal_col,
            char_col, varchar_col, text_col,
            date_col, datetime_col, time_col, year_col,
            enum_col, set_col, binary_col, varbinary_col
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """
        
        # 准备示例数据
        current_date = date.today()
        current_datetime = datetime.now()
        binary_data = b'\x01\x02\x03\x04\x05'
        
        data = (
            127, 32767, 2147483647, 9223372036854775807,
            3.14, 2.718281828, 12345.67,
            '固定长度', '可变长度字符串', '这是一段文本内容',
            current_date, current_datetime, '12:30:45', 2023,
            '选项2', '选项A,选项C', binary_data, binary_data
        )
        
        self.db_conn.execute_update(insert_sql, data)
        
        # 查询并显示数据
        logger.info("查询并显示数据类型演示表:")
        result = self.db_conn.execute_query("SELECT * FROM data_types_demo")
        if result:
            # 获取列名
            columns = [desc[0] for desc in self.db_conn.cursor.description]
            
            # 显示表头
            logger.info(" | ".join(columns))
            logger.info("-" * (len(" | ".join(columns))))
            
            # 显示数据
            for row in result:
                row_str = []
                for value in row:
                    if isinstance(value, bytes):
                        row_str.append(f"binary({len(value)})")
                    elif isinstance(value, datetime):
                        row_str.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                    elif isinstance(value, date):
                        row_str.append(value.strftime('%Y-%m-%d'))
                    else:
                        row_str.append(str(value) if value is not None else "NULL")
                logger.info(" | ".join(row_str))
    
    def table_operations_demo(self):
        """表操作演示"""
        logger.info("\n" + "="*50)
        logger.info("5. 表操作演示")
        logger.info("="*50)
        
        # 确保使用演示数据库
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # 创建学生表
        logger.info("创建学生表")
        create_students_sql = """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_number VARCHAR(20) NOT NULL UNIQUE,
            name VARCHAR(50) NOT NULL,
            gender ENUM('男', '女', '其他'),
            birth_date DATE,
            class_id INT,
            enrollment_date DATE DEFAULT (CURRENT_DATE),
            email VARCHAR(100),
            phone VARCHAR(20),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_name (name),
            INDEX idx_class_id (class_id)
        )
        """
        self.db_conn.execute_update(create_students_sql)
        
        # 创建班级表
        logger.info("创建班级表")
        create_classes_sql = """
        CREATE TABLE IF NOT EXISTS classes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            teacher VARCHAR(50),
            classroom VARCHAR(20),
            capacity INT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        self.db_conn.execute_update(create_classes_sql)
        
        # 创建课程表
        logger.info("创建课程表")
        create_courses_sql = """
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(20) NOT NULL UNIQUE,
            credit DECIMAL(3, 1) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        self.db_conn.execute_update(create_courses_sql)
        
        # 创建成绩表（多对多关系）
        logger.info("创建成绩表")
        create_scores_sql = """
        CREATE TABLE IF NOT EXISTS scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            score DECIMAL(5, 2) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            INDEX idx_student_course (student_id, course_id),
            INDEX idx_score (score),
            UNIQUE KEY uk_student_course_semester (student_id, course_id, semester)
        )
        """
        self.db_conn.execute_update(create_scores_sql)
        
        # 显示所有表
        logger.info("显示所有表:")
        result = self.db_conn.execute_query("SHOW TABLES")
        if result:
            for table in result:
                table_name = table[0]
                logger.info(f"  - {table_name}")
                
                # 显示表结构
                logger.info(f"    表结构 - {table_name}:")
                desc_result = self.db_conn.execute_query(f"DESCRIBE {table_name}")
                if desc_result:
                    for col in desc_result:
                        logger.info(f"      {col[0]} | {col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]}")
    
    def crud_operations_demo(self):
        """CRUD操作演示"""
        logger.info("\n" + "="*50)
        logger.info("6. CRUD操作演示")
        logger.info("="*50)
        
        # 确保使用演示数据库
        self.db_conn.execute_update(f"USE {self.demo_db}")
        
        # INSERT操作
        logger.info("INSERT操作 - 插入班级数据")
        classes_data = [
            ('一班', '王老师', 'A101', 40, '重点班'),
            ('二班', '李老师', 'A102', 35, '普通班'),
            ('三班', '张老师', 'A103', 38, '实验班')
        ]
        
        insert_classes_sql = "INSERT INTO classes (name, teacher, classroom, capacity, description) VALUES (%s, %s, %s, %s, %s)"
        self.db_conn.execute_many(insert_classes_sql, classes_data)
        
        # INSERT操作 - 插入课程数据
        logger.info("INSERT操作 - 插入课程数据")
        courses_data = [
            ('语文', 'CHN101', 5.0, '语文基础课程'),
            ('数学', 'MAT101', 5.0, '数学基础课程'),
            ('英语', 'ENG101', 4.0, '英语基础课程'),
            ('物理', 'PHY101', 4.0, '物理基础课程'),
            ('化学', 'CHE101', 4.0, '化学基础课程')
        ]
        
        insert_courses_sql = "INSERT INTO courses (name, code, credit, description) VALUES (%s, %s, %s, %s)"
        self.db_conn.execute_many(insert_courses_sql, courses_data)
        
        # INSERT操作 - 插入学生数据
        logger.info("INSERT操作 - 插入学生数据")
        students_data = [
            ('20230001', '张三', '男', '2005-05-15', 1, 'zhangsan@example.com', '13812345678', '北京市海淀区'),
            ('20230002', '李四', '女', '2005-08-20', 1, 'lisi@example.com', '13812345679', '北京市西城区'),
            ('20230003', '王五', '男', '2005-03-10', 2, 'wangwu@example.com', '13812345680', '北京市朝阳区'),
            ('20230004', '赵六', '女', '2005-12-25', 2, 'zhaoliu@example.com', '13812345681', '北京市丰台区'),
            ('20230005', '钱七', '男', '2005-07-08', 3, 'qianqi@example.com', '13812345682', '北京市石景山区')
        ]
        
        insert_students_sql = "INSERT INTO students (student_number, name, gender, birth_date, class_id, email, phone, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        self.db_conn.execute_many(insert_students_sql, students_data)
        
        # INSERT操作 - 插入成绩数据
        logger.info("INSERT操作 - 插入成绩数据")
        scores_data = []
        for student_id in range(1, 6):  # 学生ID 1-5
            for course_id in range(1, 6):  # 课程ID 1-5
                score = round(75 + (student_id * 3) % 25, 1)  # 生成75-100之间的分数
                scores_data.append((student_id, course_id, score, '2023春季'))
        
        insert_scores_sql = "INSERT INTO scores (student_id, course_id, score, semester) VALUES (%s, %s, %s, %s)"
        self.db_conn.execute_many(insert_scores_sql, scores_data)
        
        # SELECT操作 - 基本查询
        logger.info("SELECT操作 - 查询所有学生")
        result = self.db_conn.execute_query("SELECT * FROM students")
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # SELECT操作 - 条件查询
        logger.info("SELECT操作 - 条件查询（性别为男的学生）")
        result = self.db_conn.execute_query("SELECT id, name, gender, birth_date FROM students WHERE gender = '男'")
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # SELECT操作 - JOIN查询
        logger.info("SELECT操作 - JOIN查询（学生和班级信息）")
        join_sql = """
        SELECT s.id, s.name, s.gender, c.name as class_name, c.teacher
        FROM students s
        JOIN classes c ON s.class_id = c.id
        """
        result = self.db_conn.execute_query(join_sql)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # SELECT操作 - 复杂查询
        logger.info("SELECT操作 - 复杂查询（学生成绩统计）")
        complex_sql = """
        SELECT 
            s.id, s.name, c.name as class_name,
            COUNT(sc.course_id) as course_count,
            ROUND(AVG(sc.score), 2) as avg_score,
            MIN(sc.score) as min_score,
            MAX(sc.score) as max_score
        FROM students s
        JOIN classes c ON s.class_id = c.id
        JOIN scores sc ON s.id = sc.student_id
        GROUP BY s.id, s.name, c.name
        ORDER BY avg_score DESC
        """
        result = self.db_conn.execute_query(complex_sql)
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # UPDATE操作
        logger.info("UPDATE操作 - 更新学生信息")
        update_sql = "UPDATE students SET email = %s WHERE id = %s"
        affected_rows = self.db_conn.execute_update(update_sql, ('newemail@example.com', 1))
        logger.info(f"更新了 {affected_rows} 行数据")
        
        # 验证更新
        result = self.db_conn.execute_query("SELECT id, name, email FROM students WHERE id = 1")
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # DELETE操作
        logger.info("DELETE操作 - 删除成绩数据（删除学生ID为5的所有成绩）")
        delete_sql = "DELETE FROM scores WHERE student_id = %s"
        affected_rows = self.db_conn.execute_update(delete_sql, (5,))
        logger.info(f"删除了 {affected_rows} 行数据")
        
        # 验证删除
        result = self.db_conn.execute_query("SELECT COUNT(*) FROM scores WHERE student_id = 5")
        if result:
            logger.info(f"学生ID为5的成绩记录数: {result[0][0]}")
    
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

class BestPracticesDemo:
    """最佳实践演示"""
    
    def __init__(self, config=None):
        self.db_conn = MySQLConnection(config)
        self.demo_db = "mysql_demo"
    
    def run_demo(self):
        """运行最佳实践演示"""
        logger.info("\n" + "="*50)
        logger.info("7. 最佳实践演示")
        logger.info("="*50)
        
        if not self.db_conn.connect():
            logger.error("无法连接到MySQL服务器，停止演示")
            return
        
        try:
            # 确保使用演示数据库
            self.db_conn.execute_update(f"USE {self.demo_db}")
            
            # 1. 命名规范演示
            self.naming_convention_demo()
            
            # 2. 索引优化演示
            self.index_optimization_demo()
            
            # 3. 查询优化演示
            self.query_optimization_demo()
            
            # 4. 事务处理演示
            self.transaction_demo()
            
            logger.info("最佳实践演示完成")
            
        except Exception as e:
            logger.error(f"运行最佳实践演示时发生错误: {e}")
        finally:
            self.db_conn.disconnect()
    
    def naming_convention_demo(self):
        """命名规范演示"""
        logger.info("\n7.1 命名规范演示")
        logger.info("-" * 30)
        
        # 好的命名示例
        logger.info("好的命名示例:")
        good_examples = [
            "students",            # 表名：小写，复数形式
            "student_profiles",     # 表名：下划线分隔
            "first_name",           # 列名：小写，下划线分隔
            "created_at",           # 列名：时间戳格式
            "idx_students_name",    # 索引名：前缀+表名+列名
            "fk_students_class_id", # 外键名：前缀+表名+列名
            "uk_students_email"     # 唯一键名：前缀+表名+列名
        ]
        
        for name in good_examples:
            logger.info(f"  - {name}")
        
        # 不好的命名示例
        logger.info("\n不好的命名示例:")
        bad_examples = [
            "Students",             # 表名：大写开头
            "studentProfiles",      # 表名：驼峰命名
            "FirstName",            # 列名：大写开头
            "creationDate",         # 列名：驼峰命名
            "index1",               # 索引名：无意义
            "table1",               # 表名：无意义
            "col"                   # 列名：缩写不明确
        ]
        
        for name in bad_examples:
            logger.info(f"  - {name} (不建议)")
    
    def index_optimization_demo(self):
        """索引优化演示"""
        logger.info("\n7.2 索引优化演示")
        logger.info("-" * 30)
        
        # 创建测试表
        logger.info("创建测试表")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS index_demo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            age INT,
            department_id INT,
            salary DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_conn.execute_update(create_table_sql)
        
        # 插入测试数据
        logger.info("插入测试数据")
        insert_sql = "INSERT INTO index_demo (name, email, age, department_id, salary) VALUES (%s, %s, %s, %s, %s)"
        
        # 生成1000条测试数据
        import random
        departments = ['IT', 'HR', 'Finance', 'Marketing', 'Sales']
        first_names = ['张', '李', '王', '赵', '钱', '孙', '周', '吴', '郑', '冯']
        last_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '洋', '艳']
        
        test_data = []
        for i in range(1000):
            name = random.choice(first_names) + random.choice(last_names)
            email = f"user{i}@example.com"
            age = random.randint(22, 60)
            department_id = random.randint(1, 5)
            salary = round(random.uniform(3000, 20000), 2)
            
            test_data.append((name, email, age, department_id, salary))
        
        self.db_conn.execute_many(insert_sql, test_data)
        
        # 创建索引
        logger.info("创建索引")
        
        # 单列索引
        self.db_conn.execute_update("CREATE INDEX idx_name ON index_demo(name)")
        logger.info("创建单列索引: idx_name")
        
        # 复合索引
        self.db_conn.execute_update("CREATE INDEX idx_department_salary ON index_demo(department_id, salary)")
        logger.info("创建复合索引: idx_department_salary")
        
        # 唯一索引
        self.db_conn.execute_update("CREATE UNIQUE INDEX idx_email ON index_demo(email)")
        logger.info("创建唯一索引: idx_email")
        
        # 显示索引信息
        logger.info("显示索引信息")
        result = self.db_conn.execute_query("SHOW INDEX FROM index_demo")
        if result:
            logger.info("表索引信息:")
            for row in result:
                logger.info(f"  - 索引名: {row[2]}, 列名: {row[4]}, 唯一性: {'是' if row[1] == 0 else '否'}")
        
        # 使用EXPLAIN分析查询
        logger.info("\n使用EXPLAIN分析查询")
        
        # 不使用索引的查询
        logger.info("不使用索引的查询:")
        explain_sql = "EXPLAIN SELECT * FROM index_demo WHERE name LIKE '%张%'"
        result = self.db_conn.execute_query(explain_sql)
        if result:
            for row in result:
                logger.info(f"  - 类型: {row[3]}, 可能的键: {row[4]}, 使用的键: {row[5]}, 扫描行数: {row[8]}")
        
        # 使用索引的查询
        logger.info("\n使用索引的查询:")
        explain_sql = "EXPLAIN SELECT * FROM index_demo WHERE name = '张伟'"
        result = self.db_conn.execute_query(explain_sql)
        if result:
            for row in result:
                logger.info(f"  - 类型: {row[3]}, 可能的键: {row[4]}, 使用的键: {row[5]}, 扫描行数: {row[8]}")
        
        # 使用复合索引的查询
        logger.info("\n使用复合索引的查询:")
        explain_sql = "EXPLAIN SELECT * FROM index_demo WHERE department_id = 3 AND salary > 10000"
        result = self.db_conn.execute_query(explain_sql)
        if result:
            for row in result:
                logger.info(f"  - 类型: {row[3]}, 可能的键: {row[4]}, 使用的键: {row[5]}, 扫描行数: {row[8]}")
    
    def query_optimization_demo(self):
        """查询优化演示"""
        logger.info("\n7.3 查询优化演示")
        logger.info("-" * 30)
        
        # 避免SELECT *
        logger.info("避免使用SELECT *")
        
        # 不好的查询
        logger.info("不好的查询:")
        bad_query = "SELECT * FROM students"
        logger.info(f"  {bad_query}")
        
        # 好的查询
        logger.info("好的查询:")
        good_query = "SELECT id, name, email FROM students"
        logger.info(f"  {good_query}")
        
        # 使用LIMIT限制结果集
        logger.info("\n使用LIMIT限制结果集")
        
        # 不好的查询
        logger.info("不好的查询:")
        bad_query = "SELECT * FROM students"
        logger.info(f"  {bad_query}")
        
        # 好的查询
        logger.info("好的查询:")
        good_query = "SELECT id, name, email FROM students LIMIT 10"
        logger.info(f"  {good_query}")
        
        # 使用JOIN代替子查询
        logger.info("\n使用JOIN代替子查询")
        
        # 不好的查询（使用子查询）
        logger.info("不好的查询（使用子查询）:")
        bad_query = """
        SELECT s.name, c.name as class_name
        FROM students s
        WHERE s.class_id IN (SELECT id FROM classes WHERE teacher = '王老师')
        """
        logger.info(f"  {bad_query}")
        
        # 好的查询（使用JOIN）
        logger.info("好的查询（使用JOIN）:")
        good_query = """
        SELECT s.name, c.name as class_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE c.teacher = '王老师'
        """
        logger.info(f"  {good_query}")
        
        # 使用索引列进行条件过滤
        logger.info("\n使用索引列进行条件过滤")
        
        # 不好的查询（在未索引的列上使用函数）
        logger.info("不好的查询（在未索引的列上使用函数）:")
        bad_query = "SELECT * FROM students WHERE YEAR(birth_date) = 2005"
        logger.info(f"  {bad_query}")
        
        # 好的查询（使用范围查询）
        logger.info("好的查询（使用范围查询）:")
        good_query = "SELECT * FROM students WHERE birth_date >= '2005-01-01' AND birth_date <= '2005-12-31'"
        logger.info(f"  {good_query}")
    
    def transaction_demo(self):
        """事务处理演示"""
        logger.info("\n7.4 事务处理演示")
        logger.info("-" * 30)
        
        # 创建测试表
        logger.info("创建测试表")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            balance DECIMAL(10, 2) NOT NULL DEFAULT 0
        )
        """
        self.db_conn.execute_update(create_table_sql)
        
        # 清空表
        self.db_conn.execute_update("DELETE FROM accounts")
        
        # 插入测试数据
        logger.info("插入测试数据")
        self.db_conn.execute_update("INSERT INTO accounts (name, balance) VALUES ('张三', 1000)")
        self.db_conn.execute_update("INSERT INTO accounts (name, balance) VALUES ('李四', 2000)")
        
        # 查询初始余额
        logger.info("查询初始余额")
        result = self.db_conn.execute_query("SELECT * FROM accounts")
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 关闭自动提交
        self.db_conn.connection.autocommit = False
        
        try:
            # 开始事务
            logger.info("开始事务")
            
            # 张三转账100元给李四
            logger.info("张三转账100元给李四")
            self.db_conn.execute_update("UPDATE accounts SET balance = balance - 100 WHERE name = '张三'")
            self.db_conn.execute_update("UPDATE accounts SET balance = balance + 100 WHERE name = '李四'")
            
            # 查询转账后余额
            logger.info("查询转账后余额")
            result = self.db_conn.execute_query("SELECT * FROM accounts")
            self.display_query_result(result, self.db_conn.cursor.description)
            
            # 提交事务
            logger.info("提交事务")
            self.db_conn.connection.commit()
            
        except Exception as e:
            logger.error(f"事务执行出错: {e}")
            logger.info("回滚事务")
            self.db_conn.connection.rollback()
        
        finally:
            # 恢复自动提交
            self.db_conn.connection.autocommit = True
        
        # 查询最终余额
        logger.info("查询最终余额")
        result = self.db_conn.execute_query("SELECT * FROM accounts")
        self.display_query_result(result, self.db_conn.cursor.description)
        
        # 演示事务回滚
        logger.info("\n演示事务回滚")
        
        # 关闭自动提交
        self.db_conn.connection.autocommit = False
        
        try:
            # 开始事务
            logger.info("开始事务")
            
            # 张三转账1000元给李四（会失败，因为张三余额不足）
            logger.info("张三转账1000元给李四（会失败，因为张三余额不足）")
            self.db_conn.execute_update("UPDATE accounts SET balance = balance - 1000 WHERE name = '张三'")
            
            # 检查余额是否足够
            result = self.db_conn.execute_query("SELECT balance FROM accounts WHERE name = '张三'")
            if result and result[0][0] < 0:
                raise ValueError("余额不足")
            
            self.db_conn.execute_update("UPDATE accounts SET balance = balance + 1000 WHERE name = '李四'")
            
            # 提交事务
            logger.info("提交事务")
            self.db_conn.connection.commit()
            
        except Exception as e:
            logger.error(f"事务执行出错: {e}")
            logger.info("回滚事务")
            self.db_conn.connection.rollback()
        
        finally:
            # 恢复自动提交
            self.db_conn.connection.autocommit = True
        
        # 查询最终余额
        logger.info("查询最终余额")
        result = self.db_conn.execute_query("SELECT * FROM accounts")
        self.display_query_result(result, self.db_conn.cursor.description)
    
    def display_query_result(self, result, description):
        """显示查询结果"""
        if not result:
            logger.info("无结果")
            return
        
        # 获取列名
        columns = [desc[0] for desc in description]
        
        # 显示表头
        header = " | ".join(columns)
        logger.info(header)
        logger.info("-" * len(header))
        
        # 显示数据
        for row in result:
            row_str = []
            for value in row:
                value_str = str(value) if value is not None else "NULL"
                if isinstance(value, datetime):
                    value_str = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    value_str = value.strftime('%Y-%m-%d')
                row_str.append(value_str)
            logger.info(" | ".join(row_str))

def main():
    """主函数"""
    logger.info("MySQL第1章：入门与基础概念")
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
        # 运行基础操作演示
        basics_demo = MySQLBasicsDemo()
        basics_demo.run_all_demos()
        
        # 运行最佳实践演示
        best_practices_demo = BestPracticesDemo()
        best_practices_demo.run_demo()
        
        logger.info("所有演示运行完成")
        
    except Exception as e:
        logger.error(f"运行演示时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()