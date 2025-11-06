#!/bin/bash

# 示例脚本：展示如何使用Airflow CLI管理连接
# 注意：此脚本仅用于演示目的，在实际使用中需要根据具体环境调整

echo "=== Airflow 连接管理示例 ==="

# 1. 列出所有连接
echo "1. 列出所有连接:"
airflow connections list

# 2. 创建PostgreSQL连接示例
echo -e "\n2. 创建PostgreSQL连接:"
airflow connections add 'example_postgres' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-port 5432 \
    --conn-schema 'example_db' \
    --conn-login 'example_user' \
    --conn-password 'example_password'

# 3. 创建HTTP连接示例（用于API）
echo -e "\n3. 创建HTTP连接:"
airflow connections add 'example_api' \
    --conn-type 'http' \
    --conn-host 'api.example.com' \
    --conn-port 443 \
    --conn-extra '{"Authorization": "Bearer YOUR_API_TOKEN"}'

# 4. 查看特定连接
echo -e "\n4. 查看刚创建的连接:"
airflow connections get 'example_postgres'
airflow connections get 'example_api'

# 5. 更新连接
echo -e "\n5. 更新PostgreSQL连接:"
airflow connections update 'example_postgres' \
    --conn-host 'newhost.example.com' \
    --conn-port 5433

# 6. 删除连接
echo -e "\n6. 删除连接:"
airflow connections delete 'example_postgres'
airflow connections delete 'example_api'

echo -e "\n=== 连接管理示例完成 ==="