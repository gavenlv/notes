#!/bin/bash

set -e

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
  echo "请指定环境 (dev|staging|prod)"
  exit 1
fi

echo "部署 $ENVIRONMENT 环境..."

cd examples/environments/$ENVIRONMENT
terraform init
terraform plan -out=tfplan
terraform apply tfplan

echo "$ENVIRONMENT 环境部署完成"