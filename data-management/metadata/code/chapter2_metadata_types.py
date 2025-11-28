"""
第2章：元数据类型与分类 - 配套代码示例
本文件包含第2章中所有可运行的代码示例，帮助读者通过实践理解元数据类型与分类
"""

from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

# ===================== 2.1.1 按抽象层次分类 =====================

# ===================== 业务元数据 =====================

class BusinessMetadataManager:
    """业务元数据管理器"""
    def __init__(self):
        self.business_glossary = {}  # 业务术语表
        self.data_stewards = {}      # 数据管理员
        self.business_rules = {}     # 业务规则
    
    def add_business_term(self, term, definition, context, synonyms=None):
        """添加业务术语"""
        self.business_glossary[term] = {
            "definition": definition,
            "context": context,
            "synonyms": synonyms or [],
            "created_at": datetime.now()
        }
        return term
    
    def assign_data_steward(self, dataset, steward_info):
        """指定数据管理员"""
        self.data_stewards[dataset] = {
            "name": steward_info["name"],
            "department": steward_info["department"],
            "contact": steward_info["contact"],
            "responsibilities": steward_info.get("responsibilities", []),
            "assigned_at": datetime.now()
        }
        return dataset
    
    def add_business_rule(self, dataset, rule_name, rule_definition, validation_logic=None):
        """添加业务规则"""
        if dataset not in self.business_rules:
            self.business_rules[dataset] = {}
        
        self.business_rules[dataset][rule_name] = {
            "definition": rule_definition,
            "validation_logic": validation_logic,
            "created_at": datetime.now()
        }
        return f"{dataset}.{rule_name}"
    
    def get_business_definition(self, term):
        """获取业务术语定义"""
        return self.business_glossary.get(term, {})

def demo_business_metadata():
    """演示业务元数据的使用"""
    print("=" * 50)
    print("2.1.1 按抽象层次分类 - 业务元数据")
    print("=" * 50)
    
    # 创建业务元数据管理器
    business_manager = BusinessMetadataManager()
    
    # 添加业务术语
    business_manager.add_business_term(
        term="GMV",
        definition="商品交易总额(Gross Merchandise Volume)",
        context="电商业务指标",
        synonyms=["成交金额", "销售总额"]
    )
    
    business_manager.add_business_term(
        term="DAU",
        definition="日活跃用户数(Daily Active Users)",
        context="用户活跃度指标",
        synonyms=["日活", "活跃用户"]
    )
    
    # 指定数据管理员
    business_manager.assign_data_steward(
        dataset="订单数据",
        steward_info={
            "name": "李经理",
            "department": "运营部",
            "contact": "limanager@example.com",
            "responsibilities": ["数据质量监控", "业务指标定义", "数据权限审批"]
        }
    )
    
    # 添加业务规则
    business_manager.add_business_rule(
        dataset="订单数据",
        rule_name="订单金额验证",
        rule_definition="订单金额必须大于0且小于100万",
        validation_logic=lambda amount: 0 < amount < 1000000
    )
    
    # 查看业务术语定义
    gmv_def = business_manager.get_business_definition("GMV")
    print(f"GMV定义: {gmv_def.get('definition')}")
    print(f"GMV同义词: {gmv_def.get('synonyms')}")
    
    # 查看数据管理员
    order_steward = business_manager.data_stewards.get("订单数据", {})
    print(f"订单数据管理员: {order_steward.get('name')} - {order_steward.get('department')}")
    
    # 验证业务规则
    validation_result = business_manager.business_rules.get("订单数据", {}).get("订单金额验证", {})
    validation_logic = validation_result.get("validation_logic")
    if validation_logic:
        test_amount = 500
        is_valid = validation_logic(test_amount)
        print(f"订单金额 {test_amount} 是否有效: {is_valid}")
    
    return business_manager

# ===================== 技术元数据 =====================

class TechnicalMetadataManager:
    """技术元数据管理器"""
    def __init__(self):
        self.databases = {}       # 数据库信息
        self.tables = {}          # 表结构信息
        self.etl_jobs = {}        # ETL作业信息
        self.data_quality = {}    # 数据质量指标
    
    def register_database(self, db_info):
        """注册数据库信息"""
        db_id = db_info["host"] + ":" + str(db_info["port"]) + "/" + db_info["name"]
        self.databases[db_id] = {
            "type": db_info["type"],
            "version": db_info.get("version"),
            "host": db_info["host"],
            "port": db_info["port"],
            "name": db_info["name"],
            "connection_pool": db_info.get("connection_pool", {}),
            "registered_at": datetime.now()
        }
        return db_id
    
    def register_table(self, table_info):
        """注册表结构信息"""
        table_id = table_info["database"] + "." + table_info["schema"] + "." + table_info["name"]
        self.tables[table_id] = {
            "database": table_info["database"],
            "schema": table_info["schema"],
            "name": table_info["name"],
            "table_type": table_info.get("table_type", "table"),
            "storage_engine": table_info.get("storage_engine"),
            "columns": table_info["columns"],
            "indexes": table_info.get("indexes", []),
            "partitions": table_info.get("partitions"),
            "row_count": table_info.get("row_count"),
            "size_bytes": table_info.get("size_bytes"),
            "registered_at": datetime.now()
        }
        return table_id
    
    def register_etl_job(self, job_info):
        """注册ETL作业信息"""
        job_id = job_info["name"]
        self.etl_jobs[job_id] = {
            "name": job_info["name"],
            "type": job_info["type"],  # extract, transform, load
            "source_system": job_info["source_system"],
            "target_system": job_info["target_system"],
            "schedule": job_info.get("schedule"),
            "script_path": job_info.get("script_path"),
            "dependencies": job_info.get("dependencies", []),
            "parameters": job_info.get("parameters", {}),
            "registered_at": datetime.now()
        }
        return job_id
    
    def get_table_lineage(self, table_id):
        """获取表血缘关系"""
        upstream = []
        downstream = []
        
        for job_id, job in self.etl_jobs.items():
            if job["target_system"] == table_id:
                upstream.append(job["source_system"])
            if job["source_system"] == table_id:
                downstream.append(job["target_system"])
        
        return {
            "upstream": upstream,
            "downstream": downstream
        }
    
    def get_database_info(self, db_id):
        """获取数据库信息"""
        return self.databases.get(db_id)
    
    def get_table_info(self, table_id):
        """获取表信息"""
        return self.tables.get(table_id)

def demo_technical_metadata():
    """演示技术元数据的使用"""
    print("\n" + "=" * 50)
    print("2.1.1 按抽象层次分类 - 技术元数据")
    print("=" * 50)
    
    # 创建技术元数据管理器
    tech_manager = TechnicalMetadataManager()
    
    # 注册数据库
    db_id = tech_manager.register_database({
        "type": "MySQL",
        "version": "8.0.25",
        "host": "db-prod-01.company.com",
        "port": 3306,
        "name": "ecommerce"
    })
    print(f"注册数据库: {db_id}")
    
    # 注册表
    table_id = tech_manager.register_table({
        "database": "ecommerce",
        "schema": "public",
        "name": "orders",
        "table_type": "table",
        "storage_engine": "InnoDB",
        "columns": [
            {"name": "order_id", "type": "bigint", "nullable": False, "primary_key": True},
            {"name": "user_id", "type": "bigint", "nullable": False},
            {"name": "order_amount", "type": "decimal(10,2)", "nullable": False},
            {"name": "order_date", "type": "datetime", "nullable": False},
            {"name": "status", "type": "varchar(20)", "nullable": False}
        ],
        "indexes": [
            {"name": "idx_user_id", "columns": ["user_id"], "type": "btree"},
            {"name": "idx_order_date", "columns": ["order_date"], "type": "btree"}
        ],
        "row_count": 5000000,
        "size_bytes": 2147483648  # 2GB
    })
    print(f"注册表: {table_id}")
    
    # 注册ETL作业
    job_id = tech_manager.register_etl_job({
        "name": "order_data_sync",
        "type": "extract",
        "source_system": "mysql.ecommerce.orders",
        "target_system": "data_lake.orders.raw",
        "schedule": "0 */2 * * *",  # 每2小时执行一次
        "script_path": "/etl/scripts/order_sync.py",
        "parameters": {
            "batch_size": 10000,
            "incremental_column": "updated_at"
        }
    })
    print(f"注册ETL作业: {job_id}")
    
    # 查看表信息
    table_info = tech_manager.get_table_info(table_id)
    print(f"\n表 {table_info['name']} 的字段数量: {len(table_info['columns'])}")
    
    # 查看血缘关系
    lineage = tech_manager.get_table_lineage("mysql.ecommerce.orders")
    print(f"表 mysql.ecommerce.orders 的血缘关系:")
    print(f"  上游: {lineage['upstream']}")
    print(f"  下游: {lineage['downstream']}")
    
    return tech_manager

# ===================== 操作元数据 =====================

class OperationalMetadataManager:
    """操作元数据管理器"""
    def __init__(self):
        self.job_executions = {}     # 作业执行历史
        self.data_access = {}         # 数据访问记录
        self.quality_checks = {}      # 质量检查结果
        self.alerts = {}              # 告警信息
    
    def log_job_execution(self, job_info):
        """记录作业执行情况"""
        job_name = job_info["job_name"]
        execution_id = f"{job_name}_{int(datetime.now().timestamp())}"
        
        if job_name not in self.job_executions:
            self.job_executions[job_name] = []
        
        execution_record = {
            "execution_id": execution_id,
            "start_time": job_info["start_time"],
            "end_time": job_info.get("end_time"),
            "status": job_info["status"],  # success, failed, running
            "records_processed": job_info.get("records_processed"),
            "error_message": job_info.get("error_message"),
            "duration_seconds": job_info.get("duration_seconds"),
            "logged_at": datetime.now()
        }
        
        self.job_executions[job_name].append(execution_record)
        
        # 如果执行失败，创建告警
        if job_info["status"] == "failed":
            self.create_alert({
                "type": "job_failure",
                "source": job_name,
                "message": f"作业执行失败: {job_info.get('error_message', '未知错误')}",
                "severity": "high",
                "created_at": datetime.now()
            })
        
        return execution_id
    
    def log_data_access(self, access_info):
        """记录数据访问"""
        table_name = access_info["table_name"]
        if table_name not in self.data_access:
            self.data_access[table_name] = {
                "access_history": [],
                "daily_stats": {}
            }
        
        access_record = {
            "user": access_info["user"],
            "timestamp": access_info["timestamp"],
            "access_type": access_info["access_type"],  # read, write, delete
            "query": access_info.get("query"),
            "rows_affected": access_info.get("rows_affected")
        }
        
        self.data_access[table_name]["access_history"].append(access_record)
        
        # 更新日统计
        access_date = access_info["timestamp"].date()
        date_key = str(access_date)
        
        if date_key not in self.data_access[table_name]["daily_stats"]:
            self.data_access[table_name]["daily_stats"][date_key] = {
                "read_count": 0,
                "write_count": 0,
                "unique_users": set()
            }
        
        if access_info["access_type"] == "read":
            self.data_access[table_name]["daily_stats"][date_key]["read_count"] += 1
        else:
            self.data_access[table_name]["daily_stats"][date_key]["write_count"] += 1
        
        self.data_access[table_name]["daily_stats"][date_key]["unique_users"].add(access_info["user"])
    
    def record_quality_check(self, check_info):
        """记录质量检查结果"""
        dataset = check_info["dataset"]
        if dataset not in self.quality_checks:
            self.quality_checks[dataset] = []
        
        quality_record = {
            "check_time": check_info["check_time"],
            "dimensions": check_info["dimensions"],  # 完整性、准确性、一致性等
            "overall_score": check_info.get("overall_score"),
            "issues": check_info.get("issues", []),
            "checked_by": check_info.get("checked_by", "system")
        }
        
        self.quality_checks[dataset].append(quality_record)
        
        # 如果质量分数低于阈值，创建告警
        overall_score = check_info.get("overall_score", 0)
        if overall_score < 0.8:  # 80分以下告警
            self.create_alert({
                "type": "data_quality",
                "source": dataset,
                "message": f"数据质量评分过低: {overall_score}",
                "severity": "medium",
                "created_at": datetime.now()
            })
    
    def create_alert(self, alert_info):
        """创建告警"""
        alert_id = f"alert_{int(datetime.now().timestamp())}"
        self.alerts[alert_id] = {
            "id": alert_id,
            **alert_info,
            "status": "active",
            "acknowledged_by": None,
            "acknowledged_at": None
        }
        return alert_id
    
    def get_job_performance_stats(self, job_name, days=7):
        """获取作业性能统计"""
        if job_name not in self.job_executions:
            return {}
        
        # 获取最近N天的执行记录
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_executions = [
            exec for exec in self.job_executions[job_name]
            if datetime.fromisoformat(exec["start_time"].replace('Z', '+00:00')) > cutoff_date
        ]
        
        if not recent_executions:
            return {}
        
        # 计算统计指标
        success_count = len([e for e in recent_executions if e["status"] == "success"])
        total_count = len(recent_executions)
        avg_duration = sum([e.get("duration_seconds", 0) for e in recent_executions]) / total_count
        
        return {
            "total_executions": total_count,
            "success_rate": success_count / total_count,
            "avg_duration_seconds": avg_duration,
            "last_execution": recent_executions[-1]["status"]
        }

def demo_operational_metadata():
    """演示操作元数据的使用"""
    print("\n" + "=" * 50)
    print("2.1.1 按抽象层次分类 - 操作元数据")
    print("=" * 50)
    
    # 创建操作元数据管理器
    ops_manager = OperationalMetadataManager()
    
    # 记录作业执行
    ops_manager.log_job_execution({
        "job_name": "user_profile_calculation",
        "start_time": "2023-11-27T02:00:00Z",
        "end_time": "2023-11-27T02:23:45Z",
        "status": "success",
        "records_processed": 1054321,
        "duration_seconds": 1425
    })
    
    # 记录失败的作业执行
    ops_manager.log_job_execution({
        "job_name": "user_profile_calculation",
        "start_time": "2023-11-26T02:00:00Z",
        "end_time": "2023-11-26T02:15:30Z",
        "status": "failed",
        "error_message": "数据库连接超时",
        "duration_seconds": 930
    })
    
    # 记录数据访问
    ops_manager.log_data_access({
        "table_name": "user_profile",
        "user": "analyst_zhang",
        "timestamp": datetime.now(),
        "access_type": "read",
        "query": "SELECT * FROM user_profile WHERE age > 25",
        "rows_affected": 150000
    })
    
    ops_manager.log_data_access({
        "table_name": "user_profile",
        "user": "engineer_li",
        "timestamp": datetime.now(),
        "access_type": "write",
        "query": "UPDATE user_profile SET last_update = NOW()",
        "rows_affected": 500000
    })
    
    # 记录质量检查
    ops_manager.record_quality_check({
        "dataset": "user_profile",
        "check_time": datetime.now(),
        "dimensions": {
            "completeness": 0.98,
            "accuracy": 0.95,
            "timeliness": 0.97
        },
        "overall_score": 0.97,
        "issues": [
            {"dimension": "completeness", "description": "部分用户年龄字段缺失"}
        ]
    })
    
    # 查看作业性能统计
    stats = ops_manager.get_job_performance_stats("user_profile_calculation", days=7)
    print(f"作业性能统计:")
    print(f"  总执行次数: {stats.get('total_executions', 0)}")
    print(f"  成功率: {stats.get('success_rate', 0):.2%}")
    print(f"  平均耗时: {stats.get('avg_duration_seconds', 0):.0f}秒")
    
    # 查看告警数量
    alert_count = len(ops_manager.alerts)
    print(f"  活跃告警数量: {alert_count}")
    
    return ops_manager

# ===================== 2.1.2 按功能分类 =====================

# ===================== 结构元数据 =====================

class StructuralMetadata:
    """结构元数据管理"""
    def __init__(self):
        self.schemas = {}         # 模式定义
        self.tables = {}          # 表结构
        self.relationships = {}   # 表关系
        self.constraints = {}     # 约束条件
    
    def define_schema(self, schema_info):
        """定义数据模式"""
        schema_name = schema_info["name"]
        self.schemas[schema_name] = {
            "name": schema_name,
            "description": schema_info.get("description"),
            "owner": schema_info.get("owner"),
            "tables": schema_info.get("tables", []),
            "created_at": datetime.now()
        }
        return schema_name
    
    def define_table(self, table_info):
        """定义表结构"""
        table_id = f"{table_info['schema']}.{table_info['name']}"
        self.tables[table_id] = {
            "schema": table_info["schema"],
            "name": table_info["name"],
            "description": table_info.get("description"),
            "columns": table_info["columns"],
            "primary_key": table_info.get("primary_key"),
            "foreign_keys": table_info.get("foreign_keys", []),
            "indexes": table_info.get("indexes", []),
            "constraints": table_info.get("constraints", []),
            "created_at": datetime.now()
        }
        return table_id
    
    def define_relationship(self, rel_info):
        """定义表关系"""
        rel_id = f"{rel_info['from_table']}_to_{rel_info['to_table']}"
        self.relationships[rel_id] = {
            "from_table": rel_info["from_table"],
            "to_table": rel_info["to_table"],
            "type": rel_info["type"],  # one_to_one, one_to_many, many_to_many
            "from_columns": rel_info["from_columns"],
            "to_columns": rel_info["to_columns"],
            "description": rel_info.get("description"),
            "created_at": datetime.now()
        }
        return rel_id
    
    def get_schema_diagram(self, schema_name):
        """获取模式图信息"""
        if schema_name not in self.schemas:
            return None
        
        schema = self.schemas[schema_name]
        tables_in_schema = [t for t in self.tables.keys() if t.startswith(f"{schema_name}.")]
        
        relationships_in_schema = []
        for rel_id, rel in self.relationships.items():
            if (rel["from_table"].startswith(f"{schema_name}.") and 
                rel["to_table"].startswith(f"{schema_name}.")):
                relationships_in_schema.append(rel)
        
        return {
            "schema": schema,
            "tables": [self.tables[t] for t in tables_in_schema],
            "relationships": relationships_in_schema
        }
    
    def get_table_info(self, table_id):
        """获取表信息"""
        return self.tables.get(table_id)

def demo_structural_metadata():
    """演示结构元数据的使用"""
    print("\n" + "=" * 50)
    print("2.1.2 按功能分类 - 结构元数据")
    print("=" * 50)
    
    # 创建结构元数据管理器
    structural_metadata = StructuralMetadata()
    
    # 定义模式
    structural_metadata.define_schema({
        "name": "ecommerce",
        "description": "电商平台业务数据模式",
        "owner": "数据架构组"
    })
    
    # 定义用户表
    users_table_id = structural_metadata.define_table({
        "schema": "ecommerce",
        "name": "users",
        "description": "用户基本信息表",
        "columns": [
            {"name": "user_id", "type": "bigint", "nullable": False},
            {"name": "username", "type": "varchar(50)", "nullable": False},
            {"name": "email", "type": "varchar(100)", "nullable": False},
            {"name": "created_at", "type": "datetime", "nullable": False}
        ],
        "primary_key": ["user_id"],
        "indexes": [
            {"name": "idx_username", "columns": ["username"], "unique": True},
            {"name": "idx_email", "columns": ["email"], "unique": True}
        ]
    })
    
    # 定义订单表
    orders_table_id = structural_metadata.define_table({
        "schema": "ecommerce",
        "name": "orders",
        "description": "订单信息表",
        "columns": [
            {"name": "order_id", "type": "bigint", "nullable": False},
            {"name": "user_id", "type": "bigint", "nullable": False},
            {"name": "order_amount", "type": "decimal(10,2)", "nullable": False},
            {"name": "order_date", "type": "datetime", "nullable": False}
        ],
        "primary_key": ["order_id"],
        "foreign_keys": [
            {"name": "fk_orders_users", "from_columns": ["user_id"], "to_table": "ecommerce.users", "to_columns": ["user_id"]}
        ]
    })
    
    # 定义关系
    structural_metadata.define_relationship({
        "from_table": "ecommerce.users",
        "to_table": "ecommerce.orders",
        "type": "one_to_many",
        "from_columns": ["user_id"],
        "to_columns": ["user_id"],
        "description": "一个用户可以有多个订单"
    })
    
    # 获取模式图
    schema_diagram = structural_metadata.get_schema_diagram("ecommerce")
    print(f"模式图包含表数量: {len(schema_diagram['tables'])}")
    print(f"模式图包含关系数量: {len(schema_diagram['relationships'])}")
    
    # 查看表详情
    users_table = structural_metadata.get_table_info(users_table_id)
    print(f"用户表字段数量: {len(users_table['columns'])}")
    
    return structural_metadata

# ===================== 描述元数据 =====================

class DescriptiveMetadata:
    """描述元数据管理"""
    def __init__(self):
        self.data_dictionary = {}   # 数据字典
        self.field_descriptions = {}  # 字段描述
        self.value_domains = {}    # 值域定义
        self.business_glossary = {}   # 业务术语表
    
    def add_field_description(self, field_info):
        """添加字段描述"""
        field_id = f"{field_info['table']}.{field_info['field']}"
        self.field_descriptions[field_id] = {
            "table": field_info["table"],
            "field": field_info["field"],
            "description": field_info["description"],
            "business_meaning": field_info.get("business_meaning"),
            "example_values": field_info.get("example_values", []),
            "data_type": field_info.get("data_type"),
            "unit": field_info.get("unit"),
            "created_at": datetime.now()
        }
        return field_id
    
    def define_value_domain(self, domain_info):
        """定义值域"""
        domain_name = domain_info["name"]
        self.value_domains[domain_name] = {
            "name": domain_name,
            "description": domain_info.get("description"),
            "data_type": domain_info.get("data_type", "string"),
            "allowed_values": domain_info.get("allowed_values", []),
            "value_meanings": domain_info.get("value_meanings", {}),
            "validation_rule": domain_info.get("validation_rule"),
            "created_at": datetime.now()
        }
        return domain_name
    
    def add_business_term(self, term_info):
        """添加业务术语"""
        term_name = term_info["term"]
        self.business_glossary[term_name] = {
            "term": term_name,
            "definition": term_info["definition"],
            "context": term_info.get("context"),
            "synonyms": term_info.get("synonyms", []),
            "related_terms": term_info.get("related_terms", []),
            "examples": term_info.get("examples", []),
            "created_at": datetime.now()
        }
        return term_name
    
    def get_field_documentation(self, table, field):
        """获取字段文档"""
        field_id = f"{table}.{field}"
        description = self.field_descriptions.get(field_id, {})
        
        # 查找关联的值域
        domain_name = description.get("domain")
        domain_info = self.value_domains.get(domain_name) if domain_name else None
        
        return {
            "field_description": description,
            "value_domain": domain_info
        }
    
    def get_business_term(self, term):
        """获取业务术语"""
        return self.business_glossary.get(term, {})

def demo_descriptive_metadata():
    """演示描述元数据的使用"""
    print("\n" + "=" * 50)
    print("2.1.2 按功能分类 - 描述元数据")
    print("=" * 50)
    
    # 创建描述元数据管理器
    desc_metadata = DescriptiveMetadata()
    
    # 添加字段描述
    desc_metadata.add_field_description({
        "table": "users",
        "field": "user_level",
        "description": "用户等级",
        "business_meaning": "根据用户消费金额和活跃度划分的用户等级，用于差异化服务",
        "example_values": ["普通", "银卡", "金卡", "钻石"],
        "data_type": "varchar",
        "domain": "user_level_domain"
    })
    
    # 定义值域
    desc_metadata.define_value_domain({
        "name": "user_level_domain",
        "description": "用户等级的取值范围和含义",
        "data_type": "string",
        "allowed_values": ["普通", "银卡", "金卡", "钻石"],
        "value_meanings": {
            "普通": "新注册或活跃度较低的用户",
            "银卡": "有一定消费和活跃度的用户",
            "金卡": "高价值活跃用户",
            "钻石": "最高价值用户"
        }
    })
    
    # 添加业务术语
    desc_metadata.add_business_term({
        "term": "GMV",
        "definition": "商品交易总额(Gross Merchandise Volume)",
        "context": "电商业务指标",
        "synonyms": ["成交金额", "销售总额"],
        "examples": [
            "本月GMV达到5000万元",
            "通过促销活动提升GMV"
        ]
    })
    
    # 获取字段文档
    field_doc = desc_metadata.get_field_documentation("users", "user_level")
    print(f"字段 user_level 的描述: {field_doc['field_description'].get('description')}")
    print(f"业务含义: {field_doc['field_description'].get('business_meaning')}")
    
    if field_doc["value_domain"]:
        domain = field_doc["value_domain"]
        print(f"值域: {domain.get('allowed_values')}")
        print(f"值含义: {domain.get('value_meanings')}")
    
    # 获取业务术语
    gmv_term = desc_metadata.get_business_term("GMV")
    print(f"GMV定义: {gmv_term.get('definition')}")
    print(f"GMV同义词: {gmv_term.get('synonyms')}")
    
    return desc_metadata

# ===================== 管理元数据 =====================

class ManagementMetadata:
    """管理元数据管理"""
    def __init__(self):
        self.access_controls = {}    # 访问控制
        self.version_history = {}    # 版本历史
        self.change_logs = {}        # 变更日志
        self.retention_policies = {} # 保留策略
        self.data_classification = {} # 数据分类
    
    def define_access_control(self, access_info):
        """定义访问控制"""
        resource = access_info["resource"]
        if resource not in self.access_controls:
            self.access_controls[resource] = []
        
        access_rule = {
            "id": f"access_{int(datetime.now().timestamp())}",
            "resource": resource,
            "subject": access_info["subject"],  # user, role
            "permissions": access_info["permissions"],  # read, write, delete
            "conditions": access_info.get("conditions", {}),
            "granted_by": access_info.get("granted_by"),
            "granted_at": datetime.now(),
            "expires_at": access_info.get("expires_at")
        }
        
        self.access_controls[resource].append(access_rule)
        return access_rule["id"]
    
    def log_version_change(self, change_info):
        """记录版本变更"""
        resource = change_info["resource"]
        if resource not in self.version_history:
            self.version_history[resource] = []
        
        version_record = {
            "version": change_info["version"],
            "resource": resource,
            "change_type": change_info["change_type"],  # create, update, delete
            "description": change_info.get("description"),
            "changed_by": change_info.get("changed_by"),
            "changed_at": change_info.get("changed_at", datetime.now()),
            "previous_version": change_info.get("previous_version"),
            "affected_fields": change_info.get("affected_fields", []),
            "rollback_info": change_info.get("rollback_info")
        }
        
        self.version_history[resource].append(version_record)
        return version_record
    
    def classify_data(self, classification_info):
        """数据分类"""
        dataset = classification_info["dataset"]
        self.data_classification[dataset] = {
            "dataset": dataset,
            "classification": classification_info["classification"],  # public, internal, confidential, restricted
            "sensitivity_level": classification_info.get("sensitivity_level", 1),  # 1-5
            "personal_data": classification_info.get("personal_data", False),
            "special_categories": classification_info.get("special_categories", []),
            "retention_period": classification_info.get("retention_period"),
            "classified_by": classification_info.get("classified_by"),
            "classified_at": datetime.now()
        }
    
    def check_access_permission(self, user, resource, permission):
        """检查访问权限"""
        if resource not in self.access_controls:
            return False
        
        # 获取用户的角色（简化示例）
        user_roles = self._get_user_roles(user)
        
        # 检查直接用户权限
        for rule in self.access_controls[resource]:
            if rule["subject"] == user and permission in rule["permissions"]:
                if not rule["expires_at"] or rule["expires_at"] > datetime.now():
                    return True
        
        # 检查角色权限
        for role in user_roles:
            for rule in self.access_controls[resource]:
                if rule["subject"] == role and permission in rule["permissions"]:
                    if not rule["expires_at"] or rule["expires_at"] > datetime.now():
                        return True
        
        return False
    
    def _get_user_roles(self, user):
        """获取用户角色（简化实现）"""
        # 实际实现中会从用户管理系统获取
        role_mapping = {
            "alice": ["data_analyst", "user"],
            "bob": ["data_engineer"],
            "charlie": ["admin", "user"]
        }
        return role_mapping.get(user, [])
    
    def get_data_classification(self, dataset):
        """获取数据分类"""
        return self.data_classification.get(dataset)

def demo_management_metadata():
    """演示管理元数据的使用"""
    print("\n" + "=" * 50)
    print("2.1.2 按功能分类 - 管理元数据")
    print("=" * 50)
    
    # 创建管理元数据管理器
    mgmt_metadata = ManagementMetadata()
    
    # 定义访问控制
    mgmt_metadata.define_access_control({
        "resource": "ecommerce.orders",
        "subject": "data_analyst",
        "permissions": ["read"],
        "conditions": {"department": "analytics"},
        "granted_by": "admin"
    })
    
    mgmt_metadata.define_access_control({
        "resource": "ecommerce.orders",
        "subject": "data_engineer",
        "permissions": ["read", "write"],
        "granted_by": "admin"
    })
    
    # 记录版本变更
    mgmt_metadata.log_version_change({
        "resource": "ecommerce.orders",
        "version": "v2.1",
        "change_type": "update",
        "description": "添加支付方式字段",
        "changed_by": "engineer_john",
        "affected_fields": ["payment_method"]
    })
    
    # 数据分类
    mgmt_metadata.classify_data({
        "dataset": "user_profile",
        "classification": "confidential",
        "sensitivity_level": 3,
        "personal_data": True,
        "special_categories": ["PII"],
        "retention_period": "7年",
        "classified_by": "dpo_officer"
    })
    
    # 检查权限
    can_read = mgmt_metadata.check_access_permission("alice", "ecommerce.orders", "read")
    can_write = mgmt_metadata.check_access_permission("alice", "ecommerce.orders", "write")
    print(f"用户Alice是否有读取权限: {can_read}")
    print(f"用户Alice是否有写入权限: {can_write}")
    
    can_read_bob = mgmt_metadata.check_access_permission("bob", "ecommerce.orders", "write")
    print(f"用户Bob是否有写入权限: {can_read_bob}")
    
    # 查看数据分类
    user_profile_class = mgmt_metadata.get_data_classification("user_profile")
    if user_profile_class:
        print(f"user_profile数据分类: {user_profile_class.get('classification')}")
        print(f"敏感级别: {user_profile_class.get('sensitivity_level')}")
        print(f"包含个人数据: {user_profile_class.get('personal_data')}")
    
    return mgmt_metadata

# ===================== 2.2 元数据的多维分类模型 =====================

class EnterpriseMetadataClassification:
    """企业级元数据分类模型"""
    def __init__(self):
        self.metadata_hierarchy = {
            "business": {
                "data_governance": {
                    "ownership": [],
                    "stewardship": [],
                    "classification": []
                },
                "business_glossary": {
                    "terms": [],
                    "definitions": [],
                    "relationships": []
                },
                "business_rules": {
                    "validation": [],
                    "transformation": [],
                    "calculation": []
                }
            },
            "technical": {
                "physical_models": {
                    "databases": [],
                    "tables": [],
                    "columns": []
                },
                "logical_models": {
                    "entities": [],
                    "attributes": [],
                    "relationships": []
                },
                "system_architecture": {
                    "applications": [],
                    "interfaces": [],
                    "infrastructure": []
                }
            },
            "operational": {
                "data_quality": {
                    "metrics": [],
                    "profiles": [],
                    "issues": []
                },
                "lineage": {
                    "upstream": [],
                    "downstream": [],
                    "transformations": []
                },
                "lifecycle": {
                    "creation": [],
                    "modification": [],
                    "archival": []
                }
            }
        }
    
    def classify_metadata(self, metadata_info):
        """对元数据进行分类"""
        category = metadata_info["category"]
        subcategory = metadata_info["subcategory"]
        metadata_type = metadata_info["type"]
        content = metadata_info["content"]
        
        if category in self.metadata_hierarchy:
            if subcategory in self.metadata_hierarchy[category]:
                if metadata_type in self.metadata_hierarchy[category][subcategory]:
                    self.metadata_hierarchy[category][subcategory][metadata_type].append({
                        "content": content,
                        "created_at": datetime.now()
                    })
                    return True
        return False
    
    def get_metadata_by_category(self, category, subcategory=None, metadata_type=None):
        """按类别获取元数据"""
        result = self.metadata_hierarchy
        
        if category and category in result:
            result = result[category]
            if subcategory and subcategory in result:
                result = result[subcategory]
                if metadata_type and metadata_type in result:
                    result = result[metadata_type]
        
        return result

def demo_enterprise_classification():
    """演示企业级元数据分类模型"""
    print("\n" + "=" * 50)
    print("2.2 元数据的多维分类模型")
    print("=" * 50)
    
    # 创建企业级分类器
    enterprise_classifier = EnterpriseMetadataClassification()
    
    # 分类元数据
    enterprise_classifier.classify_metadata({
        "category": "business",
        "subcategory": "data_governance",
        "type": "ownership",
        "content": {
            "dataset": "customer_data",
            "owner": "customer_department",
            "contact": "manager@example.com"
        }
    })
    
    enterprise_classifier.classify_metadata({
        "category": "technical",
        "subcategory": "physical_models",
        "type": "tables",
        "content": {
            "name": "customers",
            "schema": "public",
            "columns": ["id", "name", "email"],
            "primary_key": "id"
        }
    })
    
    enterprise_classifier.classify_metadata({
        "category": "operational",
        "subcategory": "lineage",
        "type": "transformations",
        "content": {
            "source": "raw_customer_data",
            "target": "clean_customer_data",
            "transformation": "data_cleaning_job"
        }
    })
    
    # 获取元数据
    business_metadata = enterprise_classifier.get_metadata_by_category("business")
    technical_tables = enterprise_classifier.get_metadata_by_category("technical", "physical_models", "tables")
    
    print(f"业务元数据类别数: {len(business_metadata)}")
    print(f"技术表元数据数量: {len(technical_tables)}")
    
    # 显示元数据内容
    for category, subcategories in business_metadata.items():
        print(f"\n{category} 类别:")
        for subcategory, metadata_types in subcategories.items():
            print(f"  {subcategory}:")
            for metadata_type, items in metadata_types.items():
                print(f"    {metadata_type}: {len(items)} 条记录")
    
    return enterprise_classifier

# ===================== 2.3 元数据标准与规范 =====================

# ===================== ISO/IEC 11179标准 =====================

class ISO11179MetadataRegistry:
    """基于ISO/IEC 11179的元数据注册系统"""
    def __init__(self):
        self.data_elements = {}      # 数据元素
        self.data_element_concepts = {}  # 数据元素概念
        self.object_classes = {}     # 对象类
        self.properties = {}         # 属性
        self.representations = {}     # 表示
    
    def register_object_class(self, class_info):
        """注册对象类"""
        class_id = class_info["name"]
        self.object_classes[class_id] = {
            "name": class_info["name"],
            "definition": class_info["definition"],
            "registration_authority": class_info.get("registration_authority"),
            "submitted_by": class_info.get("submitted_by"),
            "registered_at": datetime.now()
        }
        return class_id
    
    def register_property(self, property_info):
        """注册属性"""
        property_id = property_info["name"]
        self.properties[property_id] = {
            "name": property_info["name"],
            "definition": property_info["definition"],
            "data_type": property_info.get("data_type"),
            "registration_authority": property_info.get("registration_authority"),
            "submitted_by": property_info.get("submitted_by"),
            "registered_at": datetime.now()
        }
        return property_id
    
    def register_data_element(self, element_info):
        """注册数据元素"""
        element_id = f"{element_info['object_class']}.{element_info['property']}"
        self.data_elements[element_id] = {
            "identifier": element_id,
            "name": element_info["name"],
            "object_class": element_info["object_class"],
            "property": element_info["property"],
            "representation": element_info.get("representation"),
            "definition": element_info.get("definition"),
            "registration_authority": element_info.get("registration_authority"),
            "submitted_by": element_info.get("submitted_by"),
            "registered_at": datetime.now()
        }
        return element_id
    
    def get_data_element(self, element_id):
        """获取数据元素详情"""
        element = self.data_elements.get(element_id)
        if not element:
            return None
        
        # 获取关联的对象类和属性信息
        object_class = self.object_classes.get(element["object_class"])
        property = self.properties.get(element["property"])
        representation = self.representations.get(element["representation"])
        
        return {
            "data_element": element,
            "object_class": object_class,
            "property": property,
            "representation": representation
        }
    
    def search_data_elements(self, search_criteria):
        """搜索数据元素"""
        results = []
        
        for element_id, element in self.data_elements.items():
            match = True
            
            # 简单搜索实现
            if "object_class" in search_criteria:
                if element["object_class"] != search_criteria["object_class"]:
                    match = False
            
            if "property" in search_criteria and match:
                if element["property"] != search_criteria["property"]:
                    match = False
            
            if match:
                results.append(self.get_data_element(element_id))
        
        return results

def demo_iso11179_standard():
    """演示ISO/IEC 11179标准的使用"""
    print("\n" + "=" * 50)
    print("2.3 元数据标准与规范 - ISO/IEC 11179")
    print("=" * 50)
    
    # 创建ISO11179注册系统
    iso_registry = ISO11179MetadataRegistry()
    
    # 注册对象类
    iso_registry.register_object_class({
        "name": "Person",
        "definition": "具有人类特征的自然人",
        "registration_authority": "ISO",
        "submitted_by": "metadata_admin"
    })
    
    iso_registry.register_object_class({
        "name": "Order",
        "definition": "客户购买商品的商业交易记录",
        "registration_authority": "ISO",
        "submitted_by": "metadata_admin"
    })
    
    # 注册属性
    iso_registry.register_property({
        "name": "Name",
        "definition": "用于标识个人或实体的文字符号",
        "data_type": "string",
        "registration_authority": "ISO",
        "submitted_by": "metadata_admin"
    })
    
    iso_registry.register_property({
        "name": "Amount",
        "definition": "交易或订单的货币价值",
        "data_type": "decimal",
        "registration_authority": "ISO",
        "submitted_by": "metadata_admin"
    })
    
    # 注册数据元素
    iso_registry.register_data_element({
        "name": "PersonName",
        "object_class": "Person",
        "property": "Name",
        "definition": "个人的姓名",
        "representation": "text",
        "registration_authority": "Company",
        "submitted_by": "data_steward"
    })
    
    iso_registry.register_data_element({
        "name": "OrderAmount",
        "object_class": "Order",
        "property": "Amount",
        "definition": "订单金额",
        "representation": "decimal",
        "registration_authority": "Company",
        "submitted_by": "data_steward"
    })
    
    # 查询数据元素
    person_name = iso_registry.get_data_element("Person.Name")
    print(f"Person.Name 数据元素:")
    print(f"  对象类: {person_name['object_class']['name']}")
    print(f"  属性: {person_name['property']['name']}")
    print(f"  定义: {person_name['data_element']['definition']}")
    
    # 搜索数据元素
    search_results = iso_registry.search_data_elements({"object_class": "Order"})
    print(f"\nOrder对象类的数据元素数量: {len(search_results)}")
    
    return iso_registry

# ===================== Dublin Core标准 =====================

class DublinCoreMetadata:
    """Dublin Core元数据标准实现"""
    def __init__(self):
        self.elements = {
            "title": "资源名称",
            "creator": "创建者",
            "subject": "主题",
            "description": "描述",
            "publisher": "发布者",
            "contributor": "贡献者",
            "date": "日期",
            "type": "类型",
            "format": "格式",
            "identifier": "标识符",
            "source": "来源",
            "language": "语言",
            "relation": "关联",
            "coverage": "覆盖范围",
            "rights": "权限"
        }
        self.resources = {}
    
    def register_resource(self, resource_id, metadata):
        """注册资源及其Dublin Core元数据"""
        validated_metadata = {}
        
        # 验证元数据元素
        for element, value in metadata.items():
            if element in self.elements:
                validated_metadata[element] = value
            else:
                print(f"警告: 未知元数据元素 '{element}'")
        
        # 添加内部元数据
        validated_metadata["_registered_at"] = datetime.now()
        
        self.resources[resource_id] = validated_metadata
        return resource_id
    
    def search_resources(self, search_criteria):
        """根据Dublin Core元数据搜索资源"""
        results = []
        
        for resource_id, metadata in self.resources.items():
            match = True
            
            for element, search_value in search_criteria.items():
                if element not in metadata:
                    match = False
                    break
                
                # 简单的字符串匹配（实际应用中可以更复杂）
                if search_value.lower() not in str(metadata[element]).lower():
                    match = False
                    break
            
            if match:
                results.append({
                    "resource_id": resource_id,
                    "metadata": metadata
                })
        
        return results
    
    def get_resource(self, resource_id):
        """获取资源元数据"""
        return self.resources.get(resource_id)
    
    def export_to_xml(self, resource_id):
        """导出为XML格式（简化实现）"""
        if resource_id not in self.resources:
            return None
        
        metadata = self.resources[resource_id]
        xml_lines = ['<dc:dc xmlns:dc="http://purl.org/dc/elements/1.1/">']
        
        for element, value in metadata.items():
            if element.startswith('_'):  # 跳过内部元数据
                continue
            xml_lines.append(f'  <dc:{element}>{value}</dc:{element}>')
        
        xml_lines.append('</dc:dc>')
        return '\n'.join(xml_lines)

def demo_dublin_core_standard():
    """演示Dublin Core标准的使用"""
    print("\n" + "=" * 50)
    print("2.3 元数据标准与规范 - Dublin Core")
    print("=" * 50)
    
    # 创建Dublin Core元数据注册表
    dc_registry = DublinCoreMetadata()
    
    # 注册数据集
    dc_registry.register_resource("sales_report_2023", {
        "title": "2023年销售数据分析报告",
        "creator": "数据分析团队",
        "subject": "销售分析, 年度报告",
        "description": "2023年度销售数据的综合分析，包括各产品线、地区、渠道的详细分析",
        "publisher": "公司数据部门",
        "date": "2024-01-15",
        "type": "报告",
        "format": "PDF",
        "identifier": "REPORT-SALES-2023-001",
        "language": "zh-CN"
    })
    
    # 注册另一个数据集
    dc_registry.register_resource("customer_behavior_analysis", {
        "title": "客户行为分析数据集",
        "creator": "用户研究团队",
        "subject": "用户行为, 客户分析",
        "description": "包含用户访问、购买、互动等行为数据",
        "publisher": "用户增长部门",
        "date": "2024-02-20",
        "type": "数据集",
        "format": "CSV",
        "identifier": "DATA-CUSTOMER-2024-001",
        "language": "zh-CN"
    })
    
    # 搜索资源
    search_results = dc_registry.search_resources({
        "type": "报告"
    })
    print(f"类型为'报告'的资源数量: {len(search_results)}")
    
    # 获取特定资源
    report_resource = dc_registry.get_resource("sales_report_2023")
    if report_resource:
        print(f"\n销售报告标题: {report_resource.get('title')}")
        print(f"创建者: {report_resource.get('creator')}")
        print(f"描述: {report_resource.get('description')[:50]}...")
    
    # 导出XML
    xml_metadata = dc_registry.export_to_xml("sales_report_2023")
    print(f"\nXML导出结果:\n{xml_metadata}")
    
    return dc_registry

# ===================== 主函数 - 运行所有演示 =====================

def main():
    """运行所有演示示例"""
    print("第2章：元数据类型与分类 - 代码示例")
    print("=" * 80)
    
    # 演示不同抽象层次的元数据
    business_manager = demo_business_metadata()
    tech_manager = demo_technical_metadata()
    ops_manager = demo_operational_metadata()
    
    # 演示不同功能的元数据
    structural_metadata = demo_structural_metadata()
    desc_metadata = demo_descriptive_metadata()
    mgmt_metadata = demo_management_metadata()
    
    # 演示企业级分类模型
    enterprise_classifier = demo_enterprise_classification()
    
    # 演示元数据标准
    iso_registry = demo_iso11179_standard()
    dc_registry = demo_dublin_core_standard()
    
    print("\n" + "=" * 80)
    print("所有演示完成！您可以根据自己的需求修改和扩展这些示例。")

if __name__ == "__main__":
    main()