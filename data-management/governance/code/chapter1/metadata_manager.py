"""
第1章代码示例：简单的元数据管理系统
演示如何实现基本的元数据管理和数据血缘追踪
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class MetadataManager:
    """简单的元数据管理系统，支持元数据管理和数据血缘追踪"""
    
    def __init__(self):
        """初始化元数据管理系统"""
        # 存储表元数据
        self.metadata_store = {}
        # 存储数据血缘关系
        self.data_lineage = {}
        # 存储数据质量指标
        self.quality_metrics = {}
        # 存储访问记录
        self.access_logs = []
    
    def add_metadata(self, table_name: str, description: str, schema: List[str], 
                    owner: str, quality_score: Optional[float] = None,
                    tags: Optional[List[str]] = None):
        """添加表元数据
        
        Args:
            table_name: 表名
            description: 表描述
            schema: 表结构（字段列表）
            owner: 表所有者
            quality_score: 数据质量分数（0-100）
            tags: 标签列表
        """
        self.metadata_store[table_name] = {
            'description': description,
            'schema': schema,
            'owner': owner,
            'quality_score': quality_score,
            'tags': tags if tags else [],
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        print(f"已添加表 '{table_name}' 的元数据")
    
    def update_quality_score(self, table_name: str, quality_score: float):
        """更新数据质量分数"""
        if table_name in self.metadata_store:
            self.metadata_store[table_name]['quality_score'] = quality_score
            self.metadata_store[table_name]['updated_at'] = datetime.now()
            
            # 记录质量变化历史
            if table_name not in self.quality_metrics:
                self.quality_metrics[table_name] = []
            
            self.quality_metrics[table_name].append({
                'quality_score': quality_score,
                'updated_at': datetime.now()
            })
            
            print(f"已更新表 '{table_name}' 的质量分数为: {quality_score}")
        else:
            print(f"警告: 表 '{table_name}' 不存在")
    
    def add_lineage(self, source_table: str, target_table: str, transformation: str):
        """添加数据血缘关系
        
        Args:
            source_table: 源表名
            target_table: 目标表名
            transformation: 数据转换描述
        """
        if source_table not in self.data_lineage:
            self.data_lineage[source_table] = []
        
        self.data_lineage[source_table].append({
            'target_table': target_table,
            'transformation': transformation,
            'created_at': datetime.now()
        })
        
        print(f"已添加血缘关系: {source_table} -> {target_table} ({transformation})")
    
    def log_access(self, table_name: str, user: str, operation: str):
        """记录数据访问日志
        
        Args:
            table_name: 表名
            user: 用户
            operation: 操作类型 (SELECT, INSERT, UPDATE, DELETE)
        """
        access_log = {
            'table_name': table_name,
            'user': user,
            'operation': operation,
            'access_time': datetime.now()
        }
        
        self.access_logs.append(access_log)
        print(f"已记录访问: {user} 在 {access_log['access_time']} 对 {table_name} 执行了 {operation}")
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表详细信息
        
        Args:
            table_name: 表名
            
        Returns:
            包含表元数据、血缘关系和质量指标的字典
        """
        # 获取基本元数据
        metadata = self.metadata_store.get(table_name, {})
        
        # 获取血缘信息（来源表）
        sources = []
        for source, targets in self.data_lineage.items():
            for t in targets:
                if t['target_table'] == table_name:
                    sources.append({
                        'source_table': source,
                        'transformation': t['transformation'],
                        'created_at': t['created_at']
                    })
        
        # 获取血缘信息（目标表）
        targets = self.data_lineage.get(table_name, [])
        
        # 获取质量指标
        quality_history = self.quality_metrics.get(table_name, [])
        
        # 获取访问记录（最近10条）
        recent_access = [log for log in self.access_logs if log['table_name'] == table_name][-10:]
        
        return {
            'metadata': metadata,
            'sources': sources,
            'targets': targets,
            'quality_history': quality_history,
            'recent_access': recent_access
        }
    
    def search_tables(self, keyword: str, search_by: str = 'description') -> List[str]:
        """搜索表
        
        Args:
            keyword: 搜索关键词
            search_by: 搜索范围 ('description', 'owner', 'tags')
            
        Returns:
            匹配的表名列表
        """
        matching_tables = []
        
        for table_name, metadata in self.metadata_store.items():
            if search_by == 'description' and keyword.lower() in metadata.get('description', '').lower():
                matching_tables.append(table_name)
            elif search_by == 'owner' and keyword.lower() in metadata.get('owner', '').lower():
                matching_tables.append(table_name)
            elif search_by == 'tags' and any(keyword.lower() in tag.lower() for tag in metadata.get('tags', [])):
                matching_tables.append(table_name)
        
        return matching_tables
    
    def get_data_flow_diagram(self, table_name: str) -> Dict:
        """生成数据流图结构
        
        Args:
            table_name: 中心表名
            
        Returns:
            包含节点和边的数据流图结构
        """
        nodes = {}
        edges = []
        
        # 添加中心表
        nodes[table_name] = {
            'type': 'focus',
            'metadata': self.metadata_store.get(table_name, {})
        }
        
        # 添加源表和边
        for source, targets in self.data_lineage.items():
            for target_info in targets:
                if target_info['target_table'] == table_name:
                    nodes[source] = {
                        'type': 'source',
                        'metadata': self.metadata_store.get(source, {})
                    }
                    edges.append({
                        'from': source,
                        'to': table_name,
                        'label': target_info['transformation']
                    })
        
        # 添加目标表和边
        for target_info in self.data_lineage.get(table_name, []):
            target_table = target_info['target_table']
            nodes[target_table] = {
                'type': 'target',
                'metadata': self.metadata_store.get(target_table, {})
            }
            edges.append({
                'from': table_name,
                'to': target_table,
                'label': target_info['transformation']
            })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """生成元数据报告"""
        total_tables = len(self.metadata_store)
        avg_quality = 0
        owners = set()
        all_tags = []
        
        if total_tables > 0:
            # 计算平均质量分数
            quality_scores = [m['quality_score'] for m in self.metadata_store.values() 
                           if m['quality_score'] is not None]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # 收集所有者和标签
            for metadata in self.metadata_store.values():
                owners.add(metadata.get('owner', ''))
                all_tags.extend(metadata.get('tags', []))
        
        # 统计访问量
        access_stats = {}
        for log in self.access_logs:
            table = log['table_name']
            if table not in access_stats:
                access_stats[table] = {'total': 0, 'users': set()}
            
            access_stats[table]['total'] += 1
            access_stats[table]['users'].add(log['user'])
        
        # 找出最热门的表
        hottest_table = max(access_stats.items(), key=lambda x: x[1]['total'], 
                          default=(None, {'total': 0, 'users': set()}))
        
        # 找出质量最差和最好的表
        worst_table = None
        best_table = None
        worst_score = 100
        best_score = 0
        
        for table, metadata in self.metadata_store.items():
            score = metadata.get('quality_score')
            if score is not None:
                if score < worst_score:
                    worst_score = score
                    worst_table = table
                if score > best_score:
                    best_score = score
                    best_table = table
        
        return {
            'summary': {
                'total_tables': total_tables,
                'average_quality_score': avg_quality,
                'total_owners': len(owners),
                'total_unique_tags': len(set(all_tags)),
                'hottest_table': hottest_table[0],
                'hottest_table_access_count': hottest_table[1]['total'],
                'worst_quality_table': worst_table,
                'worst_quality_score': worst_score,
                'best_quality_table': best_table,
                'best_quality_score': best_score
            },
            'access_stats': {
                table: {
                    'total_access_count': stats['total'],
                    'unique_users': len(stats['users'])
                } for table, stats in access_stats.items()
            },
            'top_tags': pd.Series(all_tags).value_counts().head(10).to_dict() if all_tags else {}
        }
    
    def export_metadata(self, filename: str):
        """导出元数据到JSON文件
        
        Args:
            filename: 导出文件名
        """
        export_data = {
            'metadata_store': {
                table: {
                    **metadata,
                    'created_at': metadata['created_at'].isoformat(),
                    'updated_at': metadata['updated_at'].isoformat()
                } for table, metadata in self.metadata_store.items()
            },
            'data_lineage': {
                source: [
                    {
                        **target,
                        'created_at': target['created_at'].isoformat()
                    } for target in targets
                ] for source, targets in self.data_lineage.items()
            },
            'quality_metrics': {
                table: [
                    {
                        **metric,
                        'updated_at': metric['updated_at'].isoformat()
                    } for metric in metrics
                ] for table, metrics in self.quality_metrics.items()
            },
            'access_logs': [
                {
                    **log,
                    'access_time': log['access_time'].isoformat()
                } for log in self.access_logs
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"元数据已导出到: {filename}")


# 演示使用元数据管理系统
def demonstrate_metadata_manager():
    """演示元数据管理系统的使用"""
    print("="*60)
    print("元数据管理系统演示")
    print("="*60)
    
    # 创建管理器实例
    manager = MetadataManager()
    
    # 1. 添加表元数据
    print("\n1. 添加表元数据")
    print("-"*40)
    
    manager.add_metadata(
        table_name="customers",
        description="客户基础信息表，包含客户基本信息和联系方式",
        schema=["customer_id", "name", "email", "phone", "address", "city", "country"],
        owner="customer_service_team",
        quality_score=95.5,
        tags=["customer", "p", "contact"]
    )
    
    manager.add_metadata(
        table_name="orders",
        description="订单信息表，记录客户订单详情",
        schema=["order_id", "customer_id", "order_date", "product_id", "quantity", "amount"],
        owner="sales_team",
        quality_score=98.2,
        tags=["order", "sales", "transaction"]
    )
    
    manager.add_metadata(
        table_name="products",
        description="产品信息表，包含产品详细信息",
        schema=["product_id", "name", "category", "price", "description"],
        owner="product_team",
        quality_score=91.8,
        tags=["product", "inventory"]
    )
    
    manager.add_metadata(
        table_name="customer_orders_summary",
        description="客户订单汇总表，提供客户级别订单统计",
        schema=["customer_id", "total_orders", "total_amount", "last_order_date"],
        owner="data_team",
        quality_score=96.5,
        tags=["customer", "order", "summary", "analytics"]
    )
    
    # 2. 添加数据血缘关系
    print("\n2. 添加数据血缘关系")
    print("-"*40)
    
    manager.add_lineage(
        source_table="customers",
        target_table="customer_orders_summary",
        transformation="左连接订单表，按customer_id分组汇总"
    )
    
    manager.add_lineage(
        source_table="orders",
        target_table="customer_orders_summary",
        transformation="左连接客户表，按customer_id分组汇总订单信息"
    )
    
    # 3. 记录数据访问
    print("\n3. 记录数据访问")
    print("-"*40)
    
    manager.log_access("customers", "analyst1", "SELECT")
    manager.log_access("orders", "analyst2", "SELECT")
    manager.log_access("customer_orders_summary", "manager1", "SELECT")
    manager.log_access("customers", "data_engineer1", "INSERT")
    manager.log_access("customer_orders_summary", "analyst1", "SELECT")
    
    # 4. 更新质量分数
    print("\n4. 更新质量分数")
    print("-"*40)
    
    manager.update_quality_score("customers", 97.2)
    manager.update_quality_score("customer_orders_summary", 94.8)
    
    # 5. 查询表信息
    print("\n5. 查询表信息")
    print("-"*40)
    
    customer_orders_info = manager.get_table_info("customer_orders_summary")
    print(f"表描述: {customer_orders_info['metadata']['description']}")
    print(f"所有者: {customer_orders_info['metadata']['owner']}")
    print(f"质量分数: {customer_orders_info['metadata']['quality_score']}")
    
    print(f"\n数据来源:")
    for source in customer_orders_info['sources']:
        print(f"- {source['source_table']}: {source['transformation']}")
    
    print(f"\n最近访问记录:")
    for log in customer_orders_info['recent_access']:
        print(f"- {log['user']} 在 {log['access_time']} 执行了 {log['operation']}")
    
    # 6. 搜索表
    print("\n6. 搜索表")
    print("-"*40)
    
    customer_tables = manager.search_tables("customer", "description")
    print(f"包含'customer'的表: {customer_tables}")
    
    analytics_tables = manager.search_tables("analytics", "tags")
    print(f"包含'analytics'标签的表: {analytics_tables}")
    
    # 7. 生成数据流图
    print("\n7. 生成数据流图")
    print("-"*40)
    
    data_flow = manager.get_data_flow_diagram("customer_orders_summary")
    print(f"数据流图节点: {list(data_flow['nodes'].keys())}")
    
    for edge in data_flow['edges']:
        print(f"数据流: {edge['from']} -> {edge['to']} ({edge['label']})")
    
    # 8. 生成报告
    print("\n8. 生成元数据报告")
    print("-"*40)
    
    report = manager.generate_report()
    summary = report['summary']
    
    print(f"总表数: {summary['total_tables']}")
    print(f"平均质量分数: {summary['average_quality_score']:.2f}")
    print(f"最热门的表: {summary['hottest_table']} (访问次数: {summary['hottest_table_access_count']})")
    print(f"质量最好的表: {summary['best_quality_table']} (分数: {summary['best_quality_score']})")
    print(f"质量最差的表: {summary['worst_quality_table']} (分数: {summary['worst_quality_score']})")
    
    # 9. 导出元数据
    print("\n9. 导出元数据")
    print("-"*40)
    
    manager.export_metadata("metadata_export.json")
    
    return manager


if __name__ == "__main__":
    # 运行演示
    manager = demonstrate_metadata_manager()
    
    print("\n元数据管理系统演示完成！")