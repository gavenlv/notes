#!/bin/bash

set -e

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
  echo "请指定环境 (dev|staging|prod)"
  exit 1
fi

echo "销毁 $ENVIRONMENT 环境..."

cd examples/environments/$ENVIRONMENT
terraform destroy -auto-approve

echo "$ENVIRONMENT 环境已销毁"