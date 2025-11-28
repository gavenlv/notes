#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL备份与恢复示例代码
本章代码演示了MySQL中各种备份与恢复技术，包括逻辑备份、物理备份、增量备份、时间点恢复等。
"""

import os
import sys
import time
import datetime
import subprocess
import logging
import shutil
import gzip
import json
import threading
import hashlib
import tempfile
from typing import Dict, List, Tuple, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MySQL备份与恢复")

class LogicalBackupManager:
    """逻辑备份管理器"""
    
    def __init__(self, config):
        self.mysql_user = config.get('mysql_user', 'root')
        self.mysql_pass = config.get('mysql_pass', '')
        self.mysql_host = config.get('mysql_host', 'localhost')
        self.backup_dir = config.get('backup_dir', '/backup/mysql')
        self.temp_dir = config.get('temp_dir', '/tmp/mysql_backup')
        self.retention_days = config.get('retention_days', 30)
        self.compression = config.get('compression', True)
        
        # 确保目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def backup_database(self, database: str, options: Dict = None) -> Tuple[bool, str]:
        """备份单个数据库"""
        options = options or {}
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{database}_{date}.sql"
        backup_path = os.path.join(self.temp_dir, backup_file)
        compressed_path = f"{backup_path}.gz"
        
        try:
            # 构建mysqldump命令
            cmd = [
                'mysqldump',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}'
            ]
            
            # 添加选项
            if options.get('single_transaction', True):
                cmd.append('--single-transaction')
            
            if options.get('routines', True):
                cmd.append('--routines')
            
            if options.get('triggers', True):
                cmd.append('--triggers')
            
            if options.get('events', True):
                cmd.append('--events')
            
            if options.get('add_drop_table', True):
                cmd.append('--add-drop-table')
            
            # 添加数据库名
            cmd.append(database)
            
            # 执行备份
            with open(backup_path, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            # 检查备份文件
            if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
                # 压缩备份文件
                if self.compression:
                    self._compress_file(backup_path, compressed_path)
                    os.remove(backup_path)
                    final_path = compressed_path
                    backup_file = f"{backup_file}.gz"
                else:
                    final_path = backup_path
                
                # 移动到备份目录
                final_backup_path = os.path.join(self.backup_dir, backup_file)
                shutil.move(final_path, final_backup_path)
                
                # 计算文件哈希值
                file_hash = self._calculate_file_hash(final_backup_path)
                
                # 记录备份信息
                backup_info = {
                    'database': database,
                    'backup_file': backup_file,
                    'backup_path': final_backup_path,
                    'backup_time': datetime.datetime.now().isoformat(),
                    'file_size': os.path.getsize(final_backup_path),
                    'file_hash': file_hash,
                    'options': options
                }
                
                self._save_backup_info(backup_info)
                
                logger.info(f"数据库 {database} 备份成功: {final_backup_path}")
                return True, final_backup_path
            else:
                error_msg = f"备份文件为空或不存在: {backup_path}"
                logger.error(error_msg)
                return False, error_msg
                
        except subprocess.CalledProcessError as e:
            error_msg = f"备份失败: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"备份过程中发生错误: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def backup_all_databases(self, options: Dict = None) -> Dict:
        """备份所有数据库"""
        options = options or {}
        databases = self._get_databases()
        results = {}
        
        for database in databases:
            # 跳过系统数据库
            if database in ['information_schema', 'performance_schema', 'sys', 'mysql']:
                continue
                
            logger.info(f"开始备份数据库: {database}")
            success, message = self.backup_database(database, options)
            results[database] = {'success': success, 'message': message}
        
        return results
    
    def restore_database(self, backup_file: str, target_database: str = None) -> Tuple[bool, str]:
        """恢复数据库"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            if not os.path.exists(backup_path):
                return False, f"备份文件不存在: {backup_path}"
            
            # 如果是压缩文件，先解压
            if backup_file.endswith('.gz'):
                temp_file = os.path.join(self.temp_dir, f"restore_{int(time.time())}.sql")
                self._decompress_file(backup_path, temp_file)
                restore_file = temp_file
            else:
                restore_file = backup_path
            
            # 确定目标数据库名
            if not target_database:
                # 从备份文件名解析数据库名
                target_database = backup_file.split('_')[0]
            
            # 构建恢复命令
            cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}',
                target_database
            ]
            
            # 执行恢复
            with open(restore_file, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True)
            
            # 清理临时文件
            if backup_file.endswith('.gz'):
                os.remove(temp_file)
            
            logger.info(f"数据库 {target_database} 恢复成功: {backup_file}")
            return True, f"数据库 {target_database} 恢复成功"
            
        except subprocess.CalledProcessError as e:
            error_msg = f"恢复失败: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"恢复过程中发生错误: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def cleanup_old_backups(self, days: int = None) -> Dict:
        """清理过期备份"""
        days = days or self.retention_days
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # 获取备份信息
        backup_info = self._load_backup_info()
        cleaned_files = []
        
        for info in backup_info:
            backup_time = datetime.datetime.fromisoformat(info['backup_time'])
            
            if backup_time < cutoff_time:
                try:
                    os.remove(info['backup_path'])
                    cleaned_files.append(info['backup_file'])
                    logger.info(f"已删除过期备份: {info['backup_file']}")
                except Exception as e:
                    logger.error(f"删除备份失败: {info['backup_file']}, 错误: {e}")
        
        # 保存更新后的备份信息
        backup_info = [info for info in backup_info 
                      if datetime.datetime.fromisoformat(info['backup_time']) >= cutoff_time]
        self._save_backup_info_list(backup_info)
        
        return {'cleaned_files': cleaned_files, 'count': len(cleaned_files)}
    
    def verify_backup(self, backup_file: str) -> Dict:
        """验证备份文件"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            if not os.path.exists(backup_path):
                return {'success': False, 'message': f"备份文件不存在: {backup_file}"}
            
            # 获取备份信息
            backup_info_list = self._load_backup_info()
            backup_info = next((info for info in backup_info_list if info['backup_file'] == backup_file), None)
            
            if not backup_info:
                return {'success': False, 'message': f"找不到备份信息: {backup_file}"}
            
            # 计算当前文件哈希值
            current_hash = self._calculate_file_hash(backup_path)
            
            # 比较哈希值
            if current_hash != backup_info['file_hash']:
                return {'success': False, 'message': f"备份文件已损坏: {backup_file}"}
            
            # 尝试恢复到测试数据库
            test_db = f"test_{backup_info['database']}_{int(time.time())}"
            
            # 创建测试数据库
            create_cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}',
                '-e',
                f"CREATE DATABASE IF NOT EXISTS {test_db}"
            ]
            subprocess.run(create_cmd, check=True)
            
            # 恢复到测试数据库
            success, message = self.restore_database(backup_file, test_db)
            
            if success:
                # 验证数据
                verify_result = self._verify_database_content(test_db, backup_info['database'])
                
                # 删除测试数据库
                drop_cmd = [
                    'mysql',
                    f'-u{self.mysql_user}',
                    f'-p{self.mysql_pass}',
                    f'-h{self.mysql_host}',
                    '-e',
                    f"DROP DATABASE {test_db}"
                ]
                subprocess.run(drop_cmd, check=True)
                
                return {'success': True, 'message': "备份验证成功", 'details': verify_result}
            else:
                return {'success': False, 'message': f"备份恢复失败: {message}"}
                
        except Exception as e:
            return {'success': False, 'message': f"验证过程中发生错误: {e}"}
    
    def list_backups(self, database: str = None) -> List[Dict]:
        """列出备份文件"""
        backup_info = self._load_backup_info()
        
        if database:
            backup_info = [info for info in backup_info if info['database'] == database]
        
        # 按备份时间排序
        backup_info.sort(key=lambda x: x['backup_time'], reverse=True)
        
        return backup_info
    
    def schedule_backup(self, databases: List[str], schedule: str, options: Dict = None):
        """调度备份任务（简单实现）"""
        # 这里只是演示概念，实际应该使用cron或其他调度器
        logger.info(f"已调度备份任务: 数据库 {', '.join(databases)}, 计划 {schedule}")
        logger.info("请使用cron或其他调度工具实现定期备份")
        
        # 生成示例cron配置
        example_cron = f"# MySQL备份任务 - {schedule}\n{schedule} /usr/bin/python3 {__file__} --backup {' '.join(databases)}\n"
        logger.info(f"示例cron配置:\n{example_cron}")
    
    def _get_databases(self) -> List[str]:
        """获取所有数据库列表"""
        try:
            cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}',
                '-e',
                'SHOW DATABASES'
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
            databases = result.stdout.strip().split('\n')
            
            # 跳过第一行（列名）
            return databases[1:]
            
        except Exception as e:
            logger.error(f"获取数据库列表失败: {e}")
            return []
    
    def _compress_file(self, input_path: str, output_path: str):
        """压缩文件"""
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _decompress_file(self, input_path: str, output_path: str):
        """解压文件"""
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _save_backup_info(self, backup_info: Dict):
        """保存备份信息"""
        backup_info_list = self._load_backup_info()
        backup_info_list.append(backup_info)
        self._save_backup_info_list(backup_info_list)
    
    def _save_backup_info_list(self, backup_info_list: List[Dict]):
        """保存备份信息列表"""
        info_file = os.path.join(self.backup_dir, "backup_info.json")
        with open(info_file, 'w') as f:
            json.dump(backup_info_list, f, indent=2)
    
    def _load_backup_info(self) -> List[Dict]:
        """加载备份信息"""
        info_file = os.path.join(self.backup_dir, "backup_info.json")
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                return json.load(f)
        return []
    
    def _verify_database_content(self, test_db: str, original_db: str) -> Dict:
        """验证数据库内容"""
        try:
            # 获取表数量
            cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}',
                '-e',
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{test_db}'"
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
            table_count = int(result.stdout.strip().split('\n')[1])
            
            # 获取前几个表的记录数
            cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}',
                '-e',
                f"SELECT table_name FROM information_schema.tables WHERE table_schema='{test_db}' LIMIT 3"
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
            tables = result.stdout.strip().split('\n')[1:]
            
            table_records = {}
            for table in tables:
                if table.strip():
                    cmd = [
                        'mysql',
                        f'-u{self.mysql_user}',
                        f'-p{self.mysql_pass}',
                        f'-h{self.mysql_host}',
                        '-e',
                        f"SELECT COUNT(*) FROM {test_db}.{table}"
                    ]
                    result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
                    count = int(result.stdout.strip().split('\n')[1])
                    table_records[table] = count
            
            return {
                'table_count': table_count,
                'sample_tables': table_records
            }
            
        except Exception as e:
            return {'error': str(e)}


class PhysicalBackupManager:
    """物理备份管理器"""
    
    def __init__(self, config):
        self.mysql_user = config.get('mysql_user', 'root')
        self.mysql_pass = config.get('mysql_pass', '')
        self.mysql_host = config.get('mysql_host', 'localhost')
        self.backup_dir = config.get('backup_dir', '/backup/mysql')
        self.mysql_data_dir = config.get('mysql_data_dir', '/var/lib/mysql')
        self.retention_days = config.get('retention_days', 30)
        
        # 确保目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def cold_backup(self) -> Tuple[bool, str]:
        """冷备份（需要停机）"""
        try:
            date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"cold_backup_{date}")
            
            logger.info("开始冷备份，将停止MySQL服务")
            
            # 停止MySQL服务
            subprocess.run(['systemctl', 'stop', 'mysql'], check=True)
            
            # 复制数据目录
            shutil.copytree(self.mysql_data_dir, backup_path)
            
            # 启动MySQL服务
            subprocess.run(['systemctl', 'start', 'mysql'], check=True)
            
            logger.info(f"冷备份完成: {backup_path}")
            return True, backup_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"冷备份失败: {e}")
            # 尝试启动MySQL服务
            try:
                subprocess.run(['systemctl', 'start', 'mysql'])
            except:
                pass
            return False, str(e)
        except Exception as e:
            logger.error(f"冷备份失败: {e}")
            return False, str(e)
    
    def hot_backup_with_lvm(self, volume_path: str) -> Tuple[bool, str]:
        """使用LVM快照进行热备份"""
        try:
            date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_name = f"mysql_snapshot_{date}"
            snapshot_path = f"/dev/mapper/{volume_path.split('/')[2]}-{snapshot_name}"
            backup_path = os.path.join(self.backup_dir, f"lvm_backup_{date}")
            
            logger.info(f"创建LVM快照: {snapshot_name}")
            
            # 获取FLUSH TABLES WITH READ LOCK，确保数据一致性
            cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                '-e',
                'FLUSH TABLES WITH READ LOCK'
            ]
            subprocess.run(cmd, check=True)
            
            # 在另一个线程中保持锁，直到快照创建完成
            lock_thread = threading.Thread(target=self._keep_lock_alive)
            lock_thread.daemon = True
            lock_thread.start()
            
            try:
                # 创建快照
                subprocess.run([
                    'lvcreate',
                    '-L', '10G',
                    '-s',
                    '-n', snapshot_name,
                    volume_path
                ], check=True)
                
                # 释放锁
                cmd = [
                    'mysql',
                    f'-u{self.mysql_user}',
                    f'-p{self.mysql_pass}',
                    '-e',
                    'UNLOCK TABLES'
                ]
                subprocess.run(cmd, check=True)
                
                # 挂载快照
                mount_point = os.path.join(self.backup_dir, 'snapshot_mount')
                os.makedirs(mount_point, exist_ok=True)
                subprocess.run([
                    'mount',
                    snapshot_path,
                    mount_point
                ], check=True)
                
                # 复制数据
                shutil.copytree(os.path.join(mount_point, 'mysql'), backup_path)
                
                # 卸载快照
                subprocess.run(['umount', mount_point], check=True)
                os.rmdir(mount_point)
                
                # 删除快照
                subprocess.run(['lvremove', '-f', snapshot_path], check=True)
                
                logger.info(f"LVM热备份完成: {backup_path}")
                return True, backup_path
                
            except Exception as e:
                # 确保释放锁
                try:
                    cmd = [
                        'mysql',
                        f'-u{self.mysql_user}',
                        f'-p{self.mysql_pass}',
                        '-e',
                        'UNLOCK TABLES'
                    ]
                    subprocess.run(cmd)
                except:
                    pass
                raise e
                
        except subprocess.CalledProcessError as e:
            logger.error(f"LVM热备份失败: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"LVM热备份失败: {e}")
            return False, str(e)
    
    def hot_backup_with_xtrabackup(self, databases: List[str] = None) -> Tuple[bool, str]:
        """使用XtraBackup进行热备份"""
        try:
            date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"xtrabackup_{date}")
            
            logger.info(f"开始XtraBackup热备份: {backup_path}")
            
            # 创建备份
            cmd = [
                'xtrabackup',
                f'--user={self.mysql_user}',
                f'--password={self.mysql_pass}',
                f'--host={self.mysql_host}',
                '--backup',
                f'--target-dir={backup_path}'
            ]
            
            if databases:
                cmd.extend(['--databases', ','.join(databases)])
            
            subprocess.run(cmd, check=True)
            
            # 准备备份
            prepare_cmd = [
                'xtrabackup',
                '--prepare',
                f'--target-dir={backup_path}'
            ]
            subprocess.run(prepare_cmd, check=True)
            
            logger.info(f"XtraBackup热备份完成: {backup_path}")
            return True, backup_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"XtraBackup热备份失败: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"XtraBackup热备份失败: {e}")
            return False, str(e)
    
    def incremental_backup(self, base_backup_path: str) -> Tuple[bool, str]:
        """增量备份"""
        try:
            date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            inc_backup_path = os.path.join(self.backup_dir, f"xtrabackup_inc_{date}")
            
            logger.info(f"开始增量备份: {inc_backup_path}")
            
            # 创建增量备份
            cmd = [
                'xtrabackup',
                f'--user={self.mysql_user}',
                f'--password={self.mysql_pass}',
                f'--host={self.mysql_host}',
                '--backup',
                f'--target-dir={inc_backup_path}',
                f'--incremental-basedir={base_backup_path}'
            ]
            
            subprocess.run(cmd, check=True)
            
            logger.info(f"增量备份完成: {inc_backup_path}")
            return True, inc_backup_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"增量备份失败: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"增量备份失败: {e}")
            return False, str(e)
    
    def restore_backup(self, backup_path: str, mysql_data_dir: str = None) -> Tuple[bool, str]:
        """恢复物理备份"""
        try:
            target_dir = mysql_data_dir or self.mysql_data_dir
            original_dir = f"{target_dir}.bak.{int(time.time())}"
            
            logger.info(f"开始恢复备份: {backup_path}")
            
            # 停止MySQL服务
            subprocess.run(['systemctl', 'stop', 'mysql'], check=True)
            
            # 备份当前数据目录
            if os.path.exists(target_dir):
                shutil.move(target_dir, original_dir)
            
            # 创建新数据目录
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制备份数据
            shutil.copytree(backup_path, target_dir, dirs_exist_ok=True)
            
            # 设置正确的权限
            subprocess.run([
                'chown',
                '-R',
                'mysql:mysql',
                target_dir
            ], check=True)
            
            # 启动MySQL服务
            subprocess.run(['systemctl', 'start', 'mysql'], check=True)
            
            logger.info(f"备份恢复完成: {backup_path}")
            return True, f"备份恢复成功，原数据目录备份至: {original_dir}"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"恢复备份失败: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"恢复备份失败: {e}")
            return False, str(e)
    
    def _keep_lock_alive(self):
        """保持表锁活跃"""
        try:
            while True:
                # 每30秒发送一个保持锁的查询
                time.sleep(30)
                cmd = [
                    'mysql',
                    f'-u{self.mysql_user}',
                    f'-p{self.mysql_pass}',
                    '-e',
                    'SELECT 1'
                ]
                subprocess.run(cmd)
        except:
            pass


class BinlogManager:
    """二进制日志管理器"""
    
    def __init__(self, config):
        self.mysql_user = config.get('mysql_user', 'root')
        self.mysql_pass = config.get('mysql_pass', '')
        self.mysql_host = config.get('mysql_host', 'localhost')
        self.backup_dir = config.get('backup_dir', '/backup/mysql')
        self.binlog_dir = config.get('binlog_dir', '/var/lib/mysql')
        
        # 确保目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_binlog_files(self) -> List[Dict]:
        """获取二进制日志文件列表"""
        try:
            cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}',
                '-e',
                'SHOW BINARY LOGS'
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            # 跳过标题行
            if len(lines) > 1:
                files = []
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2:
                        files.append({
                            'file': parts[0],
                            'size': parts[1],
                            'path': os.path.join(self.binlog_dir, parts[0])
                        })
                return files
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取二进制日志列表失败: {e}")
            return []
    
    def backup_binlog_file(self, binlog_file: str) -> Tuple[bool, str]:
        """备份二进制日志文件"""
        try:
            binlog_path = os.path.join(self.binlog_dir, binlog_file)
            
            if not os.path.exists(binlog_path):
                return False, f"二进制日志文件不存在: {binlog_path}"
            
            date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"binlog_{binlog_file}_{date}")
            
            shutil.copy2(binlog_path, backup_path)
            
            logger.info(f"二进制日志文件备份成功: {backup_path}")
            return True, backup_path
            
        except Exception as e:
            logger.error(f"备份二进制日志文件失败: {e}")
            return False, str(e)
    
    def backup_all_binlogs(self) -> Dict:
        """备份所有二进制日志文件"""
        binlog_files = self.get_binlog_files()
        results = {}
        
        for binlog_info in binlog_files:
            file = binlog_info['file']
            logger.info(f"备份二进制日志文件: {file}")
            success, message = self.backup_binlog_file(file)
            results[file] = {'success': success, 'message': message}
        
        return results
    
    def point_in_time_recovery(self, start_datetime: str, stop_datetime: str, 
                            output_file: str = None) -> Tuple[bool, str]:
        """时间点恢复"""
        try:
            if not output_file:
                date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = os.path.join(self.backup_dir, f"point_in_time_recovery_{date}.sql")
            
            # 构建mysqlbinlog命令
            cmd = [
                'mysqlbinlog',
                f'--start-datetime={start_datetime}',
                f'--stop-datetime={stop_datetime}'
            ]
            
            # 添加所有二进制日志文件
            binlog_files = self.get_binlog_files()
            for binlog_info in binlog_files:
                cmd.append(binlog_info['path'])
            
            # 执行并输出到文件
            with open(output_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            
            logger.info(f"时间点恢复SQL生成成功: {output_file}")
            return True, output_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"时间点恢复失败: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"时间点恢复失败: {e}")
            return False, str(e)
    
    def apply_binlog(self, binlog_file: str, database: str = None, 
                   start_position: str = None, stop_position: str = None) -> Tuple[bool, str]:
        """应用二进制日志"""
        try:
            # 构建mysqlbinlog命令
            cmd = [
                'mysqlbinlog'
            ]
            
            if start_position:
                cmd.extend(['--start-position', start_position])
            
            if stop_position:
                cmd.extend(['--stop-position', stop_position])
            
            cmd.append(binlog_file)
            
            # 构建mysql命令
            mysql_cmd = [
                'mysql',
                f'-u{self.mysql_user}',
                f'-p{self.mysql_pass}',
                f'-h{self.mysql_host}'
            ]
            
            if database:
                mysql_cmd.append(database)
            
            # 使用管道连接mysqlbinlog和mysql
            mysqlbinlog_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            mysql_process = subprocess.Popen(mysql_cmd, stdin=mysqlbinlog_process.stdout)
            
            # 等待完成
            mysql_process.communicate()
            
            if mysql_process.returncode == 0:
                logger.info(f"二进制日志应用成功: {binlog_file}")
                return True, f"二进制日志应用成功: {binlog_file}"
            else:
                error_msg = f"二进制日志应用失败，返回码: {mysql_process.returncode}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            logger.error(f"应用二进制日志失败: {e}")
            return False, str(e)
    
    def purge_binlogs(self, before_date: str = None, before_file: str = None) -> Tuple[bool, str]:
        """清理二进制日志"""
        try:
            if before_date:
                cmd = [
                    'mysql',
                    f'-u{self.mysql_user}',
                    f'-p{self.mysql_pass}',
                    f'-h{self.mysql_host}',
                    '-e',
                    f"PURGE BINARY LOGS BEFORE '{before_date}'"
                ]
            elif before_file:
                cmd = [
                    'mysql',
                    f'-u{self.mysql_user}',
                    f'-p{self.mysql_pass}',
                    f'-h{self.mysql_host}',
                    '-e',
                    f"PURGE BINARY LOGS TO '{before_file}'"
                ]
            else:
                return False, "必须指定before_date或before_file参数"
            
            subprocess.run(cmd, check=True)
            
            logger.info(f"二进制日志清理成功")
            return True, "二进制日志清理成功"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"清理二进制日志失败: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"清理二进制日志失败: {e}")
            return False, str(e)


class BackupScheduler:
    """备份调度器"""
    
    def __init__(self, config):
        self.logical_backup = LogicalBackupManager(config)
        self.physical_backup = PhysicalBackupManager(config)
        self.binlog_manager = BinlogManager(config)
        self.schedule_config = config.get('schedule', {})
        
        # 调度任务列表
        self.scheduled_tasks = []
    
    def add_scheduled_backup(self, backup_type: str, schedule: str, 
                          databases: List[str] = None, options: Dict = None):
        """添加调度备份任务"""
        task = {
            'type': backup_type,
            'schedule': schedule,
            'databases': databases,
            'options': options or {},
            'last_run': None,
            'next_run': None
        }
        
        self.scheduled_tasks.append(task)
        logger.info(f"已添加调度备份任务: {backup_type} - {schedule}")
        
        # 生成cron配置示例
        self._generate_cron_example(task)
        
        return task
    
    def _generate_cron_example(self, task: Dict):
        """生成cron配置示例"""
        job_name = f"{task['type']}_{task['schedule']}".replace(' ', '_')
        databases_str = ' '.join(task['databases']) if task['databases'] else ''
        options_str = json.dumps(task['options']) if task['options'] else ''
        
        script_path = os.path.abspath(__file__)
        
        cron_line = f"{task['schedule']} /usr/bin/python3 {script_path} --{task['type']} --databases '{databases_str}' --options '{options_str}'\n"
        
        cron_example = f"# {job_name}\n{cron_line}"
        
        logger.info(f"Cron配置示例:\n{cron_example}")
        
        # 写入cron示例文件
        cron_file = os.path.join(os.path.dirname(script_path), "crontab_example")
        with open(cron_file, 'a') as f:
            f.write(f"\n# {job_name}\n{cron_line}")
    
    def run_scheduled_task(self, task: Dict) -> Dict:
        """运行调度任务"""
        start_time = time.time()
        result = {
            'task': task,
            'start_time': datetime.datetime.now().isoformat(),
            'success': False,
            'message': '',
            'duration': 0
        }
        
        try:
            if task['type'] == 'logical':
                if task['databases']:
                    # 备份指定数据库
                    backup_results = {}
                    for db in task['databases']:
                        success, message = self.logical_backup.backup_database(db, task['options'])
                        backup_results[db] = {'success': success, 'message': message}
                    
                    result['success'] = all(r['success'] for r in backup_results.values())
                    result['message'] = f"逻辑备份完成: {backup_results}"
                    result['details'] = backup_results
                else:
                    # 备份所有数据库
                    backup_results = self.logical_backup.backup_all_databases(task['options'])
                    result['success'] = all(r['success'] for r in backup_results.values())
                    result['message'] = f"所有数据库逻辑备份完成: {backup_results}"
                    result['details'] = backup_results
                    
            elif task['type'] == 'physical':
                success, message = self.physical_backup.hot_backup_with_xtrabackup(task['databases'])
                result['success'] = success
                result['message'] = message
                
            elif task['type'] == 'binlog':
                backup_results = self.binlog_manager.backup_all_binlogs()
                result['success'] = all(r['success'] for r in backup_results.values())
                result['message'] = f"二进制日志备份完成: {backup_results}"
                result['details'] = backup_results
                
            else:
                result['success'] = False
                result['message'] = f"未知的备份类型: {task['type']}"
            
        except Exception as e:
            result['success'] = False
            result['message'] = f"任务执行异常: {e}"
        
        # 更新任务信息
        end_time = time.time()
        result['end_time'] = datetime.datetime.now().isoformat()
        result['duration'] = end_time - start_time
        task['last_run'] = result['start_time']
        
        return result
    
    def run_all_scheduled_tasks(self) -> List[Dict]:
        """运行所有调度任务"""
        results = []
        
        for task in self.scheduled_tasks:
            logger.info(f"运行调度任务: {task['type']}")
            result = self.run_scheduled_task(task)
            results.append(result)
            
            if result['success']:
                logger.info(f"任务成功完成: {task['type']}, 耗时: {result['duration']:.2f}秒")
            else:
                logger.error(f"任务执行失败: {task['type']}, 错误: {result['message']}")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MySQL备份与恢复管理工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--logical', action='store_true', help='执行逻辑备份')
    parser.add_argument('--physical', action='store_true', help='执行物理备份')
    parser.add_argument('--binlog', action='store_true', help='备份二进制日志')
    parser.add_argument('--databases', help='指定数据库，用逗号分隔')
    parser.add_argument('--restore', help='恢复指定的备份文件')
    parser.add_argument('--target-db', help='恢复到指定数据库')
    parser.add_argument('--verify', help='验证指定的备份文件')
    parser.add_argument('--list', action='store_true', help='列出所有备份')
    parser.add_argument('--cleanup', type=int, help='清理指定天数前的备份')
    parser.add_argument('--schedule', action='store_true', help='运行所有调度任务')
    
    args = parser.parse_args()
    
    # 默认配置
    config = {
        'mysql_user': 'root',
        'mysql_pass': 'password',
        'mysql_host': 'localhost',
        'backup_dir': '/backup/mysql',
        'temp_dir': '/tmp/mysql_backup',
        'retention_days': 30,
        'mysql_data_dir': '/var/lib/mysql',
        'binlog_dir': '/var/lib/mysql',
        'schedule': {
            'daily_logical': {
                'type': 'logical',
                'schedule': '0 2 * * *',
                'databases': ['mysql_tutorial'],
                'options': {'single_transaction': True, 'routines': True}
            },
            'weekly_physical': {
                'type': 'physical',
                'schedule': '0 3 * * 0',
                'databases': None,
                'options': {}
            },
            'hourly_binlog': {
                'type': 'binlog',
                'schedule': '0 * * * *',
                'databases': None,
                'options': {}
            }
        }
    }
    
    # 创建管理器
    logical_backup = LogicalBackupManager(config)
    physical_backup = PhysicalBackupManager(config)
    binlog_manager = BinlogManager(config)
    scheduler = BackupScheduler(config)
    
    # 添加调度任务
    for task_name, task_config in config['schedule'].items():
        scheduler.add_scheduled_backup(
            task_config['type'],
            task_config['schedule'],
            task_config['databases'],
            task_config['options']
        )
    
    try:
        # 处理命令行参数
        if args.logical:
            databases = args.databases.split(',') if args.databases else None
            if databases:
                for db in databases:
                    success, message = logical_backup.backup_database(db)
                    if success:
                        logger.info(f"数据库 {db} 备份成功: {message}")
                    else:
                        logger.error(f"数据库 {db} 备份失败: {message}")
            else:
                results = logical_backup.backup_all_databases()
                for db, result in results.items():
                    if result['success']:
                        logger.info(f"数据库 {db} 备份成功: {result['message']}")
                    else:
                        logger.error(f"数据库 {db} 备份失败: {result['message']}")
        
        elif args.physical:
            success, message = physical_backup.hot_backup_with_xtrabackup()
            if success:
                logger.info(f"物理备份成功: {message}")
            else:
                logger.error(f"物理备份失败: {message}")
        
        elif args.binlog:
            results = binlog_manager.backup_all_binlogs()
            for file, result in results.items():
                if result['success']:
                    logger.info(f"二进制日志文件 {file} 备份成功: {result['message']}")
                else:
                    logger.error(f"二进制日志文件 {file} 备份失败: {result['message']}")
        
        elif args.restore:
            success, message = logical_backup.restore_database(args.restore, args.target_db)
            if success:
                logger.info(f"恢复成功: {message}")
            else:
                logger.error(f"恢复失败: {message}")
        
        elif args.verify:
            result = logical_backup.verify_backup(args.verify)
            if result['success']:
                logger.info(f"备份验证成功: {result['message']}")
                logger.info(f"验证详情: {result.get('details', {})}")
            else:
                logger.error(f"备份验证失败: {result['message']}")
        
        elif args.list:
            databases = args.databases.split(',') if args.databases else None
            backups = logical_backup.list_backups(databases)
            
            if backups:
                logger.info("备份列表:")
                for backup in backups:
                    logger.info(f"  数据库: {backup['database']}, 文件: {backup['backup_file']}, "
                              f"时间: {backup['backup_time']}, 大小: {backup['file_size']}")
            else:
                logger.info("没有找到备份文件")
        
        elif args.cleanup:
            result = logical_backup.cleanup_old_backups(args.cleanup)
            logger.info(f"清理完成，删除了 {result['count']} 个备份文件")
            for file in result['cleaned_files']:
                logger.info(f"  已删除: {file}")
        
        elif args.schedule:
            results = scheduler.run_all_scheduled_tasks()
            logger.info(f"调度任务执行完成，共执行 {len(results)} 个任务")
            
            success_count = sum(1 for r in results if r['success'])
            logger.info(f"成功 {success_count} 个，失败 {len(results) - success_count} 个")
        
        else:
            # 默认运行示例
            logger.info("=== MySQL逻辑备份示例 ===")
            success, message = logical_backup.backup_database("mysql_tutorial")
            if success:
                logger.info(f"备份成功: {message}")
                
                # 列出备份
                backups = logical_backup.list_backups("mysql_tutorial")
                if backups:
                    latest_backup = backups[0]['backup_file']
                    logger.info(f"验证最新备份: {latest_backup}")
                    result = logical_backup.verify_backup(latest_backup)
                    if result['success']:
                        logger.info(f"备份验证成功: {result['message']}")
                    else:
                        logger.error(f"备份验证失败: {result['message']}")
            else:
                logger.error(f"备份失败: {message}")
            
            logger.info("\n=== MySQL物理备份示例 ===")
            success, message = physical_backup.hot_backup_with_xtrabackup(["mysql_tutorial"])
            if success:
                logger.info(f"物理备份成功: {message}")
            else:
                logger.error(f"物理备份失败: {message}")
            
            logger.info("\n=== 二进制日志备份示例 ===")
            results = binlog_manager.backup_all_binlogs()
            for file, result in results.items():
                if result['success']:
                    logger.info(f"二进制日志文件 {file} 备份成功")
                else:
                    logger.error(f"二进制日志文件 {file} 备份失败")
    
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
    except Exception as e:
        logger.error(f"操作失败: {e}")


if __name__ == "__main__":
    main()