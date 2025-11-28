#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL高可用与负载均衡示例代码
本章代码演示了MySQL高可用架构、负载均衡、故障转移、监控告警等关键功能。
"""

import os
import sys
import time
import json
import logging
import random
import threading
import mysql.connector
import pymysql
import hashlib
import queue
import socket
from typing import Dict, List, Tuple, Any, Optional
from mysql.connector import pooling

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MySQL高可用与负载均衡")

class MySQLNode:
    """MySQL节点信息类"""
    
    def __init__(self, node_id: str, host: str, port: int, role: str = 'unknown'):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.role = role  # master, slave, unknown
        self.is_healthy = True
        self.last_check_time = 0
        self.replication_lag = 0
        self.connections_count = 0
        
    def to_dict(self):
        """转换为字典"""
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'role': self.role,
            'is_healthy': self.is_healthy,
            'last_check_time': self.last_check_time,
            'replication_lag': self.replication_lag,
            'connections_count': self.connections_count
        }


class HealthChecker:
    """MySQL健康检查器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.check_interval = config.get('check_interval', 10)  # 默认10秒检查一次
        self.timeout = config.get('timeout', 5)  # 默认5秒超时
        self.nodes = {}  # node_id: MySQLNode
        self.running = False
        self.check_thread = None
        
    def add_node(self, node: MySQLNode):
        """添加MySQL节点"""
        self.nodes[node.node_id] = node
        logger.info(f"添加节点: {node.node_id} ({node.host}:{node.port})")
    
    def remove_node(self, node_id: str):
        """移除MySQL节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info(f"移除节点: {node_id}")
    
    def check_connection(self, node: MySQLNode) -> Tuple[bool, str]:
        """检查数据库连接"""
        try:
            conn = mysql.connector.connect(
                host=node.host,
                port=node.port,
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                connection_timeout=self.timeout
            )
            conn.close()
            return True, "连接正常"
        except mysql.connector.Error as e:
            return False, f"连接失败: {e}"
        except Exception as e:
            return False, f"检查异常: {e}"
    
    def check_performance(self, node: MySQLNode) -> Tuple[bool, str]:
        """检查数据库性能"""
        try:
            conn = mysql.connector.connect(
                host=node.host,
                port=node.port,
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                connection_timeout=self.timeout
            )
            
            # 执行简单查询测试性能
            cursor = conn.cursor()
            start_time = time.time()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            elapsed_time = time.time() - start_time
            cursor.close()
            conn.close()
            
            if elapsed_time < 0.1:  # 100ms以内认为正常
                return True, f"查询性能正常: {elapsed_time:.4f}秒"
            else:
                return False, f"查询性能异常: {elapsed_time:.4f}秒"
        except Exception as e:
            return False, f"性能检查失败: {e}"
    
    def check_replication_lag(self, node: MySQLNode) -> Tuple[int, str]:
        """检查复制延迟"""
        if node.role != 'slave':
            return 0, "非从节点"
        
        try:
            conn = mysql.connector.connect(
                host=node.host,
                port=node.port,
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                connection_timeout=self.timeout
            )
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SHOW SLAVE STATUS")
            slave_status = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not slave_status:
                return 0, "未配置复制"
            
            lag = slave_status.get('Seconds_Behind_Master', None)
            if lag is None:
                return 0, "复制未运行"
            else:
                return int(lag), f"复制延迟: {lag}秒"
        except Exception as e:
            return -1, f"复制检查失败: {e}"
    
    def check_connections_count(self, node: MySQLNode) -> Tuple[int, str]:
        """检查连接数"""
        try:
            conn = mysql.connector.connect(
                host=node.host,
                port=node.port,
                user=self.config.get('username', 'root'),
                password=self.config.get('password', ''),
                connection_timeout=self.timeout
            )
            
            cursor = conn.cursor()
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and len(result) >= 2:
                count = int(result[1])
                return count, f"当前连接数: {count}"
            else:
                return 0, "无法获取连接数"
        except Exception as e:
            return -1, f"连接数检查失败: {e}"
    
    def check_node(self, node_id: str):
        """检查单个节点"""
        if node_id not in self.nodes:
            logger.error(f"节点不存在: {node_id}")
            return
        
        node = self.nodes[node_id]
        now = time.time()
        node.last_check_time = now
        
        # 检查连接
        conn_ok, conn_msg = self.check_connection(node)
        if not conn_ok:
            node.is_healthy = False
            logger.warning(f"节点 {node_id} 连接检查失败: {conn_msg}")
            return
        
        # 检查性能
        perf_ok, perf_msg = self.check_performance(node)
        if not perf_ok:
            node.is_healthy = False
            logger.warning(f"节点 {node_id} 性能检查失败: {perf_msg}")
            return
        
        # 检查复制延迟（仅从节点）
        if node.role == 'slave':
            lag, lag_msg = self.check_replication_lag(node)
            node.replication_lag = lag
            if lag > self.config.get('max_replication_lag', 30):  # 默认30秒
                node.is_healthy = False
                logger.warning(f"节点 {node_id} 复制延迟过大: {lag_msg}")
                return
        
        # 检查连接数
        conn_count, count_msg = self.check_connections_count(node)
        node.connections_count = conn_count
        
        # 所有检查通过
        node.is_healthy = True
        logger.debug(f"节点 {node_id} 健康检查通过")
    
    def check_all_nodes(self):
        """检查所有节点"""
        logger.debug("开始健康检查所有节点")
        for node_id in list(self.nodes.keys()):
            self.check_node(node_id)
        logger.debug(f"健康检查完成，检查了 {len(self.nodes)} 个节点")
    
    def start(self):
        """启动健康检查"""
        if self.running:
            logger.warning("健康检查已在运行")
            return
        
        self.running = True
        self.check_thread = threading.Thread(target=self._check_loop)
        self.check_thread.daemon = True
        self.check_thread.start()
        logger.info("健康检查已启动")
    
    def stop(self):
        """停止健康检查"""
        if not self.running:
            logger.warning("健康检查未运行")
            return
        
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=10)
        logger.info("健康检查已停止")
    
    def _check_loop(self):
        """健康检查循环"""
        while self.running:
            try:
                self.check_all_nodes()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"健康检查循环异常: {e}")
                time.sleep(self.check_interval)
    
    def get_healthy_nodes(self, role: str = None) -> List[MySQLNode]:
        """获取健康的节点"""
        healthy_nodes = []
        for node in self.nodes.values():
            if node.is_healthy and (role is None or node.role == role):
                healthy_nodes.append(node)
        return healthy_nodes
    
    def get_master_nodes(self) -> List[MySQLNode]:
        """获取主节点"""
        return self.get_healthy_nodes('master')
    
    def get_slave_nodes(self) -> List[MySQLNode]:
        """获取从节点"""
        return self.get_healthy_nodes('slave')


class LoadBalancer:
    """MySQL负载均衡器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.health_checker = HealthChecker(config)
        self.algorithm = config.get('algorithm', 'round_robin')  # round_robin, weighted, least_connections
        self.round_robin_index = 0
        self.connection_pools = {}  # node_id: 连接池
        
    def add_node(self, node: MySQLNode):
        """添加节点到负载均衡器"""
        self.health_checker.add_node(node)
        self._create_connection_pool(node)
        logger.info(f"添加节点到负载均衡器: {node.node_id}")
    
    def remove_node(self, node_id: str):
        """从负载均衡器移除节点"""
        self.health_checker.remove_node(node_id)
        if node_id in self.connection_pools:
            pool = self.connection_pools[node_id]
            pool._remove_connections()
            del self.connection_pools[node_id]
        logger.info(f"从负载均衡器移除节点: {node_id}")
    
    def _create_connection_pool(self, node: MySQLNode):
        """为节点创建连接池"""
        pool_config = {
            'pool_name': f"pool_{node.node_id}",
            'pool_size': self.config.get('pool_size', 5),
            'pool_reset_session': True,
            'host': node.host,
            'port': node.port,
            'user': self.config.get('username', 'root'),
            'password': self.config.get('password', ''),
            'database': self.config.get('database', 'test')
        }
        
        try:
            pool = pooling.MySQLConnectionPool(**pool_config)
            self.connection_pools[node.node_id] = pool
            logger.debug(f"为节点 {node.node_id} 创建连接池成功")
        except Exception as e:
            logger.error(f"为节点 {node.node_id} 创建连接池失败: {e}")
    
    def get_master_connection(self) -> Optional[mysql.connector.connection.MySQLConnection]:
        """获取主库连接"""
        master_nodes = self.health_checker.get_master_nodes()
        if not master_nodes:
            logger.error("没有可用的主节点")
            return None
        
        # 选择最佳主节点（目前只有一个）
        master_node = master_nodes[0]
        
        try:
            if master_node.node_id in self.connection_pools:
                return self.connection_pools[master_node.node_id].get_connection()
            else:
                return mysql.connector.connect(
                    host=master_node.host,
                    port=master_node.port,
                    user=self.config.get('username', 'root'),
                    password=self.config.get('password', ''),
                    database=self.config.get('database', 'test')
                )
        except Exception as e:
            logger.error(f"获取主库连接失败: {e}")
            return None
    
    def get_slave_connection(self) -> Optional[mysql.connector.connection.MySQLConnection]:
        """获取从库连接"""
        slave_nodes = self.health_checker.get_slave_nodes()
        if not slave_nodes:
            logger.warning("没有可用的从节点，回退到主节点")
            return self.get_master_connection()
        
        # 根据算法选择从节点
        if self.algorithm == 'round_robin':
            selected_node = self._select_slave_round_robin(slave_nodes)
        elif self.algorithm == 'weighted':
            selected_node = self._select_slave_weighted(slave_nodes)
        elif self.algorithm == 'least_connections':
            selected_node = self._select_slave_least_connections(slave_nodes)
        else:
            selected_node = slave_nodes[0]
        
        try:
            if selected_node.node_id in self.connection_pools:
                return self.connection_pools[selected_node.node_id].get_connection()
            else:
                return mysql.connector.connect(
                    host=selected_node.host,
                    port=selected_node.port,
                    user=self.config.get('username', 'root'),
                    password=self.config.get('password', ''),
                    database=self.config.get('database', 'test')
                )
        except Exception as e:
            logger.error(f"获取从库连接失败: {e}")
            return None
    
    def _select_slave_round_robin(self, slave_nodes: List[MySQLNode]) -> MySQLNode:
        """轮询选择从节点"""
        if not slave_nodes:
            return None
        
        node = slave_nodes[self.round_robin_index % len(slave_nodes)]
        self.round_robin_index += 1
        return node
    
    def _select_slave_weighted(self, slave_nodes: List[MySQLNode]) -> MySQLNode:
        """加权选择从节点（基于复制延迟）"""
        if not slave_nodes:
            return None
        
        # 计算权重（延迟越小权重越高）
        weights = []
        total_weight = 0
        for node in slave_nodes:
            # 延迟越大，权重越小
            weight = max(1, 100 - node.replication_lag)
            weights.append(weight)
            total_weight += weight
        
        # 加权随机选择
        random_value = random.uniform(0, total_weight)
        current_sum = 0
        
        for i, weight in enumerate(weights):
            current_sum += weight
            if random_value <= current_sum:
                return slave_nodes[i]
        
        return slave_nodes[0]
    
    def _select_slave_least_connections(self, slave_nodes: List[MySQLNode]) -> MySQLNode:
        """选择连接数最少的从节点"""
        if not slave_nodes:
            return None
        
        return min(slave_nodes, key=lambda node: node.connections_count)
    
    def execute_query(self, query: str, params: Tuple = None, use_master: bool = False) -> List[Dict]:
        """执行查询"""
        conn = None
        cursor = None
        result = []
        
        try:
            # 根据查询类型选择连接
            if use_master or self._is_write_query(query):
                conn = self.get_master_connection()
            else:
                conn = self.get_slave_connection()
            
            if not conn:
                raise Exception("无法获取数据库连接")
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if cursor.description:  # 有结果集的查询
                result = cursor.fetchall()
            else:  # 无结果集的查询（INSERT, UPDATE, DELETE）
                result = [{'affected_rows': cursor.rowcount, 'last_insert_id': cursor.lastrowid}]
            
            conn.commit()
            
            return result
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            logger.error(f"执行查询失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def _is_write_query(self, query: str) -> bool:
        """判断是否为写操作"""
        query_lower = query.strip().lower()
        write_prefixes = ['insert', 'update', 'delete', 'create', 'drop', 'alter', 'truncate']
        return any(query_lower.startswith(prefix) for prefix in write_prefixes)
    
    def start_health_check(self):
        """启动健康检查"""
        self.health_checker.start()
    
    def stop_health_check(self):
        """停止健康检查"""
        self.health_checker.stop()
    
    def get_status(self) -> Dict:
        """获取负载均衡器状态"""
        healthy_nodes = {
            'master': [node.to_dict() for node in self.health_checker.get_master_nodes()],
            'slave': [node.to_dict() for node in self.health_checker.get_slave_nodes()]
        }
        
        all_nodes = {
            'all': [node.to_dict() for node in self.health_checker.nodes.values()]
        }
        
        return {
            'algorithm': self.algorithm,
            'healthy_nodes': healthy_nodes,
            'all_nodes': all_nodes
        }


class FailoverManager:
    """故障转移管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.health_checker = HealthChecker(config)
        self.master_candidates = config.get('master_candidates', [])
        self.failover_timeout = config.get('failover_timeout', 30)  # 故障转移超时时间
        self.check_interval = config.get('check_interval', 5)  # 主节点检查间隔
        self.running = False
        self.failover_thread = None
        self.failover_lock = threading.Lock()
        self.last_failover_time = 0
        self.failover_cooldown = config.get('failover_cooldown', 300)  # 故障转移冷却时间
        
    def add_master_candidate(self, node: MySQLNode):
        """添加主节点候选"""
        if node.node_id not in self.master_candidates:
            self.master_candidates.append(node.node_id)
            self.health_checker.add_node(node)
            logger.info(f"添加主节点候选: {node.node_id}")
    
    def start(self):
        """启动故障转移监控"""
        if self.running:
            logger.warning("故障转移管理器已在运行")
            return
        
        self.running = True
        self.failover_thread = threading.Thread(target=self._failover_loop)
        self.failover_thread.daemon = True
        self.failover_thread.start()
        logger.info("故障转移管理器已启动")
    
    def stop(self):
        """停止故障转移监控"""
        if not self.running:
            logger.warning("故障转移管理器未运行")
            return
        
        self.running = False
        if self.failover_thread:
            self.failover_thread.join(timeout=10)
        logger.info("故障转移管理器已停止")
    
    def _failover_loop(self):
        """故障转移循环"""
        while self.running:
            try:
                # 检查主节点状态
                self._check_master_status()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"故障转移循环异常: {e}")
                time.sleep(self.check_interval)
    
    def _check_master_status(self):
        """检查主节点状态"""
        master_nodes = self.health_checker.get_master_nodes()
        
        if not master_nodes:
            # 没有主节点，执行故障转移
            self._execute_failover("没有可用的主节点")
        elif len(master_nodes) > 1:
            # 多个主节点，可能存在脑裂，需要处理
            logger.warning("检测到多个主节点，可能存在脑裂")
            self._handle_split_brain(master_nodes)
        else:
            # 正常情况，只有一个主节点
            master_node = master_nodes[0]
            if not master_node.is_healthy:
                self._execute_failover(f"主节点 {master_node.node_id} 不健康")
    
    def _execute_failover(self, reason: str):
        """执行故障转移"""
        with self.failover_lock:
            # 检查是否在冷却期
            now = time.time()
            if now - self.last_failover_time < self.failover_cooldown:
                logger.info(f"故障转移在冷却期内，跳过: {reason}")
                return
            
            logger.warning(f"开始执行故障转移: {reason}")
            
            # 选择新的主节点
            new_master = self._select_new_master()
            if not new_master:
                logger.error("没有可用的主节点候选，故障转移失败")
                return
            
            # 执行故障转移
            success = self._perform_failover(new_master)
            if success:
                self.last_failover_time = now
                logger.info(f"故障转移成功，新主节点: {new_master.node_id}")
            else:
                logger.error("故障转移失败")
    
    def _select_new_master(self) -> Optional[MySQLNode]:
        """选择新的主节点"""
        healthy_slaves = self.health_checker.get_slave_nodes()
        if not healthy_slaves:
            return None
        
        # 从候选列表中选择健康的从节点
        candidate_slaves = [node for node in healthy_slaves 
                           if node.node_id in self.master_candidates]
        
        if not candidate_slaves:
            # 没有候选从节点，选择延迟最低的健康从节点
            return min(healthy_slaves, key=lambda node: node.replication_lag)
        else:
            # 选择候选中延迟最低的从节点
            return min(candidate_slaves, key=lambda node: node.replication_lag)
    
    def _perform_failover(self, new_master: MySQLNode) -> bool:
        """执行故障转移操作"""
        try:
            # 1. 停止所有从节点的复制
            self._stop_all_slaves()
            
            # 2. 提升新主节点
            self._promote_to_master(new_master)
            
            # 3. 重新配置其他从节点指向新主节点
            self._reconfigure_slaves(new_master)
            
            # 4. 更新节点角色
            self._update_node_roles(new_master)
            
            return True
        except Exception as e:
            logger.error(f"执行故障转移失败: {e}")
            return False
    
    def _stop_all_slaves(self):
        """停止所有从节点的复制"""
        for node in self.health_checker.nodes.values():
            if node.role == 'slave' and node.is_healthy:
                try:
                    conn = mysql.connector.connect(
                        host=node.host,
                        port=node.port,
                        user=self.config.get('username', 'root'),
                        password=self.config.get('password', '')
                    )
                    cursor = conn.cursor()
                    cursor.execute("STOP SLAVE")
                    cursor.close()
                    conn.close()
                    logger.debug(f"停止从节点 {node.node_id} 的复制")
                except Exception as e:
                    logger.error(f"停止从节点 {node.node_id} 的复制失败: {e}")
    
    def _promote_to_master(self, node: MySQLNode):
        """将从节点提升为主节点"""
        try:
            conn = mysql.connector.connect(
                host=node.host,
                port=node.port,
                user=self.config.get('username', 'root'),
                password=self.config.get('password', '')
            )
            cursor = conn.cursor()
            
            # 停止复制
            cursor.execute("STOP SLAVE")
            
            # 重置主服务器信息
            cursor.execute("RESET MASTER")
            
            # 设置为可写
            cursor.execute("SET GLOBAL read_only=0")
            
            cursor.close()
            conn.close()
            
            logger.info(f"节点 {node.node_id} 已提升为主节点")
        except Exception as e:
            logger.error(f"提升节点 {node.node_id} 为主节点失败: {e}")
            raise
    
    def _reconfigure_slaves(self, new_master: MySQLNode):
        """重新配置从节点指向新主节点"""
        for node in self.health_checker.nodes.values():
            if node.role == 'slave' and node.node_id != new_master.node_id and node.is_healthy:
                try:
                    conn = mysql.connector.connect(
                        host=node.host,
                        port=node.port,
                        user=self.config.get('username', 'root'),
                        password=self.config.get('password', '')
                    )
                    cursor = conn.cursor()
                    
                    # 配置复制指向新主节点
                    cursor.execute(f"""
                        CHANGE MASTER TO
                            MASTER_HOST='{new_master.host}',
                            MASTER_PORT={new_master.port},
                            MASTER_AUTO_POSITION=1
                    """)
                    
                    # 启动复制
                    cursor.execute("START SLAVE")
                    
                    cursor.close()
                    conn.close()
                    
                    logger.debug(f"从节点 {node.node_id} 已配置指向新主节点 {new_master.node_id}")
                except Exception as e:
                    logger.error(f"配置从节点 {node.node_id} 指向新主节点失败: {e}")
    
    def _update_node_roles(self, new_master: MySQLNode):
        """更新节点角色"""
        for node in self.health_checker.nodes.values():
            if node.node_id == new_master.node_id:
                node.role = 'master'
            elif node.role == 'master':
                # 原主节点标记为从节点
                node.role = 'slave'
        
        logger.info("节点角色更新完成")
    
    def _handle_split_brain(self, master_nodes: List[MySQLNode]):
        """处理脑裂问题"""
        # 简单处理：选择节点ID最小的主节点
        selected_master = min(master_nodes, key=lambda node: node.node_id)
        
        logger.warning(f"脑裂问题处理，选择主节点: {selected_master.node_id}")
        
        # 将其他主节点设置为从节点
        for node in master_nodes:
            if node.node_id != selected_master.node_id:
                try:
                    conn = mysql.connector.connect(
                        host=node.host,
                        port=node.port,
                        user=self.config.get('username', 'root'),
                        password=self.config.get('password', '')
                    )
                    cursor = conn.cursor()
                    cursor.execute("SET GLOBAL read_only=1")
                    cursor.close()
                    conn.close()
                    
                    node.role = 'slave'
                    logger.warning(f"脑裂处理：将节点 {node.node_id} 设置为从节点")
                except Exception as e:
                    logger.error(f"脑裂处理失败：{e}")


class MySQLCluster:
    """MySQL集群管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.nodes = {}  # node_id: MySQLNode
        self.load_balancer = LoadBalancer(config)
        self.failover_manager = FailoverManager(config)
        self.running = False
        
        # 初始化节点
        self._initialize_nodes()
        
        # 将节点添加到负载均衡器和故障转移管理器
        for node in self.nodes.values():
            self.load_balancer.add_node(node)
            if node.node_id in config.get('master_candidates', []):
                self.failover_manager.add_master_candidate(node)
    
    def _initialize_nodes(self):
        """初始化节点"""
        node_configs = self.config.get('nodes', [])
        for node_config in node_configs:
            node = MySQLNode(
                node_id=node_config['node_id'],
                host=node_config['host'],
                port=node_config['port'],
                role=node_config.get('role', 'unknown')
            )
            self.nodes[node.node_id] = node
    
    def start(self):
        """启动集群"""
        if self.running:
            logger.warning("集群已在运行")
            return
        
        # 启动健康检查
        self.load_balancer.start_health_check()
        
        # 启动故障转移管理器
        self.failover_manager.start()
        
        self.running = True
        logger.info("MySQL集群已启动")
    
    def stop(self):
        """停止集群"""
        if not self.running:
            logger.warning("集群未运行")
            return
        
        # 停止故障转移管理器
        self.failover_manager.stop()
        
        # 停止健康检查
        self.load_balancer.stop_health_check()
        
        self.running = False
        logger.info("MySQL集群已停止")
    
    def execute_query(self, query: str, params: Tuple = None, use_master: bool = False) -> List[Dict]:
        """执行查询"""
        return self.load_balancer.execute_query(query, params, use_master)
    
    def execute_write(self, query: str, params: Tuple = None) -> List[Dict]:
        """执行写操作"""
        return self.load_balancer.execute_query(query, params, use_master=True)
    
    def execute_read(self, query: str, params: Tuple = None) -> List[Dict]:
        """执行读操作"""
        return self.load_balancer.execute_query(query, params, use_master=False)
    
    def get_cluster_status(self) -> Dict:
        """获取集群状态"""
        lb_status = self.load_balancer.get_status()
        
        return {
            'cluster_running': self.running,
            'load_balancer': lb_status,
            'failover_manager': {
                'running': self.failover_manager.running,
                'master_candidates': self.failover_manager.master_candidates,
                'last_failover_time': self.failover_manager.last_failover_time
            }
        }
    
    def add_node(self, node: MySQLNode):
        """添加节点到集群"""
        self.nodes[node.node_id] = node
        self.load_balancer.add_node(node)
        
        if node.node_id in self.config.get('master_candidates', []):
            self.failover_manager.add_master_candidate(node)
        
        logger.info(f"节点 {node.node_id} 已添加到集群")
    
    def remove_node(self, node_id: str):
        """从集群移除节点"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.load_balancer.remove_node(node_id)
            logger.info(f"节点 {node_id} 已从集群移除")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MySQL高可用与负载均衡管理工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--demo', action='store_true', help='运行演示模式')
    
    args = parser.parse_args()
    
    # 默认配置
    config = {
        'username': 'root',
        'password': 'password',
        'database': 'mysql_tutorial',
        'check_interval': 5,
        'timeout': 3,
        'algorithm': 'least_connections',
        'pool_size': 5,
        'master_candidates': ['node1', 'node2'],
        'failover_timeout': 30,
        'check_interval': 5,
        'failover_cooldown': 300,
        'nodes': [
            {
                'node_id': 'node1',
                'host': 'localhost',
                'port': 3306,
                'role': 'master'
            },
            {
                'node_id': 'node2',
                'host': 'localhost',
                'port': 3307,
                'role': 'slave'
            },
            {
                'node_id': 'node3',
                'host': 'localhost',
                'port': 3308,
                'role': 'slave'
            }
        ]
    }
    
    # 从文件加载配置
    if args.config:
        try:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return
    
    try:
        # 创建集群
        cluster = MySQLCluster(config)
        
        # 启动集群
        cluster.start()
        
        if args.demo:
            # 演示模式
            logger.info("=== MySQL高可用与负载均衡演示 ===")
            
            # 等待健康检查完成
            time.sleep(2)
            
            # 显示集群状态
            status = cluster.get_cluster_status()
            logger.info(f"集群状态: {json.dumps(status, indent=2, default=str)}")
            
            # 执行一些测试查询
            logger.info("执行测试查询...")
            
            # 写操作（应该路由到主节点）
            try:
                # 创建测试表
                cluster.execute_write("""
                    CREATE TABLE IF NOT EXISTS test_ha (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        message VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logger.info("创建测试表成功")
                
                # 插入测试数据
                result = cluster.execute_write(
                    "INSERT INTO test_ha (message) VALUES (%s)",
                    ("Hello from HA cluster",)
                )
                logger.info(f"插入数据成功: {result}")
                
                # 读操作（应该路由到从节点）
                result = cluster.execute_read("SELECT * FROM test_ha ORDER BY id DESC LIMIT 5")
                logger.info(f"读取数据成功: {result}")
                
            except Exception as e:
                logger.error(f"测试查询失败: {e}")
            
            # 监控集群状态
            logger.info("开始监控集群状态（按Ctrl+C停止）...")
            try:
                while True:
                    time.sleep(10)
                    status = cluster.get_cluster_status()
                    
                    # 提取关键信息
                    healthy_masters = len(status['load_balancer']['healthy_nodes'].get('master', []))
                    healthy_slaves = len(status['load_balancer']['healthy_nodes'].get('slave', []))
                    
                    logger.info(f"集群状态 - 主节点: {healthy_masters}, 从节点: {healthy_slaves}")
                    
                    # 如果只有一个健康的节点，可能是故障转移状态
                    if healthy_masters == 0 and healthy_slaves > 0:
                        logger.warning("可能正在进行故障转移，没有健康的主节点")
                    
            except KeyboardInterrupt:
                logger.info("停止监控")
        else:
            # 非演示模式，启动集群并保持运行
            logger.info("MySQL集群已启动，按Ctrl+C停止")
            try:
                while True:
                    time.sleep(60)
                    # 定期检查集群状态
                    status = cluster.get_cluster_status()
                    if not status['load_balancer']['healthy_nodes'].get('master'):
                        logger.warning("没有健康的主节点")
                    
                    healthy_nodes = len(status['load_balancer']['healthy_nodes'].get('master', [])) + \
                                 len(status['load_balancer']['healthy_nodes'].get('slave', []))
                    logger.info(f"当前健康节点数: {healthy_nodes}")
                    
            except KeyboardInterrupt:
                logger.info("停止集群")
        
        # 停止集群
        cluster.stop()
        
    except Exception as e:
        logger.error(f"集群管理失败: {e}")


if __name__ == "__main__":
    main()