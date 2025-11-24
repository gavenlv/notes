#!/usr/bin/env python3
"""
业务术语表工具
提供业务术语的定义、管理和关联功能
"""

import os
import json
import sqlite3
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

class TermStatus(Enum):
    """术语状态枚举"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"

class TermType(Enum):
    """术语类型枚举"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    ACRONYM = "acronym"
    DOMAIN = "domain"
    PROCESS = "process"

@dataclass
class BusinessTerm:
    """业务术语数据类"""
    id: str
    name: str
    display_name: str
    definition: str
    type: TermType
    status: TermStatus
    domain: str
    synonyms: List[str]
    abbreviations: List[str]
    examples: List[str]
    related_terms: List[str]
    attributes: Dict[str, Any]
    steward: str
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['approved_at'] = self.approved_at.isoformat() if self.approved_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessTerm':
        """从字典创建实例"""
        data['type'] = TermType(data['type'])
        data['status'] = TermStatus(data['status'])
        data['created_at'] = datetime.datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.datetime.fromisoformat(data['updated_at'])
        if data['approved_at']:
            data['approved_at'] = datetime.datetime.fromisoformat(data['approved_at'])
        return cls(**data)

class BusinessGlossaryRepository:
    """业务术语表存储库"""
    
    def __init__(self, db_path: str = "business_glossary.db"):
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS business_terms (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    synonyms TEXT NOT NULL,
                    abbreviations TEXT NOT NULL,
                    examples TEXT NOT NULL,
                    related_terms TEXT NOT NULL,
                    attributes TEXT NOT NULL,
                    steward TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    approved_by TEXT,
                    approved_at TEXT,
                    version INTEGER NOT NULL
                )
            """)
            
            # 创建全文搜索表
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS business_terms_fts USING fts5(
                    name, display_name, definition, synonyms, abbreviations,
                    content='business_terms',
                    content_rowid='id'
                )
            """)
            
            # 创建触发器，在主表更新时同步到FTS表
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS business_terms_fts_insert AFTER INSERT ON business_terms BEGIN
                    INSERT INTO business_terms_fts(rowid, name, display_name, definition, synonyms, abbreviations)
                    VALUES (new.id, new.name, new.display_name, new.definition, new.synonyms, new.abbreviations);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS business_terms_fts_delete AFTER DELETE ON business_terms BEGIN
                    DELETE FROM business_terms_fts WHERE rowid = old.id;
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS business_terms_fts_update AFTER UPDATE ON business_terms BEGIN
                    DELETE FROM business_terms_fts WHERE rowid = old.id;
                    INSERT INTO business_terms_fts(rowid, name, display_name, definition, synonyms, abbreviations)
                    VALUES (new.id, new.name, new.display_name, new.definition, new.synonyms, new.abbreviations);
                END
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_terms_name ON business_terms (name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_terms_display_name ON business_terms (display_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_terms_type ON business_terms (type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_terms_status ON business_terms (status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_terms_domain ON business_terms (domain)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_business_terms_steward ON business_terms (steward)")
            
            conn.commit()
    
    def save_term(self, term: BusinessTerm) -> str:
        """保存业务术语"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO business_terms
                (id, name, display_name, definition, type, status, domain, synonyms,
                 abbreviations, examples, related_terms, attributes, steward,
                 created_by, created_at, updated_at, approved_by, approved_at, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                term.id, term.name, term.display_name, term.definition,
                term.type.value, term.status.value, term.domain,
                json.dumps(term.synonyms), json.dumps(term.abbreviations),
                json.dumps(term.examples), json.dumps(term.related_terms),
                json.dumps(term.attributes), term.steward, term.created_by,
                term.created_at.isoformat(), term.updated_at.isoformat(),
                term.approved_by, term.approved_at.isoformat() if term.approved_at else None,
                term.version
            ))
            conn.commit()
        
        return term.id
    
    def get_term_by_id(self, term_id: str) -> Optional[BusinessTerm]:
        """根据ID获取业务术语"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM business_terms WHERE id = ?", (term_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['synonyms'] = json.loads(data['synonyms'])
                data['abbreviations'] = json.loads(data['abbreviations'])
                data['examples'] = json.loads(data['examples'])
                data['related_terms'] = json.loads(data['related_terms'])
                data['attributes'] = json.loads(data['attributes'])
                return BusinessTerm.from_dict(data)
            return None
    
    def get_term_by_name(self, name: str) -> Optional[BusinessTerm]:
        """根据名称获取业务术语"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM business_terms WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['synonyms'] = json.loads(data['synonyms'])
                data['abbreviations'] = json.loads(data['abbreviations'])
                data['examples'] = json.loads(data['examples'])
                data['related_terms'] = json.loads(data['related_terms'])
                data['attributes'] = json.loads(data['attributes'])
                return BusinessTerm.from_dict(data)
            return None
    
    def search_terms(self, query: str = "", filters: Dict[str, Any] = None,
                     limit: int = 20, offset: int = 0) -> List[BusinessTerm]:
        """搜索业务术语"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # 构建基本查询
            if query:
                # 使用FTS进行全文搜索
                sql = """
                    SELECT bt.* FROM business_terms bt
                    JOIN business_terms_fts fts ON bt.id = fts.rowid
                    WHERE business_terms_fts MATCH ?
                """
                params = [query]
            else:
                sql = "SELECT * FROM business_terms WHERE 1=1"
                params = []
            
            # 添加过滤器
            if filters:
                if 'type' in filters and filters['type']:
                    sql += " AND type = ?"
                    params.append(filters['type'])
                
                if 'status' in filters and filters['status']:
                    sql += " AND status = ?"
                    params.append(filters['status'])
                
                if 'domain' in filters and filters['domain']:
                    sql += " AND domain = ?"
                    params.append(filters['domain'])
                
                if 'steward' in filters and filters['steward']:
                    sql += " AND steward = ?"
                    params.append(filters['steward'])
                
                if 'created_by' in filters and filters['created_by']:
                    sql += " AND created_by = ?"
                    params.append(filters['created_by'])
                
                if 'tags' in filters and filters['tags']:
                    for tag in filters['tags']:
                        sql += " AND (synonyms LIKE ? OR abbreviations LIKE ?)"
                        params.extend([f"%{tag}%", f"%{tag}%"])
            
            # 排序
            sql += " ORDER BY display_name ASC"
            
            # 分页
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            terms = []
            for row in rows:
                data = dict(row)
                data['synonyms'] = json.loads(data['synonyms'])
                data['abbreviations'] = json.loads(data['abbreviations'])
                data['examples'] = json.loads(data['examples'])
                data['related_terms'] = json.loads(data['related_terms'])
                data['attributes'] = json.loads(data['attributes'])
                terms.append(BusinessTerm.from_dict(data))
            
            return terms
    
    def get_count(self, query: str = "", filters: Dict[str, Any] = None) -> int:
        """获取搜索结果总数"""
        with sqlite3.connect(self.db_path) as conn:
            # 构建基本查询
            if query:
                sql = """
                    SELECT COUNT(*) FROM business_terms bt
                    JOIN business_terms_fts fts ON bt.id = fts.rowid
                    WHERE business_terms_fts MATCH ?
                """
                params = [query]
            else:
                sql = "SELECT COUNT(*) FROM business_terms WHERE 1=1"
                params = []
            
            # 添加过滤器（与search_terms相同的逻辑）
            if filters:
                if 'type' in filters and filters['type']:
                    sql += " AND type = ?"
                    params.append(filters['type'])
                
                if 'status' in filters and filters['status']:
                    sql += " AND status = ?"
                    params.append(filters['status'])
                
                if 'domain' in filters and filters['domain']:
                    sql += " AND domain = ?"
                    params.append(filters['domain'])
                
                if 'steward' in filters and filters['steward']:
                    sql += " AND steward = ?"
                    params.append(filters['steward'])
                
                if 'created_by' in filters and filters['created_by']:
                    sql += " AND created_by = ?"
                    params.append(filters['created_by'])
                
                if 'tags' in filters and filters['tags']:
                    for tag in filters['tags']:
                        sql += " AND (synonyms LIKE ? OR abbreviations LIKE ?)"
                        params.extend([f"%{tag}%", f"%{tag}%"])
            
            cursor = conn.execute(sql, params)
            return cursor.fetchone()[0]
    
    def get_related_terms(self, term_id: str) -> List[BusinessTerm]:
        """获取相关术语"""
        term = self.get_term_by_id(term_id)
        if not term or not term.related_terms:
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            placeholders = ','.join(['?'] * len(term.related_terms))
            cursor = conn.execute(f"""
                SELECT * FROM business_terms 
                WHERE name IN ({placeholders})
            """, term.related_terms)
            
            rows = cursor.fetchall()
            terms = []
            for row in rows:
                data = dict(row)
                data['synonyms'] = json.loads(data['synonyms'])
                data['abbreviations'] = json.loads(data['abbreviations'])
                data['examples'] = json.loads(data['examples'])
                data['related_terms'] = json.loads(data['related_terms'])
                data['attributes'] = json.loads(data['attributes'])
                terms.append(BusinessTerm.from_dict(data))
            
            return terms
    
    def get_terms_by_domain(self, domain: str) -> List[BusinessTerm]:
        """根据域获取术语"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM business_terms 
                WHERE domain = ?
                ORDER BY display_name ASC
            """, (domain,))
            
            rows = cursor.fetchall()
            terms = []
            for row in rows:
                data = dict(row)
                data['synonyms'] = json.loads(data['synonyms'])
                data['abbreviations'] = json.loads(data['abbreviations'])
                data['examples'] = json.loads(data['examples'])
                data['related_terms'] = json.loads(data['related_terms'])
                data['attributes'] = json.loads(data['attributes'])
                terms.append(BusinessTerm.from_dict(data))
            
            return terms
    
    def get_domains(self) -> List[str]:
        """获取所有域"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT domain FROM business_terms 
                ORDER BY domain ASC
            """)
            
            return [row[0] for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取业务术语表统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总术语数
            cursor = conn.execute("SELECT COUNT(*) FROM business_terms")
            total_terms = cursor.fetchone()[0]
            
            # 按类型统计
            cursor = conn.execute("""
                SELECT type, COUNT(*) FROM business_terms 
                GROUP BY type
            """)
            type_distribution = dict(cursor.fetchall())
            
            # 按状态统计
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM business_terms 
                GROUP BY status
            """)
            status_distribution = dict(cursor.fetchall())
            
            # 按域统计
            cursor = conn.execute("""
                SELECT domain, COUNT(*) FROM business_terms 
                GROUP BY domain
                ORDER BY COUNT(*) DESC
            """)
            domain_distribution = dict(cursor.fetchall())
            
            # 按管理员统计
            cursor = conn.execute("""
                SELECT steward, COUNT(*) FROM business_terms 
                GROUP BY steward
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """)
            top_stewards = dict(cursor.fetchall())
            
            # 最近7天新增术语
            seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
            cursor = conn.execute("""
                SELECT COUNT(*) FROM business_terms 
                WHERE created_at >= ?
            """, (seven_days_ago,))
            recent_terms = cursor.fetchone()[0]
            
            # 待审核术语数
            cursor = conn.execute("""
                SELECT COUNT(*) FROM business_terms 
                WHERE status = 'pending_review'
            """)
            pending_review = cursor.fetchone()[0]
        
        return {
            'total_terms': total_terms,
            'type_distribution': type_distribution,
            'status_distribution': status_distribution,
            'domain_distribution': domain_distribution,
            'top_stewards': top_stewards,
            'recent_terms': recent_terms,
            'pending_review': pending_review,
            'last_updated': datetime.datetime.now().isoformat()
        }

class BusinessGlossary:
    """业务术语表主类"""
    
    def __init__(self, repo: BusinessGlossaryRepository = None):
        self.repo = repo or BusinessGlossaryRepository()
    
    def create_term(self, term_data: Dict[str, Any], created_by: str) -> str:
        """创建业务术语"""
        # 检查名称是否已存在
        existing = self.repo.get_term_by_name(term_data.get('name', ''))
        if existing:
            raise ValueError(f"术语 '{term_data.get('name')}' 已存在")
        
        # 创建ID
        term_id = str(uuid.uuid4())
        
        # 设置时间戳
        now = datetime.datetime.now()
        
        # 创建术语对象
        term = BusinessTerm(
            id=term_id,
            name=term_data.get('name', '').lower().replace(' ', '_'),
            display_name=term_data.get('display_name', term_data.get('name', '')),
            definition=term_data.get('definition', ''),
            type=TermType(term_data.get('type', 'business')),
            status=TermStatus(term_data.get('status', 'draft')),
            domain=term_data.get('domain', ''),
            synonyms=term_data.get('synonyms', []),
            abbreviations=term_data.get('abbreviations', []),
            examples=term_data.get('examples', []),
            related_terms=term_data.get('related_terms', []),
            attributes=term_data.get('attributes', {}),
            steward=term_data.get('steward', created_by),
            created_by=created_by,
            created_at=now,
            updated_at=now,
            version=1
        )
        
        # 保存术语
        self.repo.save_term(term)
        logger.info(f"创建了业务术语: {term.display_name} (ID: {term.id})")
        
        return term.id
    
    def get_term(self, term_id: str) -> Optional[Dict[str, Any]]:
        """获取业务术语详情"""
        term = self.repo.get_term_by_id(term_id)
        if term:
            return term.to_dict()
        return None
    
    def update_term(self, term_id: str, updates: Dict[str, Any], updated_by: str) -> bool:
        """更新业务术语"""
        term = self.repo.get_term_by_id(term_id)
        if not term:
            return False
        
        # 应用更新
        if 'display_name' in updates:
            term.display_name = updates['display_name']
        
        if 'definition' in updates:
            term.definition = updates['definition']
        
        if 'type' in updates:
            term.type = TermType(updates['type'])
        
        if 'status' in updates:
            term.status = TermStatus(updates['status'])
            
            # 如果状态变为approved，设置审批信息
            if term.status == TermStatus.APPROVED and not term.approved_by:
                term.approved_by = updated_by
                term.approved_at = datetime.datetime.now()
        
        if 'domain' in updates:
            term.domain = updates['domain']
        
        if 'synonyms' in updates:
            term.synonyms = updates['synonyms']
        
        if 'abbreviations' in updates:
            term.abbreviations = updates['abbreviations']
        
        if 'examples' in updates:
            term.examples = updates['examples']
        
        if 'related_terms' in updates:
            term.related_terms = updates['related_terms']
        
        if 'attributes' in updates:
            term.attributes = updates['attributes']
        
        if 'steward' in updates:
            term.steward = updates['steward']
        
        term.updated_at = datetime.datetime.now()
        term.version += 1
        
        self.repo.save_term(term)
        return True
    
    def approve_term(self, term_id: str, approved_by: str) -> bool:
        """审批业务术语"""
        return self.update_term(term_id, {'status': 'approved'}, approved_by)
    
    def reject_term(self, term_id: str, reason: str, rejected_by: str) -> bool:
        """拒绝业务术语"""
        term = self.repo.get_term_by_id(term_id)
        if not term:
            return False
        
        term.status = TermStatus.DRAFT
        term.updated_at = datetime.datetime.now()
        term.version += 1
        
        # 添加拒绝原因到属性
        if 'rejection_reasons' not in term.attributes:
            term.attributes['rejection_reasons'] = []
        
        term.attributes['rejection_reasons'].append({
            'reason': reason,
            'rejected_by': rejected_by,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
        self.repo.save_term(term)
        return True
    
    def search(self, query: str = "", filters: Dict[str, Any] = None,
               page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """搜索业务术语"""
        offset = (page - 1) * page_size
        
        terms = self.repo.search_terms(
            query=query,
            filters=filters,
            limit=page_size,
            offset=offset
        )
        
        total = self.repo.get_count(query, filters)
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return {
            'terms': [term.to_dict() for term in terms],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages
            }
        }
    
    def get_related_terms(self, term_id: str) -> List[Dict[str, Any]]:
        """获取相关术语"""
        related_terms = self.repo.get_related_terms(term_id)
        return [term.to_dict() for term in related_terms]
    
    def get_terms_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """根据域获取术语"""
        terms = self.repo.get_terms_by_domain(domain)
        return [term.to_dict() for term in terms]
    
    def get_domains(self) -> List[str]:
        """获取所有域"""
        return self.repo.get_domains()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        return self.repo.get_statistics()
    
    def export_terms(self, format: str = "json", filters: Dict[str, Any] = None) -> str:
        """导出业务术语"""
        terms = self.repo.search_terms(query="", filters=filters, limit=10000)
        
        if format.lower() == "json":
            return json.dumps([term.to_dict() for term in terms], indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def import_terms(self, data: str, format: str = "json", created_by: str = "system", 
                    overwrite: bool = False) -> Dict[str, Any]:
        """导入业务术语"""
        if format.lower() != "json":
            raise ValueError(f"不支持的导入格式: {format}")
        
        try:
            terms_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {str(e)}")
        
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        for term_data in terms_data:
            try:
                existing = self.repo.get_term_by_name(term_data.get('name', ''))
                
                if existing and not overwrite:
                    continue  # 跳过已存在的术语
                
                if existing and overwrite:
                    # 更新现有术语
                    self.update_term(existing.id, term_data, created_by)
                    updated_count += 1
                else:
                    # 创建新术语
                    self.create_term(term_data, created_by)
                    created_count += 1
                    
            except Exception as e:
                error_count += 1
                errors.append({
                    'term_name': term_data.get('name', 'unknown'),
                    'error': str(e)
                })
        
        return {
            'created_count': created_count,
            'updated_count': updated_count,
            'error_count': error_count,
            'errors': errors
        }

def main():
    """主函数，演示业务术语表使用"""
    print("=" * 50)
    print("业务术语表工具演示")
    print("=" * 50)
    
    import math  # 需要导入math模块用于分页计算
    
    # 创建业务术语表
    glossary = BusinessGlossary()
    
    # 1. 创建示例业务术语
    print("\n1. 创建示例业务术语...")
    
    terms_data = [
        {
            'name': 'customer_lifetime_value',
            'display_name': '客户终身价值',
            'definition': '客户在与企业保持关系的整个期间内为企业创造的总价值，包括历史价值、当前价值和未来价值。',
            'type': 'business',
            'status': 'approved',
            'domain': '客户管理',
            'synonyms': ['CLV', 'LTV', '客户生命周期价值'],
            'abbreviations': ['CLV', 'LTV'],
            'examples': [
                '通过分析客户终身价值，我们可以优先服务高价值客户。',
                '提高客户终身价值的方法包括增加客户忠诚度和提升购买频率。'
            ],
            'attributes': {
                'calculation_method': '历史销售数据预测模型',
                'update_frequency': '每月'
            }
        },
        {
            'name': 'data_governance',
            'display_name': '数据治理',
            'definition': '组织为管理其信息资产而实施的人员、流程和技术框架，确保数据的质量、安全、合规和价值最大化。',
            'type': 'business',
            'status': 'approved',
            'domain': '数据管理',
            'synonyms': ['数据治理'],
            'abbreviations': ['DG'],
            'examples': [
                '公司实施了全面的数据治理策略，以确保数据质量。',
                '数据治理委员会负责制定数据管理政策和标准。'
            ],
            'related_terms': ['data_quality', 'data_stewardship', 'metadata_management'],
            'attributes': {
                'framework': 'DAMA-DMBOK',
                'governance_model': '集中式与分布式结合'
            }
        },
        {
            'name': 'etl',
            'display_name': '提取、转换、加载',
            'definition': '数据仓库中的一个过程，用于从多个源系统中提取数据，转换为适合分析和报告的格式，然后加载到目标数据仓库中。',
            'type': 'technical',
            'status': 'approved',
            'domain': '数据处理',
            'abbreviations': ['ETL'],
            'examples': [
                '我们的ETL流程每天运行，将销售数据从交易系统加载到数据仓库。',
                'ETL过程中的转换包括数据清洗、聚合和格式标准化。'
            ],
            'attributes': {
                'tools': 'Informatica, Talend, SSIS',
                'frequency': '每日'
            }
        },
        {
            'name': 'gdpr',
            'display_name': '通用数据保护条例',
            'definition': '欧盟实施的全面数据保护法规，为欧盟公民的个人数据处理提供了强有力的保护，并规范了组织如何处理个人数据。',
            'type': 'business',
            'status': 'approved',
            'domain': '合规与隐私',
            'abbreviations': ['GDPR'],
            'examples': [
                '为了遵守GDPR，我们需要获得用户明确的同意才能处理他们的个人数据。',
                'GDPR要求数据控制者在72小时内报告数据泄露事件。'
            ],
            'attributes': {
                'effective_date': '2018-05-25',
                'jurisdiction': '欧盟',
                'penalties': '最高全球年营业额的4%或2000万欧元（以较高者为准）'
            }
        }
    ]
    
    term_ids = []
    for term_data in terms_data:
        try:
            term_id = glossary.create_term(term_data, "数据管理员")
            term_ids.append(term_id)
            print(f"- 创建了: {term_data['display_name']} (ID: {term_id})")
        except ValueError as e:
            print(f"- 创建失败: {str(e)}")
    
    # 2. 创建一个待审批的术语
    print("\n2. 创建待审批术语...")
    draft_term = {
        'name': 'customer_churn',
        'display_name': '客户流失',
        'definition': '客户停止与公司业务关系的现象，通常指客户在一段时间内不再购买产品或使用服务。',
        'type': 'business',
        'status': 'draft',  # 草稿状态
        'domain': '客户管理',
        'synonyms': ['客户流失率', '客户流失分析'],
        'examples': [
            '通过预测客户流失，我们可以采取保留措施减少客户流失。',
            '客户流失率是评估业务健康状况的重要指标。'
        ]
    }
    
    try:
        draft_id = glossary.create_term(draft_term, "业务分析师")
        print(f"- 创建了待审批术语: {draft_term['display_name']} (ID: {draft_id})")
        term_ids.append(draft_id)
    except ValueError as e:
        print(f"- 创建失败: {str(e)}")
    
    # 3. 搜索术语
    print("\n3. 搜索术语...")
    search_results = glossary.search("客户")
    print(f"搜索 '客户' 的结果: {len(search_results['terms'])} 个术语")
    for term in search_results['terms']:
        print(f"- {term['display_name']} ({term['type']}, 状态: {term['status']})")
    
    # 4. 获取术语详情
    if term_ids:
        print("\n4. 获取术语详情...")
        term = glossary.get_term(term_ids[0])
        if term:
            print(f"术语名称: {term['display_name']}")
            print(f"定义: {term['definition'][:100]}...")
            print(f"类型: {term['type']}")
            print(f"状态: {term['status']}")
            print(f"域: {term['domain']}")
            print(f"同义词: {', '.join(term['synonyms'])}")
            print(f"缩写: {', '.join(term['abbreviations'])}")
            print(f"管理员: {term['steward']}")
    
    # 5. 审批术语
    if len(term_ids) > 1:  # 审批第二个术语（客户流失）
        print("\n5. 审批术语...")
        success = glossary.approve_term(term_ids[1], "业务主管")
        print(f"审批{'成功' if success else '失败'}")
        
        # 获取更新后的术语
        term = glossary.get_term(term_ids[1])
        if term:
            print(f"状态: {term['status']}")
            print(f"审批人: {term['approved_by']}")
            print(f"审批时间: {term['approved_at'][:10]}")
    
    # 6. 获取相关术语
    if term_ids:
        print("\n6. 获取相关术语...")
        related_terms = glossary.get_related_terms(term_ids[1])  # 数据治理术语的相关术语
        print(f"相关术语数量: {len(related_terms)}")
        for term in related_terms:
            print(f"- {term['display_name']} ({term['type']})")
    
    # 7. 按域获取术语
    print("\n7. 按域获取术语...")
    domains = glossary.get_domains()
    print(f"所有域: {', '.join(domains)}")
    
    if '客户管理' in domains:
        customer_domain_terms = glossary.get_terms_by_domain('客户管理')
        print(f"'客户管理'域的术语: {len(customer_domain_terms)} 个")
        for term in customer_domain_terms:
            print(f"- {term['display_name']}")
    
    # 8. 高级搜索
    print("\n8. 高级搜索...")
    filters = {
        'type': 'business',
        'status': 'approved'
    }
    
    advanced_results = glossary.search(filters=filters)
    print(f"业务类型已批准的术语: {len(advanced_results['terms'])} 个")
    for term in advanced_results['terms']:
        print(f"- {term['display_name']} (域: {term['domain']})")
    
    # 9. 获取仪表板统计
    print("\n9. 获取仪表板统计...")
    stats = glossary.get_dashboard_stats()
    print(f"总术语数: {stats['total_terms']}")
    print(f"类型分布: {stats['type_distribution']}")
    print(f"状态分布: {stats['status_distribution']}")
    print(f"域分布: {stats['domain_distribution']}")
    print(f"待审核术语数: {stats['pending_review']}")
    print(f"最近7天新增: {stats['recent_terms']}")
    
    # 10. 导出术语
    print("\n10. 导出术语...")
    exported_data = glossary.export_terms("json", {"status": "approved"})
    print(f"导出了 {len(exported_data)} 字符的已批准术语")
    
    # 11. 导入术语
    print("\n11. 导入术语...")
    import_result = glossary.import_terms(exported_data, "json", "system", overwrite=False)
    print(f"导入结果: 创建 {import_result['created_count']} 个, 更新 {import_result['updated_count']} 个, 错误 {import_result['error_count']} 个")

if __name__ == "__main__":
    main()