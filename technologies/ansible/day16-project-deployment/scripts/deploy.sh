#!/bin/bash

# Deployment Script for MyApp

set -e  # Exit on any error

# Default values
ENVIRONMENT="development"
TAG=""

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -e, --environment ENV   Set environment (development|staging|production) [default: development]"
    echo "  -t, --tag TAG          Set deployment tag/version"
    echo "  -h, --help             Display this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
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

echo "Starting deployment to $ENVIRONMENT environment..."

# Determine inventory file
INVENTORY_FILE="inventory/$ENVIRONMENT"

# Check if inventory file exists
if [[ ! -f "$INVENTORY_FILE" ]]; then
    echo "Error: Inventory file $INVENTORY_FILE not found."
    exit 1
fi

# Build extra vars
EXTRA_VARS=""
if [[ -n "$TAG" ]]; then
    EXTRA_VARS="--extra-vars app_version=$TAG"
fi

# Run Ansible playbook
echo "Running deployment playbook..."
ansible-playbook -i "$INVENTORY_FILE" playbooks/site.yml $EXTRA_VARS

if [[ $? -eq 0 ]]; then
    echo "Deployment completed successfully!"
else
    echo "Deployment failed!"
    exit 1
fi