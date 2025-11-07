#!/bin/bash

# Grafana 告警系统配置实验脚本
# 适用于 Linux/macOS 系统

echo "=== Grafana 告警系统配置实验 ==="

# 配置邮件通知渠道
echo "配置邮件通知渠道..."
curl -X POST \
  http://admin:admin@localhost:3000/api/alert-notifications \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Email Alerts",
    "type": "email",
    "isDefault": true,
    "settings": {
      "addresses": "admin@example.com"
    },
    "secureFields": []
  }' | jq .

# 配置Slack通知渠道
echo "配置Slack通知渠道..."
curl -X POST \
  http://admin:admin@localhost:3000/api/alert-notifications \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Slack Alerts",
    "type": "slack",
    "isDefault": false,
    "settings": {
      "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
      "channel": "#alerts",
      "username": "Grafana"
    },
    "secureFields": ["url"]
  }' | jq .

# 配置Webhook通知渠道
echo "配置Webhook通知渠道..."
curl -X POST \
  http://admin:admin@localhost:3000/api/alert-notifications \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Webhook Alerts",
    "type": "webhook",
    "isDefault": false,
    "settings": {
      "url": "http://localhost:8080/webhook",
      "httpMethod": "POST"
    },
    "secureFields": ["url"]
  }' | jq .

# 创建CPU使用率告警规则
echo "创建CPU使用率告警规则..."
curl -X POST \
  http://admin:admin@localhost:3000/api/provisioning/alert-rules \
  -H 'Content-Type: application/json' \
  -d '{
    "orgID": 1,
    "folderID": 0,
    "ruleGroup": "System Alerts",
    "title": "CPU Usage High",
    "condition": "A",
    "data": [
      {
        "refId": "A",
        "queryType": "",
        "relativeTimeRange": {
          "from": 300,
          "to": 0
        },
        "datasourceUid": "testdata",
        "model": {
          "expr": "up",
          "intervalMs": 1000,
          "refId": "A",
          "hide": false,
          "type": "alertgraphql"
        }
      }
    ],
    "noDataState": "NoData",
    "execErrState": "Alerting",
    "for": "1m",
    "annotations": {
      "description": "CPU使用率超过80%"
    },
    "labels": {
      "severity": "warning",
      "team": "operations"
    }
  }' | jq .

# 创建内存使用率告警规则
echo "创建内存使用率告警规则..."
curl -X POST \
  http://admin:admin@localhost:3000/api/provisioning/alert-rules \
  -H 'Content-Type: application/json' \
  -d '{
    "orgID": 1,
    "folderID": 0,
    "ruleGroup": "System Alerts",
    "title": "Memory Usage High",
    "condition": "A",
    "data": [
      {
        "refId": "A",
        "queryType": "",
        "relativeTimeRange": {
          "from": 300,
          "to": 0
        },
        "datasourceUid": "testdata",
        "model": {
          "expr": "up",
          "intervalMs": 1000,
          "refId": "A",
          "hide": false,
          "type": "alertgraphql"
        }
      }
    ],
    "noDataState": "NoData",
    "execErrState": "Alerting",
    "for": "2m",
    "annotations": {
      "description": "内存使用率超过90%"
    },
    "labels": {
      "severity": "critical",
      "team": "operations"
    }
  }' | jq .

# 创建告警静默规则(测试用)
echo "创建告警静默规则..."
SILENCE_END=$(date -d "+30 minutes" +%s)
curl -X POST \
  http://admin:admin@localhost:3000/api/alertmanager/grafana/api/v2/silences \
  -H 'Content-Type: application/json' \
  -d "{
    \"comment\": \"维护窗口期间静默所有告警\",
    \"startsAt\": \"$(date -Iseconds)\",
    \"endsAt\": \"$(date -Iseconds -d \"+30 minutes\")\",
    \"matchers\": [
      {
        \"name\": \"team\",
        \"value\": \"operations\",
        \"isRegex\": false
      }
    ],
    \"createdBy\": \"admin\"
  }" | jq .

echo "实验完成！"
echo "请访问 http://localhost:3000/alerting 查看 告警规则和通知渠道"
echo "注意：测试前请确保通知渠道的配置信息（如邮件地址、Slack Webhook URL）正确"