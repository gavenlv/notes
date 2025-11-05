#!/bin/bash

# Airflow Backup Script
# This script performs a complete backup of Airflow including:
# - Database backup
# - DAG files backup
# - Configuration files backup
# - Logs backup (optional)

set -e  # Exit on any error

# Configuration
BACKUP_DIR="/backups/airflow"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="airflow_backup_$DATE"
LOG_FILE="$BACKUP_DIR/$BACKUP_NAME.log"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Start backup process
log "Starting Airflow backup process"

# 1. Database backup
log "Backing up Airflow database"
pg_dump -h postgres -U airflow -d airflow > $BACKUP_DIR/${BACKUP_NAME}_database.sql
log "Database backup completed"

# 2. DAG files backup
log "Backing up DAG files"
tar -czf $BACKUP_DIR/${BACKUP_NAME}_dags.tar.gz /opt/airflow/dags
log "DAG files backup completed"

# 3. Configuration files backup
log "Backing up configuration files"
tar -czf $BACKUP_DIR/${BACKUP_NAME}_config.tar.gz /opt/airflow/config
log "Configuration files backup completed"

# 4. Plugins backup
log "Backing up plugins"
tar -czf $BACKUP_DIR/${BACKUP_NAME}_plugins.tar.gz /opt/airflow/plugins
log "Plugins backup completed"

# 5. Logs backup (optional - can be large)
log "Backing up logs"
tar -czf $BACKUP_DIR/${BACKUP_NAME}_logs.tar.gz /opt/airflow/logs
log "Logs backup completed"

# Create a checksum for verification
log "Creating checksums"
sha256sum $BACKUP_DIR/${BACKUP_NAME}_* > $BACKUP_DIR/${BACKUP_NAME}_checksums.txt
log "Checksums created"

# Compress all backups into a single archive
log "Creating final compressed backup"
tar -czf $BACKUP_DIR/${BACKUP_NAME}.tar.gz -C $BACKUP_DIR ${BACKUP_NAME}_*
log "Final compressed backup created"

# Clean up individual files
rm $BACKUP_DIR/${BACKUP_NAME}_*.sql
rm $BACKUP_DIR/${BACKUP_NAME}_*.tar.gz
rm $BACKUP_DIR/${BACKUP_NAME}_checksums.txt

# Verify backup integrity
log "Verifying backup integrity"
tar -tzf $BACKUP_DIR/${BACKUP_NAME}.tar.gz > /dev/null
if [ $? -eq 0 ]; then
    log "Backup integrity verified successfully"
else
    log "ERROR: Backup integrity check failed"
    exit 1
fi

# Upload to remote storage (example with AWS S3)
# Uncomment and configure the following lines if using AWS S3
# log "Uploading backup to S3"
# aws s3 cp $BACKUP_DIR/${BACKUP_NAME}.tar.gz s3://your-backup-bucket/airflow/
# if [ $? -eq 0 ]; then
#     log "Backup uploaded to S3 successfully"
# else
#     log "ERROR: Failed to upload backup to S3"
#     exit 1
# fi

log "Airflow backup process completed successfully"
log "Backup location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"