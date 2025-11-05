"""
Airflow 数据库性能优化示例代码
展示如何优化 Airflow 的数据库查询和连接
"""

import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from airflow.models import DagRun, TaskInstance
from airflow.utils.state import State
from sqlalchemy.orm import sessionmaker


# 数据库连接优化示例
def optimized_db_connection_example():
    """
    展示如何优化 Airflow 数据库连接配置
    包括连接池设置、查询优化等
    """
    
    # 获取 Airflow 数据库连接
    connection = BaseHook.get_connection('airflow_db')
    
    # 创建带优化参数的 SQLAlchemy 引擎
    engine = create_engine(
        connection.get_uri(),
        # 连接池配置优化
        poolclass=QueuePool,
        pool_size=20,           # 连接池大小
        max_overflow=30,        # 超出 pool_size 后最多可创建的连接数
        pool_recycle=3600,      # 连接回收时间（秒）
        pool_pre_ping=True,     # 连接前检查有效性
        pool_timeout=30,        # 获取连接超时时间
        echo=False              # 是否输出 SQL 日志
    )
    
    # 创建会话工厂
    Session = sessionmaker(bind=engine)
    
    return engine, Session


# 查询优化示例
def optimized_queries_example(**context):
    """
    展示如何优化 Airflow 中的数据库查询
    包括批量查询、索引使用、避免 N+1 查询等问题
    """
    # 获取数据库会话
    engine, Session = optimized_db_connection_example()
    session = Session()
    
    try:
        # 1. 批量查询优化 - 使用 in_() 而不是多次单独查询
        dag_ids = ['dag_1', 'dag_2', 'dag_3', 'dag_4', 'dag_5']
        
        start_time = time.time()
        # 优化方式：一次查询获取所有数据
        dag_runs = session.query(DagRun).filter(
            DagRun.dag_id.in_(dag_ids),
            DagRun.execution_date >= datetime.now() - timedelta(days=7)
        ).all()
        
        batch_query_time = time.time() - start_time
        print(f"批量查询耗时: {batch_query_time:.4f} 秒")
        print(f"查询到 {len(dag_runs)} 条 DagRun 记录")
        
        # 2. 索引优化示例 - 确保查询字段有适当索引
        # DagRun 表上的常用查询字段通常已有索引：
        # - dag_id
        # - execution_date
        # - state
        
        # 3. 避免 N+1 查询问题 - 使用 join 或 eager loading
        start_time = time.time()
        # 不好的做法（N+1 查询）：
        # for dag_run in dag_runs:
        #     tasks = dag_run.task_instances  # 每次都会触发新的查询
        
        # 优化做法：使用 join 一次性获取所有相关数据
        task_instances = session.query(TaskInstance).join(DagRun).filter(
            DagRun.dag_id.in_(dag_ids),
            DagRun.execution_date >= datetime.now() - timedelta(days=7)
        ).all()
        
        join_query_time = time.time() - start_time
        print(f"JOIN 查询耗时: {join_query_time:.4f} 秒")
        print(f"查询到 {len(task_instances)} 条 TaskInstance 记录")
        
        # 4. 分页查询优化 - 处理大量数据时使用分页
        page_size = 1000
        offset = 0
        total_processed = 0
        
        while True:
            paginated_runs = session.query(DagRun).filter(
                DagRun.state == State.SUCCESS
            ).order_by(
                DagRun.execution_date.desc()
            ).offset(offset).limit(page_size).all()
            
            if not paginated_runs:
                break
                
            # 处理当前页数据
            processed_count = len(paginated_runs)
            total_processed += processed_count
            print(f"处理第 {offset//page_size + 1} 页，包含 {processed_count} 条记录")
            
            offset += page_size
            
            # 避免无限循环
            if offset > 10000:  # 限制最多处理 10000 条记录
                break
        
        print(f"总共处理了 {total_processed} 条 DagRun 记录")
        
        # 5. 统计查询优化 - 使用数据库聚合函数而不是应用层计算
        start_time = time.time()
        # 优化方式：在数据库层面进行聚合计算
        stats = session.query(
            DagRun.dag_id,
            DagRun.state,
            DagRun.execution_date
        ).filter(
            DagRun.execution_date >= datetime.now() - timedelta(days=30)
        ).order_by(DagRun.execution_date.desc()).limit(100).all()
        
        db_aggregation_time = time.time() - start_time
        print(f"数据库聚合查询耗时: {db_aggregation_time:.4f} 秒")
        print(f"获取到 {len(stats)} 条统计记录")
        
        return {
            'batch_query_time': batch_query_time,
            'join_query_time': join_query_time,
            'total_processed': total_processed,
            'stats_count': len(stats)
        }
        
    except Exception as e:
        print(f"查询优化示例出错: {str(e)}")
        raise
    finally:
        session.close()


# 连接池监控示例
def monitor_connection_pool(**context):
    """
    监控数据库连接池状态
    帮助识别连接池配置是否合理
    """
    engine, _ = optimized_db_connection_example()
    
    if hasattr(engine.pool, 'size'):
        print(f"连接池当前大小: {engine.pool.size()}")
    
    if hasattr(engine.pool, 'checkedout'):
        print(f"已检出连接数: {engine.pool.checkedout()}")
        
    if hasattr(engine.pool, 'overflow'):
        print(f"溢出连接数: {engine.pool.overflow()}")
    
    # 检查连接池健康状态
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"连接池健康检查: {'成功' if result.fetchone()[0] == 1 else '失败'}")
    except Exception as e:
        print(f"连接池健康检查失败: {str(e)}")


# 数据清理优化示例
def optimized_data_cleanup(**context):
    """
    优化的数据清理策略
    避免一次性删除大量数据导致的性能问题
    """
    engine, Session = optimized_db_connection_example()
    session = Session()
    
    try:
        # 分批删除过期数据，避免长时间锁定表
        batch_size = 1000
        total_deleted = 0
        cutoff_date = datetime.now() - timedelta(days=90)  # 保留90天内的数据
        
        while True:
            # 使用 LIMIT 分批删除
            deleted_count = session.execute(
                text("""
                    DELETE FROM task_instance 
                    WHERE execution_date < :cutoff_date 
                    ORDER BY execution_date 
                    LIMIT :batch_size
                """),
                {
                    'cutoff_date': cutoff_date,
                    'batch_size': batch_size
                }
            ).rowcount
            
            session.commit()
            
            if deleted_count == 0:
                break
                
            total_deleted += deleted_count
            print(f"已删除 {deleted_count} 条过期的 task_instance 记录")
            
            # 添加短暂延迟，避免过度占用数据库资源
            time.sleep(0.1)
        
        print(f"数据清理完成，总共删除 {total_deleted} 条记录")
        
    except Exception as e:
        session.rollback()
        print(f"数据清理过程中出错: {str(e)}")
        raise
    finally:
        session.close()


# 创建 DAG 来演示数据库优化
def create_db_optimization_dag():
    default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2024, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }

    dag = DAG(
        'db_optimization_demo',
        default_args=default_args,
        description='Airflow 数据库性能优化演示',
        schedule_interval=timedelta(days=1),
        catchup=False,
        max_active_runs=1,
    )

    # 查询优化任务
    query_optimization_task = PythonOperator(
        task_id='query_optimization',
        python_callable=optimized_queries_example,
        dag=dag,
    )

    # 连接池监控任务
    pool_monitor_task = PythonOperator(
        task_id='connection_pool_monitor',
        python_callable=monitor_connection_pool,
        dag=dag,
    )

    # 数据清理任务
    cleanup_task = PythonOperator(
        task_id='data_cleanup',
        python_callable=optimized_data_cleanup,
        dag=dag,
    )

    # 设置任务依赖
    query_optimization_task >> pool_monitor_task >> cleanup_task

    return dag


# 性能基准测试函数
def performance_benchmark():
    """
    性能基准测试
    比较优化前后的查询性能
    """
    print("开始数据库性能基准测试...")
    
    # 测试优化后的查询
    start_time = time.time()
    result = optimized_queries_example()
    optimized_time = time.time() - start_time
    
    print(f"优化后查询总耗时: {optimized_time:.4f} 秒")
    print(f"处理统计: {result}")
    
    return result


# 主函数
if __name__ == '__main__':
    print("Airflow Database Optimization Examples")
    print("=" * 40)
    
    # 运行性能基准测试
    performance_benchmark()
    
    print("\n数据库优化示例创建完成!")
    print("主要包括:")
    print("- 连接池优化配置")
    print("- 查询优化技巧")
    print("- 连接池监控")
    print("- 数据清理优化")