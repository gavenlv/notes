#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第7章：元数据工具与平台 代码示例
本文件包含元数据工具与平台的实用代码示例，可直接运行
"""

import json
import random
from datetime import datetime, timedelta

# ====================
# 7.1 元数据工具比较分析
# ====================

class MetadataToolComparison:
    """
    元数据工具比较分析
    提供不同工具的功能、优缺点对比
    """
    
    def __init__(self):
        self.tools = {
            "Apache Atlas": {
                "type": "开源",
                "deployment": ["本地", "云"],
                "core_features": [
                    "元数据存储库",
                    "数据分类和标签",
                    "数据血缘追踪",
                    "安全与治理"
                ],
                "strengths": [
                    "开源免费，社区活跃",
                    "功能全面，扩展性好",
                    "与Hadoop生态系统集成度高"
                ],
                "weaknesses": [
                    "学习曲线陡峭",
                    "需要专业技术团队",
                    "UI相对简单"
                ],
                "best_for": [
                    "使用Hadoop生态系统的组织",
                    "有一定技术实力的团队",
                    "需要高度定制的场景"
                ],
                "license": "Apache License 2.0"
            },
            "DataHub": {
                "type": "开源",
                "deployment": ["本地", "云"],
                "core_features": [
                    "数据发现和搜索",
                    "数据血缘追踪",
                    "数据质量监控",
                    "数据集生命周期管理"
                ],
                "strengths": [
                    "现代架构设计",
                    "GraphQL API支持",
                    "UI界面友好",
                    "易于集成"
                ],
                "weaknesses": [
                    "功能相对有限",
                    "社区规模小于Atlas",
                    "高级功能需要商业版"
                ],
                "best_for": [
                    "注重用户体验的组织",
                    "需要快速实施的项目",
                    "现代化技术栈团队"
                ],
                "license": "Apache License 2.0"
            },
            "Amundsen": {
                "type": "开源",
                "deployment": ["本地", "云"],
                "core_features": [
                    "数据发现和搜索",
                    "元数据管理",
                    "数据使用分析",
                    "API优先设计"
                ],
                "strengths": [
                    "专注于数据发现",
                    "搜索引擎技术(Elasticsearch)强大",
                    "API设计良好",
                    "可扩展性强"
                ],
                "weaknesses": [
                    "功能较为专一",
                    "数据血缘功能有限",
                    "需要较多配置"
                ],
                "best_for": [
                    "主要关注数据发现的组织",
                    "有开发能力的团队",
                    "需要API集成的场景"
                ],
                "license": "Apache License 2.0"
            },
            "Collibra": {
                "type": "商业",
                "deployment": ["本地", "云", "混合"],
                "core_features": [
                    "企业数据目录",
                    "数据治理工作流",
                    "数据血缘",
                    "数据质量监控"
                ],
                "strengths": [
                    "功能全面完整",
                    "强大的工作流引擎",
                    "企业级安全",
                    "专业支持服务"
                ],
                "weaknesses": [
                    "价格昂贵",
                    "实施复杂",
                    "定制灵活性有限"
                ],
                "best_for": [
                    "大型企业",
                    "合规要求高的行业",
                    "需要全面治理的组织"
                ],
                "license": "商业许可"
            },
            "Alation": {
                "type": "商业",
                "deployment": ["云", "混合"],
                "core_features": [
                    "数据目录",
                    "数据发现",
                    "数据治理",
                    "协作功能"
                ],
                "strengths": [
                    "用户体验优秀",
                    "AI驱动的数据发现",
                    "强大的协作功能",
                    "知识库集成"
                ],
                "weaknesses": [
                    "定制能力有限",
                    "价格较高",
                    "主要依赖云部署"
                ],
                "best_for": [
                    "注重协作的企业",
                    "数据驱动型组织",
                    "需要快速上手的企业"
                ],
                "license": "商业许可"
            },
            "Informatica Enterprise Data Catalog": {
                "type": "商业",
                "deployment": ["本地", "云", "混合"],
                "core_features": [
                    "企业数据目录",
                    "智能数据发现",
                    "数据血缘",
                    "元数据管理"
                ],
                "strengths": [
                    "企业级功能丰富",
                    "AI/ML集成度高",
                    "与Informatica其他产品集成好",
                    "强大的数据连接器"
                ],
                "weaknesses": [
                    "复杂度高",
                    "价格昂贵",
                    "需要专业团队"
                ],
                "best_for": [
                    "已使用Informatica产品的组织",
                    "大型企业",
                    "复杂的数据环境"
                ],
                "license": "商业许可"
            }
        }
    
    def compare_tools(self, tool_names=None, criteria=None):
        """比较工具"""
        if tool_names is None:
            tool_names = list(self.tools.keys())
        
        if criteria is None:
            criteria = ["type", "deployment", "core_features", "strengths", "weaknesses"]
        
        comparison = {}
        
        for tool_name in tool_names:
            if tool_name not in self.tools:
                continue
                
            tool_info = self.tools[tool_name]
            comparison[tool_name] = {}
            
            for criterion in criteria:
                if criterion in tool_info:
                    comparison[tool_name][criterion] = tool_info[criterion]
        
        return comparison
    
    def recommend_tool(self, requirements):
        """根据需求推荐工具"""
        recommendations = []
        
        for tool_name, tool_info in self.tools.items():
            score = 0
            
            # 根据需求类型评分
            if "deployment" in requirements:
                if requirements["deployment"] in tool_info["deployment"]:
                    score += 2
            
            if "budget" in requirements:
                if requirements["budget"] == "low" and tool_info["type"] == "开源":
                    score += 3
                elif requirements["budget"] == "high" and tool_info["type"] == "商业":
                    score += 1
            
            if "organization_size" in requirements:
                if requirements["organization_size"] == "large" and tool_info["type"] == "商业":
                    score += 2
                elif requirements["organization_size"] in ["small", "medium"] and tool_info["type"] == "开源":
                    score += 2
            
            if "team_capability" in requirements:
                if requirements["team_capability"] == "technical" and tool_info["type"] == "开源":
                    score += 2
                elif requirements["team_capability"] == "business" and tool_info["type"] == "商业":
                    score += 2
            
            if "features" in requirements:
                tool_features = set(tool_info["core_features"])
                required_features = set(requirements["features"])
                overlap = len(tool_features.intersection(required_features))
                score += overlap
            
            recommendations.append({
                "tool": tool_name,
                "score": score,
                "match_percentage": (score / 10) * 100,  # 简化的匹配百分比
                "reasons": self._generate_reasons(tool_name, requirements)
            })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    def _generate_reasons(self, tool_name, requirements):
        """生成推荐理由"""
        tool_info = self.tools[tool_name]
        reasons = []
        
        # 类型匹配
        if "budget" in requirements:
            if requirements["budget"] == "low" and tool_info["type"] == "开源":
                reasons.append("开源工具，符合低预算需求")
            elif requirements["budget"] == "high" and tool_info["type"] == "商业":
                reasons.append("商业工具，提供全面功能和专业支持")
        
        # 部署方式匹配
        if "deployment" in requirements:
            if requirements["deployment"] in tool_info["deployment"]:
                reasons.append(f"支持{requirements['deployment']}部署方式")
        
        # 功能匹配
        if "features" in requirements:
            tool_features = set(tool_info["core_features"])
            required_features = set(requirements["features"])
            overlap = tool_features.intersection(required_features)
            if overlap:
                reasons.append(f"提供所需功能: {', '.join(overlap)}")
        
        # 规模匹配
        if "organization_size" in requirements:
            if requirements["organization_size"] == "large" and tool_info["type"] == "商业":
                reasons.append("企业级工具，适合大型组织")
            elif requirements["organization_size"] in ["small", "medium"] and tool_info["type"] == "开源":
                reasons.append("开源工具，适合中小型组织")
        
        if not reasons:
            reasons.append("基于综合评估的推荐")
        
        return reasons
    
    def get_implementation_roadmap(self, tool_name, scale="medium"):
        """获取工具实施路线图"""
        if tool_name not in self.tools:
            return None
        
        tool_type = self.tools[tool_name]["type"]
        
        # 基础路线图框架
        roadmap = {
            "tool_name": tool_name,
            "implementation_phases": []
        }
        
        if tool_type == "开源":
            # 开源工具实施路线图
            roadmap["implementation_phases"] = [
                {
                    "phase": "准备阶段",
                    "duration": "4-6周",
                    "activities": [
                        "需求分析和范围定义",
                        "技术环境准备",
                        "团队组建和培训",
                        "工具安装和配置"
                    ]
                },
                {
                    "phase": "基础实施",
                    "duration": "6-8周",
                    "activities": [
                        "元数据模型设计",
                        "核心数据源集成",
                        "基础功能实现",
                        "用户培训"
                    ]
                },
                {
                    "phase": "功能扩展",
                    "duration": "8-10周",
                    "activities": [
                        "高级功能开发",
                        "定制化实现",
                        "全面测试",
                        "性能优化"
                    ]
                },
                {
                    "phase": "全面推广",
                    "duration": "4-6周",
                    "activities": [
                        "全面上线",
                        "用户培训和支持",
                        "反馈收集和改进",
                        "文档完善"
                    ]
                }
            ]
        else:
            # 商业工具实施路线图
            roadmap["implementation_phases"] = [
                {
                    "phase": "规划和准备",
                    "duration": "2-4周",
                    "activities": [
                        "供应商选择和合同谈判",
                        "需求详细分析",
                        "实施团队组建",
                        "环境准备"
                    ]
                },
                {
                    "phase": "基础配置",
                    "duration": "4-6周",
                    "activities": [
                        "工具安装和基础配置",
                        "元数据模型定制",
                        "数据源连接",
                        "基础功能测试"
                    ]
                },
                {
                    "phase": "集成和定制",
                    "duration": "6-8周",
                    "activities": [
                        "数据源集成",
                        "工作流定制",
                        "用户界面调整",
                        "安全配置"
                    ]
                },
                {
                    "phase": "试点和优化",
                    "duration": "4-6周",
                    "activities": [
                        "试点部门实施",
                        "用户反馈收集",
                        "系统优化和调整",
                        "全面培训"
                    ]
                },
                {
                    "phase": "全面上线",
                    "duration": "2-4周",
                    "activities": [
                        "全组织推广",
                        "运营和支持体系建立",
                        "效果评估",
                        "持续改进计划"
                    ]
                }
            ]
        
        # 根据规模调整时间
        if scale == "small":
            for phase in roadmap["implementation_phases"]:
                # 减少时间
                duration = phase["duration"].split("-")
                min_weeks = int(duration[0].replace("周", ""))
                max_weeks = int(duration[1].replace("周", ""))
                new_min = int(min_weeks * 0.7)
                new_max = int(max_weeks * 0.7)
                phase["duration"] = f"{new_min}-{new_max}周"
        
        elif scale == "large":
            for phase in roadmap["implementation_phases"]:
                # 增加时间
                duration = phase["duration"].split("-")
                min_weeks = int(duration[0].replace("周", ""))
                max_weeks = int(duration[1].replace("周", ""))
                new_min = int(min_weeks * 1.3)
                new_max = int(max_weeks * 1.3)
                phase["duration"] = f"{new_min}-{new_max}周"
        
        return roadmap


# ====================
# 7.2 Apache Atlas 元数据管理器
# ====================

class AtlasMetadataManager:
    """
    Apache Atlas元数据管理器
    提供与Atlas交互的核心功能
    """
    
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:{port}/api/atlas/v2"
        self.auth = (username, password)
    
    def create_entity_type(self, type_definition):
        """创建实体类型"""
        endpoint = f"{self.base_url}/types/typedefs"
        
        # 简化的请求构建
        payload = {
            "entityDefs": [type_definition]
        }
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.post(endpoint, json=payload, auth=self.auth)
        # return response.json()
        
        # 模拟返回
        return {
            "entityDefs": [
                {
                    "name": type_definition["name"],
                    "createdBy": self.username,
                    "date": datetime.now().isoformat()
                }
            ]
        }
    
    def create_entity(self, entity):
        """创建实体"""
        endpoint = f"{self.base_url}/entity"
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.post(endpoint, json=entity, auth=self.auth)
        # return response.json()
        
        # 模拟返回
        return {
            "entity": {
                "guid": f"guid-{random.randint(1000, 9999)}",
                "status": "ACTIVE",
                "createdBy": self.username,
                "updatedBy": self.username,
                "createTime": datetime.now().isoformat(),
                "updateTime": datetime.now().isoformat(),
                "version": 1
            }
        }
    
    def get_entity(self, guid):
        """获取实体"""
        endpoint = f"{self.base_url}/entity/guid/{guid}"
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.get(endpoint, auth=self.auth)
        # return response.json()
        
        # 模拟返回
        return {
            "entity": {
                "guid": guid,
                "status": "ACTIVE",
                "type": "DataSet",
                "attributes": {
                    "name": "customer_data",
                    "qualifiedName": "customer_data@primary",
                    "description": "客户基本信息数据集"
                }
            }
        }
    
    def search_entities(self, query, limit=10, offset=0):
        """搜索实体"""
        endpoint = f"{self.base_url}/search/basic"
        
        params = {
            "query": query,
            "limit": limit,
            "offset": offset
        }
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.get(endpoint, params=params, auth=self.auth)
        # return response.json()
        
        # 模拟返回
        return {
            "searchResults": [
                {
                    "entity": {
                        "guid": f"guid-{random.randint(1000, 9999)}",
                        "type": "DataSet",
                        "attributes": {
                            "name": f"result_{i}",
                            "description": f"搜索结果 {i}"
                        }
                    }
                }
                for i in range(min(3, limit))
            ],
            "searchParameters": {
                "query": query,
                "limit": limit,
                "offset": offset
            }
        }
    
    def get_lineage(self, guid):
        """获取数据血缘"""
        endpoint = f"{self.base_url}/lineage/{guid}"
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.get(endpoint, auth=self.auth)
        # return response.json()
        
        # 模拟返回
        return {
            "guidEntityMap": {
                "guid-1001": {
                    "guid": "guid-1001",
                    "typeName": "DataSet",
                    "attributes": {
                        "name": "raw_customer_data",
                        "qualifiedName": "raw_customer_data@primary"
                    }
                },
                "guid-1002": {
                    "guid": "guid-1002",
                    "typeName": "DataSet",
                    "attributes": {
                        "name": "clean_customer_data",
                        "qualifiedName": "clean_customer_data@primary"
                    }
                },
                "guid-1003": {
                    "guid": "guid-1003",
                    "typeName": "Process",
                    "attributes": {
                        "name": "customer_etl_process",
                        "qualifiedName": "customer_etl_process@primary"
                    }
                }
            },
            "relations": [
                {
                    "fromEntityId": "guid-1001",
                    "toEntityId": "guid-1003",
                    "relationshipType": "DataSetProcessInputs"
                },
                {
                    "fromEntityId": "guid-1003",
                    "toEntityId": "guid-1002",
                    "relationshipType": "ProcessDataSetOutputs"
                }
            ]
        }


# ====================
# 7.3 DataHub 元数据管理器
# ====================

class DataHubMetadataManager:
    """
    DataHub元数据管理器
    提供与DataHub交互的核心功能
    """
    
    def __init__(self, server_url, token=None):
        self.server_url = server_url
        self.token = token
        self.graphql_endpoint = f"{server_url}/api/graphql"
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def create_dataset(self, urn, name, description, properties=None):
        """创建数据集"""
        mutation = """
        mutation createDataset($input: DatasetInput!) {
            createDataset(input: $input) {
                dataset {
                    urn
                    name
                    description
                    properties {
                        customProperties {
                            key
                            value
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "urn": urn,
                "name": name,
                "description": description,
                "properties": properties or {}
            }
        }
        
        # 在实际应用中，这里应该使用requests库发送GraphQL请求
        # response = requests.post(
        #     self.graphql_endpoint,
        #     json={"query": mutation, "variables": variables},
        #     headers=self.headers
        # )
        # return response.json()
        
        # 模拟返回
        return {
            "data": {
                "createDataset": {
                    "dataset": {
                        "urn": urn,
                        "name": name,
                        "description": description,
                        "properties": {
                            "customProperties": properties or {}
                        }
                    }
                }
            }
        }
    
    def search_entities(self, query, entity_type="DATASET", start=0, count=10):
        """搜索实体"""
        gql_query = """
        query search($input: SearchInput!) {
            search(input: $input) {
                start
                count
                total
                searchResults {
                    entity {
                        urn
                        type
                        ... on Dataset {
                            name
                            description
                            origin
                            tags {
                                tag {
                                    name
                                }
                            }
                        }
                    }
                    matchedFields
                    score
                }
            }
        }
        """
        
        variables = {
            "input": {
                "type": entity_type,
                "query": query,
                "start": start,
                "count": count
            }
        }
        
        # 在实际应用中，这里应该使用requests库发送GraphQL请求
        # response = requests.post(
        #     self.graphql_endpoint,
        #     json={"query": gql_query, "variables": variables},
        #     headers=self.headers
        # )
        # return response.json()
        
        # 模拟返回
        return {
            "data": {
                "search": {
                    "start": 0,
                    "count": min(3, count),
                    "total": min(3, count),
                    "searchResults": [
                        {
                            "entity": {
                                "urn": f"urn:li:dataset:(urn:li:dataPlatform:hive,test_dataset_{i})",
                                "type": "DATASET",
                                "name": f"test_dataset_{i}",
                                "description": f"测试数据集 {i}",
                                "origin": "PROD",
                                "tags": {
                                    "tag": [{"name": "test"}]
                                }
                            },
                            "matchedFields": ["name"],
                            "score": 0.95 - i * 0.1
                        }
                        for i in range(min(3, count))
                    ]
                }
            }
        }
    
    def get_lineage(self, urn, direction="BOTH", max_hops=3):
        """获取数据血缘"""
        gql_query = """
        query getLineage($input: LineageInput!) {
            getLineage(input: $input) {
                total
                relationships {
                    entity {
                        urn
                        type
                    }
                    degree
                    ... on Dataset {
                        name
                        description
                    }
                }
            }
        }
        """
        
        variables = {
            "input": {
                "urn": urn,
                "direction": direction,
                "maxHops": max_hops
            }
        }
        
        # 在实际应用中，这里应该使用requests库发送GraphQL请求
        # response = requests.post(
        #     self.graphql_endpoint,
        #     json={"query": gql_query, "variables": variables},
        #     headers=self.headers
        # )
        # return response.json()
        
        # 模拟返回
        return {
            "data": {
                "getLineage": {
                    "total": 4,
                    "relationships": [
                        {
                            "entity": {
                                "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,raw_customer_data)",
                                "type": "DATASET",
                                "name": "raw_customer_data",
                                "description": "原始客户数据"
                            },
                            "degree": 1
                        },
                        {
                            "entity": {
                                "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,clean_customer_data)",
                                "type": "DATASET",
                                "name": "clean_customer_data",
                                "description": "清洗后客户数据"
                            },
                            "degree": 0
                        },
                        {
                            "entity": {
                                "urn": "urn:li:dataset:(urn:li:dataPlatform:hive,customer_metrics)",
                                "type": "DATASET",
                                "name": "customer_metrics",
                                "description": "客户指标数据"
                            },
                            "degree": -1
                        }
                    ]
                }
            }
        }
    
    def add_tags(self, urn, tags):
        """添加标签"""
        mutation = """
        mutation addTags($input: TagsInput!) {
            addTags(input: $input)
        }
        """
        
        variables = {
            "input": {
                "urn": urn,
                "tags": tags
            }
        }
        
        # 在实际应用中，这里应该使用requests库发送GraphQL请求
        # response = requests.post(
        #     self.graphql_endpoint,
        #     json={"query": mutation, "variables": variables},
        #     headers=self.headers
        # )
        # return response.json()
        
        # 模拟返回
        return {
            "data": {
                "addTags": True
            }
        }
    
    def get_dataset_stats(self, urn):
        """获取数据集统计信息"""
        gql_query = """
        query getDatasetStats($urn: String!) {
            dataset(urn: $urn) {
                ... on Dataset {
                    name
                    description
                    lastModified {
                        time
                        actor
                    }
                    dataHub {
                        viewCount
                        lastViewed
                    }
                    properties {
                        customProperties {
                            key
                            value
                        }
                    }
                }
            }
        }
        """
        
        variables = {
            "urn": urn
        }
        
        # 在实际应用中，这里应该使用requests库发送GraphQL请求
        # response = requests.post(
        #     self.graphql_endpoint,
        #     json={"query": gql_query, "variables": variables},
        #     headers=self.headers
        # )
        # return response.json()
        
        # 模拟返回
        return {
            "data": {
                "dataset": {
                    "name": "customer_data",
                    "description": "客户基本信息数据",
                    "lastModified": {
                        "time": 1640995200000,
                        "actor": "urn:li:corpuser:data_admin"
                    },
                    "dataHub": {
                        "viewCount": 127,
                        "lastViewed": 1640995200000
                    },
                    "properties": {
                        "customProperties": [
                            {"key": "business_domain", "value": "销售"},
                            {"key": "data_quality_score", "value": "0.92"}
                        ]
                    }
                }
            }
        }


# ====================
# 7.4 Amundsen 元数据管理器
# ====================

class AmundsenMetadataManager:
    """
    Amundsen元数据管理器
    提供与Amundsen交互的核心功能
    """
    
    def __init__(self, metadata_service_url, search_service_url):
        self.metadata_service_url = metadata_service_url
        self.search_service_url = search_service_url
        self.headers = {"Content-Type": "application/json"}
    
    def publish_table(self, table_metadata):
        """发布表元数据"""
        endpoint = f"{self.metadata_service_url}/table"
        
        # 构建表元数据结构
        payload = {
            "name": table_metadata["name"],
            "description": table_metadata.get("description", ""),
            "cluster": table_metadata.get("cluster", "prod"),
            "database": table_metadata["database"],
            "schema": table_metadata["schema"],
            "columns": table_metadata.get("columns", []),
            "tags": table_metadata.get("tags", []),
            "table_readme": table_metadata.get("readme", ""),
            "is_view": table_metadata.get("is_view", False)
        }
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.put(endpoint, json=payload, headers=self.headers)
        # return response.json()
        
        # 模拟返回
        return {
            "table": {
                "name": table_metadata["name"],
                "cluster": table_metadata.get("cluster", "prod"),
                "database": table_metadata["database"],
                "schema": table_metadata["schema"]
            },
            "status": "published"
        }
    
    def search_tables(self, query_term, page_index=0, results_per_page=10):
        """搜索表"""
        endpoint = f"{self.search_service_url}/search"
        
        payload = {
            "query_term": query_term,
            "page_index": page_index,
            "results_per_page": results_per_page
        }
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.post(endpoint, json=payload, headers=self.headers)
        # return response.json()
        
        # 模拟返回
        return {
            "total_results": min(3, results_per_page),
            "results": [
                {
                    "type": "table",
                    "name": f"test_table_{i}",
                    "cluster": "prod",
                    "database": "test_db",
                    "schema": "public",
                    "description": f"测试表 {i}",
                    "tags": ["test"],
                    "badges": [],
                    "last_updated_timestamp": 1640995200000
                }
                for i in range(min(3, results_per_page))
            ]
        }
    
    def get_table_metadata(self, database, cluster, schema, table):
        """获取表元数据"""
        endpoint = f"{self.metadata_service_url}/table/{database}/{cluster}/{schema}/{table}"
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.get(endpoint, headers=self.headers)
        # return response.json()
        
        # 模拟返回
        return {
            "table": {
                "name": table,
                "description": f"表 {table} 的描述",
                "cluster": cluster,
                "database": database,
                "schema": schema,
                "columns": [
                    {
                        "name": f"col_{i}",
                        "description": f"列 {i} 的描述",
                        "col_type": "varchar",
                        "sort_order": i
                    }
                    for i in range(5)
                ],
                "table_readme": "# 表说明\n这是一个示例表",
                "is_view": False,
                "tags": ["test", "example"],
                "badges": [],
                "last_updated_timestamp": 1640995200000
            },
            "owners": [
                {
                    "user_id": "user1",
                    "profile_url": "http://example.com/user/user1",
                    "display_name": "User One"
                }
            ],
            "source": {
                "name": "test_source",
                "source_type": "mysql"
            }
        }
    
    def add_table_tag(self, database, cluster, schema, table, tag):
        """为表添加标签"""
        endpoint = f"{self.metadata_service_url}/table/tag"
        
        payload = {
            "tag": tag,
            "table_key": f"{cluster}://{database}.{schema}/{table}"
        }
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.put(endpoint, json=payload, headers=self.headers)
        # return response.json()
        
        # 模拟返回
        return {
            "status": "success",
            "message": f"Tag '{tag}' added to table"
        }
    
    def get_table_usage(self, database, cluster, schema, table):
        """获取表使用统计"""
        endpoint = f"{self.metadata_service_url}/table/{database}/{cluster}/{schema}/{table}/usage"
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.get(endpoint, headers=self.headers)
        # return response.json()
        
        # 模拟返回
        return {
            "table_usage": [
                {
                    "user_id": "user1",
                    "count_reads": 15,
                    "read_frequency": "weekly"
                },
                {
                    "user_id": "user2",
                    "count_reads": 8,
                    "read_frequency": "monthly"
                }
            ],
            "total_reads": 23,
            "unique_user_count": 2
        }
    
    def update_table_description(self, database, cluster, schema, table, description):
        """更新表描述"""
        endpoint = f"{self.metadata_service_url}/table/description"
        
        payload = {
            "description": description,
            "table_key": f"{cluster}://{database}.{schema}/{table}"
        }
        
        # 在实际应用中，这里应该使用requests库发送HTTP请求
        # response = requests.put(endpoint, json=payload, headers=self.headers)
        # return response.json()
        
        # 模拟返回
        return {
            "status": "success",
            "message": "Table description updated"
        }


# ====================
# 7.5 Collibra 实施指南
# ====================

class CollibraImplementation:
    """
    Collibra实施指南
    提供Collibra平台的实施步骤和最佳实践
    """
    
    def __init__(self):
        self.phases = [
            {
                "name": "评估与规划",
                "duration": "4-6周",
                "activities": [
                    "业务需求分析",
                    "技术评估",
                    "实施规划",
                    "团队组建",
                    "基础设施准备"
                ],
                "deliverables": [
                    "业务需求文档",
                    "技术架构设计",
                    "实施路线图",
                    "资源计划"
                ],
                "key_decisions": [
                    "部署模型选择（本地/云/混合）",
                    "集成范围确定",
                    "定制化程度评估",
                    "治理框架设计"
                ]
            },
            {
                "name": "基础配置",
                "duration": "6-8周",
                "activities": [
                    "系统安装配置",
                    "元数据模型设计",
                    "用户权限配置",
                    "基础数据导入",
                    "初始工作流设置"
                ],
                "deliverables": [
                    "配置完成的Collibra环境",
                    "元数据模型文档",
                    "权限矩阵",
                    "导入数据报告"
                ],
                "key_decisions": [
                    "元数据模型设计",
                    "数据域划分",
                    "角色权限分配",
                    "数据分类标准"
                ]
            },
            {
                "name": "集成开发",
                "duration": "8-10周",
                "activities": [
                    "数据源连接器开发",
                    "ETL元数据集成",
                    "API集成开发",
                    "定制化组件开发",
                    "集成测试"
                ],
                "deliverables": [
                    "数据连接器",
                    "集成接口文档",
                    "定制化组件",
                    "测试报告"
                ],
                "key_decisions": [
                    "集成方式选择",
                    "API设计标准",
                    "数据同步策略",
                    "错误处理机制"
                ]
            },
            {
                "name": "试点实施",
                "duration": "6-8周",
                "activities": [
                    "选择试点部门",
                    "试点用户培训",
                    "试点数据导入",
                    "业务流程测试",
                    "用户反馈收集"
                ],
                "deliverables": [
                    "试点实施报告",
                    "用户反馈汇总",
                    "优化建议",
                    "培训材料"
                ],
                "key_decisions": [
                    "试点范围确定",
                    "用户培训策略",
                    "反馈处理机制",
                    "优化优先级"
                ]
            },
            {
                "name": "全面推广",
                "duration": "8-12周",
                "activities": [
                    "全组织推广计划",
                    "用户全面培训",
                    "数据全量导入",
                    "业务流程调整",
                    "运维体系建立"
                ],
                "deliverables": [
                    "推广计划文档",
                    "培训手册",
                    "操作指南",
                    "运维手册"
                ],
                "key_decisions": [
                    "推广策略",
                    "培训方式",
                    "数据迁移计划",
                    "运维模式"
                ]
            },
            {
                "name": "优化与扩展",
                "duration": "持续进行",
                "activities": [
                    "使用情况分析",
                    "功能优化",
                    "新需求评估",
                    "平台扩展",
                    "持续改进"
                ],
                "deliverables": [
                    "使用情况报告",
                    "优化方案",
                    "扩展规划",
                    "改进计划"
                ],
                "key_decisions": [
                    "优化方向",
                    "扩展范围",
                    "新功能优先级",
                    "改进频率"
                ]
            }
        ]
    
    def get_implementation_plan(self, scale="medium"):
        """获取实施计划"""
        plan = self.phases.copy()
        
        # 根据规模调整时间
        if scale == "small":
            for phase in plan:
                # 减少时间
                duration = phase["duration"].split("-")
                min_weeks = int(duration[0].replace("周", ""))
                max_weeks = int(duration[1].replace("周", ""))
                new_min = int(min_weeks * 0.7)
                new_max = int(max_weeks * 0.7)
                phase["duration"] = f"{new_min}-{new_max}周"
        
        elif scale == "large":
            for phase in plan:
                # 增加时间
                duration = phase["duration"].split("-")
                min_weeks = int(duration[0].replace("周", ""))
                max_weeks = int(duration[1].replace("周", ""))
                new_min = int(min_weeks * 1.5)
                new_max = int(max_weeks * 1.5)
                phase["duration"] = f"{new_min}-{new_max}周"
        
        return plan
    
    def get_best_practices(self):
        """获取最佳实践"""
        return [
            {
                "category": "元数据模型设计",
                "practices": [
                    "基于业务需求设计元数据模型",
                    "遵循行业标准规范",
                    "保持模型的灵活性和可扩展性",
                    "定期评估和优化模型"
                ]
            },
            {
                "category": "数据治理",
                "practices": [
                    "建立明确的治理组织结构",
                    "制定数据治理政策和流程",
                    "实施元数据质量监控",
                    "定期进行治理效果评估"
                ]
            },
            {
                "category": "系统集成",
                "practices": [
                    "使用标准化的集成接口",
                    "确保数据同步的准确性和及时性",
                    "实施错误监控和恢复机制",
                    "建立集成性能监控"
                ]
            },
            {
                "category": "用户培训",
                "practices": [
                    "提供分角色的培训内容",
                    "设计实用的工作场景培训",
                    "建立持续的知识分享机制",
                    "定期更新培训材料"
                ]
            },
            {
                "category": "平台运营",
                "practices": [
                    "建立专职运营团队",
                    "实施全面的监控和告警",
                    "定期进行平台优化",
                    "建立用户反馈处理机制"
                ]
            }
        ]
    
    def get_common_challenges(self):
        """获取常见挑战及解决方案"""
        return [
            {
                "challenge": "用户参与度低",
                "description": "员工不愿意使用元数据平台，导致平台利用率低",
                "solutions": [
                    "提高平台的易用性和用户体验",
                    "展示平台的价值和收益",
                    "建立激励机制鼓励使用",
                    "定期收集用户反馈并改进"
                ]
            },
            {
                "challenge": "元数据质量不高",
                "description": "元数据不准确、不完整，影响平台价值",
                "solutions": [
                    "建立元数据质量标准",
                    "实施自动化元数据收集",
                    "定期进行元数据审核",
                    "建立元数据质量监控机制"
                ]
            },
            {
                "challenge": "集成复杂度高",
                "description": "与现有系统集成困难，实施周期长",
                "solutions": [
                    "采用分阶段集成策略",
                    "优先集成核心数据源",
                    "使用标准化集成工具",
                    "建立专业的集成团队"
                ]
            },
            {
                "challenge": "缺乏明确的ROI",
                "description": "难以证明元数据平台的投资回报",
                "solutions": [
                    "建立量化指标体系",
                    "定期评估平台价值",
                    "分享成功案例和最佳实践",
                    "关注长期价值而非短期收益"
                ]
            }
        ]
    
    def get_success_metrics(self):
        """获取成功指标"""
        return [
            {
                "category": "使用指标",
                "metrics": [
                    "日活跃用户数",
                    "周活跃用户数",
                    "平台使用频率",
                    "功能使用分布"
                ]
            },
            {
                "category": "内容指标",
                "metrics": [
                    "元数据覆盖率",
                    "元数据完整性",
                    "元数据准确性",
                    "元数据更新频率"
                ]
            },
            {
                "category": "业务价值指标",
                "metrics": [
                    "数据查找时间减少",
                    "重复工作减少",
                    "数据质量问题减少",
                    "合规风险降低"
                ]
            },
            {
                "category": "用户满意度指标",
                "metrics": [
                    "用户满意度评分",
                    "NPS（净推荐值）",
                    "用户反馈数量",
                    "功能请求分析"
                ]
            }
        ]


# ====================
# 7.6 元数据平台选择器
# ====================

class MetadataPlatformSelector:
    """
    元数据平台选择器
    提供系统化的平台选型评估和推荐
    """
    
    def __init__(self):
        self.evaluation_criteria = {
            "functionality": {
                "metadata_storage": {
                    "description": "元数据存储与检索能力",
                    "weight": 0.15
                },
                "lineage_tracking": {
                    "description": "数据血缘追踪能力",
                    "weight": 0.15
                },
                "discovery_search": {
                    "description": "数据发现与搜索能力",
                    "weight": 0.15
                },
                "quality_monitoring": {
                    "description": "数据质量监控能力",
                    "weight": 0.10
                },
                "governance": {
                    "description": "数据治理功能",
                    "weight": 0.15
                },
                "integration": {
                    "description": "集成能力",
                    "weight": 0.10
                },
                "user_experience": {
                    "description": "用户体验",
                    "weight": 0.10
                },
                "scalability": {
                    "description": "可扩展性",
                    "weight": 0.10
                }
            },
            "technical": {
                "architecture": {
                    "description": "架构设计",
                    "weight": 0.15
                },
                "performance": {
                    "description": "性能表现",
                    "weight": 0.15
                },
                "security": {
                    "description": "安全性",
                    "weight": 0.20
                },
                "deployment": {
                    "description": "部署灵活性",
                    "weight": 0.15
                },
                "api_design": {
                    "description": "API设计",
                    "weight": 0.15
                },
                "reliability": {
                    "description": "可靠性",
                    "weight": 0.10
                },
                "monitoring": {
                    "description": "监控能力",
                    "weight": 0.10
                }
            },
            "business": {
                "cost": {
                    "description": "总拥有成本",
                    "weight": 0.25
                },
                "license": {
                    "description": "许可证模式",
                    "weight": 0.15
                },
                "support": {
                    "description": "支持服务",
                    "weight": 0.20
                },
                "community": {
                    "description": "社区活跃度",
                    "weight": 0.10
                },
                "innovation": {
                    "description": "创新能力",
                    "weight": 0.15
                },
                "roadmap": {
                    "description": "产品路线图",
                    "weight": 0.15
                }
            },
            "organizational": {
                "learning_curve": {
                    "description": "学习曲线",
                    "weight": 0.20
                },
                "customization": {
                    "description": "定制能力",
                    "weight": 0.15
                },
                "team_fit": {
                    "description": "团队技能匹配",
                    "weight": 0.15
                },
                "implementation": {
                    "description": "实施复杂度",
                    "weight": 0.20
                },
                "maintenance": {
                    "description": "运维需求",
                    "weight": 0.15
                },
                "vendor_stability": {
                    "description": "供应商稳定性",
                    "weight": 0.15
                }
            }
        }
        
        # 平台评估数据（模拟数据，实际应用中应根据评估结果填写）
        self.platform_scores = {
            "Apache Atlas": {
                "functionality": {
                    "metadata_storage": 0.85,
                    "lineage_tracking": 0.90,
                    "discovery_search": 0.75,
                    "quality_monitoring": 0.70,
                    "governance": 0.80,
                    "integration": 0.85,
                    "user_experience": 0.65,
                    "scalability": 0.90
                },
                "technical": {
                    "architecture": 0.80,
                    "performance": 0.75,
                    "security": 0.85,
                    "deployment": 0.75,
                    "api_design": 0.70,
                    "reliability": 0.80,
                    "monitoring": 0.70
                },
                "business": {
                    "cost": 0.95,  # 开源免费
                    "license": 0.90,
                    "support": 0.60,  # 社区支持
                    "community": 0.85,
                    "innovation": 0.75,
                    "roadmap": 0.80
                },
                "organizational": {
                    "learning_curve": 0.60,  # 学习曲线陡峭
                    "customization": 0.85,
                    "team_fit": 0.70,
                    "implementation": 0.65,
                    "maintenance": 0.60,
                    "vendor_stability": 0.80
                }
            },
            "DataHub": {
                "functionality": {
                    "metadata_storage": 0.80,
                    "lineage_tracking": 0.85,
                    "discovery_search": 0.90,
                    "quality_monitoring": 0.75,
                    "governance": 0.70,
                    "integration": 0.85,
                    "user_experience": 0.85,
                    "scalability": 0.85
                },
                "technical": {
                    "architecture": 0.90,
                    "performance": 0.85,
                    "security": 0.80,
                    "deployment": 0.85,
                    "api_design": 0.95,
                    "reliability": 0.80,
                    "monitoring": 0.80
                },
                "business": {
                    "cost": 0.95,  # 开源免费
                    "license": 0.90,
                    "support": 0.65,  # 社区支持
                    "community": 0.75,
                    "innovation": 0.85,
                    "roadmap": 0.85
                },
                "organizational": {
                    "learning_curve": 0.75,
                    "customization": 0.80,
                    "team_fit": 0.80,
                    "implementation": 0.80,
                    "maintenance": 0.70,
                    "vendor_stability": 0.75
                }
            },
            "Collibra": {
                "functionality": {
                    "metadata_storage": 0.90,
                    "lineage_tracking": 0.85,
                    "discovery_search": 0.85,
                    "quality_monitoring": 0.80,
                    "governance": 0.95,
                    "integration": 0.80,
                    "user_experience": 0.90,
                    "scalability": 0.80
                },
                "technical": {
                    "architecture": 0.75,
                    "performance": 0.80,
                    "security": 0.90,
                    "deployment": 0.85,
                    "api_design": 0.75,
                    "reliability": 0.85,
                    "monitoring": 0.80
                },
                "business": {
                    "cost": 0.40,  # 昂贵
                    "license": 0.50,  # 商业许可
                    "support": 0.95,  # 专业支持
                    "community": 0.30,  # 商业产品
                    "innovation": 0.80,
                    "roadmap": 0.90
                },
                "organizational": {
                    "learning_curve": 0.85,
                    "customization": 0.60,
                    "team_fit": 0.85,
                    "implementation": 0.70,
                    "maintenance": 0.80,
                    "vendor_stability": 0.95
                }
            }
        }
    
    def calculate_category_score(self, platform, category):
        """计算平台在特定类别的得分"""
        if platform not in self.platform_scores or category not in self.platform_scores[platform]:
            return 0
        
        category_scores = self.platform_scores[platform][category]
        criteria = self.evaluation_criteria[category]
        
        total_weighted_score = 0
        total_weight = 0
        
        for criterion, weight in criteria.items():
            score = category_scores.get(criterion, 0)
            total_weighted_score += score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0
    
    def calculate_overall_score(self, platform, weight_config=None):
        """计算平台总体得分"""
        if platform not in self.platform_scores:
            return 0
        
        # 默认权重配置
        default_weights = {
            "functionality": 0.35,
            "technical": 0.25,
            "business": 0.20,
            "organizational": 0.20
        }
        
        weights = weight_config or default_weights
        
        overall_score = 0
        for category, weight in weights.items():
            category_score = self.calculate_category_score(platform, category)
            overall_score += category_score * weight
        
        return overall_score
    
    def compare_platforms(self, platforms=None):
        """比较平台"""
        if platforms is None:
            platforms = list(self.platform_scores.keys())
        
        comparison = {}
        
        for platform in platforms:
            platform_scores = {}
            
            # 计算各类别得分
            for category in self.evaluation_criteria.keys():
                platform_scores[category] = self.calculate_category_score(platform, category)
            
            # 计算总体得分
            platform_scores["overall"] = self.calculate_overall_score(platform)
            
            comparison[platform] = platform_scores
        
        return comparison
    
    def recommend_platform(self, requirements, platforms=None):
        """根据需求推荐平台"""
        if platforms is None:
            platforms = list(self.platform_scores.keys())
        
        # 根据需求调整权重
        weights = {
            "functionality": 0.35,
            "technical": 0.25,
            "business": 0.20,
            "organizational": 0.20
        }
        
        # 根据需求调整权重
        if "budget" in requirements:
            if requirements["budget"] == "low":
                weights["business"] = 0.35  # 更重视成本
                weights["functionality"] = 0.25
            elif requirements["budget"] == "high":
                weights["functionality"] = 0.40  # 更重视功能
                weights["business"] = 0.15
        
        if "team_capability" in requirements:
            if requirements["team_capability"] == "technical":
                weights["technical"] = 0.35  # 技术团队更重视技术特性
                weights["organizational"] = 0.15
            elif requirements["team_capability"] == "business":
                weights["organizational"] = 0.35  # 业务团队更重视易用性
                weights["technical"] = 0.15
        
        if "organization_size" in requirements:
            if requirements["organization_size"] == "large":
                weights["business"] = 0.25  # 大企业更重视支持
                weights["technical"] = 0.20
        
        # 评估每个平台
        recommendations = []
        for platform in platforms:
            overall_score = self.calculate_overall_score(platform, weights)
            
            # 计算匹配度
            match_percentage = overall_score * 100
            
            # 生成推荐理由
            reasons = self._generate_recommendation_reasons(platform, requirements)
            
            recommendations.append({
                "platform": platform,
                "score": overall_score,
                "match_percentage": match_percentage,
                "reasons": reasons
            })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations
    
    def _generate_recommendation_reasons(self, platform, requirements):
        """生成推荐理由"""
        reasons = []
        platform_scores = self.platform_scores[platform]
        
        # 基于预算的理由
        if "budget" in requirements:
            if requirements["budget"] == "low" and platform in ["Apache Atlas", "DataHub"]:
                reasons.append("开源免费，符合低预算需求")
            elif requirements["budget"] == "high" and platform == "Collibra":
                reasons.append("商业平台提供全面功能和专业支持")
        
        # 基于团队能力的理由
        if "team_capability" in requirements:
            if requirements["team_capability"] == "technical" and platform in ["Apache Atlas", "DataHub"]:
                reasons.append("开源平台提供更多定制空间，适合技术团队")
            elif requirements["team_capability"] == "business" and platform == "Collibra":
                reasons.append("商业平台界面友好，易于业务用户使用")
        
        # 基于规模的理由
        if "organization_size" in requirements:
            if requirements["organization_size"] == "large" and platform == "Collibra":
                reasons.append("企业级平台，支持大规模部署和复杂治理需求")
            elif requirements["organization_size"] in ["small", "medium"] and platform in ["Apache Atlas", "DataHub"]:
                reasons.append("开源平台灵活性好，适合中小型组织快速部署")
        
        # 基于功能的理由
        if "features" in requirements:
            required_features = requirements["features"]
            if "governance" in required_features and platform == "Collibra":
                reasons.append("提供全面的数据治理功能")
            if "discovery" in required_features and platform == "DataHub":
                reasons.append("数据发现和搜索功能强大")
            if "lineage" in required_features and platform == "Apache Atlas":
                reasons.append("数据血缘功能成熟稳定")
        
        return reasons


# ====================
# 示例使用代码
# ====================

def demo_tool_comparison():
    """演示工具比较"""
    print("=== 元数据工具比较演示 ===")
    
    tool_comparison = MetadataToolComparison()
    
    # 比较几个工具
    comparison = tool_comparison.compare_tools(
        tool_names=["Apache Atlas", "DataHub", "Collibra", "Alation"],
        criteria=["type", "deployment", "strengths", "weaknesses"]
    )
    
    print("工具比较:")
    for tool, details in comparison.items():
        print(f"\n{tool}:")
        print(f"- 类型: {details['type']}")
        print(f"- 部署方式: {', '.join(details['deployment'])}")
        print("- 优势:")
        for strength in details['strengths']:
            print(f"  * {strength}")
        print("- 劣势:")
        for weakness in details['weaknesses']:
            print(f"  * {weakness}")
    
    # 根据需求推荐工具
    requirements = {
        "budget": "medium",
        "deployment": "本地",
        "organization_size": "medium",
        "team_capability": "technical",
        "features": ["数据血缘", "元数据存储库"]
    }
    
    recommendations = tool_comparison.recommend_tool(requirements)
    print(f"\n工具推荐:")
    for rec in recommendations:
        print(f"- {rec['tool']}: {rec['match_percentage']:.1f}% 匹配度")
        print("  推荐理由:")
        for reason in rec['reasons']:
            print(f"    * {reason}")
    
    # 获取实施路线图
    roadmap = tool_comparison.get_implementation_roadmap("DataHub")
    if roadmap:
        print(f"\n{roadmap['tool_name']} 实施路线图:")
        for i, phase in enumerate(roadmap["implementation_phases"], 1):
            print(f"{i}. {phase['phase']} ({phase['duration']}):")
            for activity in phase['activities']:
                print(f"   - {activity}")


def demo_atlas():
    """演示Apache Atlas使用"""
    print("\n=== Apache Atlas 演示 ===")
    
    atlas_manager = AtlasMetadataManager("localhost", 21000, "admin", "admin")
    
    # 创建数据集类型
    dataset_type = {
        "name": "CustomDataSet",
        "superTypes": ["DataSet"],
        "attributeDefinitions": [
            {
                "name": "businessDomain",
                "typeName": "string",
                "isOptional": True,
                "cardinality": "SINGLE"
            },
            {
                "name": "dataQualityScore",
                "typeName": "double",
                "isOptional": True,
                "cardinality": "SINGLE"
            }
        ]
    }
    
    create_type_result = atlas_manager.create_entity_type(dataset_type)
    print(f"创建实体类型: {create_type_result}")
    
    # 创建数据集实体
    dataset_entity = {
        "entity": {
            "typeName": "CustomDataSet",
            "attributes": {
                "name": "customer_data",
                "qualifiedName": "customer_data@primary",
                "description": "客户基本信息数据集",
                "businessDomain": "销售",
                "dataQualityScore": 0.92
            }
        }
    }
    
    create_entity_result = atlas_manager.create_entity(dataset_entity)
    print(f"创建实体: {create_entity_result}")
    
    # 搜索实体
    search_result = atlas_manager.search_entities("customer")
    print(f"搜索结果: {search_result}")
    
    # 获取血缘
    if "entity" in create_entity_result and "guid" in create_entity_result["entity"]:
        guid = create_entity_result["entity"]["guid"]
        lineage_result = atlas_manager.get_lineage(guid)
        print(f"血缘关系: {lineage_result}")


def demo_datahub():
    """演示DataHub使用"""
    print("\n=== DataHub 演示 ===")
    
    datahub_manager = DataHubMetadataManager("http://localhost:9002", token="your_token_here")
    
    # 创建数据集
    dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:hive,customer_data)"
    create_result = datahub_manager.create_dataset(
        urn=dataset_urn,
        name="customer_data",
        description="客户基本信息数据",
        properties={
            "business_domain": "销售",
            "data_quality_score": "0.92"
        }
    )
    print(f"创建数据集: {create_result}")
    
    # 搜索数据集
    search_result = datahub_manager.search_entities("customer", count=5)
    print(f"搜索结果: {search_result}")
    
    # 获取血缘关系
    lineage_result = datahub_manager.get_lineage(dataset_urn)
    print(f"血缘关系: {lineage_result}")
    
    # 添加标签
    tag_result = datahub_manager.add_tags(dataset_urn, ["customer", "personal_info"])
    print(f"添加标签: {tag_result}")
    
    # 获取数据集统计
    stats_result = datahub_manager.get_dataset_stats(dataset_urn)
    print(f"数据集统计: {stats_result}")


def demo_amundsen():
    """演示Amundsen使用"""
    print("\n=== Amundsen 演示 ===")
    
    amundsen_manager = AmundsenMetadataManager(
        "http://localhost:5000",
        "http://localhost:5001"
    )
    
    # 发布表元数据
    table_metadata = {
        "name": "customer_data",
        "description": "客户基本信息表",
        "cluster": "prod",
        "database": "analytics",
        "schema": "public",
        "columns": [
            {
                "name": "customer_id",
                "description": "客户唯一标识",
                "col_type": "varchar",
                "sort_order": 0
            },
            {
                "name": "name",
                "description": "客户姓名",
                "col_type": "varchar",
                "sort_order": 1
            },
            {
                "name": "email",
                "description": "电子邮箱",
                "col_type": "varchar",
                "sort_order": 2
            }
        ],
        "tags": ["customer", "pii"]
    }
    
    publish_result = amundsen_manager.publish_table(table_metadata)
    print(f"发布表: {publish_result}")
    
    # 搜索表
    search_result = amundsen_manager.search_tables("customer", page_index=0, results_per_page=5)
    print(f"搜索结果: {search_result}")
    
    # 获取表元数据
    metadata_result = amundsen_manager.get_table_metadata(
        database="analytics",
        cluster="prod",
        schema="public",
        table="customer_data"
    )
    print(f"表元数据: {metadata_result}")
    
    # 添加标签
    tag_result = amundsen_manager.add_table_tag(
        database="analytics",
        cluster="prod",
        schema="public",
        table="customer_data",
        tag="personal_info"
    )
    print(f"添加标签: {tag_result}")
    
    # 获取使用统计
    usage_result = amundsen_manager.get_table_usage(
        database="analytics",
        cluster="prod",
        schema="public",
        table="customer_data"
    )
    print(f"使用统计: {usage_result}")


def demo_collibra():
    """演示Collibra实施指南"""
    print("\n=== Collibra 实施指南演示 ===")
    
    collibra_impl = CollibraImplementation()
    
    # 获取实施计划
    implementation_plan = collibra_impl.get_implementation_plan(scale="medium")
    print(f"Collibra实施计划 (中型企业):")
    total_min_weeks = 0
    total_max_weeks = 0
    
    for phase in implementation_plan:
        print(f"\n{phase['name']} ({phase['duration']}):")
        for activity in phase['activities']:
            print(f"  - {activity}")
        
        # 计算总时间
        duration = phase["duration"].split("-")
        min_weeks = int(duration[0].replace("周", ""))
        max_weeks = int(duration[1].replace("周", ""))
        total_min_weeks += min_weeks
        total_max_weeks += max_weeks
    
    print(f"\n总体实施时间: {total_min_weeks}-{total_max_weeks} 周")
    
    # 获取最佳实践
    best_practices = collibra_impl.get_best_practices()
    print(f"\n最佳实践:")
    for category in best_practices:
        print(f"\n{category['category']}:")
        for practice in category['practices']:
            print(f"  - {practice}")


def demo_platform_selector():
    """演示平台选择器"""
    print("\n=== 元数据平台选择器演示 ===")
    
    selector = MetadataPlatformSelector()
    
    # 比较平台
    comparison = selector.compare_platforms(["Apache Atlas", "DataHub", "Collibra"])
    print("平台比较:")
    for platform, scores in comparison.items():
        print(f"\n{platform}:")
        for category, score in scores.items():
            print(f"  {category}: {score:.2f} ({score*100:.1f}%)")
    
    # 根据需求推荐平台
    requirements = {
        "budget": "medium",
        "organization_size": "medium",
        "team_capability": "technical",
        "features": ["discovery", "lineage"]
    }
    
    recommendations = selector.recommend_platform(requirements)
    print(f"\n推荐平台:")
    for rec in recommendations:
        print(f"{rec['platform']}: {rec['match_percentage']:.1f}% 匹配度")
        print("  推荐理由:")
        for reason in rec['reasons']:
            print(f"    - {reason}")


def main():
    """主函数，运行所有演示"""
    demo_tool_comparison()
    demo_atlas()
    demo_datahub()
    demo_amundsen()
    demo_collibra()
    demo_platform_selector()


if __name__ == "__main__":
    main()