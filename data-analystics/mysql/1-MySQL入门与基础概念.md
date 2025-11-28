# 第1章：MySQL入门与基础概念

## 目录
1. [什么是MySQL](#1-什么是mysql)
2. [关系型数据库基础](#2-关系型数据库基础)
3. [MySQL安装与配置](#3-mysql安装与配置)
4. [MySQL基本操作](#4-mysql基本操作)
5. [数据类型](#5-数据类型)
6. [SQL基础](#6-sql基础)
7. [最佳实践](#7-最佳实践)

## 1. 什么是MySQL

### 1.1 MySQL简介

MySQL是一个开源的关系型数据库管理系统（RDBMS），由瑞典MySQL AB公司开发，现在属于Oracle公司。MySQL是最流行的关系型数据库管理系统之一，广泛应用于Web应用开发中。

### 1.2 MySQL特点

- **开源免费**：MySQL社区版是免费的，企业版提供更多功能和支持
- **跨平台**：支持多种操作系统，包括Windows、Linux、MacOS等
- **高性能**：优化的查询执行引擎，支持高并发
- **可靠性**：提供事务支持、崩溃恢复等机制
- **易用性**：简单易学的SQL语言，丰富的管理工具
- **扩展性**：支持多种存储引擎，可根据需求选择
- **安全性**：提供多种安全机制，如用户权限、SSL加密等

### 1.3 MySQL应用场景

- **Web应用**：作为网站后台数据库，存储用户信息、商品数据等
- **日志系统**：存储和分析系统日志
- **数据仓库**：存储和分析大量业务数据
- **嵌入式应用**：作为嵌入式数据库使用

### 1.4 MySQL vs 其他数据库

| 特性 | MySQL | PostgreSQL | SQLite | Oracle |
|------|-------|------------|--------|--------|
| 开源 | 是 | 是 | 是 | 否 |
| 跨平台 | 是 | 是 | 是 | 是 |
| 事务支持 | 是 | 是 | 是 | 是 |
| 性能 | 高 | 中 | 低 | 高 |
| 学习难度 | 简单 | 中等 | 简单 | 复杂 |
| 社区支持 | 强 | 强 | 中 | 强 |

## 2. 关系型数据库基础

### 2.1 数据库基本概念

#### 什么是数据库

数据库是按照数据结构来组织、存储和管理数据的仓库。它是一个长期存储在计算机内的、有组织的、可共享的、统一管理的大量数据的集合。

#### 数据库管理系统（DBMS）

数据库管理系统是位于用户与操作系统之间的一层数据管理软件，它为用户或应用程序提供访问数据的方法，包括数据库的建立、查询、更新及各种数据控制。

### 2.2 关系型数据库核心概念

#### 表（Table）

表是关系型数据库中最基本的数据结构，由行和列组成的二维结构。例如，一个学生表可能包含学号、姓名、年龄等列，每个学生对应一行数据。

```
学生表 (students)
+----+--------+------+--------+
| id | name   | age  | class  |
+----+--------+------+--------+
| 1  | 张三   | 18   | 一班   |
| 2  | 李四   | 19   | 二班   |
| 3  | 王五   | 18   | 一班   |
+----+--------+------+--------+
```

#### 字段（Field/Column）

表中的每一列称为一个字段，描述了数据的某种属性。例如，上表中的"id"、"name"、"age"、"class"都是字段。

#### 记录（Record/Row）

表中的每一行称为一条记录，是一个完整的实体信息。例如，上表中的每一行都代表一个学生。

#### 主键（Primary Key）

主键是表中唯一标识每条记录的字段或字段组合。主键的值不能重复，也不能为NULL。例如，学生表中的"id"字段可以作为主键。

#### 外键（Foreign Key）

外键是一个表中的字段，其值引用另一个表的主键。外键用于建立表与表之间的关联关系。

### 2.3 数据库范式

#### 第一范式（1NF）

第一范式要求表中的每个字段都是不可再分的基本数据项。也就是说，每个字段只包含一个值，不能包含重复组。

**不符合1NF的例子：**
```
学生表
+----+--------+----------------+
| id | name   | hobbies        |
+----+--------+----------------+
| 1  | 张三   | 篮球,游泳      |
+----+--------+----------------+
```

**符合1NF的例子：**
```
学生表
+----+--------+
| id | name   |
+----+--------+
| 1  | 张三   |
+----+--------+

爱好表
+----+------------+
| id | hobby      |
+----+------------+
| 1  | 篮球       |
| 1  | 游泳       |
+----+------------+
```

#### 第二范式（2NF）

第二范式在满足第一范式的基础上，要求非主键字段完全依赖于主键，不能只依赖于主键的一部分（适用于复合主键）。

#### 第三范式（3NF）

第三范式在满足第二范式的基础上，要求非主键字段之间不存在传递依赖关系。

**不符合3NF的例子：**
```
学生表
+----+--------+------+-----------+
| id | name   | age  | class_name |
+----+--------+------+-----------+
| 1  | 张三   | 18   | 一班      |
+----+--------+------+-----------+
```

**符合3NF的例子：**
```
学生表
+----+--------+------+----------+
| id | name   | age  | class_id |
+----+--------+------+----------+
| 1  | 张三   | 18   | 1        |
+----+--------+------+----------+

班级表
+----------+-----------+
| class_id | class_name|
+----------+-----------+
| 1        | 一班      |
+----------+-----------+
```

## 3. MySQL安装与配置

### 3.1 Windows系统安装

1. 下载MySQL安装包：访问[MySQL官网](https://dev.mysql.com/downloads/mysql/)下载MySQL Community Server
2. 运行安装程序：双击下载的安装包，按照提示进行安装
3. 配置MySQL：在安装过程中设置root用户密码，选择默认字符集等
4. 验证安装：打开命令提示符，输入`mysql -u root -p`，输入密码验证安装

### 3.2 Linux系统安装（Ubuntu/Debian）

```bash
# 更新软件包列表
sudo apt update

# 安装MySQL服务器
sudo apt install mysql-server

# 启动MySQL服务
sudo systemctl start mysql

# 设置MySQL开机自启
sudo systemctl enable mysql

# 运行安全脚本
sudo mysql_secure_installation
```

### 3.3 MacOS系统安装

```bash
# 使用Homebrew安装
brew install mysql

# 启动MySQL服务
brew services start mysql

# 设置root密码
mysql_secure_installation
```

### 3.4 基本配置

#### 修改配置文件

MySQL的配置文件通常位于：
- Windows: `C:\ProgramData\MySQL\MySQL Server 8.0\my.ini`
- Linux: `/etc/mysql/mysql.conf.d/mysqld.cnf`或`/etc/my.cnf`
- MacOS: `/usr/local/etc/my.cnf`或`/etc/my.cnf`

#### 常用配置项

```ini
[mysqld]
# 设置默认字符集
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 设置默认存储引擎
default-storage-engine=INNODB

# 设置端口
port=3306

# 设置最大连接数
max_connections=100

# 设置查询缓存
query_cache_type=1
query_cache_size=32M

# 设置日志
log-error=/var/log/mysql/error.log
```

## 4. MySQL基本操作

### 4.1 连接与断开MySQL

#### 连接MySQL

```bash
# 基本连接命令
mysql -u username -p

# 指定主机和端口连接
mysql -h hostname -P port -u username -p

# 直接指定密码（不安全）
mysql -u username -ppassword

# 连接到指定数据库
mysql -u username -p database_name
```

#### 断开连接

```sql
-- 在MySQL命令行中执行
EXIT;
QUIT;
```

### 4.2 MySQL常用命令

#### 显示数据库

```sql
-- 显示所有数据库
SHOW DATABASES;

-- 显示当前数据库
SELECT DATABASE();
```

#### 选择数据库

```sql
-- 选择要使用的数据库
USE database_name;
```

#### 创建数据库

```sql
-- 创建数据库
CREATE DATABASE mydb;

-- 创建数据库并指定字符集
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 如果不存在则创建数据库
CREATE DATABASE IF NOT EXISTS mydb;
```

#### 删除数据库

```sql
-- 删除数据库
DROP DATABASE mydb;

-- 如果存在则删除数据库
DROP DATABASE IF EXISTS mydb;
```

#### 显示表

```sql
-- 显示当前数据库中的所有表
SHOW TABLES;

-- 显示表的结构
DESCRIBE table_name;
-- 或者
DESC table_name;
```

### 4.3 用户管理

#### 创建用户

```sql
-- 创建用户
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';

-- 创建用户并指定权限
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password' WITH GRANT OPTION;

-- 创建可以从任何主机连接的用户
CREATE USER 'username'@'%' IDENTIFIED BY 'password';
```

#### 修改用户密码

```sql
-- 修改用户密码
ALTER USER 'username'@'localhost' IDENTIFIED BY 'new_password';

-- 使用SET PASSWORD修改密码
SET PASSWORD FOR 'username'@'localhost' = PASSWORD('new_password');
```

#### 删除用户

```sql
-- 删除用户
DROP USER 'username'@'localhost';
```

#### 授予权限

```sql
-- 授予用户在所有数据库上的所有权限
GRANT ALL PRIVILEGES ON *.* TO 'username'@'localhost';

-- 授予用户在特定数据库上的所有权限
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';

-- 授予用户在特定表上的特定权限
GRANT SELECT, INSERT, UPDATE ON database_name.table_name TO 'username'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;
```

#### 撤销权限

```sql
-- 撤销用户的所有权限
REVOKE ALL PRIVILEGES ON *.* FROM 'username'@'localhost';

-- 撤销用户在特定数据库上的所有权限
REVOKE ALL PRIVILEGES ON database_name.* FROM 'username'@'localhost';
```

## 5. 数据类型

### 5.1 数值类型

#### 整数类型

| 类型 | 字节 | 最小值 | 最大值 |
|------|------|--------|--------|
| TINYINT | 1 | -128 | 127 |
| SMALLINT | 2 | -32768 | 32767 |
| MEDIUMINT | 3 | -8388608 | 8388607 |
| INT | 4 | -2147483648 | 2147483647 |
| BIGINT | 8 | -9223372036854775808 | 9223372036854775807 |

可以使用`UNSIGNED`关键字使整数类型变为无符号，只存储非负值：

```sql
-- 创建表使用无符号整数
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    age TINYINT UNSIGNED,
    score SMALLINT UNSIGNED
);
```

#### 浮点类型

| 类型 | 字节 | 描述 |
|------|------|------|
| FLOAT | 4 | 单精度浮点数 |
| DOUBLE | 8 | 双精度浮点数 |
| DECIMAL(M, D) | 变长 | 定点数，M表示总位数，D表示小数位数 |

```sql
-- 创建表使用浮点类型
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2),  -- 总共10位，其中2位小数
    weight FLOAT
);
```

### 5.2 字符串类型

#### 固定长度字符串

- **CHAR(M)**：固定长度的字符串，长度为M个字符。如果存储的字符串长度小于M，会用空格填充。最大长度为255。

```sql
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    gender CHAR(1)  -- 存储单个字符，如'M'或'F'
);
```

#### 可变长度字符串

- **VARCHAR(M)**：可变长度的字符串，最大长度为M个字符。实际存储长度为字符串的实际长度加1或2字节（用于记录长度）。

```sql
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT
);
```

#### 文本类型

- **TINYTEXT**：最大长度255个字符
- **TEXT**：最大长度65535个字符
- **MEDIUMTEXT**：最大长度16777215个字符
- **LONGTEXT**：最大长度4294967295个字符

```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    summary TEXT,        -- 适用于一般长文本
    content LONGTEXT    -- 适用于长篇文章
);
```

#### 二进制类型

- **BINARY(M)**：固定长度的二进制数据
- **VARBINARY(M)**：可变长度的二进制数据
- **BLOB**：二进制大对象，用于存储图像、音频等二进制数据

### 5.3 日期和时间类型

| 类型 | 格式 | 范围 | 描述 |
|------|------|------|------|
| DATE | 'YYYY-MM-DD' | '1000-01-01' to '9999-12-31' | 日期 |
| TIME | 'HH:MM:SS' | '-838:59:59' to '838:59:59' | 时间 |
| DATETIME | 'YYYY-MM-DD HH:MM:SS' | '1000-01-01 00:00:00' to '9999-12-31 23:59:59' | 日期和时间 |
| TIMESTAMP | 'YYYY-MM-DD HH:MM:SS' | '1970-01-01 00:00:01' UTC to '2038-01-19 03:14:07' UTC | 时间戳 |
| YEAR | YYYY | 1901 to 2155 | 年份 |

```sql
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    event_date DATE,
    event_time TIME,
    created_at DATETIME,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    year YEAR
);
```

### 5.4 枚举和集合类型

#### ENUM类型

ENUM类型用于存储一组预定义的值中的一个值。

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    gender ENUM('男', '女', '其他'),  -- 只能存储这三个值中的一个
    status ENUM('active', 'inactive', 'banned')
);
```

#### SET类型

SET类型用于存储一组预定义的值中的零个或多个值。

```sql
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    features SET('防水', '耐磨', '防震', '轻便')  -- 可以存储多个特性的组合
);
```

## 6. SQL基础

### 6.1 SQL简介

SQL（Structured Query Language，结构化查询语言）是用于管理关系型数据库的标准语言。SQL包括以下几个部分：

- **DQL（Data Query Language）**：数据查询语言，如SELECT
- **DML（Data Manipulation Language）**：数据操作语言，如INSERT、UPDATE、DELETE
- **DDL（Data Definition Language）**：数据定义语言，如CREATE、ALTER、DROP
- **DCL（Data Control Language）**：数据控制语言，如GRANT、REVOKE
- **TCL（Transaction Control Language）**：事务控制语言，如COMMIT、ROLLBACK

### 6.2 创建表（CREATE TABLE）

```sql
-- 基本语法
CREATE TABLE table_name (
    column1 datatype [constraints],
    column2 datatype [constraints],
    ...
    [table_constraints]
);

-- 示例：创建学生表
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_number VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男', '女', '其他'),
    birth_date DATE,
    class_id INT,
    enrollment_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
```

### 6.3 插入数据（INSERT）

```sql
-- 插入完整行
INSERT INTO students (student_number, name, gender, birth_date, class_id)
VALUES ('20230001', '张三', '男', '2005-05-15', 1);

-- 插入部分列
INSERT INTO students (student_number, name, gender)
VALUES ('20230002', '李四', '女');

-- 插入多行
INSERT INTO students (student_number, name, gender, birth_date, class_id)
VALUES 
    ('20230003', '王五', '男', '2004-08-20', 2),
    ('20230004', '赵六', '女', '2005-03-10', 1),
    ('20230005', '钱七', '男', '2004-11-25', 3);
```

### 6.4 查询数据（SELECT）

```sql
-- 基本查询
SELECT * FROM students;

-- 查询指定列
SELECT id, name, gender FROM students;

-- 带条件查询
SELECT * FROM students WHERE gender = '男';

-- 使用AND和OR
SELECT * FROM students WHERE gender = '男' AND class_id = 1;
SELECT * FROM students WHERE gender = '女' OR class_id = 2;

-- 使用IN
SELECT * FROM students WHERE class_id IN (1, 2);

-- 使用BETWEEN
SELECT * FROM students WHERE birth_date BETWEEN '2004-01-01' AND '2005-12-31';

-- 使用LIKE进行模糊查询
SELECT * FROM students WHERE name LIKE '张%';  -- 姓张的学生
SELECT * FROM students WHERE name LIKE '%三';  -- 名字以三结尾的学生

-- 使用ORDER BY排序
SELECT * FROM students ORDER BY name ASC;      -- 按姓名升序
SELECT * FROM students ORDER BY birth_date DESC;  -- 按出生日期降序

-- 使用LIMIT限制结果数量
SELECT * FROM students LIMIT 10;              -- 前10条记录
SELECT * FROM students LIMIT 5, 10;           -- 从第6条开始的10条记录
```

### 6.5 更新数据（UPDATE）

```sql
-- 更新单条记录
UPDATE students 
SET name = '张小三' 
WHERE id = 1;

-- 更新多条记录
UPDATE students 
SET class_id = 2 
WHERE gender = '女';

-- 更新多个字段
UPDATE students 
SET name = '李大四', birth_date = '2004-07-15' 
WHERE id = 2;
```

### 6.6 删除数据（DELETE）

```sql
-- 删除单条记录
DELETE FROM students WHERE id = 3;

-- 删除多条记录
DELETE FROM students WHERE gender = '男' AND class_id = 1;

-- 删除所有记录（保留表结构）
DELETE FROM students;
-- 或者
TRUNCATE TABLE students;
```

### 6.7 修改表结构（ALTER TABLE）

```sql
-- 添加列
ALTER TABLE students ADD COLUMN email VARCHAR(100);

-- 添加列并指定位置
ALTER TABLE students ADD COLUMN phone VARCHAR(20) AFTER name;

-- 删除列
ALTER TABLE students DROP COLUMN email;

-- 修改列定义
ALTER TABLE students MODIFY COLUMN name VARCHAR(100) NOT NULL;

-- 重命名列
ALTER TABLE students CHANGE COLUMN phone telephone VARCHAR(20);

-- 添加主键
ALTER TABLE students ADD PRIMARY KEY (id);

-- 添加外键
ALTER TABLE students ADD CONSTRAINT fk_class 
FOREIGN KEY (class_id) REFERENCES classes(id);

-- 重命名表
ALTER TABLE students RENAME TO student_info;
```

### 6.8 删除表（DROP TABLE）

```sql
-- 删除表
DROP TABLE students;

-- 如果存在则删除
DROP TABLE IF EXISTS students;
```

## 7. 最佳实践

### 7.1 命名规范

- 数据库名：小写字母，使用下划线分隔，如`school_management`
- 表名：小写字母，使用下划线分隔，如`students`、`student_scores`
- 列名：小写字母，使用下划线分隔，如`first_name`、`created_at`
- 索引名：`idx_表名_列名`，如`idx_students_name`
- 外键名：`fk_表名_列名`，如`fk_students_class_id`

### 7.2 设计原则

1. **遵循范式**：通常设计到第三范式，避免数据冗余
2. **合理选择数据类型**：选择最小够用的数据类型，节省存储空间
3. **使用主键**：每个表都应该有主键，通常是自增整数
4. **使用外键**：使用外键维护表之间的关联关系
5. **添加必要约束**：NOT NULL、UNIQUE、CHECK等约束保证数据完整性
6. **添加索引**：为经常查询的列添加索引，提高查询效率

### 7.3 安全建议

1. **使用复杂密码**：root用户和普通用户都应使用复杂密码
2. **最小权限原则**：用户只授予必要的权限
3. **限制远程访问**：只允许必要的IP地址远程连接
4. **定期备份**：定期备份数据库，防止数据丢失
5. **更新版本**：及时更新到最新的安全版本

### 7.4 性能优化建议

1. **合理选择存储引擎**：根据需求选择InnoDB或MyISAM
2. **优化查询**：避免SELECT *，使用EXPLAIN分析查询计划
3. **使用索引**：为WHERE、JOIN、ORDER BY子句中的列创建索引
4. **避免长事务**：长事务会占用大量资源
5. **定期优化表**：使用OPTIMIZE TABLE命令优化表结构

## 总结

本章介绍了MySQL的基础概念、安装配置、基本操作、数据类型、SQL基础和最佳实践。通过本章的学习，您应该能够：

1. 理解MySQL和关系型数据库的基本概念
2. 成功安装和配置MySQL
3. 使用基本命令操作MySQL
4. 了解MySQL的各种数据类型及其应用场景
5. 掌握基本的SQL语句，包括创建表、插入、查询、更新和删除数据
6. 遵循数据库设计和使用的最佳实践

这些基础知识是学习MySQL的起点，下一章我们将深入学习MySQL的高级查询技巧。