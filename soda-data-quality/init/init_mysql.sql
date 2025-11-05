-- Create data_quality database
CREATE DATABASE IF NOT EXISTS data_quality;

USE data_quality;

-- Create data quality scans table
CREATE TABLE IF NOT EXISTS data_quality_scans (
    id VARCHAR(36) PRIMARY KEY,
    scan_time DATETIME NOT NULL,
    environment VARCHAR(50) NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    scan_results JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Create data quality checks table
CREATE TABLE IF NOT EXISTS data_quality_checks (
    id VARCHAR(36) PRIMARY KEY,
    scan_id VARCHAR(36) NOT NULL,
    check_name VARCHAR(255) NOT NULL,
    check_type VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    result JSON NOT NULL,
    duration FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES data_quality_scans(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create data quality logs table
CREATE TABLE IF NOT EXISTS data_quality_logs (
    id VARCHAR(36) PRIMARY KEY,
    scan_id VARCHAR(36) NOT NULL,
    log_level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES data_quality_scans(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create data quality metrics table
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id VARCHAR(36) PRIMARY KEY,
    scan_id VARCHAR(36) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES data_quality_scans(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create indexes for better query performance
CREATE INDEX idx_scans_environment ON data_quality_scans(environment);
CREATE INDEX idx_scans_data_source ON data_quality_scans(data_source);
CREATE INDEX idx_scans_scan_time ON data_quality_scans(scan_time);

CREATE INDEX idx_checks_scan_id ON data_quality_checks(scan_id);
CREATE INDEX idx_checks_status ON data_quality_checks(status);
CREATE INDEX idx_checks_check_type ON data_quality_checks(check_type);

CREATE INDEX idx_logs_scan_id ON data_quality_logs(scan_id);
CREATE INDEX idx_logs_log_level ON data_quality_logs(log_level);
CREATE INDEX idx_logs_timestamp ON data_quality_logs(timestamp);

CREATE INDEX idx_metrics_scan_id ON data_quality_metrics(scan_id);
CREATE INDEX idx_metrics_metric_name ON data_quality_metrics(metric_name);
CREATE INDEX idx_metrics_metric_type ON data_quality_metrics(metric_type);