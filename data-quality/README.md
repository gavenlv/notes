# Data Quality Framework for ClickHouse

This folder contains a comprehensive data quality framework for ClickHouse that allows you to define data quality rules in YAML format.

## Overview

The data quality framework provides:
- YAML-based rule definitions
- Automated data quality checks with total fail count reporting (no percentages)
- Customizable validation rules
- Comprehensive reporting in summary and detail formats
- Integration with ClickHouse monitoring
- Python scripts suitable for Jenkins execution

## Key Features

- **No Percentage Calculations**: Checks fail if any violations are found, reporting total fail counts
- **Jenkins-Ready**: Python scripts designed for CI/CD pipeline integration
- **Reporting Only**: Focus on printing check results in summary and detail formats
- **Referential Integrity**: Check table relationships (column X in table A refers to column Y in table B)
- **Case Sensitivity**: Validate case consistency in text data
- **Enhanced Data Range**: Comprehensive range validation for numeric fields

## Structure

```
data-quality/
├── rules/                    # YAML rule definitions
│   ├── completeness/         # Data completeness rules
│   ├── accuracy/            # Data accuracy rules
│   ├── consistency/         # Data consistency rules
│   └── timeliness/          # Data timeliness rules
├── configs/                 # Configuration files
│   └── data-quality-config.yml
├── scripts/                 # Execution scripts
│   ├── run-quality-checks.py
│   └── generate-report.py
├── examples/                # Example implementations
│   ├── sample-rules.yml
│   ├── demo-checks.sql
│   ├── referential-integrity-example.yml
│   ├── case-sensitivity-example.yml
│   └── data-range-example.yml
└── templates/               # Rule templates
    ├── completeness-template.yml
    ├── accuracy-template.yml
    ├── consistency-template.yml
    └── case-sensitivity-template.yml
```

## Usage

1. Define your data quality rules in YAML format
2. Configure the data quality framework
3. Run automated quality checks using Python
4. Review printed results in summary and detail formats

## Rule Types

- **Completeness**: Check for missing or null values (fails if any found)
- **Accuracy**: Validate data against business rules and ranges
- **Consistency**: Ensure data consistency across tables including referential integrity
- **Timeliness**: Verify data freshness and update frequency
- **Case Sensitivity**: Validate case consistency in text fields

## Getting Started

### Prerequisites

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure ClickHouse is running and accessible

### Usage

1. **Run with command line arguments:**
   ```bash
   python scripts/run-quality-checks.py --rules examples/sample-rules.yml
   ```

2. **Run the example script:**
   ```bash
   python run-example.py
   ```

3. **Generate reports from existing results:**
   ```bash
   python scripts/generate-report.py --results reports/quality_report_YYYYMMDD_HHMMSS.json
   ```

### Examples

See the examples in the `examples/` folder for sample implementations including:
- Basic completeness checks
- Referential integrity validation
- Case sensitivity checking
- Enhanced data range validation 