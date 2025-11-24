#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据血缘管理器
功能：实现数据血缘的捕获、存储、查询和分析
作者：数据治理团队
日期：2023-11-23
"""

import json
import datetime
import uuid
import re
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class DataLineageManager:
    """数据血缘管理器主类"""
    
    def __init__(self, db_path="data_lineage.db"):
        """初始化数据血缘管理器"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._initialize_database()
        
        # 使用NetworkX构建内存中的血缘图
        self.lineage_graph = nx.DiGraph()
        self._load_graph_from_db()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        # 数据对象表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_objects (
                object_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                object_type TEXT NOT NULL,
                system_name TEXT,
                schema_name TEXT,
                description TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 血缘关系表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lineage_relationships (
                relationship_id TEXT PRIMARY KEY,
                source_object_id TEXT NOT NULL,
                target_object_id TEXT NOT NULL,
                transformation_type TEXT,
                transformation_logic TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_object_id) REFERENCES data_objects(object_id),
                FOREIGN KEY (target_object_id) REFERENCES data_objects(object_id)
            )
        """)
        
        # 血缘捕获日志表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lineage_capture_logs (
                log_id TEXT PRIMARY KEY,
                capture_method TEXT,
                source_system TEXT,
                capture_status TEXT,
                details TEXT,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def _load_graph_from_db(self):
        """从数据库加载血缘图"""
        self.lineage_graph.clear()
        
        # 加载所有数据对象作为节点
        self.cursor.execute("SELECT * FROM data_objects")
        for row in self.cursor.fetchall():
            object_id, name, object_type, system_name, schema_name, description, properties, created_at, updated_at = row
            self.lineage_graph.add_node(
                object_id,
                name=name,
                object_type=object_type,
                system_name=system_name,
                schema_name=schema_name,
                description=description,
                properties=json.loads(properties) if properties else {}
            )
        
        # 加载所有血缘关系作为边
        self.cursor.execute("SELECT * FROM lineage_relationships")
        for row in self.cursor.fetchall():
            relationship_id, source_id, target_id, transformation_type, transformation_logic, properties, created_at = row
            self.lineage_graph.add_edge(
                source_id,
                target_id,
                relationship_id=relationship_id,
                transformation_type=transformation_type,
                transformation_logic=transformation_logic,
                properties=json.loads(properties) if properties else {}
            )
    
    def register_data_object(self, object_id, name, object_type, system_name=None, 
                            schema_name=None, description=None, properties=None):
        """注册数据对象"""
        properties_json = json.dumps(properties) if properties else None
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO data_objects 
            (object_id, name, object_type, system_name, schema_name, description, properties, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (object_id, name, object_type, system_name, schema_name, description, properties_json))
        
        self.conn.commit()
        
        # 更新内存中的图
        self.lineage_graph.add_node(
            object_id,
            name=name,
            object_type=object_type,
            system_name=system_name,
            schema_name=schema_name,
            description=description,
            properties=properties or {}
        )
        
        return object_id
    
    def add_lineage_relationship(self, source_id, target_id, transformation_type=None, 
                               transformation_logic=None, properties=None):
        """添加血缘关系"""
        relationship_id = str(uuid.uuid4())
        properties_json = json.dumps(properties) if properties else None
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO lineage_relationships 
            (relationship_id, source_object_id, target_object_id, transformation_type, transformation_logic, properties)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (relationship_id, source_id, target_id, transformation_type, transformation_logic, properties_json))
        
        self.conn.commit()
        
        # 更新内存中的图
        self.lineage_graph.add_edge(
            source_id,
            target_id,
            relationship_id=relationship_id,
            transformation_type=transformation_type,
            transformation_logic=transformation_logic,
            properties=properties or {}
        )
        
        return relationship_id
    
    def extract_lineage_from_sql(self, sql_query, job_name=None):
        """从SQL查询中提取血缘关系"""
        try:
            # 简化的SQL解析器，实际应用中可能需要更复杂的解析
            source_tables = self._extract_source_tables(sql_query)
            target_tables = self._extract_target_tables(sql_query)
            
            extracted_lineage = {
                "job_id": str(uuid.uuid4()),
                "job_name": job_name,
                "sql_query": sql_query,
                "source_tables": source_tables,
                "target_tables": target_tables,
                "extracted_at": datetime.datetime.now().isoformat()
            }
            
            # 记录血缘捕获日志
            self._log_lineage_capture("sql_parsing", "SQL Query", "success", 
                                     f"提取到{len(source_tables)}个源表和{len(target_tables)}个目标表")
            
            return extracted_lineage
            
        except Exception as e:
            self._log_lineage_capture("sql_parsing", "SQL Query", "error", str(e))
            raise e
    
    def _extract_source_tables(self, sql_query):
        """从SQL中提取源表"""
        source_tables = []
        
        # 简化实现：通过正则表达式提取FROM子句中的表名
        from_pattern = r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        join_pattern = r'(?:INNER|LEFT|RIGHT|FULL)\s+JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        
        # 提取FROM子句中的表
        from_matches = re.findall(from_pattern, sql_query, re.IGNORECASE)
        source_tables.extend(from_matches)
        
        # 提取JOIN子句中的表
        join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)
        source_tables.extend(join_matches)
        
        # 去重并返回
        return list(set(source_tables))
    
    def _extract_target_tables(self, sql_query):
        """从SQL中提取目标表"""
        target_tables = []
        
        # 简化实现：通过正则表达式提取INSERT INTO或CREATE TABLE AS中的表名
        insert_pattern = r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        create_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        
        # 提取INSERT INTO中的表
        insert_matches = re.findall(insert_pattern, sql_query, re.IGNORECASE)
        target_tables.extend(insert_matches)
        
        # 提取CREATE TABLE中的表
        create_matches = re.findall(create_pattern, sql_query, re.IGNORECASE)
        target_tables.extend(create_matches)
        
        # 去重并返回
        return list(set(target_tables))
    
    def apply_extracted_lineage(self, extracted_lineage, system_name="default"):
        """应用提取的血缘关系"""
        try:
            source_tables = extracted_lineage["source_tables"]
            target_tables = extracted_lineage["target_tables"]
            transformation_logic = extracted_lineage["sql_query"]
            
            created_relationships = []
            
            # 为每个源表-目标表对创建血缘关系
            for source_table in source_tables:
                for target_table in target_tables:
                    # 确保源表和目标表已注册
                    source_id = self._ensure_table_registered(source_table, system_name)
                    target_id = self._ensure_table_registered(target_table, system_name)
                    
                    # 添加血缘关系
                    relationship_id = self.add_lineage_relationship(
                        source_id, 
                        target_id, 
                        transformation_type="SQL",
                        transformation_logic=transformation_logic,
                        properties={
                            "job_id": extracted_lineage["job_id"],
                            "job_name": extracted_lineage.get("job_name"),
                            "extracted_at": extracted_lineage["extracted_at"]
                        }
                    )
                    
                    created_relationships.append(relationship_id)
            
            # 记录血缘捕获日志
            self._log_lineage_capture("apply_lineage", system_name, "success", 
                                     f"创建了{len(created_relationships)}个血缘关系")
            
            return created_relationships
            
        except Exception as e:
            self._log_lineage_capture("apply_lineage", system_name, "error", str(e))
            raise e
    
    def _ensure_table_registered(self, table_name, system_name):
        """确保表已注册"""
        # 拆分表名为模式名和表名
        if "." in table_name:
            schema_name, table_name_only = table_name.split(".", 1)
        else:
            schema_name = None
            table_name_only = table_name
        
        # 生成对象ID
        object_id = f"{system_name}.{schema_name}.{table_name_only}" if schema_name else f"{system_name}.{table_name_only}"
        
        # 检查是否已注册
        if not self.lineage_graph.has_node(object_id):
            # 注册新表
            self.register_data_object(
                object_id=object_id,
                name=table_name_only,
                object_type="table",
                system_name=system_name,
                schema_name=schema_name,
                description=f"表 {table_name}"
            )
        
        return object_id
    
    def _log_lineage_capture(self, capture_method, source_system, capture_status, details):
        """记录血缘捕获日志"""
        log_id = str(uuid.uuid4())
        details_json = json.dumps({"details": details}) if details else None
        
        self.cursor.execute("""
            INSERT INTO lineage_capture_logs 
            (log_id, capture_method, source_system, capture_status, details)
            VALUES (?, ?, ?, ?, ?)
        """, (log_id, capture_method, source_system, capture_status, details_json))
        
        self.conn.commit()
    
    def get_upstream_lineage(self, object_id, max_depth=3):
        """获取上游血缘"""
        if not self.lineage_graph.has_node(object_id):
            return []
        
        upstream_nodes = []
        visited = set()
        
        # 使用广度优先搜索获取上游节点
        for depth in range(1, max_depth + 1):
            depth_nodes = []
            
            if depth == 1:
                # 第一层：直接上游
                for predecessor in self.lineage_graph.predecessors(object_id):
                    if predecessor not in visited:
                        node_data = self.lineage_graph.nodes[predecessor]
                        edge_data = self.lineage_graph.edges[predecessor, object_id]
                        
                        depth_nodes.append({
                            "object_id": predecessor,
                            "depth": depth,
                            "path": [predecessor, object_id],
                            "node_data": node_data,
                            "edge_data": edge_data
                        })
                        visited.add(predecessor)
            else:
                # 更深层：间接上游
                for prev_depth_node in upstream_nodes:
                    if prev_depth_node["depth"] == depth - 1:
                        source_id = prev_depth_node["object_id"]
                        
                        for predecessor in self.lineage_graph.predecessors(source_id):
                            if predecessor not in visited:
                                node_data = self.lineage_graph.nodes[predecessor]
                                edge_data = self.lineage_graph.edges[predecessor, source_id]
                                path = prev_depth_node["path"].copy()
                                path.insert(0, predecessor)
                                
                                depth_nodes.append({
                                    "object_id": predecessor,
                                    "depth": depth,
                                    "path": path,
                                    "node_data": node_data,
                                    "edge_data": edge_data
                                })
                                visited.add(predecessor)
            
            if depth_nodes:
                upstream_nodes.extend(depth_nodes)
        
        return upstream_nodes
    
    def get_downstream_lineage(self, object_id, max_depth=3):
        """获取下游血缘"""
        if not self.lineage_graph.has_node(object_id):
            return []
        
        downstream_nodes = []
        visited = set()
        
        # 使用广度优先搜索获取下游节点
        for depth in range(1, max_depth + 1):
            depth_nodes = []
            
            if depth == 1:
                # 第一层：直接下游
                for successor in self.lineage_graph.successors(object_id):
                    if successor not in visited:
                        node_data = self.lineage_graph.nodes[successor]
                        edge_data = self.lineage_graph.edges[object_id, successor]
                        
                        depth_nodes.append({
                            "object_id": successor,
                            "depth": depth,
                            "path": [object_id, successor],
                            "node_data": node_data,
                            "edge_data": edge_data
                        })
                        visited.add(successor)
            else:
                # 更深层：间接下游
                for prev_depth_node in downstream_nodes:
                    if prev_depth_node["depth"] == depth - 1:
                        target_id = prev_depth_node["object_id"]
                        
                        for successor in self.lineage_graph.successors(target_id):
                            if successor not in visited:
                                node_data = self.lineage_graph.nodes[successor]
                                edge_data = self.lineage_graph.edges[target_id, successor]
                                path = prev_depth_node["path"].copy()
                                path.append(successor)
                                
                                depth_nodes.append({
                                    "object_id": successor,
                                    "depth": depth,
                                    "path": path,
                                    "node_data": node_data,
                                    "edge_data": edge_data
                                })
                                visited.add(successor)
            
            if depth_nodes:
                downstream_nodes.extend(depth_nodes)
        
        return downstream_nodes
    
    def get_lineage_summary(self):
        """获取血缘摘要统计"""
        total_nodes = self.lineage_graph.number_of_nodes()
        total_edges = self.lineage_graph.number_of_edges()
        
        # 按对象类型统计
        object_types = {}
        for node_id, node_data in self.lineage_graph.nodes(data=True):
            object_type = node_data.get("object_type", "unknown")
            object_types[object_type] = object_types.get(object_type, 0) + 1
        
        # 按系统统计
        systems = {}
        for node_id, node_data in self.lineage_graph.nodes(data=True):
            system_name = node_data.get("system_name", "unknown")
            systems[system_name] = systems.get(system_name, 0) + 1
        
        # 按转换类型统计
        transformation_types = {}
        for _, _, edge_data in self.lineage_graph.edges(data=True):
            transformation_type = edge_data.get("transformation_type", "unknown")
            transformation_types[transformation_type] = transformation_types.get(transformation_type, 0) + 1
        
        return {
            "total_objects": total_nodes,
            "total_relationships": total_edges,
            "object_types": object_types,
            "systems": systems,
            "transformation_types": transformation_types,
            "is_fully_connected": nx.is_weakly_connected(self.lineage_graph),
            "connected_components": nx.number_weakly_connected_components(self.lineage_graph)
        }
    
    def analyze_impact(self, changed_objects, max_depth=3):
        """分析数据变更的影响"""
        impact_results = {
            "changed_objects": changed_objects,
            "direct_impacts": [],
            "indirect_impacts": [],
            "critical_paths": [],
            "affected_systems": {},
            "summary": {}
        }
        
        all_affected = set()
        system_impacts = {}
        
        for obj_id in changed_objects:
            # 获取下游血缘
            downstream_lineage = self.get_downstream_lineage(obj_id, max_depth)
            
            # 分析直接影响（第一层）
            direct_impacts = [item for item in downstream_lineage if item["depth"] == 1]
            impact_results["direct_impacts"].extend(direct_impacts)
            
            # 分析间接影响（更深层）
            indirect_impacts = [item for item in downstream_lineage if item["depth"] > 1]
            impact_results["indirect_impacts"].extend(indirect_impacts)
            
            # 收集所有受影响的对象
            for item in downstream_lineage:
                all_affected.add(item["object_id"])
                
                # 统计受影响的系统
                node_data = item["node_data"]
                system_name = node_data.get("system_name", "unknown")
                if system_name not in system_impacts:
                    system_impacts[system_name] = 0
                system_impacts[system_name] += 1
        
        # 识别关键路径
        impact_results["critical_paths"] = self._identify_critical_paths(changed_objects)
        
        impact_results["affected_systems"] = system_impacts
        
        # 生成摘要
        impact_results["summary"] = {
            "total_changed_objects": len(changed_objects),
            "total_directly_affected": len(impact_results["direct_impacts"]),
            "total_indirectly_affected": len(impact_results["indirect_impacts"]),
            "total_affected_systems": len(system_impacts),
            "total_affected_objects": len(all_affected)
        }
        
        return impact_results
    
    def _identify_critical_paths(self, changed_objects, max_paths=5):
        """识别关键路径"""
        critical_paths = []
        
        for obj_id in changed_objects:
            # 使用最短路径算法找到重要路径
            all_paths = []
            
            # 获取所有下游对象
            for target_id in self.lineage_graph.nodes():
                if obj_id != target_id and nx.has_path(self.lineage_graph, obj_id, target_id):
                    # 获取最短路径
                    shortest_path = nx.shortest_path(self.lineage_graph, obj_id, target_id)
                    
                    # 计算路径重要性
                    importance = self._calculate_path_importance(shortest_path)
                    
                    all_paths.append({
                        "path": shortest_path,
                        "importance": importance
                    })
            
            # 按重要性排序，取前max_paths条
            all_paths.sort(key=lambda x: x["importance"], reverse=True)
            
            for i, path_info in enumerate(all_paths[:max_paths]):
                critical_paths.append({
                    "source_object": obj_id,
                    "target_object": path_info["path"][-1],
                    "path_length": len(path_info["path"]) - 1,
                    "importance": path_info["importance"],
                    "path_nodes": path_info["path"]
                })
        
        # 按重要性排序所有关键路径
        critical_paths.sort(key=lambda x: x["importance"], reverse=True)
        
        return critical_paths
    
    def _calculate_path_importance(self, path):
        """计算路径重要性"""
        # 基于路径中节点的类型和系统重要性计算
        importance_scores = {
            "table": 0.8,
            "view": 0.7,
            "report": 0.9,
            "dashboard": 0.9,
            "api": 0.8
        }
        
        system_scores = {
            "production": 0.9,
            "staging": 0.7,
            "development": 0.5,
            "analytics": 0.8,
            "reporting": 0.9
        }
        
        total_score = 0
        for node_id in path:
            node_data = self.lineage_graph.nodes[node_id]
            
            system_name = node_data.get("system_name", "development")
            object_type = node_data.get("object_type", "table")
            
            system_score = system_scores.get(system_name, 0.5)
            type_score = importance_scores.get(object_type, 0.5)
            
            total_score += (system_score + type_score) / 2
        
        # 归一化分数
        normalized_score = total_score / len(path) if path else 0
        return min(normalized_score, 1.0)  # 确保不超过1.0
    
    def visualize_lineage_graph(self, output_file="data_lineage_graph.png", 
                              focus_objects=None, max_depth=2):
        """可视化血缘图"""
        # 创建子图
        if focus_objects:
            subgraph_nodes = set(focus_objects)
            
            # 添加相关节点
            for obj_id in focus_objects:
                # 添加上游节点
                upstream = self.get_upstream_lineage(obj_id, max_depth)
                for item in upstream:
                    subgraph_nodes.add(item["object_id"])
                    subgraph_nodes.update(item["path"])
                
                # 添加下游节点
                downstream = self.get_downstream_lineage(obj_id, max_depth)
                for item in downstream:
                    subgraph_nodes.add(item["object_id"])
                    subgraph_nodes.update(item["path"])
            
            subgraph = self.lineage_graph.subgraph(subgraph_nodes)
        else:
            subgraph = self.lineage_graph
        
        # 设置图形大小
        plt.figure(figsize=(15, 10))
        
        # 使用spring layout布局
        pos = nx.spring_layout(subgraph, k=0.5, iterations=50)
        
        # 按对象类型设置节点颜色
        node_colors = []
        for node_id in subgraph.nodes():
            node_data = subgraph.nodes[node_id]
            object_type = node_data.get("object_type", "unknown")
            
            if object_type == "table":
                node_colors.append('skyblue')
            elif object_type == "view":
                node_colors.append('lightgreen')
            elif object_type == "report":
                node_colors.append('salmon')
            elif object_type == "dashboard":
                node_colors.append('orange')
            elif object_type == "api":
                node_colors.append('purple')
            else:
                node_colors.append('gray')
        
        # 绘制节点
        nx.draw_networkx_nodes(
            subgraph, pos,
            node_size=800,
            node_color=node_colors,
            alpha=0.8
        )
        
        # 绘制边
        nx.draw_networkx_edges(
            subgraph, pos,
            width=1.5,
            alpha=0.6,
            edge_color='gray',
            arrows=True,
            arrowsize=20
        )
        
        # 绘制标签
        labels = {}
        for node_id in subgraph.nodes():
            node_data = subgraph.nodes[node_id]
            name = node_data.get("name", node_id)
            # 限制标签长度
            labels[node_id] = name[:15] + "..." if len(name) > 15 else name
        
        nx.draw_networkx_labels(
            subgraph, pos,
            labels=labels,
            font_size=10,
            font_family='sans-serif'
        )
        
        # 如果有焦点对象，突出显示
        if focus_objects:
            focus_pos = {obj_id: pos[obj_id] for obj_id in focus_objects if obj_id in pos}
            nx.draw_networkx_nodes(
                subgraph, focus_pos,
                node_size=1000,
                node_color='red',
                alpha=0.8
            )
        
        # 添加图例
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='skyblue', markersize=10, label='表'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=10, label='视图'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='salmon', markersize=10, label='报告'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='仪表板'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=10, label='API')
        ]
        
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title("数据血缘图", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图片
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return f"血缘图已保存为 {output_file}"
    
    def generate_lineage_report(self, object_id, output_file=None):
        """生成血缘报告"""
        if not self.lineage_graph.has_node(object_id):
            return {"error": f"数据对象 {object_id} 不存在"}
        
        # 获取对象详情
        node_data = self.lineage_graph.nodes[object_id]
        
        # 获取上游血缘
        upstream_lineage = self.get_upstream_lineage(object_id, 3)
        
        # 获取下游血缘
        downstream_lineage = self.get_downstream_lineage(object_id, 3)
        
        # 计算指标
        direct_upstream_count = len([item for item in upstream_lineage if item["depth"] == 1])
        total_upstream_count = len(upstream_lineage)
        direct_downstream_count = len([item for item in downstream_lineage if item["depth"] == 1])
        total_downstream_count = len(downstream_lineage)
        
        # 生成报告
        report = {
            "object_id": object_id,
            "object_name": node_data.get("name", object_id),
            "object_type": node_data.get("object_type", "unknown"),
            "system_name": node_data.get("system_name", "unknown"),
            "report_generated_at": datetime.datetime.now().isoformat(),
            "lineage_metrics": {
                "direct_upstream_count": direct_upstream_count,
                "total_upstream_count": total_upstream_count,
                "direct_downstream_count": direct_downstream_count,
                "total_downstream_count": total_downstream_count,
                "total_dependencies": direct_upstream_count + direct_downstream_count
            },
            "upstream_lineage": upstream_lineage,
            "downstream_lineage": downstream_lineage,
            "critical_paths": self._identify_critical_paths([object_id], 3)
        }
        
        # 如果指定了输出文件，保存报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            report["output_file"] = output_file
        
        return report
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    """主函数"""
    print("=" * 50)
    print("数据血缘管理器")
    print("=" * 50)
    
    # 创建数据血缘管理器
    lineage_manager = DataLineageManager()
    
    # 注册示例数据对象
    print("注册示例数据对象...")
    data_objects = [
        {"object_id": "db.sales.customers", "name": "customers", "object_type": "table", "system_name": "db", "schema_name": "sales"},
        {"object_id": "db.sales.orders", "name": "orders", "object_type": "table", "system_name": "db", "schema_name": "sales"},
        {"object_id": "dw.sales.customer_orders", "name": "customer_orders", "object_type": "table", "system_name": "dw", "schema_name": "sales"},
        {"object_id": "dw.analytics.daily_sales", "name": "daily_sales", "object_type": "view", "system_name": "dw", "schema_name": "analytics"},
        {"object_id": "reporting.sales.monthly_report", "name": "monthly_report", "object_type": "report", "system_name": "reporting", "schema_name": "sales"},
        {"object_id": "dashboard.sales.overview", "name": "overview", "object_type": "dashboard", "system_name": "dashboard", "schema_name": "sales"}
    ]
    
    for obj in data_objects:
        lineage_manager.register_data_object(**obj)
    
    print(f"已注册 {len(data_objects)} 个数据对象")
    
    # 从SQL提取血缘
    print("\n从SQL查询中提取血缘...")
    sql_queries = [
        {
            "sql": """
            CREATE TABLE dw.sales.customer_orders AS
            SELECT c.customer_id, c.name, o.order_id, o.order_date, o.amount
            FROM db.sales.customers c
            JOIN db.sales.orders o ON c.customer_id = o.customer_id
            """,
            "name": "创建客户订单表"
        },
        {
            "sql": """
            INSERT INTO dw.analytics.daily_sales (date, total_amount, order_count)
            SELECT 
                order_date as date,
                SUM(amount) as total_amount,
                COUNT(*) as order_count
            FROM dw.sales.customer_orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY order_date
            """,
            "name": "更新日销售分析"
        },
        {
            "sql": """
            INSERT INTO reporting.sales.monthly_report (month, revenue, customers)
            SELECT 
                DATE_TRUNC('month', date) as month,
                SUM(total_amount) as revenue,
                COUNT(DISTINCT customer_id) as customers
            FROM dw.analytics.daily_sales
            WHERE date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', date)
            """,
            "name": "更新月度报告"
        }
    ]
    
    for query in sql_queries:
        extracted_lineage = lineage_manager.extract_lineage_from_sql(query["sql"], query["name"])
        lineage_manager.apply_extracted_lineage(extracted_lineage, "ETL")
    
    print("已提取并应用血缘关系")
    
    # 添加一些手动血缘关系
    lineage_manager.add_lineage_relationship(
        "dw.analytics.daily_sales", 
        "dashboard.sales.overview", 
        transformation_type="API"
    )
    
    # 获取血缘摘要
    print("\n获取血缘摘要...")
    lineage_summary = lineage_manager.get_lineage_summary()
    print(f"数据对象总数: {lineage_summary['total_objects']}")
    print(f"血缘关系总数: {lineage_summary['total_relationships']}")
    print(f"对象类型分布: {lineage_summary['object_types']}")
    print(f"系统分布: {lineage_summary['systems']}")
    
    # 获取特定对象的上游血缘
    print("\n获取对象 'dw.analytics.daily_sales' 的上游血缘...")
    upstream_lineage = lineage_manager.get_upstream_lineage("dw.analytics.daily_sales", 3)
    print(f"上游对象数: {len(upstream_lineage)}")
    for item in upstream_lineage:
        print(f"- {item['object_id']} (深度: {item['depth']})")
    
    # 获取特定对象的下游血缘
    print("\n获取对象 'dw.sales.customer_orders' 的下游血缘...")
    downstream_lineage = lineage_manager.get_downstream_lineage("dw.sales.customer_orders", 3)
    print(f"下游对象数: {len(downstream_lineage)}")
    for item in downstream_lineage:
        print(f"- {item['object_id']} (深度: {item['depth']})")
    
    # 分析影响
    print("\n分析变更 'db.sales.customers' 的影响...")
    impact_analysis = lineage_manager.analyze_impact(["db.sales.customers"], 3)
    print(f"直接影响对象数: {impact_analysis['summary']['total_directly_affected']}")
    print(f"间接影响对象数: {impact_analysis['summary']['total_indirectly_affected']}")
    print(f"受影响系统数: {impact_analysis['summary']['total_affected_systems']}")
    
    # 生成血缘报告
    print("\n生成血缘报告...")
    report = lineage_manager.generate_lineage_report("dw.sales.customer_orders", "customer_orders_lineage_report.json")
    print("血缘报告已生成")
    
    # 可视化血缘图
    print("\n生成血缘图...")
    viz_result = lineage_manager.visualize_lineage_graph(
        focus_objects=["dw.sales.customer_orders"],
        max_depth=2,
        output_file="data_lineage_example.png"
    )
    print(viz_result)
    
    # 关闭连接
    lineage_manager.close()
    
    print("\n分析完成!")

if __name__ == "__main__":
    main()