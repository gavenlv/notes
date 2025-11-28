#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL教程第8章：函数和存储过程Python示例

这个脚本演示了如何在Python中使用psycopg2库调用PostgreSQL的函数和存储过程，
包括基础函数调用、存储过程执行、触发器管理等内容。

运行前请确保：
1. 安装必要的依赖: pip install -r requirements.txt
2. 配置正确的数据库连接参数
3. 确保PostgreSQL服务器正在运行
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('function_examples.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostgreSQLFunctionExecutor:
    """PostgreSQL函数和存储过程执行器"""
    
    def __init__(self, host='localhost', database='postgres', user='postgres', password='password', port=5432):
        """初始化数据库连接"""
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开数据库连接"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            logger.info("数据库连接已断开")
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
    
    def execute_function(self, function_name: str, params: List[Any] = None, return_type: str = None) -> Any:
        """执行PostgreSQL函数"""
        try:
            if params is None:
                params = []
            
            # 构建函数调用SQL
            if return_type:
                query = f"SELECT * FROM {function_name}(%s)"
                if len(params) > 1:
                    query = f"SELECT * FROM {function_name}({', '.join(['%s'] * len(params))})"
            else:
                query = f"SELECT {function_name}(%s)"
                if len(params) > 1:
                    query = f"SELECT {function_name}({', '.join(['%s'] * len(params))})"
            
            self.cursor.execute(query, params)
            
            if return_type:
                result = self.cursor.fetchall()
                return result
            else:
                result = self.cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"执行函数 {function_name} 失败: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            raise
    
    def execute_procedure(self, procedure_name: str, params: List[Any] = None, return_result: bool = True) -> Any:
        """执行PostgreSQL存储过程"""
        try:
            if params is None:
                params = []
            
            # 构建存储过程调用SQL
            if params:
                placeholders = ', '.join(['%s'] * len(params))
                query = f"CALL {procedure_name}({placeholders})"
            else:
                query = f"CALL {procedure_name}()"
            
            self.cursor.execute(query, params)
            
            if return_result:
                # 存储过程通常通过OUT参数返回结果
                # 这里需要根据具体的存储过程来调整
                result = self.cursor.fetchall() if self.cursor.description else None
                return result
            else:
                self.conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"执行存储过程 {procedure_name} 失败: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            raise
    
    def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        try:
            self.cursor.execute(query, params)
            if self.cursor.description:
                columns = [desc[0] for desc in self.cursor.description]
                results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
                return results
            else:
                self.conn.commit()
                return []
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            raise
    
    def batch_execute(self, queries: List[tuple]) -> bool:
        """批量执行SQL语句"""
        try:
            self.cursor.executemany("", queries)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"批量执行失败: {e}")
            self.conn.rollback()
            return False

class FunctionExamples:
    """函数和存储过程示例"""
    
    def __init__(self, executor: PostgreSQLFunctionExecutor):
        self.executor = executor
    
    def demo_basic_functions(self):
        """演示基础函数调用"""
        logger.info("=== 基础函数示例 ===")
        
        try:
            # 1. 调用无参数函数
            employee_count = self.executor.execute_function("get_employee_count")
            logger.info(f"员工总数: {employee_count}")
            
            # 2. 调用带参数函数
            bonus = self.executor.execute_function("calculate_bonus", [12000.00, 0.05])
            logger.info(f"奖金计算结果: {bonus}")
            
            # 3. 调用返回记录的函数
            emp_details = self.executor.execute_function("get_employee_details", [1])
            if emp_details:
                for detail in emp_details:
                    logger.info(f"员工详情: {detail}")
            
            # 4. 调用返回集合的函数
            high_salary_emps = self.executor.execute_function("get_high_salary_employees", [10000.00])
            if high_salary_emps:
                for emp in high_salary_emps:
                    logger.info(f"高薪员工: {emp}")
            
            # 5. 测试多态函数
            max_int = self.executor.execute_function("get_max_value", [10, 20])
            logger.info(f"最大值(整数): {max_int}")
            
            max_string = self.executor.execute_function("get_max_value", ["apple", "banana"])
            logger.info(f"最大值(字符串): {max_string}")
            
        except Exception as e:
            logger.error(f"基础函数演示失败: {e}")
    
    def demo_stored_procedures(self):
        """演示存储过程调用"""
        logger.info("=== 存储过程示例 ===")
        
        try:
            # 1. 调用初始化数据库存储过程
            self.executor.execute_procedure("initialize_database")
            logger.info("数据库初始化完成")
            
            # 2. 调用添加员工存储过程
            self.executor.execute_procedure("add_employee", [
                "Python", "Developer", "python.dev@company.com", "SE", 
                13500.00, 1, 1001
            ])
            logger.info("新员工添加完成")
            
            # 3. 调用带输出参数的存储过程
            result = self.executor.execute_procedure("calculate_employee_stats", [1])
            logger.info(f"员工统计结果: {result}")
            
            # 4. 调用员工转部门存储过程
            self.executor.execute_procedure("transfer_employee", [2, 1, 1001, 500.00])
            logger.info("员工转部门完成")
            
            # 5. 调用批量薪资调整存储过程
            result = self.executor.execute_procedure("bulk_salary_adjustment", [2, 5.0])
            logger.info(f"批量薪资调整结果: {result}")
            
            # 6. 调用绩效评估存储过程
            result = self.executor.execute_procedure("process_performance_review", [1, 4, "Excellent performance"])
            logger.info(f"绩效评估结果: {result}")
            
        except Exception as e:
            logger.error(f"存储过程演示失败: {e}")
    
    def demo_transaction_procedures(self):
        """演示事务性存储过程"""
        logger.info("=== 事务性存储过程示例 ===")
        
        try:
            # 调用复杂的事务存储过程
            self.executor.execute_procedure("complete_employee_transfer", [
                3, 1, 2, 1002, 1000.00
            ])
            logger.info("完整员工转移完成")
            
            # 调用订单处理存储过程
            order_items = json.dumps([
                {"product_id": 1, "quantity": 1},
                {"product_id": 2, "quantity": 2}
            ])
            
            result = self.executor.execute_procedure("process_order", [1, order_items])
            logger.info(f"订单处理结果: {result}")
            
        except Exception as e:
            logger.error(f"事务性存储过程演示失败: {e}")
    
    def demo_advanced_functions(self):
        """演示高级函数特性"""
        logger.info("=== 高级函数示例 ===")
        
        try:
            # 1. 测试数组处理函数
            average = self.executor.execute_function("calculate_average_multiple", [[10, 20, 30, 40, 50]])
            logger.info(f"数组平均值: {average}")
            
            # 2. 测试变长参数函数
            message = self.executor.execute_function("format_message", [
                "INFO", "System started", "Version 1.0", "Environment: Production"
            ])
            logger.info(f"格式化消息: {message}")
            
            # 3. 测试验证函数
            email_valid = self.executor.execute_function("is_valid_email", ["user@example.com"])
            logger.info(f"邮箱验证结果: {email_valid}")
            
            # 4. 测试数据清理函数
            clean_name = self.executor.execute_function("clean_product_name", ["  laptop pro  "])
            logger.info(f"清理后的产品名: {clean_name}")
            
            # 5. 测试安全除法函数
            division_result = self.executor.execute_function("safe_divide", [10, 3])
            logger.info(f"安全除法结果: {division_result}")
            
        except Exception as e:
            logger.error(f"高级函数演示失败: {e}")
    
    def demo_business_logic_functions(self):
        """演示业务逻辑函数"""
        logger.info("=== 业务逻辑函数示例 ===")
        
        try:
            # 1. 库存管理函数
            stock_result = self.executor.execute_function("update_stock", [1, 5, "Stock replenishment"])
            logger.info(f"库存更新结果: {stock_result}")
            
            # 2. 销售分析函数
            performance_result = self.executor.execute_function("get_product_performance", [
                date(2024, 1, 1), date(2024, 1, 31), 1000.00
            ])
            if performance_result:
                for perf in performance_result:
                    logger.info(f"产品业绩: {perf}")
            
            # 3. 价格计算函数
            price_result = self.executor.execute_function("calculate_final_price", [
                1, 2, 10.0, 0.13, True, 1
            ])
            if price_result:
                for price in price_result:
                    logger.info(f"价格计算结果: {price}")
            
            # 4. 排名函数
            rankings = self.executor.execute_function("get_product_rankings", ["Electronics"])
            if rankings:
                for rank in rankings:
                    logger.info(f"产品排名: {rank}")
            
        except Exception as e:
            logger.error(f"业务逻辑函数演示失败: {e}")
    
    def demo_trigger_operations(self):
        """演示触发器相关操作"""
        logger.info("=== 触发器操作示例 ===")
        
        try:
            # 1. 查看触发器列表
            triggers = self.executor.execute_query("SELECT * FROM list_triggers()")
            logger.info("触发器列表:")
            for trigger in triggers:
                logger.info(f"  - {trigger}")
            
            # 2. 插入测试数据（会触发触发器）
            logger.info("插入测试数据...")
            self.executor.execute_query("""
                INSERT INTO employees (first_name, last_name, email, phone, job_id, salary, department_id) 
                VALUES ('Test', 'User2', 'test.user2@company.com', '13900139001', 'TW', 8000.00, 2)
            """)
            
            # 3. 更新测试数据（会触发触发器）
            logger.info("更新测试数据...")
            self.executor.execute_query("""
                UPDATE employees 
                SET salary = 9000.00 
                WHERE email = 'test.user2@company.com'
            """)
            
            # 4. 查看审计日志
            audit_logs = self.executor.execute_query("""
                SELECT * FROM audit_log 
                ORDER BY changed_at DESC 
                LIMIT 10
            """)
            logger.info("最近的审计日志:")
            for log in audit_logs:
                logger.info(f"  - {log}")
            
            # 5. 查看薪资变更历史
            salary_history = self.executor.execute_query("""
                SELECT * FROM employee_history 
                WHERE change_type = 'SALARY_CHANGE'
                ORDER BY changed_at DESC 
                LIMIT 5
            """)
            logger.info("薪资变更历史:")
            for history in salary_history:
                logger.info(f"  - {history}")
            
        except Exception as e:
            logger.error(f"触发器操作演示失败: {e}")
    
    def demo_performance_monitoring(self):
        """演示性能监控功能"""
        logger.info("=== 性能监控示例 ===")
        
        try:
            # 1. 检查数据库健康状态
            self.executor.execute_procedure("check_database_health")
            
            # 2. 生成部门报告
            dept_report = self.executor.execute_procedure("generate_department_report", [1])
            logger.info(f"部门报告: {dept_report}")
            
            # 3. 清理旧日志
            cleanup_result = self.executor.execute_procedure("cleanup_old_audit_logs", [30])
            logger.info(f"清理结果: {cleanup_result}")
            
            # 4. 数据库维护
            self.executor.execute_procedure("database_maintenance")
            
        except Exception as e:
            logger.error(f"性能监控演示失败: {e}")
    
    def demo_error_handling(self):
        """演示错误处理"""
        logger.info("=== 错误处理示例 ===")
        
        try:
            # 1. 测试无效操作（会触发业务规则）
            try:
                self.executor.execute_function("safe_divide", [10, 0])
            except Exception as e:
                logger.info(f"预期的错误被正确捕获: {e}")
            
            # 2. 测试薪资限制（会触发触发器）
            try:
                self.executor.execute_query("""
                    UPDATE employees 
                    SET salary = 50000.00 
                    WHERE email = 'john.smith@company.com'
                """)
            except Exception as e:
                logger.info(f"薪资限制被正确触发: {e}")
            
            # 3. 测试数据验证
            validation_result = self.executor.execute_function("validate_product_data", [
                "", -100, -5  # 无效的产品名称、负价格、负库存
            ])
            logger.info(f"数据验证结果: {validation_result}")
            
        except Exception as e:
            logger.error(f"错误处理演示失败: {e}")
    
    def run_all_demos(self):
        """运行所有示例"""
        logger.info("开始运行PostgreSQL函数和存储过程示例...")
        
        try:
            self.demo_basic_functions()
            self.demo_stored_procedures()
            self.demo_transaction_procedures()
            self.demo_advanced_functions()
            self.demo_business_logic_functions()
            self.demo_trigger_operations()
            self.demo_performance_monitoring()
            self.demo_error_handling()
            
            logger.info("所有示例运行完成!")
            
        except Exception as e:
            logger.error(f"示例运行失败: {e}")
            raise

def main():
    """主函数"""
    # 数据库连接配置
    db_config = {
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'password',
        'port': 5432
    }
    
    logger.info("PostgreSQL函数和存储过程Python示例")
    logger.info("=" * 50)
    
    # 创建数据库执行器
    executor = PostgreSQLFunctionExecutor(**db_config)
    
    try:
        # 连接数据库
        executor.connect()
        
        # 创建示例实例并运行
        examples = FunctionExamples(executor)
        examples.run_all_demos()
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        logger.error(f"错误详情: {traceback.format_exc()}")
    
    finally:
        # 断开连接
        executor.disconnect()

if __name__ == "__main__":
    main()

# 额外的辅助函数
def test_connection():
    """测试数据库连接"""
    try:
        executor = PostgreSQLFunctionExecutor()
        executor.connect()
        
        # 测试基本查询
        result = executor.execute_query("SELECT version()")
        logger.info(f"数据库版本: {result[0]['version']}")
        
        executor.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"连接测试失败: {e}")
        return False

def create_test_data():
    """创建测试数据"""
    try:
        executor = PostgreSQLFunctionExecutor()
        executor.connect()
        
        # 执行setup脚本创建表和数据
        setup_queries = [
            """
            CREATE TABLE IF NOT EXISTS test_products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(200),
                price DECIMAL(10,2),
                stock_quantity INTEGER
            )
            """,
            """
            INSERT INTO test_products (product_name, price, stock_quantity) 
            VALUES 
                ('Laptop', 2999.99, 50),
                ('Mouse', 199.99, 200),
                ('Keyboard', 299.99, 150)
            ON CONFLICT DO NOTHING
            """
        ]
        
        for query in setup_queries:
            executor.execute_query(query)
        
        logger.info("测试数据创建完成")
        executor.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"创建测试数据失败: {e}")
        return False

# 使用示例
if __name__ == "__main__":
    print("请运行以下命令来使用这个脚本:")
    print("1. 测试连接: python -c 'from function_examples import test_connection; test_connection()'")
    print("2. 创建测试数据: python -c 'from function_examples import create_test_data; create_test_data()'")
    print("3. 运行完整示例: python function_examples.py")
