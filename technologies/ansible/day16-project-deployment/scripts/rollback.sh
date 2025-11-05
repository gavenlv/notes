#!/bin/bash

# Rollback Script for MyApp

set -e  # Exit on any error

# Default values
ENVIRONMENT="development"
VERSION=""

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -e, --environment ENV   Set environment (development|staging|production) [default: development]"
    echo "  -v, --version VERSION   Set version to rollback to"
    echo "  -h, --help              Display this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "Error: Invalid environment. Must be development, staging, or production."
    exit 1
fi

echo "Starting rollback for $ENVIRONMENT environment..."

# Determine inventory file
INVENTORY_FILE="inventory/$ENVIRONMENT"

# Check if inventory file exists
if [[ ! -f "$INVENTORY_FILE" ]]; then
    echo "Error: Inventory file $INVENTORY_FILE not found."
    exit 1
fi

# Build extra vars
EXTRA_VARS=""
if [[ -n "$VERSION" ]]; then
    EXTRA_VARS="--extra-vars rollback_version=$VERSION"
fi

# Run Ansible rollback playbook
echo "Running rollback playbook..."
ansible-playbook -i "$INVENTORY_FILE" playbooks/rollback.yml $EXTRA_VARS

if [[ $? -eq 0 ]]; then
    echo "Rollback completed successfully!"
else
    echo "Rollback failed!"
    exit 1
fi