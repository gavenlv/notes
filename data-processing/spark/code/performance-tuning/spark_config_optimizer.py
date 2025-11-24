#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark配置优化器
根据系统资源和作业特点，自动生成优化的Spark配置。

运行方式:
python spark_config_optimizer.py
"""

import os
import psutil
import json

class SparkConfigOptimizer:
    """Spark配置优化器"""
    
    def __init__(self, cluster_mode="local"):
        """
        初始化配置优化器
        
        参数:
        - cluster_mode: 集群模式，可以是"local", "standalone", "yarn", "kubernetes"
        """
        self.cluster_mode = cluster_mode
        self.system_info = self._get_system_info()
    
    def _get_system_info(self):
        """获取系统信息"""
        # CPU信息
        cpu_count = os.cpu_count()
        
        # 内存信息
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024 ** 3)  # 转换为GB
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        total_disk_gb = disk.total / (1024 ** 3)
        
        return {
            "cpu_count": cpu_count,
            "total_memory_gb": total_memory_gb,
            "total_disk_gb": total_disk_gb
        }
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            # 应用程序配置
            "spark.app.name": "OptimizedSparkApp",
            "spark.submit.deployMode": "client",
            
            # 序列化配置
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            
            # 内存配置
            "spark.memory.fraction": "0.6",
            "spark.memory.storageFraction": "0.5",
            
            # SQL优化配置
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.sql.autoBroadcastJoinThreshold": "10MB",
            
            # 网络配置
            "spark.network.timeout": "300s",
            "spark.rpc.askTimeout": "300s",
            
            # 错误处理配置
            "spark.task.maxFailures": "4",
            "spark.stage.maxConsecutiveAttempts": "4"
        }
    
    def optimize_for_local_mode(self, job_type="general"):
        """
        为本地模式优化配置
        
        参数:
        - job_type: 作业类型，可以是"general", "ml", "streaming", "sql"
        """
        config = self._get_default_config()
        
        # 根据系统资源调整配置
        cpu_count = self.system_info["cpu_count"]
        total_memory_gb = self.system_info["total_memory_gb"]
        
        # 调整并行度
        config["spark.default.parallelism"] = str(cpu_count * 2)
        config["spark.sql.shuffle.partitions"] = str(cpu_count * 2)
        
        # 调整内存配置
        # 为本地模式，将大部分内存分配给Executor
        executor_memory_gb = max(1, int(total_memory_gb * 0.6))
        driver_memory_gb = max(1, int(total_memory_gb * 0.2))
        
        config["spark.driver.memory"] = f"{driver_memory_gb}g"
        config["spark.executor.memory"] = f"{executor_memory_gb}g"
        
        # 本地模式特定配置
        config["spark.master"] = f"local[{cpu_count}]"
        
        # 根据作业类型进行特定优化
        if job_type == "ml":
            # 机器学习作业优化
            config["spark.sql.execution.arrow.enabled"] = "true"
            config["spark.driver.extraJavaOptions"] = "-XX:+UseG1GC"
        elif job_type == "streaming":
            # 流处理作业优化
            config["spark.streaming.backpressure.enabled"] = "true"
            config["spark.streaming.stopGracefullyOnShutdown"] = "true"
        elif job_type == "sql":
            # SQL作业优化
            config["spark.sql.adaptive.enabled"] = "true"
            config["spark.sql.adaptive.coalescePartitions.enabled"] = "true"
            config["spark.sql.adaptive.skewJoin.enabled"] = "true"
        
        return config
    
    def optimize_for_cluster_mode(self, cluster_nodes=10, job_type="general"):
        """
        为集群模式优化配置
        
        参数:
        - cluster_nodes: 集群节点数
        - job_type: 作业类型
        """
        config = self._get_default_config()
        
        # 集群模式并行度配置
        config["spark.default.parallelism"] = str(cluster_nodes * 2)
        config["spark.sql.shuffle.partitions"] = str(cluster_nodes * 3)
        
        # 资源配置
        total_memory_gb = self.system_info["total_memory_gb"]
        
        # 假设每个节点有相同的资源
        node_memory_gb = total_memory_gb / cluster_nodes
        node_cores = self.system_info["cpu_count"] / cluster_nodes
        
        # Executor配置
        executor_memory_gb = max(2, int(node_memory_gb * 0.6))
        executor_cores = max(1, int(node_cores * 0.8))
        
        config["spark.executor.memory"] = f"{executor_memory_gb}g"
        config["spark.executor.cores"] = str(executor_cores)
        
        # Driver配置
        config["spark.driver.memory"] = "2g"
        config["spark.driver.cores"] = "1"
        
        # Executor实例数
        config["spark.executor.instances"] = str(cluster_nodes)
        
        # 根据作业类型进行特定优化
        if job_type == "ml":
            # 机器学习作业优化
            config["spark.sql.execution.arrow.enabled"] = "true"
            config["spark.executor.extraJavaOptions"] = "-XX:+UseG1GC"
            config["spark.driver.extraJavaOptions"] = "-XX:+UseG1GC"
        elif job_type == "streaming":
            # 流处理作业优化
            config["spark.streaming.backpressure.enabled"] = "true"
            config["spark.streaming.stopGracefullyOnShutdown"] = "true"
            config["spark.streaming.blockInterval"] = "200ms"
            config["spark.streaming.receiver.maxRate"] = "1000"
        elif job_type == "sql":
            # SQL作业优化
            config["spark.sql.adaptive.enabled"] = "true"
            config["spark.sql.adaptive.coalescePartitions.enabled"] = "true"
            config["spark.sql.adaptive.skewJoin.enabled"] = "true"
        
        # 动态分配
        config["spark.dynamicAllocation.enabled"] = "true"
        config["spark.dynamicAllocation.minExecutors"] = "2"
        config["spark.dynamicAllocation.maxExecutors"] = str(cluster_nodes)
        config["spark.dynamicAllocation.initialExecutors"] = str(int(cluster_nodes / 2))
        
        # Shuffle服务
        config["spark.shuffle.service.enabled"] = "true"
        
        # 根据集群模式特定配置
        if self.cluster_mode == "yarn":
            config["spark.submit.deployMode"] = "cluster"
            config["spark.yarn.maxAppAttempts"] = "4"
            config["spark.yarn.am.attemptFailuresValidityInterval"] = "1h"
        elif self.cluster_mode == "kubernetes":
            config["spark.kubernetes.authenticate.driver.serviceAccountName"] = "spark"
            config["spark.kubernetes.namespace"] = "default"
        
        return config
    
    def optimize_for_memory_intensive(self, data_size_gb):
        """
        为内存密集型作业优化配置
        
        参数:
        - data_size_gb: 数据大小（GB）
        """
        config = self._get_default_config()
        
        total_memory_gb = self.system_info["total_memory_gb"]
        
        # 根据数据大小调整内存配置
        if data_size_gb < total_memory_gb * 0.1:
            # 数据较小，可以全缓存
            config["spark.storage.memoryFraction"] = "0.7"
            config["spark.memory.fraction"] = "0.8"
        elif data_size_gb < total_memory_gb * 0.5:
            # 数据中等，部分缓存
            config["spark.storage.memoryFraction"] = "0.5"
            config["spark.memory.fraction"] = "0.6"
        else:
            # 数据较大，少部分缓存
            config["spark.storage.memoryFraction"] = "0.3"
            config["spark.memory.fraction"] = "0.6"
        
        # GC优化
        config["spark.executor.extraJavaOptions"] = "-XX:+UseG1GC -XX:MaxGCPauseMillis=200"
        config["spark.driver.extraJavaOptions"] = "-XX:+UseG1GC -XX:MaxGCPauseMillis=200"
        
        return config
    
    def optimize_for_cpu_intensive(self):
        """为CPU密集型作业优化配置"""
        config = self._get_default_config()
        
        # 增加并行度
        cpu_count = self.system_info["cpu_count"]
        config["spark.default.parallelism"] = str(cpu_count * 4)
        config["spark.sql.shuffle.partitions"] = str(cpu_count * 4)
        
        # 启用推测执行
        config["spark.speculation"] = "true"
        config["spark.speculation.quantile"] = "0.75"
        config["spark.speculation.multiplier"] = "1.5"
        
        return config
    
    def optimize_for_io_intensive(self):
        """为IO密集型作业优化配置"""
        config = self._get_default_config()
        
        # 并行度设置
        cpu_count = self.system_info["cpu_count"]
        config["spark.default.parallelism"] = str(cpu_count * 2)
        config["spark.sql.shuffle.partitions"] = str(cpu_count * 2)
        
        # IO相关配置
        config["spark.file.transferTo"] = "true"
        config["spark.hadoop.cloneConf"] = "true"
        
        # 本地Dir配置
        config["spark.local.dir"] = "/tmp/spark-temp"
        
        return config
    
    def get_optimized_config(self, job_type="general", data_size_gb=1, cluster_nodes=1):
        """
        获取优化配置
        
        参数:
        - job_type: 作业类型
        - data_size_gb: 数据大小
        - cluster_nodes: 集群节点数
        """
        # 根据集群模式选择基础配置
        if self.cluster_mode == "local":
            config = self.optimize_for_local_mode(job_type)
        else:
            config = self.optimize_for_cluster_mode(cluster_nodes, job_type)
        
        # 根据作业特性进行进一步优化
        if job_type == "memory_intensive":
            # 合并内存密集型配置
            memory_config = self.optimize_for_memory_intensive(data_size_gb)
            config.update(memory_config)
        elif job_type == "cpu_intensive":
            # 合并CPU密集型配置
            cpu_config = self.optimize_for_cpu_intensive()
            config.update(cpu_config)
        elif job_type == "io_intensive":
            # 合并IO密集型配置
            io_config = self.optimize_for_io_intensive()
            config.update(io_config)
        
        return config
    
    def print_config(self, config):
        """打印配置"""
        print("=== 优化的Spark配置 ===")
        print(f"集群模式: {self.cluster_mode}")
        print(f"系统资源: CPU={self.system_info['cpu_count']}, 内存={self.system_info['total_memory_gb']:.1f}GB")
        print("\n配置参数:")
        
        for key, value in sorted(config.items()):
            print(f"  {key}: {value}")
    
    def save_config(self, config, filename="spark_config.json"):
        """保存配置到文件"""
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
        print(f"配置已保存到: {filename}")

def main():
    """主函数"""
    print("Spark配置优化器")
    print("==================")
    
    # 获取系统信息
    system_info = {
        "cpu_count": os.cpu_count(),
        "total_memory_gb": psutil.virtual_memory().total / (1024 ** 3),
        "total_disk_gb": psutil.disk_usage('/').total / (1024 ** 3)
    }
    
    print(f"系统资源: CPU={system_info['cpu_count']}, 内存={system_info['total_memory_gb']:.1f}GB, 磁盘={system_info['total_disk_gb']:.1f}GB")
    print()
    
    # 创建本地模式优化器
    print("=== 本地模式配置优化 ===")
    local_optimizer = SparkConfigOptimizer("local")
    
    # 通用作业配置
    print("1. 通用作业配置:")
    general_config = local_optimizer.get_optimized_config("general")
    local_optimizer.print_config(general_config)
    local_optimizer.save_config(general_config, "spark_local_general.json")
    print()
    
    # 机器学习作业配置
    print("2. 机器学习作业配置:")
    ml_config = local_optimizer.get_optimized_config("ml")
    local_optimizer.print_config(ml_config)
    local_optimizer.save_config(ml_config, "spark_local_ml.json")
    print()
    
    # 内存密集型作业配置
    print("3. 内存密集型作业配置 (数据大小: 2GB):")
    memory_config = local_optimizer.get_optimized_config("memory_intensive", data_size_gb=2)
    local_optimizer.print_config(memory_config)
    local_optimizer.save_config(memory_config, "spark_local_memory.json")
    print()
    
    # CPU密集型作业配置
    print("4. CPU密集型作业配置:")
    cpu_config = local_optimizer.get_optimized_config("cpu_intensive")
    local_optimizer.print_config(cpu_config)
    local_optimizer.save_config(cpu_config, "spark_local_cpu.json")
    print()
    
    # 创建集群模式优化器
    print("=== 集群模式配置优化 (10个节点) ===")
    cluster_optimizer = SparkConfigOptimizer("yarn")
    
    # 通用作业配置
    print("1. 通用作业配置:")
    general_cluster_config = cluster_optimizer.get_optimized_config("general", cluster_nodes=10)
    cluster_optimizer.print_config(general_cluster_config)
    cluster_optimizer.save_config(general_cluster_config, "spark_cluster_general.json")
    
    print("\n配置优化完成!")

if __name__ == "__main__":
    main()