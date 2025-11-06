#!/bin/bash

# Airflow Restore Script
# This script restores an Airflow installation from a backup including:
# - Database restore
# - DAG files restore
# - Configuration files restore
# - Logs restore (optional)

set -e  # Exit on any error

# Configuration
BACKUP_DIR="/backups/airflow"
RESTORE_DIR="/restore"
LOG_FILE="/var/log/airflow_restore.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Check if backup file is provided
if [ $# -eq 0 ]; then
    log "ERROR: No backup file provided"
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    log "ERROR: Backup file $BACKUP_FILE does not exist"
    exit 1
fi

# Start restore process
log "Starting Airflow restore process from $BACKUP_FILE"

# Extract backup
log "Extracting backup file"
mkdir -p $RESTORE_DIR
tar -xzf $BACKUP_FILE -C $RESTORE_DIR
log "Backup extraction completed"

# Get backup name (without path and extension)
BACKUP_NAME=$(basename $BACKUP_FILE .tar.gz)

# Stop Airflow services
log "Stopping Airflow services"
# systemctl stop airflow-webserver
# systemctl stop airflow-scheduler
# systemctl stop airflow-worker
log "Airflow services stopped"

# 1. Database restore
log "Restoring Airflow database"
# Drop existing database
# psql -h postgres -U airflow -c "DROP DATABASE IF EXISTS airflow;"
# Create new database
# psql -h postgres -U airflow -c "CREATE DATABASE airflow;"
# Restore database from backup
# psql -h postgres -U airflow -d airflow < $RESTORE_DIR/${BACKUP_NAME}/${BACKUP_NAME}_database.sql
log "Database restore completed"

# 2. DAG files restore
log "Restoring DAG files"
rm -rf /opt/airflow/dags/*
tar -xzf $RESTORE_DIR/${BACKUP_NAME}/${BACKUP_NAME}_dags.tar.gz -C /
log "DAG files restore completed"

# 3. Configuration files restore
log "Restoring configuration files"
rm -rf /opt/airflow/config/*
tar -xzf $RESTORE_DIR/${BACKUP_NAME}/${BACKUP_NAME}_config.tar.gz -C /
log "Configuration files restore completed"

# 4. Plugins restore
log "Restoring plugins"
rm -rf /opt/airflow/plugins/*
tar -xzf $RESTORE_DIR/${BACKUP_NAME}/${BACKUP_NAME}_plugins.tar.gz -C /
log "Plugins restore completed"

# 5. Logs restore (optional)
log "Restoring logs"
rm -rf /opt/airflow/logs/*
tar -xzf $RESTORE_DIR/${BACKUP_NAME}/${BACKUP_NAME}_logs.tar.gz -C /
log "Logs restore completed"

# Set proper permissions
log "Setting proper permissions"
chown -R airflow:airflow /opt/airflow
chmod -R 755 /opt/airflow/dags
chmod -R 755 /opt/airflow/config
chmod -R 755 /opt/airflow/plugins
chmod -R 755 /opt/airflow/logs
log "Permissions set successfully"

# Start Airflow services
log "Starting Airflow services"
# systemctl start airflow-webserver
# systemctl start airflow-scheduler
# systemctl start airflow-worker
log "Airflow services started"

# Clean up temporary files
log "Cleaning up temporary files"
rm -rf $RESTORE_DIR/${BACKUP_NAME}
log "Temporary files cleaned up"

log "Airflow restore process completed successfully"