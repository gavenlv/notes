#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL血缘分析器
功能：从SQL查询中提取数据血缘关系，支持多种SQL方言
作者：数据治理团队
日期：2023-11-23
"""

import re
import json
import datetime
import uuid
from typing import Dict, List, Tuple, Any, Optional, Set
import warnings
warnings.filterwarnings('ignore')

class SQLLineageAnalyzer:
    """SQL血缘分析器"""
    
    def __init__(self):
        # SQL关键字模式
        self.sql_keywords = {
            "select": ["SELECT"],
            "from": ["FROM"],
            "where": ["WHERE"],
            "join": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "JOIN"],
            "insert": ["INSERT", "INSERT INTO"],
            "create": ["CREATE", "CREATE TABLE", "CREATE VIEW"],
            "update": ["UPDATE"],
            "delete": ["DELETE", "DELETE FROM"],
            "with": ["WITH"],
            "union": ["UNION", "UNION ALL"],
            "subquery": ["EXISTS", "IN", "NOT IN"]
        }
        
        # 表名提取模式
        self.table_patterns = [
            # 标准表名：schema.table 或 table
            r'(?:FROM|JOIN|INTO|UPDATE)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            # 子查询中的表名
            r'(?:FROM|JOIN|INTO|UPDATE)\s+\(([^)]+)\)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            # CTE中的表名
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\('
        ]
        
        # 列名提取模式
        self.column_patterns = [
            # 标准列名：table.column 或 column
            r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
            # 函数中的列名
            r'[A-Z_]+\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)',
            # 别名
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        # 支持的SQL方言
        self.supported_dialects = {
            "ansi": "标准SQL",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "sqlserver": "SQL Server",
            "oracle": "Oracle",
            "hive": "Apache Hive",
            "sparksql": "Spark SQL",
            "bigquery": "Google BigQuery"
        }
    
    def extract_lineage(self, sql_query, dialect="ansi", include_columns=False):
        """从SQL查询中提取血缘关系"""
        try:
            # 预处理SQL
            normalized_sql = self._normalize_sql(sql_query, dialect)
            
            # 识别SQL类型
            sql_type = self._identify_sql_type(normalized_sql)
            
            # 根据SQL类型提取血缘
            if sql_type in ["SELECT", "WITH"]:
                lineage = self._extract_select_lineage(normalized_sql, include_columns)
            elif sql_type in ["INSERT", "CREATE_TABLE_AS", "CREATE_VIEW_AS"]:
                lineage = self._extract_insert_lineage(normalized_sql, include_columns)
            elif sql_type in ["UPDATE"]:
                lineage = self._extract_update_lineage(normalized_sql, include_columns)
            elif sql_type in ["MERGE", "UPSERT"]:
                lineage = self._extract_merge_lineage(normalized_sql, include_columns)
            else:
                lineage = {
                    "sql_type": sql_type,
                    "source_tables": [],
                    "target_tables": [],
                    "source_columns": [],
                    "target_columns": [],
                    "transformations": []
                }
            
            # 添加元数据
            lineage.update({
                "sql_query": sql_query,
                "normalized_sql": normalized_sql,
                "sql_type": sql_type,
                "dialect": dialect,
                "include_columns": include_columns,
                "extracted_at": datetime.datetime.now().isoformat(),
                "lineage_id": str(uuid.uuid4())
            })
            
            # 验证血缘关系
            lineage = self._validate_lineage(lineage)
            
            return lineage
            
        except Exception as e:
            return {
                "error": str(e),
                "sql_query": sql_query,
                "extracted_at": datetime.datetime.now().isoformat()
            }
    
    def _normalize_sql(self, sql_query, dialect):
        """标准化SQL查询"""
        # 移除注释
        sql = re.sub(r'--.*?$', '', sql_query, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # 标准化大小写
        sql = sql.upper()
        
        # 标准化空格和换行
        sql = re.sub(r'\s+', ' ', sql)
        sql = sql.strip()
        
        # 处理特定方言的特殊语法
        if dialect == "postgresql":
            # 处理PostgreSQL特定的语法
            sql = re.sub(r'ILLUSION|SKIP LOCKED', '', sql)
        elif dialect == "mysql":
            # 处理MySQL特定的语法
            sql = re.sub(r'STRAIGHT_JOIN|SQL_SMALL_RESULT', '', sql)
        elif dialect == "sqlserver":
            # 处理SQL Server特定的语法
            sql = re.sub(r'WITH\s*\(\s*NOLOCK\s*\)', '', sql)
        elif dialect == "oracle":
            # 处理Oracle特定的语法
            sql = re.sub(r'CONNECT BY|START WITH', '', sql)
        
        return sql
    
    def _identify_sql_type(self, normalized_sql):
        """识别SQL类型"""
        if normalized_sql.startswith("SELECT"):
            return "SELECT"
        elif normalized_sql.startswith("WITH"):
            return "WITH"
        elif normalized_sql.startswith("INSERT"):
            return "INSERT"
        elif normalized_sql.startswith("CREATE TABLE"):
            if "AS" in normalized_sql and "SELECT" in normalized_sql:
                return "CREATE_TABLE_AS"
            else:
                return "CREATE_TABLE"
        elif normalized_sql.startswith("CREATE VIEW"):
            if "AS" in normalized_sql and "SELECT" in normalized_sql:
                return "CREATE_VIEW_AS"
            else:
                return "CREATE_VIEW"
        elif normalized_sql.startswith("UPDATE"):
            return "UPDATE"
        elif normalized_sql.startswith("DELETE"):
            return "DELETE"
        elif "MERGE" in normalized_sql or "UPSERT" in normalized_sql:
            return "MERGE"
        else:
            return "UNKNOWN"
    
    def _extract_select_lineage(self, normalized_sql, include_columns):
        """提取SELECT语句的血缘"""
        lineage = {
            "source_tables": [],
            "target_tables": [],
            "source_columns": [],
            "target_columns": [],
            "transformations": []
        }
        
        # 提取FROM和JOIN子句中的表名
        from_clause = self._extract_from_clause(normalized_sql)
        source_tables = self._extract_tables_from_clause(from_clause)
        lineage["source_tables"] = source_tables
        
        # 提取列映射关系
        if include_columns:
            select_clause = self._extract_select_clause(normalized_sql)
            column_mappings = self._extract_column_mappings(select_clause, from_clause)
            lineage["source_columns"] = [mapping["source"] for mapping in column_mappings]
            lineage["target_columns"] = [mapping["target"] for mapping in column_mappings]
            
            # 添加列转换信息
            for mapping in column_mappings:
                if mapping["transformation"]:
                    lineage["transformations"].append({
                        "type": "column_transformation",
                        "source_column": mapping["source"],
                        "target_column": mapping["target"],
                        "transformation": mapping["transformation"]
                    })
        
        # 处理CTE（公用表表达式）
        cte_clauses = self._extract_cte_clauses(normalized_sql)
        for cte_name, cte_sql in cte_clauses.items():
            cte_lineage = self._extract_select_lineage(cte_sql, include_columns)
            
            # 将CTE视为临时目标表
            lineage["target_tables"].append(cte_name)
            
            # 添加CTE转换信息
            lineage["transformations"].append({
                "type": "cte",
                "cte_name": cte_name,
                "source_tables": cte_lineage["source_tables"],
                "transformation": cte_sql
            })
        
        # 处理子查询
        subqueries = self._extract_subqueries(normalized_sql)
        for subquery in subqueries:
            subquery_lineage = self._extract_select_lineage(subquery, include_columns)
            
            # 合并源表
            for table in subquery_lineage["source_tables"]:
                if table not in lineage["source_tables"]:
                    lineage["source_tables"].append(table)
        
        return lineage
    
    def _extract_insert_lineage(self, normalized_sql, include_columns):
        """提取INSERT语句的血缘"""
        lineage = {
            "source_tables": [],
            "target_tables": [],
            "source_columns": [],
            "target_columns": [],
            "transformations": []
        }
        
        # 提取目标表
        target_match = re.search(r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', normalized_sql)
        if target_match:
            target_table = target_match.group(1)
            lineage["target_tables"].append(target_table)
        
        # 检查是否是INSERT INTO ... SELECT
        if "SELECT" in normalized_sql:
            # 提取SELECT部分
            select_match = re.search(r'SELECT\s+(.*?)(?:\s+FROM\s+|$)', normalized_sql)
            if select_match:
                select_clause = select_match.group(1)
                
                # 提取列映射
                if include_columns:
                    # 获取目标列（如果指定了列列表）
                    columns_match = re.search(r'INSERT\s+INTO\s+[^(]+\((.*?)\)', normalized_sql)
                    if columns_match:
                        target_columns = [col.strip() for col in columns_match.group(1).split(',')]
                    else:
                        # 如果没有指定列，从SELECT子句推断
                        target_columns = self._parse_select_columns(select_clause)
                    
                    lineage["target_columns"] = target_columns
                
                # 提取FROM部分
                from_match = re.search(r'FROM\s+([^;]*)', normalized_sql)
                if from_match:
                    from_clause = from_match.group(1)
                    source_tables = self._extract_tables_from_clause(from_clause)
                    lineage["source_tables"] = source_tables
        
        # 处理INSERT INTO ... VALUES
        elif "VALUES" in normalized_sql:
            # VALUES子句不包含数据血缘
            lineage["transformations"].append({
                "type": "insert_values",
                "description": "INSERT语句使用VALUES子句，无数据血缘"
            })
        
        return lineage
    
    def _extract_update_lineage(self, normalized_sql, include_columns):
        """提取UPDATE语句的血缘"""
        lineage = {
            "source_tables": [],
            "target_tables": [],
            "source_columns": [],
            "target_columns": [],
            "transformations": []
        }
        
        # 提取目标表
        target_match = re.search(r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', normalized_sql)
        if target_match:
            target_table = target_match.group(1)
            lineage["target_tables"].append(target_table)
            lineage["source_tables"].append(target_table)  # UPDATE的目标表也是源表
        
        # 提取FROM子句中的其他表
        from_match = re.search(r'FROM\s+([^;]*)', normalized_sql)
        if from_match:
            from_clause = from_match.group(1)
            source_tables = self._extract_tables_from_clause(from_clause)
            
            for table in source_tables:
                if table not in lineage["source_tables"]:
                    lineage["source_tables"].append(table)
        
        # 添加UPDATE转换信息
        lineage["transformations"].append({
            "type": "update_operation",
            "description": "UPDATE操作"
        })
        
        return lineage
    
    def _extract_merge_lineage(self, normalized_sql, include_columns):
        """提取MERGE语句的血缘"""
        lineage = {
            "source_tables": [],
            "target_tables": [],
            "source_columns": [],
            "target_columns": [],
            "transformations": []
        }
        
        # 提取目标表
        target_match = re.search(r'MERGE\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', normalized_sql)
        if target_match:
            target_table = target_match.group(1)
            lineage["target_tables"].append(target_table)
        
        # 提取源表
        source_match = re.search(r'USING\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', normalized_sql)
        if source_match:
            source_table = source_match.group(1)
            lineage["source_tables"].append(source_table)
        
        # 提取子查询中的表
        subqueries = self._extract_subqueries(normalized_sql)
        for subquery in subqueries:
            subquery_lineage = self._extract_select_lineage(subquery, include_columns)
            
            # 合并源表
            for table in subquery_lineage["source_tables"]:
                if table not in lineage["source_tables"]:
                    lineage["source_tables"].append(table)
        
        # 添加MERGE转换信息
        lineage["transformations"].append({
            "type": "merge_operation",
            "description": "MERGE操作"
        })
        
        return lineage
    
    def _extract_from_clause(self, normalized_sql):
        """提取FROM子句"""
        # 简化实现：提取第一个FROM到下一个关键字之间的内容
        from_match = re.search(r'FROM\s+(.*?)(?:\s+WHERE\s+|\s+GROUP\s+BY\s+|\s+HAVING\s+|\s+ORDER\s+BY\s+|\s+LIMIT\s+|$)', normalized_sql)
        if from_match:
            return from_match.group(1)
        return ""
    
    def _extract_select_clause(self, normalized_sql):
        """提取SELECT子句"""
        # 简化实现：提取SELECT到FROM之间的内容
        select_match = re.search(r'SELECT\s+(.*?)\s+FROM\s+', normalized_sql)
        if select_match:
            return select_match.group(1)
        return ""
    
    def _extract_tables_from_clause(self, from_clause):
        """从FROM子句中提取表名"""
        tables = []
        
        # 提取标准表名
        table_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)', from_clause)
        tables.extend(table_matches)
        
        # 提取子查询中的表
        subquery_pattern = r'\(\s*SELECT.*?\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
        subquery_matches = re.findall(subquery_pattern, from_clause, re.IGNORECASE | re.DOTALL)
        tables.extend(subquery_matches)
        
        # 去重并过滤掉可能是别名的内容
        unique_tables = []
        for table in tables:
            # 简单的别名过滤：如果后面紧跟AS且不在点号后面，可能是别名
            if table not in unique_tables:
                unique_tables.append(table)
        
        return unique_tables
    
    def _extract_column_mappings(self, select_clause, from_clause):
        """提取列映射关系"""
        mappings = []
        
        # 解析SELECT子句中的列
        select_columns = self._parse_select_columns(select_clause)
        
        # 对于每个列，尝试确定其来源
        for col in select_columns:
            mapping = {
                "target": col,
                "source": col,  # 默认认为源列和目标列相同
                "transformation": None
            }
            
            # 检查是否有转换
            if self._has_column_transformation(col):
                # 尝试提取原始列名
                original_col = self._extract_original_column(col)
                if original_col:
                    mapping["source"] = original_col
                    mapping["transformation"] = self._extract_transformation(col)
            
            mappings.append(mapping)
        
        return mappings
    
    def _parse_select_columns(self, select_clause):
        """解析SELECT子句中的列"""
        columns = []
        
        # 简单处理：按逗号分割，但要考虑括号和引号
        parts = self._split_by_comma(select_clause)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 提取列名或表达式
            if "AS" in part:
                # 有别名的情况
                col_match = re.search(r'AS\s+([a-zA-Z_][a-zA-Z0-9_]*)', part, re.IGNORECASE)
                if col_match:
                    columns.append(col_match.group(1))
                else:
                    columns.append(part)
            else:
                # 没有别名的情况
                if "." in part:
                    # 可能是 table.column 格式
                    col_parts = part.split('.')
                    columns.append(col_parts[-1])
                else:
                    columns.append(part)
        
        return columns
    
    def _split_by_comma(self, text):
        """按逗号分割文本，但考虑括号和引号"""
        parts = []
        current_part = ""
        paren_level = 0
        in_quote = False
        quote_char = None
        
        for char in text:
            if char == "'" or char == '"':
                if in_quote and char == quote_char:
                    in_quote = False
                    quote_char = None
                elif not in_quote:
                    in_quote = True
                    quote_char = char
                current_part += char
            elif char == '(' and not in_quote:
                paren_level += 1
                current_part += char
            elif char == ')' and not in_quote:
                paren_level -= 1
                current_part += char
            elif char == ',' and paren_level == 0 and not in_quote:
                parts.append(current_part)
                current_part = ""
            else:
                current_part += char
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    def _has_column_transformation(self, column):
        """检查列是否有转换"""
        # 简单的转换检测：是否包含函数或操作符
        patterns = [
            r'\(\s*.*\s*\)',  # 函数调用
            r'\s*\+\s*',     # 加法
            r'\s*\-\s*',     # 减法
            r'\s*\*\s*',     # 乘法
            r'\s*\/\s*',     # 除法
            r'CASE\s+WHEN',  # CASE语句
            r'CAST\s*\(',    # 类型转换
            r'CONVERT\s*\(', # 类型转换
        ]
        
        for pattern in patterns:
            if re.search(pattern, column, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_original_column(self, transformed_column):
        """从转换后的列中提取原始列名"""
        # 简单实现：提取表.列格式的列名
        column_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)', transformed_column)
        if column_match:
            return column_match.group(1)
        
        # 尝试提取简单的列名
        simple_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)', transformed_column)
        if simple_match:
            return simple_match.group(1)
        
        return None
    
    def _extract_transformation(self, transformed_column):
        """提取转换操作"""
        # 简单实现：返回整个转换表达式
        return transformed_column
    
    def _extract_cte_clauses(self, normalized_sql):
        """提取CTE（公用表表达式）"""
        cte_clauses = {}
        
        # 查找WITH子句
        with_match = re.match(r'WITH\s+(.*?)\s+SELECT', normalized_sql, re.DOTALL)
        if with_match:
            with_clause = with_match.group(1)
            
            # 按逗号分割多个CTE
            cte_parts = self._split_by_comma(with_clause)
            
            for part in cte_parts:
                part = part.strip()
                if not part:
                    continue
                
                # 提取CTE名和SQL
                cte_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+AS\s*\((.*?)\)', part, re.DOTALL | re.IGNORECASE)
                if cte_match:
                    cte_name = cte_match.group(1)
                    cte_sql = cte_match.group(2)
                    cte_clauses[cte_name] = cte_sql
        
        return cte_clauses
    
    def _extract_subqueries(self, normalized_sql):
        """提取子查询"""
        subqueries = []
        
        # 简单实现：查找括号内的SELECT语句
        paren_level = 0
        in_quote = False
        quote_char = None
        current_subquery = ""
        in_select = False
        
        for i, char in enumerate(normalized_sql):
            if char == "'" or char == '"':
                if in_quote and char == quote_char:
                    in_quote = False
                    quote_char = None
                elif not in_quote:
                    in_quote = True
                    quote_char = char
                if in_select:
                    current_subquery += char
            elif char == '(' and not in_quote:
                paren_level += 1
                if in_select:
                    current_subquery += char
            elif char == ')' and not in_quote:
                paren_level -= 1
                if in_select:
                    current_subquery += char
                    if paren_level == 0:
                        # 子查询结束
                        subqueries.append(current_subquery)
                        current_subquery = ""
                        in_select = False
            elif paren_level > 0 and in_select:
                current_subquery += char
            elif normalized_sql[i:i+6].upper() == "SELECT" and not in_quote and paren_level > 0:
                # 在括号内遇到SELECT，可能是子查询
                in_select = True
                current_subquery = "SELECT"
        
        return subqueries
    
    def _validate_lineage(self, lineage):
        """验证血缘关系"""
        if "error" in lineage:
            return lineage
        
        # 检查是否有有效的表名
        if not lineage.get("source_tables") and not lineage.get("target_tables"):
            lineage["warnings"] = ["未能识别出任何表名"]
        
        # 检查循环依赖
        source_set = set(lineage.get("source_tables", []))
        target_set = set(lineage.get("target_tables", []))
        
        common_tables = source_set.intersection(target_set)
        if common_tables:
            lineage["warnings"] = lineage.get("warnings", [])
            lineage["warnings"].append(f"检测到可能的循环依赖: {', '.join(common_tables)}")
        
        return lineage

class BatchSQLLineageProcessor:
    """批量SQL血缘处理器"""
    
    def __init__(self, analyzer=None):
        self.analyzer = analyzer or SQLLineageAnalyzer()
        self.processed_queries = []
    
    def process_sql_file(self, file_path, dialect="ansi", include_columns=False):
        """处理SQL文件中的所有查询"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分割多个SQL查询
            queries = self._split_sql_queries(content)
            
            results = {
                "file_path": file_path,
                "total_queries": len(queries),
                "dialect": dialect,
                "include_columns": include_columns,
                "processed_at": datetime.datetime.now().isoformat(),
                "queries": []
            }
            
            for i, query in enumerate(queries):
                query = query.strip()
                if not query:
                    continue
                
                lineage = self.analyzer.extract_lineage(query, dialect, include_columns)
                
                query_result = {
                    "query_number": i + 1,
                    "query": query,
                    "lineage": lineage
                }
                
                results["queries"].append(query_result)
                self.processed_queries.append(query_result)
            
            return results
            
        except Exception as e:
            return {
                "error": str(e),
                "file_path": file_path,
                "processed_at": datetime.datetime.now().isoformat()
            }
    
    def _split_sql_queries(self, content):
        """分割多个SQL查询"""
        # 简单实现：按分号分割
        queries = []
        current_query = ""
        
        for char in content:
            current_query += char
            
            if char == ';':
                queries.append(current_query)
                current_query = ""
        
        # 添加最后一个查询（如果没有分号）
        if current_query.strip():
            queries.append(current_query)
        
        return queries
    
    def generate_lineage_summary(self):
        """生成血缘摘要"""
        summary = {
            "total_queries": len(self.processed_queries),
            "successful_extractions": 0,
            "failed_extractions": 0,
            "unique_source_tables": set(),
            "unique_target_tables": set(),
            "query_types": {},
            "dialects": {},
            "generated_at": datetime.datetime.now().isoformat()
        }
        
        for query_result in self.processed_queries:
            lineage = query_result["lineage"]
            
            if "error" in lineage:
                summary["failed_extractions"] += 1
                continue
            
            summary["successful_extractions"] += 1
            
            # 收集表名
            source_tables = lineage.get("source_tables", [])
            target_tables = lineage.get("target_tables", [])
            
            summary["unique_source_tables"].update(source_tables)
            summary["unique_target_tables"].update(target_tables)
            
            # 收集SQL类型
            sql_type = lineage.get("sql_type", "UNKNOWN")
            summary["query_types"][sql_type] = summary["query_types"].get(sql_type, 0) + 1
            
            # 收集方言
            dialect = lineage.get("dialect", "unknown")
            summary["dialects"][dialect] = summary["dialects"].get(dialect, 0) + 1
        
        # 转换set为list以便JSON序列化
        summary["unique_source_tables"] = list(summary["unique_source_tables"])
        summary["unique_target_tables"] = list(summary["unique_target_tables"])
        
        return summary

def main():
    """主函数"""
    print("=" * 50)
    print("SQL血缘分析器")
    print("=" * 50)
    
    # 创建SQL血缘分析器
    analyzer = SQLLineageAnalyzer()
    
    # 示例SQL查询
    sample_queries = [
        {
            "name": "简单SELECT查询",
            "sql": """
            SELECT c.customer_id, c.name, o.order_id, o.order_date, o.amount
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_date >= '2023-01-01'
            """,
            "dialect": "postgresql"
        },
        {
            "name": "复杂SELECT查询与CTE",
            "sql": """
            WITH customer_orders AS (
                SELECT customer_id, COUNT(*) as order_count, SUM(amount) as total_amount
                FROM orders
                WHERE order_date >= '2023-01-01'
                GROUP BY customer_id
            ),
            active_customers AS (
                SELECT c.customer_id, c.name
                FROM customers c
                JOIN customer_orders co ON c.customer_id = co.customer_id
                WHERE co.order_count > 5
            )
            SELECT ac.customer_id, ac.name, co.order_count, co.total_amount
            FROM active_customers ac
            JOIN customer_orders co ON ac.customer_id = co.customer_id
            ORDER BY co.total_amount DESC
            """,
            "dialect": "postgresql",
            "include_columns": True
        },
        {
            "name": "INSERT INTO SELECT查询",
            "sql": """
            INSERT INTO sales_report (date, product_id, total_sales, total_orders)
            SELECT 
                DATE(order_date) as date,
                product_id,
                SUM(amount) as total_sales,
                COUNT(*) as total_orders
            FROM order_items
            WHERE order_date >= '2023-01-01'
            GROUP BY DATE(order_date), product_id
            """,
            "dialect": "mysql"
        },
        {
            "name": "CREATE TABLE AS查询",
            "sql": """
            CREATE TABLE customer_summary AS
            SELECT 
                c.customer_id,
                c.name,
                c.email,
                COUNT(o.order_id) as order_count,
                COALESCE(SUM(o.amount), 0) as total_amount,
                MAX(o.order_date) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.name, c.email
            """,
            "dialect": "postgresql"
        },
        {
            "name": "UPDATE查询",
            "sql": """
            UPDATE customers c
            SET last_order_date = (
                SELECT MAX(order_date)
                FROM orders o
                WHERE o.customer_id = c.customer_id
            )
            WHERE EXISTS (
                SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
            )
            """,
            "dialect": "sqlserver"
        }
    ]
    
    # 处理每个查询
    for query_info in sample_queries:
        print(f"\n处理查询: {query_info['name']}")
        print("-" * 40)
        
        sql = query_info["sql"]
        dialect = query_info.get("dialect", "ansi")
        include_columns = query_info.get("include_columns", False)
        
        # 提取血缘
        lineage = analyzer.extract_lineage(sql, dialect, include_columns)
        
        # 显示结果
        if "error" in lineage:
            print(f"错误: {lineage['error']}")
            continue
        
        print(f"SQL类型: {lineage['sql_type']}")
        print(f"方言: {lineage['dialect']}")
        
        if lineage.get("source_tables"):
            print(f"源表: {', '.join(lineage['source_tables'])}")
        
        if lineage.get("target_tables"):
            print(f"目标表: {', '.join(lineage['target_tables'])}")
        
        if include_columns and lineage.get("source_columns"):
            print(f"源列: {', '.join(lineage['source_columns'])}")
            
        if include_columns and lineage.get("target_columns"):
            print(f"目标列: {', '.join(lineage['target_columns'])}")
        
        if lineage.get("transformations"):
            print("转换:")
            for transform in lineage["transformations"]:
                print(f"  - {transform['type']}: {transform.get('description', 'N/A')}")
        
        if lineage.get("warnings"):
            print("警告:")
            for warning in lineage["warnings"]:
                print(f"  - {warning}")
    
    # 批量处理示例
    print("\n" + "=" * 50)
    print("批量处理示例")
    print("=" * 50)
    
    # 创建批量处理器
    batch_processor = BatchSQLLineageProcessor()
    
    # 创建临时SQL文件
    temp_sql_content = """
    -- 清理旧数据
    DELETE FROM temp_data WHERE created_at < '2023-01-01';
    
    -- 插入新数据
    INSERT INTO customer_stats (customer_id, order_count, total_amount)
    SELECT customer_id, COUNT(*), SUM(amount)
    FROM orders
    WHERE created_at >= '2023-01-01'
    GROUP BY customer_id;
    
    -- 创建汇总表
    CREATE TABLE daily_sales AS
    SELECT 
        DATE(created_at) as sale_date,
        SUM(amount) as daily_total,
        COUNT(*) as order_count
    FROM orders
    WHERE created_at >= '2023-01-01'
    GROUP BY DATE(created_at);
    """
    
    with open("temp_queries.sql", "w", encoding="utf-8") as f:
        f.write(temp_sql_content)
    
    # 处理SQL文件
    print("处理SQL文件...")
    batch_result = batch_processor.process_sql_file("temp_queries.sql", "postgresql")
    
    if "error" in batch_result:
        print(f"处理错误: {batch_result['error']}")
    else:
        print(f"成功处理 {batch_result['total_queries']} 个查询")
        
        # 生成血缘摘要
        summary = batch_processor.generate_lineage_summary()
        print(f"\n血缘摘要:")
        print(f"- 成功提取: {summary['successful_extractions']}")
        print(f"- 提取失败: {summary['failed_extractions']}")
        print(f"- 唯一源表数: {len(summary['unique_source_tables'])}")
        print(f"- 唯一目标表数: {len(summary['unique_target_tables'])}")
        
        print(f"\n查询类型分布:")
        for query_type, count in summary["query_types"].items():
            print(f"- {query_type}: {count}")
    
    print("\n分析完成!")

if __name__ == "__main__":
    import os
    main()