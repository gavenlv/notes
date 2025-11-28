"""
第1章：元数据管理基础概念 - 配套代码示例
本文件包含第1章中所有可运行的代码示例，帮助读者通过实践理解元数据管理概念
"""

from datetime import datetime
import json
from typing import Dict, List, Optional

# ===================== 1.1 什么是元数据 =====================

def demonstrate_metadata_concept():
    """演示元数据与数据的关系"""
    print("=" * 50)
    print("1.1.2 元数据与数据的关系 - 演示示例")
    print("=" * 50)
    
    # 这是数据（实际内容）
    user_data = {
        "id": 1001,
        "name": "张三",
        "email": "zhangsan@example.com",
        "created_at": "2023-05-15"
    }
    
    # 这是元数据（描述数据的信息）
    metadata = {
        "table_name": "users",
        "description": "系统用户基本信息表",
        "columns": [
            {"name": "id", "type": "integer", "description": "用户唯一标识"},
            {"name": "name", "type": "varchar(50)", "description": "用户姓名"},
            {"name": "email", "type": "varchar(100)", "description": "用户邮箱"},
            {"name": "created_at", "type": "datetime", "description": "创建时间"}
        ],
        "owner": "数据管理团队",
        "last_updated": "2023-11-27",
        "data_volume": "约100万条记录"
    }
    
    print("数据（实际内容）:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
    print("\n元数据（描述数据的信息）:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    return user_data, metadata

# ===================== 1.3.2 对数据分析师的价值 =====================

def find_data_analyst_pain():
    """分析师在没有元数据管理时面临的典型问题"""
    problems = [
        "不知道哪些数据可用",
        "不理解数据字段含义",
        "不清楚数据质量状况",
        "找不到数据负责人",
        "无法追溯数据来源"
    ]
    return problems

def metadata_solution_benefits():
    """元数据管理带来的解决方案"""
    solutions = [
        "通过数据目录快速查找数据",
        "查看字段说明和业务含义",
        "了解数据质量评估结果",
        "快速定位数据负责人",
        "查看完整的数据血缘关系"
    ]
    return solutions

def demonstrate_analyst_benefits():
    """演示元数据管理对分析师的价值"""
    print("=" * 50)
    print("1.3.2 对数据分析师的价值 - 演示示例")
    print("=" * 50)
    
    pain_points = find_data_analyst_pain()
    solutions = metadata_solution_benefits()
    
    print("没有元数据管理时，分析师面临的困境:")
    for i, point in enumerate(pain_points, 1):
        print(f"{i}. {point}")
    
    print("\n有元数据管理后的解决方案:")
    for i, solution in enumerate(solutions, 1):
        print(f"{i}. {solution}")

# ===================== 1.4.1 数据目录（Data Catalog） =====================

class SimpleDataCatalog:
    """简化的数据目录实现"""
    def __init__(self):
        self.datasets = {}
        self.relationships = {}
    
    def register_dataset(self, dataset_info):
        """注册数据集"""
        dataset_id = dataset_info["id"]
        self.datasets[dataset_id] = {
            "name": dataset_info["name"],
            "description": dataset_info["description"],
            "owner": dataset_info["owner"],
            "schema": dataset_info["schema"],
            "tags": dataset_info.get("tags", []),
            "created_at": dataset_info.get("created_at", datetime.now())
        }
        return dataset_id
    
    def search_datasets(self, keyword):
        """搜索数据集"""
        results = []
        for dataset_id, dataset in self.datasets.items():
            if (keyword.lower() in dataset["name"].lower() or 
                keyword.lower() in dataset["description"].lower() or
                any(keyword.lower() in tag.lower() for tag in dataset["tags"])):
                results.append({"id": dataset_id, **dataset})
        return results
    
    def get_lineage(self, dataset_id):
        """获取数据血缘"""
        upstream = self.relationships.get(dataset_id, {}).get("upstream", [])
        downstream = self.relationships.get(dataset_id, {}).get("downstream", [])
        return {
            "dataset_id": dataset_id,
            "upstream": upstream,
            "downstream": downstream
        }
    
    def get_dataset(self, dataset_id):
        """获取数据集详情"""
        return self.datasets.get(dataset_id)

def demo_data_catalog():
    """演示数据目录的使用"""
    print("=" * 50)
    print("1.4.1 数据目录（Data Catalog）- 演示示例")
    print("=" * 50)
    
    # 创建数据目录
    catalog = SimpleDataCatalog()
    
    # 注册数据集
    catalog.register_dataset({
        "id": "user_profile",
        "name": "用户画像表",
        "description": "包含用户基本属性和行为的综合画像数据",
        "owner": "数据团队",
        "schema": {
            "user_id": "string",
            "age": "integer",
            "city": "string",
            "purchase_count": "integer"
        },
        "tags": ["用户", "画像", "行为数据"]
    })
    
    catalog.register_dataset({
        "id": "order_summary",
        "name": "订单汇总表",
        "description": "每日订单数据汇总，包含GMV、订单数等关键指标",
        "owner": "业务运营团队",
        "schema": {
            "date": "date",
            "order_count": "integer",
            "gmv": "decimal(18,2)",
            "user_count": "integer"
        },
        "tags": ["订单", "GMV", "业务指标"]
    })
    
    catalog.register_dataset({
        "id": "product_info",
        "name": "商品信息表",
        "description": "商品基本信息和属性数据",
        "owner": "商品团队",
        "schema": {
            "product_id": "string",
            "product_name": "string",
            "category": "string",
            "price": "decimal(10,2)"
        },
        "tags": ["商品", "基础数据"]
    })
    
    # 搜索数据集
    print("搜索关键词'用户':")
    user_results = catalog.search_datasets("用户")
    for result in user_results:
        print(f"  - {result['name']}: {result['description']}")
    
    print("\n搜索关键词'数据':")
    data_results = catalog.search_datasets("数据")
    for result in data_results:
        print(f"  - {result['name']}: {result['description']}")
    
    # 查看数据集详情
    print("\n用户画像表详细信息:")
    profile = catalog.get_dataset("user_profile")
    print(json.dumps(profile, indent=2, ensure_ascii=False, default=str))
    
    return catalog

# ===================== 1.4.2 数据血缘（Data Lineage） =====================

class DataLineage:
    """数据血缘管理"""
    def __init__(self):
        self.graph = {}  # 数据血缘图
    
    def add_transformation(self, source, target, transformation_info):
        """添加数据转换关系"""
        if source not in self.graph:
            self.graph[source] = {"outputs": [], "inputs": []}
        if target not in self.graph:
            self.graph[target] = {"outputs": [], "inputs": []}
        
        self.graph[source]["outputs"].append({
            "target": target,
            "transformation": transformation_info
        })
        self.graph[target]["inputs"].append({
            "source": source,
            "transformation": transformation_info
        })
    
    def get_upstream(self, dataset, depth=None):
        """获取上游数据"""
        return self._traverse(dataset, "inputs", depth)
    
    def get_downstream(self, dataset, depth=None):
        """获取下游数据"""
        return self._traverse(dataset, "outputs", depth)
    
    def _traverse(self, dataset, direction, depth, visited=None):
        """递归遍历血缘关系"""
        if visited is None:
            visited = set()
        if dataset in visited or (depth is not None and depth < 0):
            return []
        
        visited.add(dataset)
        result = [dataset]
        
        for edge in self.graph.get(dataset, {}).get(direction, []):
            next_dataset = edge["target"] if direction == "outputs" else edge["source"]
            next_depth = None if depth is None else depth - 1
            result.extend(self._traverse(next_dataset, direction, next_depth, visited))
        
        return result
    
    def get_transformation_details(self, source, target):
        """获取转换详情"""
        for edge in self.graph.get(source, {}).get("outputs", []):
            if edge["target"] == target:
                return edge["transformation"]
        return None

def demo_data_lineage():
    """演示数据血缘的使用"""
    print("=" * 50)
    print("1.4.2 数据血缘（Data Lineage）- 演示示例")
    print("=" * 50)
    
    # 创建血缘管理
    lineage = DataLineage()
    
    # 添加血缘关系
    lineage.add_transformation(
        "原始订单表", 
        "清洗订单表", 
        {"job": "订单数据清洗", "schedule": "每日2:00", "script": "clean_order_data.py"}
    )
    
    lineage.add_transformation(
        "清洗订单表", 
        "订单汇总表", 
        {"job": "订单数据汇总", "schedule": "每日6:00", "script": "aggregate_order.py"}
    )
    
    lineage.add_transformation(
        "用户表", 
        "用户订单关联表", 
        {"job": "用户订单关联", "schedule": "每日7:00", "script": "join_user_order.py"}
    )
    
    lineage.add_transformation(
        "订单汇总表", 
        "用户订单关联表", 
        {"job": "用户订单关联", "schedule": "每日7:00", "script": "join_user_order.py"}
    )
    
    lineage.add_transformation(
        "用户订单关联表", 
        "用户行为分析报表", 
        {"job": "用户行为分析", "schedule": "每日8:00", "script": "user_behavior_analysis.py"}
    )
    
    # 查看血缘关系
    print("用户订单关联表的上游数据:")
    upstream = lineage.get_upstream("用户订单关联表")
    for dataset in upstream:
        print(f"  - {dataset}")
    
    print("\n原始订单表的下游数据:")
    downstream = lineage.get_downstream("原始订单表")
    for dataset in downstream:
        print(f"  - {dataset}")
    
    # 查看特定深度的血缘
    print("\n用户行为分析报表的2级上游数据:")
    upstream_2 = lineage.get_upstream("用户行为分析报表", depth=2)
    for dataset in upstream_2:
        print(f"  - {dataset}")
    
    # 查看转换详情
    print("\n清洗订单表 -> 订单汇总表的转换详情:")
    transform_detail = lineage.get_transformation_details("清洗订单表", "订单汇总表")
    print(json.dumps(transform_detail, indent=2, ensure_ascii=False))
    
    return lineage

# ===================== 1.6 实践案例：构建简单的元数据管理系统 =====================

class MetadataManagementSystem:
    """简化的元数据管理系统"""
    def __init__(self):
        self.catalog = SimpleDataCatalog()
        self.lineage = DataLineage()
        self.quality_scores = {}
        self.business_terms = {}
    
    def register_data_asset(self, asset_info):
        """注册数据资产"""
        asset_id = self.catalog.register_dataset(asset_info)
        return asset_id
    
    def define_business_term(self, term, definition, related_terms=None):
        """定义业务术语"""
        self.business_terms[term] = {
            "definition": definition,
            "related_terms": related_terms or [],
            "created_at": datetime.now()
        }
    
    def update_data_quality(self, dataset_id, quality_metrics):
        """更新数据质量指标"""
        self.quality_scores[dataset_id] = {
            "metrics": quality_metrics,
            "updated_at": datetime.now()
        }
    
    def get_data_profile(self, dataset_id):
        """获取数据完整画像"""
        dataset = self.catalog.datasets.get(dataset_id, {})
        lineage_info = self.lineage.get_lineage(dataset_id)
        quality_info = self.quality_scores.get(dataset_id, {})
        
        return {
            "basic_info": dataset,
            "lineage": lineage_info,
            "quality": quality_info
        }
    
    def search_data_assets(self, keyword):
        """搜索数据资产"""
        return self.catalog.search_datasets(keyword)
    
    def get_business_definition(self, term):
        """获取业务术语定义"""
        return self.business_terms.get(term, {})

def demo_metadata_management():
    """元数据管理系统的实际应用示例"""
    print("=" * 50)
    print("1.6 实践案例：构建简单的元数据管理系统")
    print("=" * 50)
    
    # 创建元数据管理系统
    mms = MetadataManagementSystem()
    
    # 1. 定义业务术语
    print("步骤1: 定义业务术语")
    mms.define_business_term(
        "GMV", 
        "商品交易总额（Gross Merchandise Volume）",
        ["销售额", "成交金额"]
    )
    mms.define_business_term(
        "DAU", 
        "日活跃用户数（Daily Active Users）",
        ["活跃用户", "用户活跃度"]
    )
    mms.define_business_term(
        "AOV", 
        "平均订单价值（Average Order Value）",
        ["客单价", "平均订单金额"]
    )
    
    print("已定义业务术语:", list(mms.business_terms.keys()))
    
    # 2. 注册数据资产
    print("\n步骤2: 注册数据资产")
    user_behavior_id = mms.register_data_asset({
        "id": "user_behavior_daily",
        "name": "用户行为日报表",
        "description": "每日用户行为数据汇总，包含DAU、使用时长等关键指标",
        "owner": "数据分析团队",
        "schema": {
            "date": "date",
            "user_id": "string",
            "page_views": "integer",
            "session_duration": "float",
            "last_active_time": "timestamp"
        },
        "tags": ["用户行为", "日汇总", "核心指标"],
        "refresh_frequency": "每日",
        "data_volume": "约50万条/日"
    })
    
    order_summary_id = mms.register_data_asset({
        "id": "order_summary_daily",
        "name": "订单汇总日报表",
        "description": "每日订单数据汇总，包含GMV、订单数、AOV等关键指标",
        "owner": "业务运营团队",
        "schema": {
            "date": "date",
            "order_count": "integer",
            "gmv": "decimal(18,2)",
            "user_count": "integer",
            "avg_order_value": "decimal(18,2)"
        },
        "tags": ["订单", "日汇总", "GMV", "AOV"],
        "refresh_frequency": "每日",
        "data_volume": "约10万条/日"
    })
    
    product_info_id = mms.register_data_asset({
        "id": "product_info",
        "name": "商品信息表",
        "description": "商品基本信息和属性数据",
        "owner": "商品管理团队",
        "schema": {
            "product_id": "string",
            "product_name": "string",
            "category": "string",
            "price": "decimal(10,2)",
            "brand": "string"
        },
        "tags": ["商品", "基础数据", "静态数据"],
        "refresh_frequency": "每日",
        "data_volume": "约100万条"
    })
    
    print(f"已注册数据资产: {user_behavior_id}, {order_summary_id}, {product_info_id}")
    
    # 3. 建立血缘关系
    print("\n步骤3: 建立血缘关系")
    mms.lineage.add_transformation(
        "user_behavior_log",
        "user_behavior_daily",
        {"job": "用户行为聚合", "schedule": "每日8:00", "owner": "数据团队"}
    )
    
    mms.lineage.add_transformation(
        "order_detail",
        "order_summary_daily", 
        {"job": "订单汇总", "schedule": "每日8:30", "owner": "数据团队"}
    )
    
    mms.lineage.add_transformation(
        "user_behavior_daily",
        "user_activity_report",
        {"job": "用户活跃度分析", "schedule": "每日9:00", "owner": "分析团队"}
    )
    
    mms.lineage.add_transformation(
        "order_summary_daily",
        "business_performance_report",
        {"job": "业务绩效分析", "schedule": "每日9:30", "owner": "分析团队"}
    )
    
    print("已建立数据血缘关系")
    
    # 4. 记录数据质量
    print("\n步骤4: 记录数据质量")
    mms.update_data_quality("user_behavior_daily", {
        "completeness": 0.98,  # 完整性98%
        "accuracy": 0.95,       # 准确性95%
        "timeliness": 0.99,     # 及时性99%
        "consistency": 0.97,    # 一致性97%
        "overall_score": 0.97   # 总体评分97%
    })
    
    mms.update_data_quality("order_summary_daily", {
        "completeness": 0.96,
        "accuracy": 0.99,
        "timeliness": 0.98,
        "consistency": 0.95,
        "overall_score": 0.97
    })
    
    print("已记录数据质量指标")
    
    # 5. 演示查询功能
    print("\n步骤5: 演示查询功能")
    
    # 搜索数据资产
    print("搜索包含'用户'的数据资产:")
    user_assets = mms.search_data_assets("用户")
    for asset in user_assets:
        print(f"  - {asset['name']}: {asset['description']}")
    
    # 查看业务术语定义
    print("\nGMV的业务定义:")
    gmv_def = mms.get_business_definition("GMV")
    if gmv_def:
        print(f"  定义: {gmv_def['definition']}")
        print(f"  相关术语: {', '.join(gmv_def['related_terms'])}")
    
    # 查看数据画像
    print("\n用户行为日报表的数据画像:")
    profile = mms.get_data_profile("user_behavior_daily")
    print(json.dumps(profile, indent=2, ensure_ascii=False, default=str))
    
    return mms

# ===================== 主函数 - 运行所有演示 =====================

def main():
    """运行所有演示示例"""
    print("第1章：元数据管理基础概念 - 代码示例")
    print("=" * 80)
    
    # 演示元数据概念
    user_data, metadata = demonstrate_metadata_concept()
    
    # 演示分析师价值
    demonstrate_analyst_benefits()
    
    # 演示数据目录
    catalog = demo_data_catalog()
    
    # 演示数据血缘
    lineage = demo_data_lineage()
    
    # 演示完整元数据管理系统
    mms = demo_metadata_management()
    
    print("\n" + "=" * 80)
    print("所有演示完成！您可以根据自己的需求修改和扩展这些示例。")

if __name__ == "__main__":
    main()