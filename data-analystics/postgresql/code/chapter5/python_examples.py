"""
第5章：高级查询技术 - Python示例
展示如何在Python中使用psycopg2执行高级SQL查询
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'testdb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432')
}

def create_connection():
    """创建数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def setup_sample_data(conn):
    """设置示例数据"""
    cursor = conn.cursor()
    
    # 创建示例表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department_id INTEGER REFERENCES departments(id),
            salary DECIMAL(10,2),
            hire_date DATE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department_id INTEGER REFERENCES departments(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_projects (
            employee_id INTEGER REFERENCES employees(id),
            project_id INTEGER REFERENCES projects(id),
            hours_worked INTEGER,
            PRIMARY KEY (employee_id, project_id)
        )
    """)
    
    # 插入示例数据
    cursor.execute("TRUNCATE TABLE employee_projects, projects, employees, departments RESTART IDENTITY CASCADE")
    
    departments = [('Engineering',), ('Marketing',), ('Sales',), ('HR',)]
    cursor.executemany("INSERT INTO departments (name) VALUES (%s)", departments)
    
    employees = [
        ('John Doe', 1, 75000, '2020-01-15'),
        ('Jane Smith', 1, 80000, '2019-03-20'),
        ('Bob Johnson', 2, 65000, '2021-05-10'),
        ('Alice Brown', 1, 85000, '2018-07-01'),
        ('Charlie Wilson', 3, 70000, '2020-11-28'),
        ('Diana Prince', 2, 68000, '2019-09-15')
    ]
    cursor.executemany("INSERT INTO employees (name, department_id, salary, hire_date) VALUES (%s, %s, %s, %s)", employees)
    
    projects = [
        ('Project Alpha', 1),
        ('Project Beta', 1),
        ('Project Gamma', 2),
        ('Project Delta', 3)
    ]
    cursor.executemany("INSERT INTO projects (name, department_id) VALUES (%s, %s)", projects)
    
    employee_projects = [
        (1, 1, 120),
        (1, 2, 80),
        (2, 1, 100),
        (3, 3, 90),
        (4, 1, 150),
        (5, 4, 110)
    ]
    cursor.executemany("INSERT INTO employee_projects (employee_id, project_id, hours_worked) VALUES (%s, %s, %s)", employee_projects)
    
    conn.commit()
    cursor.close()

def demonstrate_joins(conn):
    """演示连接查询"""
    cursor = conn.cursor()
    
    print("=== 连接查询示例 ===")
    
    # 内连接：查询员工及其部门信息
    cursor.execute("""
        SELECT 
            e.name AS employee_name,
            e.salary,
            d.name AS department_name
        FROM employees e
        INNER JOIN departments d ON e.department_id = d.id
    """)
    
    print("内连接 - 员工及其部门信息:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - ${row[1]} - {row[2]}")
    
    # 左连接：查询所有员工及其部门信息（包括未分配部门的员工）
    cursor.execute("""
        SELECT 
            e.name AS employee_name,
            e.salary,
            d.name AS department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
    """)
    
    print("\n左连接 - 所有员工及其部门信息:")
    for row in cursor.fetchall():
        dept = row[2] if row[2] else "未分配部门"
        print(f"  {row[0]} - ${row[1]} - {dept}")
    
    cursor.close()

def demonstrate_subqueries(conn):
    """演示子查询"""
    cursor = conn.cursor()
    
    print("\n=== 子查询示例 ===")
    
    # 非关联子查询：查询薪资高于平均薪资的员工
    cursor.execute("""
        SELECT name, salary
        FROM employees
        WHERE salary > (SELECT AVG(salary) FROM employees)
    """)
    
    print("薪资高于平均薪资的员工:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - ${row[1]}")
    
    # 关联子查询：查询每个部门薪资最高的员工
    cursor.execute("""
        SELECT 
            e1.name,
            e1.salary,
            d.name AS department_name
        FROM employees e1
        INNER JOIN departments d ON e1.department_id = d.id
        WHERE e1.salary = (
            SELECT MAX(e2.salary)
            FROM employees e2
            WHERE e2.department_id = e1.department_id
        )
    """)
    
    print("\n每个部门薪资最高的员工:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - ${row[1]} - {row[2]}")
    
    cursor.close()

def demonstrate_set_operations(conn):
    """演示集合操作"""
    cursor = conn.cursor()
    
    print("\n=== 集合操作示例 ===")
    
    # UNION：查询高薪员工和项目负责人的并集
    cursor.execute("""
        (SELECT name, 'High Earner' AS category
         FROM employees
         WHERE salary > 75000)
        UNION
        (SELECT e.name, 'Project Lead' AS category
         FROM employees e
         JOIN employee_projects ep ON e.id = ep.employee_id
         WHERE ep.hours_worked > 100)
        ORDER BY name
    """)
    
    print("高薪员工和项目负责人的并集:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}")
    
    cursor.close()

def demonstrate_window_functions(conn):
    """演示窗口函数"""
    cursor = conn.cursor()
    
    print("\n=== 窗口函数示例 ===")
    
    # 使用窗口函数查询每个部门薪资排名前三的员工
    cursor.execute("""
        SELECT 
            name,
            department_name,
            salary,
            salary_rank
        FROM (
            SELECT 
                e.name,
                d.name AS department_name,
                e.salary,
                ROW_NUMBER() OVER (PARTITION BY d.id ORDER BY e.salary DESC) AS salary_rank
            FROM employees e
            JOIN departments d ON e.department_id = d.id
        ) ranked_employees
        WHERE salary_rank <= 3
        ORDER BY department_name, salary_rank
    """)
    
    print("每个部门薪资排名前三的员工:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]} - ${row[2]} (排名第{row[3]})")
    
    cursor.close()

def main():
    """主函数"""
    conn = create_connection()
    if not conn:
        return
    
    try:
        # 设置示例数据
        setup_sample_data(conn)
        
        # 演示各种高级查询技术
        demonstrate_joins(conn)
        demonstrate_subqueries(conn)
        demonstrate_set_operations(conn)
        demonstrate_window_functions(conn)
        
    except Exception as e:
        print(f"执行查询时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()