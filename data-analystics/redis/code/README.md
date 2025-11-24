# Redis代码示例

本目录包含Redis从入门到专家的完整代码示例，对应教程的各个章节。

## 目录结构

```
code/
├── chapter1/          # 第1章：Redis简介与安装
│   ├── install_redis.py
│   └── basic_operations.py
├── chapter2/          # 第2章：Redis数据结构与命令
│   ├── string_operations.py
│   ├── hash_operations.py
│   ├── list_operations.py
│   ├── set_operations.py
│   └── sorted_set_operations.py
├── chapter3/          # 第3章：Redis持久化与复制
│   ├── persistence_demo.py
│   └── replication_demo.py
├── chapter4/          # 第4章：Redis高级特性与事务
│   ├── transaction_demo.py
│   ├── pipeline_demo.py
│   └── lua_script_demo.py
├── chapter5/          # 第5章：Redis集群与高可用
│   ├── cluster_demo.py
│   └── sentinel_demo.py
├── chapter6/          # 第6章：Redis性能优化与监控
│   ├── performance_optimization.py
│   └── monitoring_demo.py
├── chapter7/          # 第7章：Redis应用场景与最佳实践
│   ├── cache_demo.py
│   ├── session_demo.py
│   └── message_queue_demo.py
├── requirements.txt   # Python依赖包
└── run_all.py        # 运行所有示例
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行示例

```bash
# 运行特定章节的示例
python chapter1/basic_operations.py

# 运行所有示例
python run_all.py
```

### 3. 配置Redis连接

在运行代码前，请确保Redis服务正在运行。默认连接配置：
- 主机：localhost
- 端口：6379
- 密码：无（如需密码，请在代码中修改）

## 代码说明

每个代码文件都包含：
- 详细的注释说明
- 实际可运行的示例
- 错误处理和最佳实践
- 性能优化建议

## 注意事项

1. 确保Redis服务已安装并运行
2. 部分高级功能需要Redis集群或哨兵模式
3. 生产环境代码包含安全配置和性能优化
4. 所有代码都经过测试，可直接运行

## 贡献

欢迎提交改进建议和新的代码示例！