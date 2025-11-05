#!/usr/bin/env python3
"""
Sample Application for Ansible CI/CD Integration Demo
"""

import os
import sys
import logging
from flask import Flask, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/myapp/app.log')
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config['NAME'] = os.environ.get('APP_NAME', 'MyApp')
app.config['VERSION'] = os.environ.get('APP_VERSION', '1.0.0')
app.config['PORT'] = int(os.environ.get('APP_PORT', 8080))

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': f'Welcome to {app.config["NAME"]}!',
        'version': app.config['VERSION'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/info')
def info():
    """Application info endpoint"""
    return jsonify({
        'name': app.config['NAME'],
        'version': app.config['VERSION'],
        'port': app.config['PORT'],
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })

if __name__ == '__main__':
    logger.info(f"Starting {app.config['NAME']} v{app.config['VERSION']} on port {app.config['PORT']}")
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=False
    )