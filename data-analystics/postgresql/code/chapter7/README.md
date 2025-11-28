# PostgreSQL教程第7章：事务管理与并发控制

## 目录内容

本章包含以下文件，用于演示PostgreSQL事务管理和并发控制的各种概念和技术：

### 主要文件说明

1. **transaction_basics.sql** - 基础事务操作演示
   - BEGIN/COMMIT/ROLLBACK语句的使用
   - SAVEPOINT和ROLLBACK TO的嵌套事务处理
   - 自动提交模式设置

2. **isolation_levels.sql** - 隔离级别演示
   - 四个事务隔离级别的详细展示
   - 脏读、不可重复读、幻读现象演示
   - 不同隔离级别下的并发行为

3. **locking_mechanisms.sql** - 锁机制演示
   - 表级锁和行级锁的类型和使用
   - 共享锁(SHARE)、排他锁(EXCLUSIVE)演示
   - 意向锁(INTENT)机制说明

4. **mvcc_demo.sql** - MVCC多版本并发控制演示
   - 版本链和快照隔离原理
   - 可见性判断规则
   - VACUUM和自动清理机制

5. **concurrency_examples.sql** - 并发控制实战案例
   - 银行业务转账示例
   - 库存管理并发问题
   - 死锁检测和预防

6. **python_examples.py** - Python事务处理示例
   - 使用psycopg2进行事务管理
   - 异常处理和回滚机制
   - 连接池中的事务处理

### 运行说明

#### 准备工作
1. 确保PostgreSQL服务正在运行
2. 创建测试数据库（如果需要）
3. 安装Python依赖：`pip install -r requirements.txt`

#### 执行顺序
建议按以下顺序执行SQL文件：

1. **transaction_basics.sql** - 学习基础事务操作
2. **isolation_levels.sql** - 理解不同隔离级别
3. **locking_mechanisms.sql** - 掌握锁机制
4. **mvcc_demo.sql** - 深入理解MVCC
5. **concurrency_examples.sql** - 实战案例练习

#### Python示例运行
```bash
python python_examples.py
```

### 主要功能演示

#### 1. 事务基础
- 原子性操作保证
- 保存点设置和回滚
- 事务自动提交模式

#### 2. 隔离级别控制
- READ UNCOMMITTED（读未提交）
- READ COMMITTED（读已提交）
- REPEATABLE READ（可重复读）
- SERIALIZABLE（串行化）

#### 3. 锁管理
- 表级锁类型和应用场景
- 行级锁的获取和释放
- 死锁检测和处理

#### 4. MVCC机制
- 多版本数据存储
- 快照隔离实现
- 并发读取无阻塞

#### 5. 实际应用
- 电商订单处理
- 财务报表生成
- 数据一致性保证

### 注意事项

1. **事务范围控制**：合理设置事务边界，避免长时间持有锁
2. **锁粒度选择**：根据业务需求选择合适的锁粒度
3. **死锁预防**：按相同顺序访问表，减少死锁发生
4. **隔离级别选择**：平衡一致性和性能，选择合适的隔离级别
5. **连接管理**：正确处理连接关闭和异常情况

### 相关文档

- PostgreSQL官方文档：[事务隔离](https://www.postgresql.org/docs/current/transaction-iso.html)
- [锁机制详解](https://www.postgresql.org/docs/current/explicit-locking.html)
- [MVCC原理](https://www.postgresql.org/docs/current/mvcc-intro.html)

### 实践建议

1. 在生产环境中优先使用默认隔离级别（READ COMMITTED）
2. 对于高并发写操作，考虑使用SERIALIZABLE级别
3. 定期监控锁等待和死锁情况
4. 使用连接池管理数据库连接
5. 在应用层实现重试机制处理临时性错误