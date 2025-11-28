#!/bin/bash

# Spark Shell 启动脚本，集成 Iceberg

# 设置 Spark 版本和 Iceberg 版本
SPARK_VERSION="3.5.0"
ICEBERG_VERSION="1.6.1"
SCALA_VERSION="2.12"

# 启动 Spark Shell 并添加 Iceberg 依赖
spark-shell \
  --packages org.apache.iceberg:iceberg-spark-runtime-${SPARK_VERSION}_${SCALA_VERSION}:${ICEBERG_VERSION} \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
  --conf spark.sql.catalog.spark_catalog.type=hive \
  --conf spark.sql.catalog.local=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.local.type=hadoop \
  --conf spark.sql.catalog.local.warehouse=file:///tmp/iceberg/warehouse \
  --conf spark.sql.defaultCatalog=local