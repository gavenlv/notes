"""
ETL工作流设计示例
创建DolphinScheduler工作流定义的Python脚本
"""

import json
import datetime

def create_etl_workflow():
    """创建ETL工作流定义"""
    workflow = {
        "globalParams": [
            {
                "prop": "bizDate",
                "direct": "IN",
                "type": "VARCHAR",
                "value": "${system.biz.date}"
            }
        ],
        "tasks": [
            # 1. 数据抽取任务
            {
                "id": "task-1",
                "type": "SHELL",
                "name": "数据抽取",
                "params": {
                    "rawScript": """
#!/bin/bash
# 数据抽取脚本
echo "开始数据抽取，业务日期: ${bizDate}"

# 抽取订单数据
sqoop import \\
  --connect jdbc:mysql://mysql.example.com/orders \\
  --username sqoop_user \\
  --password sqoop_password \\
  --table orders \\
  --where "create_date = '${bizDate}'" \\
  --target-dir /data/orders/${bizDate} \\
  --as-avrodatafile \\
  --m 4

if [ $? -eq 0 ]; then
    echo "数据抽取成功"
    echo "DS_OUTPUT_SYNC_COUNT=1000"
    echo "DS_OUTPUT_SYNC_SIZE=500MB"
    exit 0
else
    echo "数据抽取失败"
    exit 1
fi
""",
                    "localParams": [],
                    "resourceList": []
                },
                "description": "从源系统抽取订单数据",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 3,
                "retryInterval": 3,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": []
            },
            
            # 2. 数据清洗任务
            {
                "id": "task-2",
                "type": "PYTHON",
                "name": "数据清洗",
                "params": {
                    "rawScript": """
import pandas as pd
import numpy as np
import os
import datetime

# 获取参数
biz_date = os.environ.get('bizDate')
input_path = f"/data/orders/{biz_date}"
output_path = f"/data/cleaned_orders/{biz_date}"

# 确保输出目录存在
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# 读取数据
print(f"读取数据: {input_path}")
orders_df = pd.read_avro(f"{input_path}/part-*.avro")

print(f"原始数据行数: {len(orders_df)}")

# 数据清洗
# 1. 去除重复记录
orders_df.drop_duplicates(subset=['order_id'], keep='first', inplace=True)

# 2. 处理缺失值
orders_df['customer_id'].fillna(0, inplace=True)
orders_df['total_amount'].fillna(0, inplace=True)

# 3. 过滤异常值
# 移除金额为负数的订单
orders_df = orders_df[orders_df['total_amount'] >= 0]

# 移除客户ID为异常值的订单
orders_df = orders_df[(orders_df['customer_id'] > 0) & (orders_df['customer_id'] < 1000000)]

# 4. 数据类型转换
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
orders_df['total_amount'] = pd.to_numeric(orders_df['total_amount'])

print(f"清洗后数据行数: {len(orders_df)}")

# 保存清洗后的数据
orders_df.to_csv(output_path + ".csv", index=False)

# 输出统计信息
clean_count = len(orders_df)
removed_count = 1000 - clean_count  # 假设原始为1000行

print(f"清洗完成，共移除 {removed_count} 条记录")
print(f"DS_OUTPUT_CLEAN_COUNT={clean_count}")
print(f"DS_OUTPUT_REMOVED_COUNT={removed_count}")
""",
                    "localParams": [],
                    "resourceList": []
                },
                "description": "清洗抽取的数据",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 3,
                "retryInterval": 3,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": ["task-1"]
            },
            
            # 3. 数据转换任务
            {
                "id": "task-3",
                "type": "SQL",
                "name": "数据转换",
                "params": {
                    "type": "HIVE",
                    "datasource": 1,
                    "sql": """
-- 创建临时表存储清洗后的数据
CREATE TABLE IF NOT EXISTS temp_orders_${bizDate} (
    order_id BIGINT,
    customer_id BIGINT,
    order_date DATE,
    total_amount DECIMAL(10,2),
    status STRING
) STORED AS PARQUET;

-- 加载清洗后的数据
LOAD DATA INPATH '/data/cleaned_orders/${bizDate}.csv'
INTO TABLE temp_orders_${bizDate};

-- 数据转换：添加业务字段
INSERT INTO dw_orders
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount,
    status,
    DATE_FORMAT(order_date, 'yyyy-MM') AS order_month,
    CASE
        WHEN total_amount < 50 THEN '低价值订单'
        WHEN total_amount < 200 THEN '中价值订单'
        ELSE '高价值订单'
    END AS order_value_level
FROM temp_orders_${bizDate};

-- 删除临时表
DROP TABLE IF EXISTS temp_orders_${bizDate};
""",
                    "udfs": "",
                    "showType": "TABLE",
                    "connParams": "",
                    "preStatements": [],
                    "postStatements": []
                },
                "description": "转换数据并加载到数据仓库",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 3,
                "retryInterval": 3,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": ["task-2"]
            },
            
            # 4. 数据质量检查任务
            {
                "id": "task-4",
                "type": "SHELL",
                "name": "数据质量检查",
                "params": {
                    "rawScript": """
#!/bin/bash
# 数据质量检查脚本
bizDate=${bizDate}

echo "开始数据质量检查，业务日期: ${bizDate}"

# 检查数据完整性
echo "1. 检查数据完整性..."
rowCount=$(hive -e "SELECT COUNT(*) FROM dw_orders WHERE DATE_FORMAT(order_date, 'yyyy-MM-dd') = '${bizDate}'")
echo "当日订单数据行数: $rowCount"

if [ $rowCount -lt 100 ]; then
    echo "错误: 当日订单数据行数少于100行"
    echo "DS_OUTPUT_QC_STATUS=FAILED"
    echo "DS_OUTPUT_QC_ERROR=数据行数不足"
    exit 1
fi

# 检查金额字段有效性
echo "2. 检查金额字段有效性..."
invalidAmountCount=$(hive -e "SELECT COUNT(*) FROM dw_orders WHERE DATE_FORMAT(order_date, 'yyyy-MM-dd') = '${bizDate}' AND total_amount < 0")
echo "金额为负数的订单数: $invalidAmountCount"

if [ $invalidAmountCount -gt 0 ]; then
    echo "错误: 发现金额为负数的订单"
    echo "DS_OUTPUT_QC_STATUS=FAILED"
    echo "DS_OUTPUT_QC_ERROR=金额字段异常"
    exit 1
fi

# 检查客户ID有效性
echo "3. 检查客户ID有效性..."
invalidCustomerIdCount=$(hive -e "SELECT COUNT(*) FROM dw_orders WHERE DATE_FORMAT(order_date, 'yyyy-MM-dd') = '${bizDate}' AND (customer_id <= 0 OR customer_id > 1000000)")
echo "客户ID异常的订单数: $invalidCustomerIdCount"

if [ $invalidCustomerIdCount -gt 0 ]; then
    echo "错误: 发现客户ID异常的订单"
    echo "DS_OUTPUT_QC_STATUS=FAILED"
    echo "DS_OUTPUT_QC_ERROR=客户ID异常"
    exit 1
fi

# 检查数据唯一性
echo "4. 检查数据唯一性..."
duplicateOrderCount=$(hive -e "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM dw_orders WHERE DATE_FORMAT(order_date, 'yyyy-MM-dd') = '${bizDate}'")
echo "重复订单数: $duplicateOrderCount"

if [ $duplicateOrderCount -gt 0 ]; then
    echo "警告: 发现重复订单"
    echo "DS_OUTPUT_QC_STATUS=WARNING"
    echo "DS_OUTPUT_QC_ERROR=存在重复订单"
else
    echo "DS_OUTPUT_QC_STATUS=PASSED"
    echo "DS_OUTPUT_QC_ERROR=无"
fi

# 输出质量检查结果
echo "数据质量检查完成"
echo "DS_OUTPUT_TOTAL_COUNT=$rowCount"
echo "DS_OUTPUT_INVALID_AMOUNT_COUNT=$invalidAmountCount"
echo "DS_OUTPUT_INVALID_CUSTOMER_ID_COUNT=$invalidCustomerIdCount"
echo "DS_OUTPUT_DUPLICATE_COUNT=$duplicateOrderCount"
""",
                    "localParams": [],
                    "resourceList": []
                },
                "description": "检查数据质量",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 3,
                "retryInterval": 3,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": ["task-3"]
            },
            
            # 5. 条件分支任务
            {
                "id": "task-5",
                "type": "CONDITIONS",
                "name": "质量检查结果判断",
                "params": {
                    "conditionResult": {
                        "successNode": [
                            "task-6"
                        ],
                        "failedNode": [
                            "task-7"
                        ]
                    },
                    "dependence": {
                        "relation": "AND",
                        "dependTaskList": [
                            {
                                "relation": "AND",
                                "dependItemList": [
                                    {
                                        "regx": "PASSED|WARNING",
                                        "depTaskCode": "task-4",
                                        "status": "SUCCESS"
                                    }
                                ]
                            }
                        ]
                    }
                },
                "description": "根据数据质量检查结果决定后续处理流程",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 0,
                "retryInterval": 1,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": ["task-4"]
            },
            
            # 6. 数据加载任务（质量检查通过）
            {
                "id": "task-6",
                "type": "SQL",
                "name": "数据加载到报表库",
                "params": {
                    "type": "MYSQL",
                    "datasource": 2,
                    "sql": """
-- 从数据仓库加载数据到报表库
INSERT INTO report.orders_report
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount,
    status,
    order_month,
    order_value_level
FROM dw_orders
WHERE DATE_FORMAT(order_date, 'yyyy-MM-dd') = '${bizDate}'
ON DUPLICATE KEY UPDATE
    customer_id = VALUES(customer_id),
    order_date = VALUES(order_date),
    total_amount = VALUES(total_amount),
    status = VALUES(status),
    order_month = VALUES(order_month),
    order_value_level = VALUES(order_value_level);
""",
                    "udfs": "",
                    "showType": "TABLE",
                    "connParams": "",
                    "preStatements": [],
                    "postStatements": []
                },
                "description": "数据加载到报表库",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 3,
                "retryInterval": 3,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": ["task-5"]
            },
            
            # 7. 发送告警任务（质量检查失败）
            {
                "id": "task-7",
                "type": "SHELL",
                "name": "发送质量检查失败告警",
                "params": {
                    "rawScript": """
#!/bin/bash
# 发送告警脚本
bizDate=${bizDate}

echo "发送数据质量检查失败告警，业务日期: ${bizDate}"

# 获取质量检查结果
qcStatus=$(echo ${qcStatus})
qcError=$(echo ${qcError})

# 构建告警消息
message="数据质量检查失败\n"
message+="业务日期: ${bizDate}\n"
message+="检查状态: ${qcStatus}\n"
message+="错误信息: ${qcError}\n"
message+="请检查ETL工作流执行情况"

# 发送钉钉告警
curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN" \\
    -H 'Content-Type: application/json' \\
    -d "{
        \"msgtype\": \"text\",
        \"text\": {
            \"content\": \"${message}\"
        }
    }"

echo "告警已发送"
""",
                    "localParams": [],
                    "resourceList": []
                },
                "description": "发送质量检查失败告警",
                "runFlag": "NORMAL",
                "conditionResult": {
                    "successNode": [
                        ""
                    ],
                    "failedNode": [
                        ""
                    ]
                },
                "dependence": {},
                "maxRetryTimes": 3,
                "retryInterval": 3,
                "timeout": {
                    "strategy": "FAILED",
                    "interval": 1,
                    "enable": false
                },
                "taskInstancePriority": "MEDIUM",
                "workerGroup": "default",
                "preTasks": ["task-5"]
            }
        ],
        "tenantId": 1,
        "timeout": 0
    }
    
    return workflow

def save_workflow_json():
    """保存工作流定义为JSON文件"""
    workflow = create_etl_workflow()
    
    with open('etl_workflow.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)
    
    print("工作流定义已保存为 etl_workflow.json")

if __name__ == "__main__":
    save_workflow_json()