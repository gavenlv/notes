#!/usr/bin/env python3
"""
数据剖析工具
分析数据分布、特征和质量指标
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
import datetime
import re
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataType(Enum):
    """数据类型枚举"""
    NUMERIC = "numeric"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"
    UNKNOWN = "unknown"

class QualityDimension(Enum):
    """质量维度枚举"""
    COMPLETENESS = "completeness"      # 完整性
    UNIQUENESS = "uniqueness"          # 唯一性
    VALIDITY = "validity"              # 有效性
    CONSISTENCY = "consistency"        # 一致性
    ACCURACY = "accuracy"              # 准确性

@dataclass
class ColumnProfile:
    """列剖析结果数据类"""
    column_name: str
    data_type: DataType
    total_count: int
    null_count: int
    unique_count: int
    duplicate_count: int
    min_value: Any
    max_value: Any
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_dev: Optional[float] = None
    value_distribution: Dict[str, int] = None
    outlier_count: int = 0
    outlier_values: List[Any] = None
    pattern: str = ""
    format_validity: float = 0.0
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['data_type'] = self.data_type.value
        # 处理NaN值
        if data['min_value'] is not None and pd.isna(data['min_value']):
            data['min_value'] = None
        if data['max_value'] is not None and pd.isna(data['max_value']):
            data['max_value'] = None
        return data

@dataclass
class TableProfile:
    """表剖析结果数据类"""
    table_name: str
    total_rows: int
    total_columns: int
    column_profiles: List[ColumnProfile]
    completeness_score: float
    uniqueness_score: float
    validity_score: float
    overall_quality_score: float
    profiling_date: datetime.datetime
    data_source: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['profiling_date'] = self.profiling_date.isoformat()
        data['column_profiles'] = [col.to_dict() for col in self.column_profiles]
        return data

class DataProfiler:
    """数据剖析器"""
    
    def __init__(self):
        self.date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S'
        ]
    
    def profile_table(self, df: pd.DataFrame, table_name: str, data_source: str = "") -> TableProfile:
        """剖析数据表"""
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # 剖析每一列
        column_profiles = []
        for col in df.columns:
            column_profile = self.profile_column(df[col], col)
            column_profiles.append(column_profile)
        
        # 计算表级别的质量分数
        completeness_score = self._calculate_completeness_score(column_profiles, total_rows)
        uniqueness_score = self._calculate_uniqueness_score(column_profiles, total_rows)
        validity_score = self._calculate_validity_score(column_profiles)
        overall_quality_score = (completeness_score + uniqueness_score + validity_score) / 3
        
        return TableProfile(
            table_name=table_name,
            total_rows=total_rows,
            total_columns=total_columns,
            column_profiles=column_profiles,
            completeness_score=completeness_score,
            uniqueness_score=uniqueness_score,
            validity_score=validity_score,
            overall_quality_score=overall_quality_score,
            profiling_date=datetime.datetime.now(),
            data_source=data_source
        )
    
    def profile_column(self, series: pd.Series, column_name: str) -> ColumnProfile:
        """剖析单列数据"""
        # 基本统计
        total_count = len(series)
        null_count = series.isnull().sum()
        non_null_series = series.dropna()
        unique_count = non_null_series.nunique()
        duplicate_count = total_count - null_count - unique_count
        
        # 确定数据类型
        data_type = self._detect_data_type(non_null_series)
        
        # 计算基本统计量
        min_value, max_value, mean_value, median_value, std_dev = self._calculate_basic_stats(non_null_series, data_type)
        
        # 分析值分布
        value_distribution = self._analyze_value_distribution(non_null_series)
        
        # 检测异常值
        outlier_count, outlier_values = self._detect_outliers(non_null_series, data_type)
        
        # 分析数据模式
        pattern = self._analyze_pattern(non_null_series)
        
        # 计算格式有效性
        format_validity = self._calculate_format_validity(non_null_series, data_type)
        
        # 计算质量分数
        quality_score = self._calculate_column_quality_score(
            null_count, total_count, duplicate_count, total_count, 
            unique_count, total_count, format_validity
        )
        
        return ColumnProfile(
            column_name=column_name,
            data_type=data_type,
            total_count=total_count,
            null_count=null_count,
            unique_count=unique_count,
            duplicate_count=duplicate_count,
            min_value=min_value,
            max_value=max_value,
            mean_value=mean_value,
            median_value=median_value,
            std_dev=std_dev,
            value_distribution=value_distribution,
            outlier_count=outlier_count,
            outlier_values=outlier_values,
            pattern=pattern,
            format_validity=format_validity,
            quality_score=quality_score
        )
    
    def _detect_data_type(self, series: pd.Series) -> DataType:
        """检测数据类型"""
        if len(series) == 0:
            return DataType.UNKNOWN
        
        # 尝试转换为各种类型
        sample_size = min(100, len(series))
        sample = series.sample(sample_size)
        
        # 检查是否为布尔型
        try:
            if sample.astype(bool).all():
                return DataType.BOOLEAN
        except:
            pass
        
        # 检查是否为整数
        try:
            if pd.to_numeric(sample, errors='raise').apply(float.is_integer).all():
                return DataType.INTEGER
        except:
            pass
        
        # 检查是否为浮点数
        try:
            pd.to_numeric(sample, errors='raise')
            return DataType.FLOAT
        except:
            pass
        
        # 检查是否为日期时间
        for fmt in self.date_formats:
            try:
                pd.to_datetime(sample, format=fmt, errors='raise')
                return DataType.DATETIME
            except:
                continue
        
        # 检查是否为分类数据
        unique_ratio = sample.nunique() / len(sample)
        if unique_ratio < 0.1:  # 唯一值比例小于10%认为是分类数据
            return DataType.CATEGORICAL
        
        # 默认为字符串
        return DataType.STRING
    
    def _calculate_basic_stats(self, series: pd.Series, data_type: DataType) -> Tuple[Any, Any, Optional[float], Optional[float], Optional[float]]:
        """计算基本统计量"""
        if len(series) == 0:
            return None, None, None, None, None
        
        min_value = series.min()
        max_value = series.max()
        
        # 对于数值型数据，计算均值、中位数和标准差
        if data_type in [DataType.INTEGER, DataType.FLOAT]:
            try:
                numeric_series = pd.to_numeric(series, errors='coerce')
                mean_value = float(numeric_series.mean())
                median_value = float(numeric_series.median())
                std_dev = float(numeric_series.std())
            except:
                mean_value = median_value = std_dev = None
        else:
            mean_value = median_value = std_dev = None
        
        return min_value, max_value, mean_value, median_value, std_dev
    
    def _analyze_value_distribution(self, series: pd.Series, top_n: int = 10) -> Dict[str, int]:
        """分析值分布"""
        if len(series) == 0:
            return {}
        
        # 计算值频率
        value_counts = series.value_counts().head(top_n)
        
        # 转换为字典
        distribution = {}
        for value, count in value_counts.items():
            # 将值转换为字符串作为键
            key = str(value)
            # 处理空值
            if pd.isna(value):
                key = "NULL"
            distribution[key] = int(count)
        
        return distribution
    
    def _detect_outliers(self, series: pd.Series, data_type: DataType) -> Tuple[int, List[Any]]:
        """检测异常值"""
        if len(series) == 0 or data_type not in [DataType.INTEGER, DataType.FLOAT]:
            return 0, []
        
        try:
            numeric_series = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_series) < 4:  # 数据点太少，不检测异常值
                return 0, []
            
            # 使用IQR方法检测异常值
            Q1 = numeric_series.quantile(0.25)
            Q3 = numeric_series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(numeric_series < lower_bound) | (numeric_series > upper_bound)]
            outlier_values = outliers.tolist()
            
            return len(outliers), outlier_values
        except:
            return 0, []
    
    def _analyze_pattern(self, series: pd.Series) -> str:
        """分析数据模式"""
        if len(series) == 0:
            return ""
        
        # 取样分析模式
        sample_size = min(100, len(series))
        sample = series.sample(sample_size)
        
        # 分析字符串长度模式
        if sample.apply(lambda x: isinstance(x, str)).all():
            lengths = sample.apply(len)
            
            # 如果长度都相同，返回固定长度模式
            if len(lengths.unique()) == 1:
                return f"固定长度({lengths.iloc[0]})"
            
            # 分析长度分布
            avg_length = lengths.mean()
            return f"可变长度(平均:{avg_length:.1f})"
        
        # 对于非字符串数据，返回基本统计
        return f"值类型:{type(sample.iloc[0]).__name__}"
    
    def _calculate_format_validity(self, series: pd.Series, data_type: DataType) -> float:
        """计算格式有效性"""
        if len(series) == 0:
            return 1.0
        
        # 对于数值型数据，检查是否可以转换为数值
        if data_type in [DataType.INTEGER, DataType.FLOAT]:
            try:
                numeric_series = pd.to_numeric(series, errors='coerce')
                valid_count = numeric_series.notna().sum()
                return valid_count / len(series)
            except:
                return 0.0
        
        # 对于日期时间型数据，检查是否符合日期格式
        if data_type == DataType.DATETIME:
            valid_count = 0
            for fmt in self.date_formats:
                try:
                    datetime_series = pd.to_datetime(series, format=fmt, errors='coerce')
                    valid_count = max(valid_count, datetime_series.notna().sum())
                except:
                    continue
            return valid_count / len(series)
        
        # 对于字符串数据，检查是否为非空字符串
        if data_type == DataType.STRING:
            non_empty_count = series.apply(lambda x: isinstance(x, str) and x.strip()).sum()
            return non_empty_count / len(series)
        
        # 其他类型，默认返回有效
        return 1.0
    
    def _calculate_column_quality_score(self, null_count: int, total_count: int, 
                                       duplicate_count: int, total_non_null: int, 
                                       unique_count: int, total_count_for_unique: int, 
                                       format_validity: float) -> float:
        """计算列质量分数"""
        # 完整性 (40%)
        completeness = 1.0 - (null_count / total_count)
        
        # 唯一性 (30%)
        uniqueness = unique_count / total_count_for_unique if total_count_for_unique > 0 else 1.0
        
        # 格式有效性 (30%)
        validity = format_validity
        
        # 加权平均
        quality_score = completeness * 0.4 + uniqueness * 0.3 + validity * 0.3
        
        return round(quality_score, 2)
    
    def _calculate_completeness_score(self, column_profiles: List[ColumnProfile], total_rows: int) -> float:
        """计算完整性分数"""
        if total_rows == 0:
            return 1.0
        
        total_cells = total_rows * len(column_profiles)
        total_nulls = sum(col.null_count for col in column_profiles)
        
        return 1.0 - (total_nulls / total_cells)
    
    def _calculate_uniqueness_score(self, column_profiles: List[ColumnProfile], total_rows: int) -> float:
        """计算唯一性分数"""
        if total_rows == 0:
            return 1.0
        
        # 计算所有列的平均唯一性
        avg_uniqueness = sum(col.unique_count / total_rows for col in column_profiles) / len(column_profiles)
        
        return avg_uniqueness
    
    def _calculate_validity_score(self, column_profiles: List[ColumnProfile]) -> float:
        """计算有效性分数"""
        # 计算所有列的平均格式有效性
        avg_validity = sum(col.format_validity for col in column_profiles) / len(column_profiles)
        
        return avg_validity

class DataProfileRepository:
    """数据剖析结果存储库"""
    
    def __init__(self, db_path: str = "data_profile.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS table_profiles (
                    id TEXT PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    total_rows INTEGER NOT NULL,
                    total_columns INTEGER NOT NULL,
                    column_profiles TEXT NOT NULL,
                    completeness_score REAL NOT NULL,
                    uniqueness_score REAL NOT NULL,
                    validity_score REAL NOT NULL,
                    overall_quality_score REAL NOT NULL,
                    profiling_date TEXT NOT NULL,
                    data_source TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS column_profiles (
                    id TEXT PRIMARY KEY,
                    table_profile_id TEXT NOT NULL,
                    column_name TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    total_count INTEGER NOT NULL,
                    null_count INTEGER NOT NULL,
                    unique_count INTEGER NOT NULL,
                    duplicate_count INTEGER NOT NULL,
                    min_value TEXT,
                    max_value TEXT,
                    mean_value REAL,
                    median_value REAL,
                    std_dev REAL,
                    value_distribution TEXT NOT NULL,
                    outlier_count INTEGER NOT NULL,
                    outlier_values TEXT,
                    pattern TEXT,
                    format_validity REAL NOT NULL,
                    quality_score REAL NOT NULL,
                    FOREIGN KEY (table_profile_id) REFERENCES table_profiles (id)
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_table_profiles_table_name ON table_profiles (table_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_table_profiles_profiling_date ON table_profiles (profiling_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_column_profiles_table_profile_id ON column_profiles (table_profile_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_column_profiles_column_name ON column_profiles (column_name)")
            
            conn.commit()
    
    def save_profile(self, profile: TableProfile) -> str:
        """保存剖析结果"""
        profile_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            # 保存表级别剖析结果
            conn.execute("""
                INSERT INTO table_profiles
                (id, table_name, total_rows, total_columns, column_profiles,
                 completeness_score, uniqueness_score, validity_score,
                 overall_quality_score, profiling_date, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, profile.table_name, profile.total_rows, profile.total_columns,
                json.dumps([col.to_dict() for col in profile.column_profiles]),
                profile.completeness_score, profile.uniqueness_score, profile.validity_score,
                profile.overall_quality_score, profile.profiling_date.isoformat(),
                profile.data_source
            ))
            
            # 保存列级别剖析结果
            for col in profile.column_profiles:
                col_id = str(uuid.uuid4())
                
                conn.execute("""
                    INSERT INTO column_profiles
                    (id, table_profile_id, column_name, data_type, total_count,
                     null_count, unique_count, duplicate_count, min_value, max_value,
                     mean_value, median_value, std_dev, value_distribution,
                     outlier_count, outlier_values, pattern, format_validity, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    col_id, profile_id, col.column_name, col.data_type.value,
                    col.total_count, col.null_count, col.unique_count, col.duplicate_count,
                    str(col.min_value) if col.min_value is not None else None,
                    str(col.max_value) if col.max_value is not None else None,
                    col.mean_value, col.median_value, col.std_dev,
                    json.dumps(col.value_distribution), col.outlier_count,
                    json.dumps(col.outlier_values) if col.outlier_values else None,
                    col.pattern, col.format_validity, col.quality_score
                ))
            
            conn.commit()
        
        return profile_id
    
    def get_profile_by_table(self, table_name: str) -> Optional[TableProfile]:
        """根据表名获取最新的剖析结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM table_profiles 
                WHERE table_name = ? 
                ORDER BY profiling_date DESC
                LIMIT 1
            """, (table_name,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return self._row_to_profile(row)
    
    def get_all_profiles(self, limit: int = 100) -> List[TableProfile]:
        """获取所有剖析结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM table_profiles 
                ORDER BY profiling_date DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [self._row_to_profile(row) for row in rows]
    
    def get_column_profiles_by_table(self, table_name: str) -> List[ColumnProfile]:
        """根据表名获取列剖析结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT cp.* FROM column_profiles cp
                JOIN table_profiles tp ON cp.table_profile_id = tp.id
                WHERE tp.table_name = ?
                ORDER BY tp.profiling_date DESC, cp.column_name
            """, (table_name,))
            
            rows = cursor.fetchall()
            return [self._row_to_column_profile(row) for row in rows]
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """获取质量摘要"""
        with sqlite3.connect(self.db_path) as conn:
            # 总表数
            cursor = conn.execute("SELECT COUNT(*) FROM table_profiles")
            total_tables = cursor.fetchone()[0]
            
            # 平均质量分数
            cursor = conn.execute("SELECT AVG(overall_quality_score) FROM table_profiles")
            avg_quality_score = cursor.fetchone()[0] or 0
            
            # 质量分布
            cursor = conn.execute("""
                SELECT 
                    CASE 
                        WHEN overall_quality_score >= 0.9 THEN '优秀'
                        WHEN overall_quality_score >= 0.8 THEN '良好'
                        WHEN overall_quality_score >= 0.6 THEN '可接受'
                        ELSE '需改进'
                    END as quality_level,
                    COUNT(*) as count
                FROM table_profiles
                GROUP BY quality_level
            """)
            quality_distribution = dict(cursor.fetchall())
            
            # 质量最低的5张表
            cursor = conn.execute("""
                SELECT table_name, overall_quality_score, profiling_date
                FROM table_profiles
                ORDER BY overall_quality_score ASC
                LIMIT 5
            """)
            lowest_quality = [dict(row) for row in cursor.fetchall()]
            
            # 质量最高的5张表
            cursor = conn.execute("""
                SELECT table_name, overall_quality_score, profiling_date
                FROM table_profiles
                ORDER BY overall_quality_score DESC
                LIMIT 5
            """)
            highest_quality = [dict(row) for row in cursor.fetchall()]
            
            return {
                'total_tables': total_tables,
                'average_quality_score': round(avg_quality_score, 2),
                'quality_distribution': quality_distribution,
                'lowest_quality_tables': lowest_quality,
                'highest_quality_tables': highest_quality,
                'last_updated': datetime.datetime.now().isoformat()
            }
    
    def _row_to_profile(self, row) -> TableProfile:
        """将数据库行转换为TableProfile对象"""
        column_profiles_data = json.loads(row['column_profiles'])
        column_profiles = [ColumnProfile(**col) for col in column_profiles_data]
        
        return TableProfile(
            table_name=row['table_name'],
            total_rows=row['total_rows'],
            total_columns=row['total_columns'],
            column_profiles=column_profiles,
            completeness_score=row['completeness_score'],
            uniqueness_score=row['uniqueness_score'],
            validity_score=row['validity_score'],
            overall_quality_score=row['overall_quality_score'],
            profiling_date=datetime.datetime.fromisoformat(row['profiling_date']),
            data_source=row['data_source'] or ""
        )
    
    def _row_to_column_profile(self, row) -> ColumnProfile:
        """将数据库行转换为ColumnProfile对象"""
        value_distribution = json.loads(row['value_distribution'])
        outlier_values = json.loads(row['outlier_values']) if row['outlier_values'] else []
        
        return ColumnProfile(
            column_name=row['column_name'],
            data_type=DataType(row['data_type']),
            total_count=row['total_count'],
            null_count=row['null_count'],
            unique_count=row['unique_count'],
            duplicate_count=row['duplicate_count'],
            min_value=row['min_value'],
            max_value=row['max_value'],
            mean_value=row['mean_value'],
            median_value=row['median_value'],
            std_dev=row['std_dev'],
            value_distribution=value_distribution,
            outlier_count=row['outlier_count'],
            outlier_values=outlier_values,
            pattern=row['pattern'],
            format_validity=row['format_validity'],
            quality_score=row['quality_score']
        )

class DataProfileManager:
    """数据剖析管理器"""
    
    def __init__(self, profiler: DataProfiler = None, repository: DataProfileRepository = None):
        self.profiler = profiler or DataProfiler()
        self.repository = repository or DataProfileRepository()
    
    def profile_csv_file(self, file_path: str, table_name: str = None, encoding: str = 'utf-8') -> str:
        """剖析CSV文件"""
        if not table_name:
            # 从文件名生成表名
            base_name = os.path.basename(file_path)
            table_name = os.path.splitext(base_name)[0]
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 剖析数据
            profile = self.profiler.profile_table(df, table_name, file_path)
            
            # 保存剖析结果
            profile_id = self.repository.save_profile(profile)
            
            logger.info(f"成功剖析CSV文件: {file_path}, 保存ID: {profile_id}")
            return profile_id
        
        except Exception as e:
            logger.error(f"剖析CSV文件失败: {file_path}, 错误: {str(e)}")
            raise
    
    def profile_excel_file(self, file_path: str, sheet_name: str = None, table_name: str = None) -> str:
        """剖析Excel文件"""
        if not table_name:
            # 从文件名生成表名
            base_name = os.path.basename(file_path)
            table_name = os.path.splitext(base_name)[0]
            if sheet_name:
                table_name = f"{table_name}_{sheet_name}"
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 剖析数据
            profile = self.profiler.profile_table(df, table_name, file_path)
            
            # 保存剖析结果
            profile_id = self.repository.save_profile(profile)
            
            logger.info(f"成功剖析Excel文件: {file_path}, 工作表: {sheet_name}, 保存ID: {profile_id}")
            return profile_id
        
        except Exception as e:
            logger.error(f"剖析Excel文件失败: {file_path}, 工作表: {sheet_name}, 错误: {str(e)}")
            raise
    
    def profile_dataframe(self, df: pd.DataFrame, table_name: str, data_source: str = "") -> str:
        """剖析DataFrame"""
        try:
            # 剖析数据
            profile = self.profiler.profile_table(df, table_name, data_source)
            
            # 保存剖析结果
            profile_id = self.repository.save_profile(profile)
            
            logger.info(f"成功剖析DataFrame: {table_name}, 保存ID: {profile_id}")
            return profile_id
        
        except Exception as e:
            logger.error(f"剖析DataFrame失败: {table_name}, 错误: {str(e)}")
            raise
    
    def get_profile(self, table_name: str) -> Optional[Dict[str, Any]]:
        """获取剖析结果"""
        profile = self.repository.get_profile_by_table(table_name)
        return profile.to_dict() if profile else None
    
    def get_column_profiles(self, table_name: str) -> List[Dict[str, Any]]:
        """获取列剖析结果"""
        column_profiles = self.repository.get_column_profiles_by_table(table_name)
        return [col.to_dict() for col in column_profiles]
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """获取质量摘要"""
        return self.repository.get_quality_summary()
    
    def compare_profiles(self, table_name: str) -> Dict[str, Any]:
        """比较同一表的不同时间点的剖析结果"""
        # 这个功能需要扩展数据库查询，获取多个时间点的结果
        # 这里简化实现，只获取最新的结果
        profile = self.repository.get_profile_by_table(table_name)
        if not profile:
            return {"error": f"未找到表 {table_name} 的剖析结果"}
        
        return {
            "current": profile.to_dict(),
            "historical_comparison": "需要扩展实现以获取历史数据"
        }
    
    def generate_quality_report(self, table_name: str, format: str = "json") -> str:
        """生成质量报告"""
        profile = self.repository.get_profile_by_table(table_name)
        if not profile:
            return f"未找到表 {table_name} 的剖析结果"
        
        if format.lower() == "json":
            return json.dumps(profile.to_dict(), indent=2, ensure_ascii=False)
        elif format.lower() == "text":
            return self._generate_text_report(profile)
        else:
            return f"不支持的报告格式: {format}"
    
    def _generate_text_report(self, profile: TableProfile) -> str:
        """生成文本格式报告"""
        report = []
        report.append(f"数据质量报告")
        report.append(f"表名: {profile.table_name}")
        report.append(f"数据源: {profile.data_source}")
        report.append(f"剖析时间: {profile.profiling_date.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append(f"表级别摘要:")
        report.append(f"- 总行数: {profile.total_rows}")
        report.append(f"- 总列数: {profile.total_columns}")
        report.append(f"- 完整性评分: {profile.completeness_score:.2f}")
        report.append(f"- 唯一性评分: {profile.uniqueness_score:.2f}")
        report.append(f"- 有效性评分: {profile.validity_score:.2f}")
        report.append(f"- 总体质量评分: {profile.overall_quality_score:.2f}")
        report.append("")
        
        report.append(f"列级别详情:")
        for col in profile.column_profiles:
            report.append(f"- 列名: {col.column_name}")
            report.append(f"  数据类型: {col.data_type.value}")
            report.append(f"  总行数: {col.total_count}")
            report.append(f"  空值数: {col.null_count} ({col.null_count/col.total_count:.1%})")
            report.append(f"  唯一值数: {col.unique_count}")
            report.append(f"  重复值数: {col.duplicate_count}")
            report.append(f"  格式有效性: {col.format_validity:.2f}")
            report.append(f"  质量评分: {col.quality_score:.2f}")
            
            if col.data_type in [DataType.INTEGER, DataType.FLOAT]:
                report.append(f"  最小值: {col.min_value}")
                report.append(f"  最大值: {col.max_value}")
                report.append(f"  平均值: {col.mean_value:.2f}" if col.mean_value else "")
                report.append(f"  中位数: {col.median_value:.2f}" if col.median_value else "")
            
            if col.outlier_count > 0:
                report.append(f"  异常值数: {col.outlier_count}")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """主函数，演示数据剖析工具使用"""
    print("=" * 50)
    print("数据剖析工具演示")
    print("=" * 50)
    
    # 创建数据剖析管理器
    manager = DataProfileManager()
    
    # 1. 创建示例数据
    print("\n1. 创建示例数据...")
    # 创建一个包含各种数据类型的DataFrame
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
        'age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com', 
                  'eve@example.com', 'frank@example.com', 'grace@example.com', 'henry@example.com',
                  'ivy@example.com', 'invalid-email'],  # 包含一个无效邮箱
        'salary': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 500000],  # 包含一个异常值
        'join_date': ['2020-01-15', '2019-05-20', '2018-11-10', '2021-02-28', 
                      '2017-07-05', '2022-03-12', '2016-09-18', '2023-01-25', 
                      '2015-04-30', '2022-12-08'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing', 'HR', 'IT', 'Finance', 'Marketing', None],  # 包含一个空值
        'is_active': [True, True, False, True, True, False, True, True, False, True]
    }
    
    df = pd.DataFrame(data)
    print(f"创建了示例DataFrame，包含 {len(df)} 行和 {len(df.columns)} 列")
    
    # 2. 剖析DataFrame
    print("\n2. 剖析DataFrame...")
    profile_id = manager.profile_dataframe(df, "employees", "示例数据")
    print(f"剖析完成，保存ID: {profile_id}")
    
    # 3. 获取剖析结果
    print("\n3. 获取剖析结果...")
    profile = manager.get_profile("employees")
    if profile:
        print(f"表名: {profile['table_name']}")
        print(f"总行数: {profile['total_rows']}")
        print(f"总列数: {profile['total_columns']}")
        print(f"完整性评分: {profile['completeness_score']:.2f}")
        print(f"唯一性评分: {profile['uniqueness_score']:.2f}")
        print(f"有效性评分: {profile['validity_score']:.2f}")
        print(f"总体质量评分: {profile['overall_quality_score']:.2f}")
    
    # 4. 获取列级别剖析结果
    print("\n4. 获取列级别剖析结果...")
    column_profiles = manager.get_column_profiles("employees")
    for col in column_profiles:
        print(f"\n列名: {col['column_name']}")
        print(f"数据类型: {col['data_type']}")
        print(f"空值数: {col['null_count']} ({col['null_count']/col['total_count']:.1%})")
        print(f"唯一值数: {col['unique_count']}")
        print(f"质量评分: {col['quality_score']:.2f}")
        
        # 对于数值型列，显示更多统计信息
        if col['data_type'] in ['integer', 'float']:
            print(f"最小值: {col['min_value']}")
            print(f"最大值: {col['max_value']}")
            print(f"平均值: {col['mean_value']:.2f}" if col['mean_value'] else "")
        
        # 显示值分布
        if col['value_distribution']:
            print("值分布 (前5个):")
            for value, count in list(col['value_distribution'].items())[:5]:
                print(f"  {value}: {count}")
        
        # 显示异常值
        if col['outlier_count'] > 0:
            print(f"异常值数: {col['outlier_count']}")
    
    # 5. 生成质量报告
    print("\n5. 生成质量报告...")
    text_report = manager.generate_quality_report("employees", "text")
    print(text_report)
    
    # 6. 获取质量摘要
    print("\n6. 获取质量摘要...")
    summary = manager.get_quality_summary()
    print(f"总表数: {summary['total_tables']}")
    print(f"平均质量评分: {summary['average_quality_score']}")
    print(f"质量分布: {summary['quality_distribution']}")
    
    if summary['highest_quality_tables']:
        print("\n质量最高的表:")
        for table in summary['highest_quality_tables']:
            print(f"- {table['table_name']}: {table['overall_quality_score']:.2f}")
    
    # 7. 创建并剖析第二个表进行比较
    print("\n7. 创建并剖析第二个表进行比较...")
    # 创建一个质量较低的数据集
    poor_data = {
        'product_id': [1, 2, 3, 4, 5, None, 7, 8, 9, 10],  # 包含空值
        'product_name': ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard', 'Mouse', 'Speaker', 'Camera', 'Printer', None],  # 包含空值
        'price': [999.99, 699.99, 399.99, 299.99, 79.99, 49.99, 149.99, 599.99, 199.99, 'expensive'],  # 包含非数值
        'stock': [100, 150, 200, 50, 300, 250, 80, 120, 90, 180],
        'release_date': ['2022-01-15', '2022-03-20', '2022-05-10', '2022-07-05', 
                         '2022-09-12', '2022-11-18', '2023-01-25', '2023-03-30', 
                         '2023-05-15', 'invalid-date']  # 包含无效日期
    }
    
    poor_df = pd.DataFrame(poor_data)
    poor_profile_id = manager.profile_dataframe(poor_df, "products", "低质量示例数据")
    print(f"低质量表剖析完成，保存ID: {poor_profile_id}")
    
    # 8. 比较两个表的质量
    print("\n8. 比较两个表的质量...")
    products_profile = manager.get_profile("products")
    if products_profile:
        print(f"产品表质量评分: {products_profile['overall_quality_score']:.2f}")
        print(f"员工表质量评分: {profile['overall_quality_score']:.2f}")
        
        # 找出质量评分最低的列
        lowest_quality_col = min(products_profile['column_profiles'], key=lambda x: x['quality_score'])
        print(f"产品表中质量最低的列: {lowest_quality_col['column_name']} (评分: {lowest_quality_col['quality_score']:.2f})")
    
    # 9. 更新质量摘要
    print("\n9. 更新后的质量摘要...")
    updated_summary = manager.get_quality_summary()
    print(f"总表数: {updated_summary['total_tables']}")
    print(f"平均质量评分: {updated_summary['average_quality_score']}")
    print(f"质量分布: {updated_summary['quality_distribution']}")
    
    if updated_summary['lowest_quality_tables']:
        print("\n质量最低的表:")
        for table in updated_summary['lowest_quality_tables']:
            print(f"- {table['table_name']}: {table['overall_quality_score']:.2f}")

if __name__ == "__main__":
    main()