#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
血缘影响分析工具
功能：基于数据血缘关系分析数据变更的影响，支持根因分析和合规检查
作者：数据治理团队
日期：2023-11-23
"""

import json
import datetime
import uuid
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional, Set
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class LineageImpactAnalyzer:
    """血缘影响分析器"""
    
    def __init__(self, lineage_graph=None):
        """初始化血缘影响分析器"""
        if lineage_graph is None:
            self.lineage_graph = nx.DiGraph()
        else:
            self.lineage_graph = lineage_graph
        
        # 定义系统重要性权重
        self.system_importance = {
            "production": 0.9,
            "staging": 0.7,
            "development": 0.5,
            "analytics": 0.8,
            "reporting": 0.9,
            "sandbox": 0.3,
            "unknown": 0.5
        }
        
        # 定义对象类型重要性权重
        self.object_type_importance = {
            "table": 0.7,
            "view": 0.6,
            "materialized_view": 0.8,
            "report": 0.9,
            "dashboard": 0.9,
            "api": 0.8,
            "ml_model": 0.9,
            "file": 0.5,
            "stream": 0.8,
            "unknown": 0.5
        }
        
        # 定义变更类型影响权重
        self.change_type_impact = {
            "schema_change": 0.9,
            "data_deletion": 0.9,
            "data_update": 0.7,
            "data_addition": 0.4,
            "permission_change": 0.6,
            "performance_change": 0.5,
            "renaming": 0.8,
            "unknown": 0.5
        }
    
    def add_data_object(self, object_id, name, object_type, system_name, 
                       properties=None):
        """添加数据对象到血缘图"""
        properties = properties or {}
        self.lineage_graph.add_node(
            object_id,
            name=name,
            object_type=object_type,
            system_name=system_name,
            properties=properties
        )
        return object_id
    
    def add_lineage_relationship(self, source_id, target_id, 
                                transformation_type=None, properties=None):
        """添加血缘关系到血缘图"""
        properties = properties or {}
        self.lineage_graph.add_edge(
            source_id,
            target_id,
            transformation_type=transformation_type,
            properties=properties
        )
        return (source_id, target_id)
    
    def analyze_change_impact(self, changed_objects, change_type="data_update", 
                             max_depth=3, include_upstream=True):
        """分析数据变更的影响"""
        impact_results = {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "change_type": change_type,
            "changed_objects": changed_objects,
            "max_depth": max_depth,
            "include_upstream": include_upstream,
            "impact_summary": {},
            "detailed_impacts": {
                "direct_impacts": [],
                "indirect_impacts": [],
                "upstream_impacts": [],
                "downstream_impacts": []
            },
            "critical_paths": [],
            "affected_systems": {},
            "risk_assessment": {},
            "recommendations": []
        }
        
        # 分析每个变更对象的影响
        all_direct_impacts = []
        all_indirect_impacts = []
        all_upstream_impacts = []
        all_downstream_impacts = []
        
        for obj_id in changed_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            # 获取下游血缘
            downstream_impacts = self._get_downstream_impacts(
                obj_id, max_depth, change_type
            )
            
            # 获取上游血缘（如果需要）
            upstream_impacts = []
            if include_upstream:
                upstream_impacts = self._get_upstream_impacts(
                    obj_id, max_depth, change_type
                )
            
            # 分类直接影响和间接影响
            direct_downstream = [item for item in downstream_impacts if item["depth"] == 1]
            indirect_downstream = [item for item in downstream_impacts if item["depth"] > 1]
            
            direct_upstream = [item for item in upstream_impacts if item["depth"] == 1]
            indirect_upstream = [item for item in upstream_impacts if item["depth"] > 1]
            
            # 添加影响详情
            all_direct_impacts.extend(direct_downstream + direct_upstream)
            all_indirect_impacts.extend(indirect_downstream + indirect_upstream)
            all_upstream_impacts.extend(upstream_impacts)
            all_downstream_impacts.extend(downstream_impacts)
        
        # 识别关键路径
        impact_results["critical_paths"] = self._identify_critical_paths(
            changed_objects, max_depth
        )
        
        # 分析受影响的系统
        impact_results["affected_systems"] = self._analyze_affected_systems(
            all_direct_impacts + all_indirect_impacts
        )
        
        # 评估风险
        impact_results["risk_assessment"] = self._assess_change_risk(
            changed_objects, change_type, 
            len(all_direct_impacts), len(all_indirect_impacts)
        )
        
        # 生成推荐
        impact_results["recommendations"] = self._generate_change_recommendations(
            change_type, impact_results["risk_assessment"], 
            impact_results["affected_systems"]
        )
        
        # 生成影响摘要
        impact_results["impact_summary"] = {
            "changed_objects_count": len(changed_objects),
            "direct_impacts_count": len(all_direct_impacts),
            "indirect_impacts_count": len(all_indirect_impacts),
            "total_impacts_count": len(all_direct_impacts) + len(all_indirect_impacts),
            "upstream_impacts_count": len(all_upstream_impacts),
            "downstream_impacts_count": len(all_downstream_impacts),
            "affected_systems_count": len(impact_results["affected_systems"]),
            "critical_paths_count": len(impact_results["critical_paths"]),
            "overall_risk_level": impact_results["risk_assessment"]["risk_level"]
        }
        
        # 去重并组织影响详情
        impact_results["detailed_impacts"]["direct_impacts"] = self._deduplicate_impacts(all_direct_impacts)
        impact_results["detailed_impacts"]["indirect_impacts"] = self._deduplicate_impacts(all_indirect_impacts)
        impact_results["detailed_impacts"]["upstream_impacts"] = self._deduplicate_impacts(all_upstream_impacts)
        impact_results["detailed_impacts"]["downstream_impacts"] = self._deduplicate_impacts(all_downstream_impacts)
        
        return impact_results
    
    def _get_downstream_impacts(self, object_id, max_depth, change_type):
        """获取下游影响"""
        impacts = []
        
        # 使用广度优先搜索
        for depth in range(1, max_depth + 1):
            # 获取当前深度的下游节点
            if depth == 1:
                targets = list(self.lineage_graph.successors(object_id))
            else:
                # 获取上一深度节点的下游节点
                prev_depth_targets = [
                    item["object_id"] for item in impacts 
                    if item["depth"] == depth - 1
                ]
                targets = []
                for target_id in prev_depth_targets:
                    targets.extend(list(self.lineage_graph.successors(target_id)))
                
                # 去重
                targets = list(set(targets))
            
            # 为每个目标节点创建影响项
            for target_id in targets:
                if not self.lineage_graph.has_node(target_id):
                    continue
                
                node_data = self.lineage_graph.nodes[target_id]
                
                # 获取路径
                path = nx.shortest_path(self.lineage_graph, object_id, target_id)
                
                # 计算影响分数
                impact_score = self._calculate_impact_score(
                    object_id, target_id, path, change_type
                )
                
                impact_item = {
                    "object_id": target_id,
                    "object_name": node_data.get("name", target_id),
                    "object_type": node_data.get("object_type", "unknown"),
                    "system_name": node_data.get("system_name", "unknown"),
                    "depth": depth,
                    "path": path,
                    "impact_score": impact_score,
                    "transformation": self._get_transformation_along_path(path)
                }
                
                impacts.append(impact_item)
        
        return impacts
    
    def _get_upstream_impacts(self, object_id, max_depth, change_type):
        """获取上游影响"""
        impacts = []
        
        # 使用广度优先搜索
        for depth in range(1, max_depth + 1):
            # 获取当前深度的上游节点
            if depth == 1:
                sources = list(self.lineage_graph.predecessors(object_id))
            else:
                # 获取上一深度节点的上游节点
                prev_depth_sources = [
                    item["object_id"] for item in impacts 
                    if item["depth"] == depth - 1
                ]
                sources = []
                for source_id in prev_depth_sources:
                    sources.extend(list(self.lineage_graph.predecessors(source_id)))
                
                # 去重
                sources = list(set(sources))
            
            # 为每个源节点创建影响项
            for source_id in sources:
                if not self.lineage_graph.has_node(source_id):
                    continue
                
                node_data = self.lineage_graph.nodes[source_id]
                
                # 获取路径
                path = nx.shortest_path(self.lineage_graph, source_id, object_id)
                
                # 计算影响分数
                impact_score = self._calculate_impact_score(
                    source_id, object_id, path, change_type
                )
                
                impact_item = {
                    "object_id": source_id,
                    "object_name": node_data.get("name", source_id),
                    "object_type": node_data.get("object_type", "unknown"),
                    "system_name": node_data.get("system_name", "unknown"),
                    "depth": depth,
                    "path": path,
                    "impact_score": impact_score,
                    "transformation": self._get_transformation_along_path(path)
                }
                
                impacts.append(impact_item)
        
        return impacts
    
    def _calculate_impact_score(self, source_id, target_id, path, change_type):
        """计算影响分数"""
        # 基础分数基于变更类型
        base_score = self.change_type_impact.get(change_type, 0.5)
        
        # 系统重要性
        target_node = self.lineage_graph.nodes[target_id]
        system_name = target_node.get("system_name", "unknown")
        system_score = self.system_importance.get(system_name, 0.5)
        
        # 对象类型重要性
        object_type = target_node.get("object_type", "unknown")
        type_score = self.object_type_importance.get(object_type, 0.5)
        
        # 路径长度影响（路径越长，影响越小）
        path_length_factor = max(0.1, 1.0 - (len(path) - 1) * 0.1)
        
        # 计算综合分数
        impact_score = base_score * system_score * type_score * path_length_factor
        
        # 确保分数在0-1之间
        return min(max(impact_score, 0), 1)
    
    def _get_transformation_along_path(self, path):
        """获取路径上的转换信息"""
        transformations = []
        
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            if self.lineage_graph.has_edge(source, target):
                edge_data = self.lineage_graph.edges[source, target]
                transformation_type = edge_data.get("transformation_type", "unknown")
                transformations.append(transformation_type)
        
        return transformations
    
    def _identify_critical_paths(self, changed_objects, max_depth):
        """识别关键路径"""
        critical_paths = []
        
        for obj_id in changed_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            # 获取所有下游路径
            for target_id in self.lineage_graph.nodes():
                if obj_id != target_id and nx.has_path(self.lineage_graph, obj_id, target_id):
                    # 获取最短路径
                    try:
                        path = nx.shortest_path(self.lineage_graph, obj_id, target_id)
                        
                        # 计算路径重要性
                        importance = self._calculate_path_importance(path)
                        
                        # 只添加高重要性路径
                        if importance >= 0.7:
                            critical_paths.append({
                                "source_object": obj_id,
                                "target_object": target_id,
                                "path_length": len(path) - 1,
                                "importance": importance,
                                "path_nodes": path
                            })
                    except nx.NetworkXNoPath:
                        continue
        
        # 按重要性排序
        critical_paths.sort(key=lambda x: x["importance"], reverse=True)
        
        return critical_paths
    
    def _calculate_path_importance(self, path):
        """计算路径重要性"""
        total_importance = 0
        
        for node_id in path:
            node_data = self.lineage_graph.nodes[node_id]
            
            # 系统重要性
            system_name = node_data.get("system_name", "unknown")
            system_importance = self.system_importance.get(system_name, 0.5)
            
            # 对象类型重要性
            object_type = node_data.get("object_type", "unknown")
            type_importance = self.object_type_importance.get(object_type, 0.5)
            
            # 节点重要性
            node_importance = (system_importance + type_importance) / 2
            total_importance += node_importance
        
        # 平均重要性并考虑路径长度
        avg_importance = total_importance / len(path)
        path_factor = max(0.1, 1.0 - (len(path) - 1) * 0.05)  # 路径越长，重要性略有降低
        
        return min(avg_importance * path_factor, 1.0)
    
    def _analyze_affected_systems(self, impacts):
        """分析受影响的系统"""
        affected_systems = {}
        
        for impact in impacts:
            system_name = impact["system_name"]
            
            if system_name not in affected_systems:
                affected_systems[system_name] = {
                    "impact_count": 0,
                    "direct_impact_count": 0,
                    "indirect_impact_count": 0,
                    "avg_impact_score": 0,
                    "max_impact_score": 0,
                    "object_types": {}
                }
            
            # 更新计数
            affected_systems[system_name]["impact_count"] += 1
            
            if impact["depth"] == 1:
                affected_systems[system_name]["direct_impact_count"] += 1
            else:
                affected_systems[system_name]["indirect_impact_count"] += 1
            
            # 更新影响分数
            impact_score = impact["impact_score"]
            current_avg = affected_systems[system_name]["avg_impact_score"]
            current_count = affected_systems[system_name]["impact_count"]
            
            # 计算新的平均分
            affected_systems[system_name]["avg_impact_score"] = (
                (current_avg * (current_count - 1) + impact_score) / current_count
            )
            
            # 更新最大影响分数
            affected_systems[system_name]["max_impact_score"] = max(
                affected_systems[system_name]["max_impact_score"],
                impact_score
            )
            
            # 更新对象类型统计
            object_type = impact["object_type"]
            if object_type not in affected_systems[system_name]["object_types"]:
                affected_systems[system_name]["object_types"][object_type] = 0
            affected_systems[system_name]["object_types"][object_type] += 1
        
        return affected_systems
    
    def _assess_change_risk(self, changed_objects, change_type, 
                            direct_impact_count, indirect_impact_count):
        """评估变更风险"""
        # 基础风险分数
        base_risk = self.change_type_impact.get(change_type, 0.5)
        
        # 影响范围风险
        impact_risk = min((direct_impact_count * 0.05 + indirect_impact_count * 0.02), 0.5)
        
        # 系统风险
        system_risk = 0
        for obj_id in changed_objects:
            if self.lineage_graph.has_node(obj_id):
                node_data = self.lineage_graph.nodes[obj_id]
                system_name = node_data.get("system_name", "unknown")
                system_importance = self.system_importance.get(system_name, 0.5)
                system_risk = max(system_risk, system_importance)
        
        # 计算综合风险分数
        total_risk = (base_risk + impact_risk + system_risk) / 3
        
        # 确定风险级别
        if total_risk >= 0.8:
            risk_level = "高"
        elif total_risk >= 0.5:
            risk_level = "中"
        else:
            risk_level = "低"
        
        return {
            "risk_score": total_risk,
            "risk_level": risk_level,
            "risk_factors": {
                "change_type_risk": base_risk,
                "impact_scope_risk": impact_risk,
                "system_importance_risk": system_risk
            }
        }
    
    def _generate_change_recommendations(self, change_type, risk_assessment, affected_systems):
        """生成变更推荐"""
        recommendations = []
        risk_level = risk_assessment["risk_level"]
        
        # 基于风险级别的推荐
        if risk_level == "高":
            recommendations.append({
                "priority": "高",
                "category": "风险管理",
                "recommendation": "建议在测试环境先进行变更验证，并制定回滚计划",
                "action_items": [
                    "在测试环境验证变更",
                    "制定详细的回滚计划",
                    "安排变更窗口",
                    "通知所有相关方"
                ]
            })
            
            recommendations.append({
                "priority": "高",
                "category": "沟通协调",
                "recommendation": "需要与受影响系统的所有者协调变更计划",
                "action_items": [
                    "识别所有受影响系统的所有者",
                    "安排变更评审会议",
                    "获取所有相关方的批准"
                ]
            })
        elif risk_level == "中":
            recommendations.append({
                "priority": "中",
                "category": "测试验证",
                "recommendation": "建议在非生产环境进行测试，验证变更影响",
                "action_items": [
                    "在开发环境进行测试",
                    "验证核心功能",
                    "记录测试结果"
                ]
            })
        else:
            recommendations.append({
                "priority": "低",
                "category": "标准流程",
                "recommendation": "遵循标准变更管理流程即可",
                "action_items": [
                    "创建变更请求",
                    "获取必要批准",
                    "记录变更"
                ]
            })
        
        # 基于变更类型的推荐
        if change_type == "schema_change":
            recommendations.append({
                "priority": "高",
                "category": "技术验证",
                "recommendation": "架构变更需要特别关注兼容性问题",
                "action_items": [
                    "验证应用程序兼容性",
                    "检查ETL作业是否需要更新",
                    "更新文档"
                ]
            })
        elif change_type == "data_deletion":
            recommendations.append({
                "priority": "高",
                "category": "数据保护",
                "recommendation": "数据删除前确保有适当的备份",
                "action_items": [
                    "创建数据备份",
                    "验证备份完整性",
                    "确认删除的合规性"
                ]
            })
        
        # 基于受影响系统的推荐
        high_risk_systems = [
            system for system, details in affected_systems.items()
            if details["max_impact_score"] >= 0.8
        ]
        
        if high_risk_systems:
            recommendations.append({
                "priority": "中",
                "category": "系统监控",
                "recommendation": f"变更后需要特别关注以下系统: {', '.join(high_risk_systems)}",
                "action_items": [
                    "增强监控告警",
                    "准备应急响应计划",
                    "安排值班人员"
                ]
            })
        
        return recommendations
    
    def _deduplicate_impacts(self, impacts):
        """去重影响项"""
        unique_impacts = {}
        
        for impact in impacts:
            obj_id = impact["object_id"]
            
            if obj_id not in unique_impacts or impact["depth"] < unique_impacts[obj_id]["depth"]:
                unique_impacts[obj_id] = impact
        
        return list(unique_impacts.values())
    
    def analyze_root_cause(self, problematic_objects, issue_type="data_quality", max_depth=3):
        """分析数据问题的根因"""
        root_cause_results = {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "issue_type": issue_type,
            "problematic_objects": problematic_objects,
            "max_depth": max_depth,
            "suspected_sources": [],
            "potential_causes": [],
            "analysis_paths": [],
            "confidence_scores": {},
            "recommendations": []
        }
        
        all_suspected_sources = []
        all_potential_causes = []
        all_analysis_paths = []
        
        # 分析每个问题对象
        for obj_id in problematic_objects:
            if not self.lineage_graph.has_node(obj_id):
                continue
            
            # 获取上游血缘
            upstream_paths = self._get_upstream_paths(obj_id, max_depth)
            all_analysis_paths.extend(upstream_paths)
            
            # 识别可疑来源
            suspected_sources = self._identify_suspected_sources(obj_id, upstream_paths, issue_type)
            all_suspected_sources.extend(suspected_sources)
            
            # 分析潜在原因
            potential_causes = self._analyze_potential_causes(obj_id, upstream_paths, issue_type)
            all_potential_causes.extend(potential_causes)
        
        # 去重
        root_cause_results["suspected_sources"] = self._deduplicate_sources(all_suspected_sources)
        root_cause_results["potential_causes"] = self._deduplicate_causes(all_potential_causes)
        root_cause_results["analysis_paths"] = self._deduplicate_paths(all_analysis_paths)
        
        # 计算置信度分数
        root_cause_results["confidence_scores"] = self._calculate_confidence_scores(
            root_cause_results["suspected_sources"], 
            root_cause_results["potential_causes"]
        )
        
        # 生成推荐
        root_cause_results["recommendations"] = self._generate_root_cause_recommendations(
            issue_type, root_cause_results["suspected_sources"]
        )
        
        return root_cause_results
    
    def _get_upstream_paths(self, object_id, max_depth):
        """获取上游路径"""
        paths = []
        
        # 获取所有上游节点
        for source_id in self.lineage_graph.nodes():
            if source_id == object_id:
                continue
                
            if nx.has_path(self.lineage_graph, source_id, object_id):
                try:
                    path = nx.shortest_path(self.lineage_graph, source_id, object_id)
                    if len(path) <= max_depth + 1:  # 路径长度不超过max_depth+1
                        paths.append({
                            "source_id": source_id,
                            "target_id": object_id,
                            "path": path,
                            "length": len(path) - 1
                        })
                except nx.NetworkXNoPath:
                    continue
        
        return paths
    
    def _identify_suspected_sources(self, object_id, upstream_paths, issue_type):
        """识别可疑来源"""
        suspected_sources = []
        
        for path_info in upstream_paths:
            source_id = path_info["source_id"]
            path = path_info["path"]
            
            # 检查源对象是否有问题
            if self._has_source_issues(source_id, issue_type):
                node_data = self.lineage_graph.nodes[source_id]
                
                suspected_source = {
                    "source_id": source_id,
                    "source_name": node_data.get("name", source_id),
                    "object_type": node_data.get("object_type", "unknown"),
                    "system_name": node_data.get("system_name", "unknown"),
                    "path_length": path_info["length"],
                    "path": path,
                    "issues": self._get_source_issues(source_id, issue_type),
                    "likelihood": self._calculate_source_likelihood(source_id, path_info["length"])
                }
                
                suspected_sources.append(suspected_source)
        
        return suspected_sources
    
    def _has_source_issues(self, source_id, issue_type):
        """检查源对象是否有问题"""
        # 在实际实现中，这里会查询数据质量监控系统
        # 为了演示，我们使用简单的模拟逻辑
        return hash(source_id) % 3 == 0  # 简单的伪随机逻辑
    
    def _get_source_issues(self, source_id, issue_type):
        """获取源对象的问题"""
        # 在实际实现中，这里会查询数据质量监控系统
        # 为了演示，我们返回模拟的问题
        issues = []
        
        if hash(source_id) % 2 == 0:
            issues.append({
                "type": issue_type,
                "description": f"检测到{issue_type}问题",
                "severity": "中"
            })
        
        if hash(source_id) % 4 == 0:
            issues.append({
                "type": "data_freshness",
                "description": "数据 freshness 问题",
                "severity": "低"
            })
        
        return issues
    
    def _calculate_source_likelihood(self, source_id, path_length):
        """计算源是根本原因的可能性"""
        # 路径越短，可能性越高
        base_likelihood = 1.0 / (path_length + 1)
        
        # 添加一些随机性
        random_factor = 0.8 + (hash(source_id) % 5) / 10
        
        return min(base_likelihood * random_factor, 1.0)
    
    def _analyze_potential_causes(self, object_id, upstream_paths, issue_type):
        """分析潜在原因"""
        potential_causes = []
        
        # 分析转换问题
        transformation_issues = self._analyze_transformation_issues(upstream_paths, issue_type)
        potential_causes.extend(transformation_issues)
        
        # 分析数据质量问题
        data_quality_issues = self._analyze_data_quality_issues(upstream_paths, issue_type)
        potential_causes.extend(data_quality_issues)
        
        # 分析系统问题
        system_issues = self._analyze_system_issues(upstream_paths, issue_type)
        potential_causes.extend(system_issues)
        
        return potential_causes
    
    def _analyze_transformation_issues(self, upstream_paths, issue_type):
        """分析转换问题"""
        transformation_issues = []
        
        for path_info in upstream_paths:
            path = path_info["path"]
            
            # 检查路径中的转换
            for i in range(len(path) - 1):
                source = path[i]
                target = path[i + 1]
                
                if self.lineage_graph.has_edge(source, target):
                    edge_data = self.lineage_graph.edges[source, target]
                    transformation_type = edge_data.get("transformation_type", "unknown")
                    
                    # 检查是否可能有转换问题
                    if self._has_transformation_issue(transformation_type, issue_type):
                        transformation_issues.append({
                            "type": "transformation_issue",
                            "description": f"转换 {transformation_type} 可能导致 {issue_type} 问题",
                            "source": source,
                            "target": target,
                            "transformation_type": transformation_type,
                            "likelihood": 0.6
                        })
        
        return transformation_issues
    
    def _has_transformation_issue(self, transformation_type, issue_type):
        """检查是否有转换问题"""
        # 在实际实现中，这里会有更复杂的逻辑
        # 为了演示，我们使用简单的匹配逻辑
        high_risk_transformations = ["join", "union", "aggregation"]
        return transformation_type.lower() in high_risk_transformations
    
    def _analyze_data_quality_issues(self, upstream_paths, issue_type):
        """分析数据质量问题"""
        data_quality_issues = []
        
        # 分析上游路径中的数据质量问题
        source_ids = set(path["source_id"] for path in upstream_paths)
        
        for source_id in source_ids:
            if self.lineage_graph.has_node(source_id):
                node_data = self.lineage_graph.nodes[source_id]
                
                # 检查数据质量指标
                quality_metrics = self._get_data_quality_metrics(source_id)
                
                for metric, value in quality_metrics.items():
                    if value < 0.8 and self._is_metric_related_to_issue(metric, issue_type):
                        data_quality_issues.append({
                            "type": "data_quality_issue",
                            "description": f"源对象 {source_id} 的 {metric} 指标过低",
                            "source_id": source_id,
                            "metric": metric,
                            "value": value,
                            "threshold": 0.8,
                            "likelihood": 1.0 - value
                        })
        
        return data_quality_issues
    
    def _get_data_quality_metrics(self, source_id):
        """获取数据质量指标"""
        # 在实际实现中，这里会查询数据质量系统
        # 为了演示，我们返回模拟的指标
        base_metrics = {
            "completeness": 0.85,
            "accuracy": 0.92,
            "consistency": 0.78,
            "timeliness": 0.9
        }
        
        # 添加一些随机性
        import random
        return {
            metric: max(0.5, min(1.0, value + (random.random() - 0.5) * 0.2))
            for metric, value in base_metrics.items()
        }
    
    def _is_metric_related_to_issue(self, metric, issue_type):
        """检查指标是否与问题类型相关"""
        metric_issue_mapping = {
            "completeness": ["null_values", "missing_data"],
            "accuracy": ["inaccurate_data", "incorrect_values"],
            "consistency": ["inconsistent_data", "format_issues"],
            "timeliness": ["stale_data", "latency_issues"]
        }
        
        related_issues = metric_issue_mapping.get(metric, [])
        return issue_type in related_issues
    
    def _analyze_system_issues(self, upstream_paths, issue_type):
        """分析系统问题"""
        system_issues = []
        
        # 分析上游路径中的系统
        source_systems = set()
        for path_info in upstream_paths:
            path = path_info["path"]
            for node_id in path:
                if self.lineage_graph.has_node(node_id):
                    node_data = self.lineage_graph.nodes[node_id]
                    system_name = node_data.get("system_name", "unknown")
                    source_systems.add(system_name)
        
        # 检查系统是否有问题
        for system_name in source_systems:
            if self._has_system_issues(system_name):
                system_issues.append({
                    "type": "system_issue",
                    "description": f"系统 {system_name} 可能有性能或可用性问题",
                    "system_name": system_name,
                    "likelihood": 0.5
                })
        
        return system_issues
    
    def _has_system_issues(self, system_name):
        """检查系统是否有问题"""
        # 在实际实现中，这里会查询系统监控系统
        # 为了演示，我们使用简单的随机逻辑
        import random
        return random.random() < 0.2  # 20%的概率有系统问题
    
    def _deduplicate_sources(self, suspected_sources):
        """去重可疑来源"""
        unique_sources = {}
        
        for source in suspected_sources:
            source_id = source["source_id"]
            
            if source_id not in unique_sources:
                unique_sources[source_id] = source
            else:
                # 合并问题
                existing_issues = set(
                    issue["type"] for issue in unique_sources[source_id]["issues"]
                )
                new_issues = set(
                    issue["type"] for issue in source["issues"]
                )
                
                # 添加新问题
                for issue in source["issues"]:
                    if issue["type"] not in existing_issues:
                        unique_sources[source_id]["issues"].append(issue)
                
                # 更新可能性（取较高值）
                unique_sources[source_id]["likelihood"] = max(
                    unique_sources[source_id]["likelihood"],
                    source["likelihood"]
                )
        
        return list(unique_sources.values())
    
    def _deduplicate_causes(self, potential_causes):
        """去重潜在原因"""
        unique_causes = {}
        
        for cause in potential_causes:
            cause_key = f"{cause['type']}_{cause.get('source', 'unknown')}_{cause.get('target', 'unknown')}"
            
            if cause_key not in unique_causes:
                unique_causes[cause_key] = cause
            else:
                # 更新可能性（取较高值）
                unique_causes[cause_key]["likelihood"] = max(
                    unique_causes[cause_key]["likelihood"],
                    cause["likelihood"]
                )
        
        return list(unique_causes.values())
    
    def _deduplicate_paths(self, analysis_paths):
        """去重分析路径"""
        unique_paths = {}
        
        for path in analysis_paths:
            path_key = f"{path['source_id']}->{path['target_id']}"
            
            if path_key not in unique_paths:
                unique_paths[path_key] = path
            else:
                # 保留较短的路径
                if path["length"] < unique_paths[path_key]["length"]:
                    unique_paths[path_key] = path
        
        return list(unique_paths.values())
    
    def _calculate_confidence_scores(self, suspected_sources, potential_causes):
        """计算置信度分数"""
        confidence_scores = {}
        
        # 为每个可疑来源计算置信度
        for source in suspected_sources:
            source_id = source["source_id"]
            confidence_scores[f"source_{source_id}"] = source["likelihood"]
        
        # 为每个潜在原因计算置信度
        for cause in potential_causes:
            cause_key = f"cause_{cause['type']}_{cause.get('source', 'unknown')}_{cause.get('target', 'unknown')}"
            confidence_scores[cause_key] = cause["likelihood"]
        
        return confidence_scores
    
    def _generate_root_cause_recommendations(self, issue_type, suspected_sources):
        """生成根因分析推荐"""
        recommendations = []
        
        # 基于问题类型的推荐
        if issue_type == "data_quality":
            recommendations.append({
                "priority": "高",
                "category": "数据质量",
                "recommendation": "建议实施数据质量监控和清洗流程",
                "action_items": [
                    "建立数据质量检查规则",
                    "实施数据质量仪表板",
                    "定期审查数据质量问题"
                ]
            })
        elif issue_type == "performance":
            recommendations.append({
                "priority": "中",
                "category": "性能优化",
                "recommendation": "建议优化数据处理性能",
                "action_items": [
                    "分析处理瓶颈",
                    "优化查询或ETL流程",
                    "增加资源分配"
                ]
            })
        
        # 基于可疑来源的推荐
        if suspected_sources:
            high_likelihood_sources = [
                source for source in suspected_sources
                if source["likelihood"] >= 0.7
            ]
            
            if high_likelihood_sources:
                recommendations.append({
                    "priority": "高",
                    "category": "问题修复",
                    "recommendation": f"优先处理高可能性的问题来源: {', '.join([s['source_id'] for s in high_likelihood_sources])}",
                    "action_items": [
                        "调查高可能性来源的具体问题",
                        "实施修复措施",
                        "验证修复效果"
                    ]
                })
        
        return recommendations
    
    def visualize_impact_analysis(self, impact_results, output_file="impact_analysis.png"):
        """可视化影响分析结果"""
        # 创建图表
        plt.figure(figsize=(15, 10))
        
        # 1. 影响分布饼图
        plt.subplot(2, 2, 1)
        labels = ['直接影响', '间接影响']
        sizes = [
            impact_results["impact_summary"]["direct_impacts_count"],
            impact_results["impact_summary"]["indirect_impacts_count"]
        ]
        colors = ['lightcoral', 'lightskyblue']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('影响分布')
        
        # 2. 受影响系统条形图
        plt.subplot(2, 2, 2)
        systems = list(impact_results["affected_systems"].keys())
        impact_counts = [
            impact_results["affected_systems"][system]["impact_count"]
            for system in systems
        ]
        
        plt.barh(systems, impact_counts, color='skyblue')
        plt.title('受影响系统')
        plt.xlabel('影响对象数量')
        
        # 3. 风险评估
        plt.subplot(2, 2, 3)
        risk_factors = impact_results["risk_assessment"]["risk_factors"]
        factor_names = list(risk_factors.keys())
        factor_values = list(risk_factors.values())
        
        plt.bar(factor_names, factor_values, color='lightgreen')
        plt.title('风险因素')
        plt.xticks(rotation=45)
        plt.ylabel('风险分数')
        
        # 4. 关键路径重要性
        plt.subplot(2, 2, 4)
        if impact_results["critical_paths"]:
            paths = [f"路径{i+1}" for i in range(min(5, len(impact_results["critical_paths"])))]
            importances = [
                path["importance"] for path in impact_results["critical_paths"][:5]
            ]
            
            plt.bar(paths, importances, color='orange')
            plt.title('关键路径重要性')
            plt.ylabel('重要性分数')
            plt.xticks(rotation=45)
        else:
            plt.text(0.5, 0.5, '无关键路径', ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('关键路径重要性')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"影响分析图表已保存为 {output_file}"
    
    def generate_impact_report(self, impact_results, output_file=None):
        """生成影响分析报告"""
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.datetime.now().isoformat(),
            "report_type": "impact_analysis",
            "summary": impact_results["impact_summary"],
            "risk_assessment": impact_results["risk_assessment"],
            "affected_systems": impact_results["affected_systems"],
            "recommendations": impact_results["recommendations"],
            "detailed_results": {
                "direct_impacts": impact_results["detailed_impacts"]["direct_impacts"],
                "indirect_impacts": impact_results["detailed_impacts"]["indirect_impacts"]
            },
            "critical_paths": impact_results["critical_paths"][:5]  # 只包含前5个关键路径
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            report["output_file"] = output_file
        
        return report

def create_sample_lineage_graph():
    """创建示例血缘图"""
    analyzer = LineageImpactAnalyzer()
    
    # 添加数据对象
    objects = [
        {"id": "raw.customers", "name": "customers", "type": "table", "system": "production"},
        {"id": "raw.orders", "name": "orders", "type": "table", "system": "production"},
        {"id": "raw.products", "name": "products", "type": "table", "system": "production"},
        {"id": "staging.customer_orders", "name": "customer_orders", "type": "table", "system": "staging"},
        {"id": "dw.daily_sales", "name": "daily_sales", "type": "table", "system": "analytics"},
        {"id": "dw.monthly_sales", "name": "monthly_sales", "type": "view", "system": "analytics"},
        {"id": "reports.sales_dashboard", "name": "sales_dashboard", "type": "dashboard", "system": "reporting"},
        {"id": "reports.executive_report", "name": "executive_report", "type": "report", "system": "reporting"},
        {"id": "ml.sales_forecast", "name": "sales_forecast", "type": "ml_model", "system": "analytics"},
        {"id": "api.sales_api", "name": "sales_api", "type": "api", "system": "production"}
    ]
    
    for obj in objects:
        analyzer.add_data_object(obj["id"], obj["name"], obj["type"], obj["system"])
    
    # 添加血缘关系
    relationships = [
        {"source": "raw.customers", "target": "staging.customer_orders", "type": "etl"},
        {"source": "raw.orders", "target": "staging.customer_orders", "type": "etl"},
        {"source": "raw.products", "target": "staging.customer_orders", "type": "etl"},
        {"source": "staging.customer_orders", "target": "dw.daily_sales", "type": "aggregation"},
        {"source": "dw.daily_sales", "target": "dw.monthly_sales", "type": "aggregation"},
        {"source": "dw.monthly_sales", "target": "reports.sales_dashboard", "type": "visualization"},
        {"source": "dw.monthly_sales", "target": "reports.executive_report", "type": "reporting"},
        {"source": "dw.daily_sales", "target": "ml.sales_forecast", "type": "ml_training"},
        {"source": "dw.daily_sales", "target": "api.sales_api", "type": "api_exposure"}
    ]
    
    for rel in relationships:
        analyzer.add_lineage_relationship(rel["source"], rel["target"], rel["type"])
    
    return analyzer

def main():
    """主函数"""
    print("=" * 50)
    print("血缘影响分析工具")
    print("=" * 50)
    
    # 创建示例血缘图
    print("创建示例血缘图...")
    analyzer = create_sample_lineage_graph()
    
    print(f"血缘图包含 {analyzer.lineage_graph.number_of_nodes()} 个节点和 {analyzer.lineage_graph.number_of_edges()} 条边")
    
    # 分析变更影响
    print("\n分析变更影响...")
    changed_objects = ["raw.customers", "dw.daily_sales"]
    change_type = "schema_change"
    
    impact_results = analyzer.analyze_change_impact(
        changed_objects, change_type, max_depth=3, include_upstream=True
    )
    
    # 显示影响摘要
    summary = impact_results["impact_summary"]
    print(f"\n影响摘要:")
    print(f"- 变更对象数: {summary['changed_objects_count']}")
    print(f"- 直接影响数: {summary['direct_impacts_count']}")
    print(f"- 间接影响数: {summary['indirect_impacts_count']}")
    print(f"- 受影响系统数: {summary['affected_systems_count']}")
    print(f"- 关键路径数: {summary['critical_paths_count']}")
    print(f"- 整体风险级别: {summary['overall_risk_level']}")
    
    # 显示风险因素
    print("\n风险因素:")
    risk_factors = impact_results["risk_assessment"]["risk_factors"]
    for factor, score in risk_factors.items():
        print(f"- {factor}: {score:.2f}")
    
    # 显示受影响的系统
    print("\n受影响的系统:")
    for system, details in impact_results["affected_systems"].items():
        print(f"- {system}: {details['impact_count']} 个对象受影响, 平均影响分数: {details['avg_impact_score']:.2f}")
    
    # 显示关键路径
    print("\n关键路径 (前3条):")
    for i, path in enumerate(impact_results["critical_paths"][:3]):
        print(f"{i+1}. {path['source_object']} -> {path['target_object']} (重要性: {path['importance']:.2f})")
    
    # 显示推荐措施
    print("\n推荐措施:")
    for i, rec in enumerate(impact_results["recommendations"][:3]):
        print(f"{i+1}. [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    
    # 可视化影响分析
    print("\n生成影响分析可视化...")
    viz_result = analyzer.visualize_impact_analysis(impact_results, "lineage_impact_analysis.png")
    print(viz_result)
    
    # 生成影响分析报告
    print("\n生成影响分析报告...")
    report = analyzer.generate_impact_report(impact_results, "impact_analysis_report.json")
    print("报告已生成")
    
    # 根因分析示例
    print("\n" + "=" * 50)
    print("根因分析示例")
    print("=" * 50)
    
    problematic_objects = ["reports.sales_dashboard", "ml.sales_forecast"]
    issue_type = "data_quality"
    
    print(f"分析对象: {problematic_objects}")
    print(f"问题类型: {issue_type}")
    
    root_cause_results = analyzer.analyze_root_cause(problematic_objects, issue_type, max_depth=3)
    
    # 显示可疑来源
    print(f"\n可疑来源 (前3条):")
    for i, source in enumerate(root_cause_results["suspected_sources"][:3]):
        print(f"{i+1}. {source['source_id']} (可能性: {source['likelihood']:.2f})")
        print(f"   问题: {', '.join([issue['type'] for issue in source['issues']])}")
    
    # 显示潜在原因
    print(f"\n潜在原因 (前3条):")
    for i, cause in enumerate(root_cause_results["potential_causes"][:3]):
        print(f"{i+1}. {cause['type']}: {cause['description']} (可能性: {cause['likelihood']:.2f})")
    
    # 显示置信度分数
    print("\n置信度分数 (前5条):")
    for i, (key, score) in enumerate(list(root_cause_results["confidence_scores"].items())[:5]):
        print(f"{i+1}. {key}: {score:.2f}")
    
    # 显示根因分析推荐
    print("\n根因分析推荐:")
    for i, rec in enumerate(root_cause_results["recommendations"][:3]):
        print(f"{i+1}. [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
    
    print("\n分析完成!")

if __name__ == "__main__":
    main()