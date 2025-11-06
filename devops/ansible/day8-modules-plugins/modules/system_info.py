#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: system_info
short_description: Collect detailed system information
description:
    - Collects comprehensive system information
    - Supports filtering by information type
    - Provides performance monitoring data
    - Returns structured data for analysis
version_added: "1.0.0"
author:
    - "Ansible Learning Project"
options:
    info_type:
        description:
            - Type of information to collect
        type: str
        choices: ['all', 'hardware', 'network', 'storage', 'processes', 'services']
        default: all
    format:
        description:
            - Output format for the information
        type: str
        choices: ['json', 'yaml', 'table']
        default: json
    top_processes:
        description:
            - Number of top processes to return
        type: int
        default: 10
    include_services:
        description:
            - Include running services information
        type: bool
        default: false
requirements:
    - python >= 3.6
    - psutil (for detailed system information)
'''

EXAMPLES = '''
# Collect all system information
- name: Get complete system info
  system_info:
    info_type: all
  register: system_data

# Get only hardware information
- name: Get hardware info
  system_info:
    info_type: hardware
    format: json

# Get top 5 processes
- name: Get top processes
  system_info:
    info_type: processes
    top_processes: 5

# Include services information
- name: Get system info with services
  system_info:
    info_type: all
    include_services: true
'''

RETURN = '''
system_info:
    description: Collected system information
    returned: always
    type: dict
    contains:
        basic:
            description: Basic system information
            type: dict
            sample:
                hostname: "server01"
                platform: "Linux-5.4.0-42-generic-x86_64-with-glibc2.31"
                python_version: "3.8.5"
                uptime_seconds: 86400
        hardware:
            description: Hardware information
            type: dict
            sample:
                cpu_count: 4
                cpu_percent: 15.2
                memory_total: 8589934592
                memory_available: 6442450944
                memory_percent: 25.0
        network:
            description: Network information
            type: dict
            sample:
                interfaces: {}
                connections: 45
        storage:
            description: Storage information
            type: dict
            sample:
                disk_usage: {}
        processes:
            description: Process information
            type: dict
            sample:
                top_processes: []
        services:
            description: Service information
            type: dict
            sample:
                running_services: []
'''

import platform
import os
import time
import json
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule

def get_basic_info():
    """Get basic system information"""
    try:
        import psutil
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time
    except ImportError:
        uptime = 0
    
    return {
        'hostname': platform.node(),
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'uptime_seconds': int(uptime),
        'current_time': datetime.now().isoformat()
    }

def get_hardware_info():
    """Get hardware information"""
    try:
        import psutil
        
        # CPU information
        cpu_info = {
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': dict(psutil.cpu_freq()._asdict()) if psutil.cpu_freq() else None
        }
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'cached': getattr(memory, 'cached', 0),
            'buffers': getattr(memory, 'buffers', 0)
        }
        
        # Swap information
        swap = psutil.swap_memory()
        swap_info = {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent
        }
        
        return {
            'cpu': cpu_info,
            'memory': memory_info,
            'swap': swap_info
        }
    except ImportError:
        return {'error': 'psutil module not available'}

def get_network_info():
    """Get network information"""
    try:
        import psutil
        
        # Network interfaces
        interfaces = {}
        for interface, addrs in psutil.net_if_addrs().items():
            interfaces[interface] = []
            for addr in addrs:
                interfaces[interface].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
        
        # Network I/O statistics
        net_io = psutil.net_io_counters(pernic=True)
        io_stats = {}
        for interface, stats in net_io.items():
            io_stats[interface] = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errin': stats.errin,
                'errout': stats.errout,
                'dropin': stats.dropin,
                'dropout': stats.dropout
            }
        
        # Network connections
        connections = len(psutil.net_connections())
        
        return {
            'interfaces': interfaces,
            'io_counters': io_stats,
            'connections_count': connections
        }
    except ImportError:
        return {'error': 'psutil module not available'}

def get_storage_info():
    """Get storage information"""
    try:
        import psutil
        
        # Disk partitions
        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                })
            except PermissionError:
                # Skip partitions we can't access
                continue
        
        # Disk I/O statistics
        disk_io = psutil.disk_io_counters(perdisk=True)
        io_stats = {}
        for disk, stats in disk_io.items():
            io_stats[disk] = {
                'read_count': stats.read_count,
                'write_count': stats.write_count,
                'read_bytes': stats.read_bytes,
                'write_bytes': stats.write_bytes,
                'read_time': stats.read_time,
                'write_time': stats.write_time
            }
        
        return {
            'partitions': partitions,
            'io_counters': io_stats
        }
    except ImportError:
        return {'error': 'psutil module not available'}

def get_process_info(top_n=10):
    """Get process information"""
    try:
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                pinfo['cpu_percent'] = proc.cpu_percent()
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage and get top N
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        top_processes = processes[:top_n]
        
        return {
            'total_processes': len(processes),
            'top_processes': top_processes,
            'process_count_by_status': {
                status: len([p for p in processes if p.get('status') == status])
                for status in ['running', 'sleeping', 'disk-sleep', 'stopped', 'zombie']
            }
        }
    except ImportError:
        return {'error': 'psutil module not available'}

def get_service_info():
    """Get service information (Linux systemd)"""
    try:
        import subprocess
        
        # Try to get systemd services
        try:
            result = subprocess.run(
                ['systemctl', 'list-units', '--type=service', '--no-pager', '--no-legend'],
                capture_output=True,
                text=True,
                check=True
            )
            
            services = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        services.append({
                            'name': parts[0],
                            'load': parts[1],
                            'active': parts[2],
                            'sub': parts[3],
                            'description': ' '.join(parts[4:]) if len(parts) > 4 else ''
                        })
            
            return {
                'services': services,
                'total_services': len(services),
                'active_services': len([s for s in services if s['active'] == 'active'])
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {'error': 'systemctl not available or not accessible'}
    except ImportError:
        return {'error': 'subprocess module not available'}

def format_output(data, format_type):
    """Format output according to specified format"""
    if format_type == 'json':
        return data
    elif format_type == 'yaml':
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False)
        except ImportError:
            return data  # Fall back to JSON if yaml not available
    elif format_type == 'table':
        # Simple table format for basic info
        if isinstance(data, dict):
            table = []
            for key, value in data.items():
                if isinstance(value, dict):
                    table.append(f"{key}:")
                    for subkey, subvalue in value.items():
                        table.append(f"  {subkey}: {subvalue}")
                else:
                    table.append(f"{key}: {value}")
            return '\n'.join(table)
        return str(data)
    else:
        return data

def main():
    module = AnsibleModule(
        argument_spec=dict(
            info_type=dict(
                type='str',
                choices=['all', 'hardware', 'network', 'storage', 'processes', 'services'],
                default='all'
            ),
            format=dict(
                type='str',
                choices=['json', 'yaml', 'table'],
                default='json'
            ),
            top_processes=dict(type='int', default=10),
            include_services=dict(type='bool', default=False)
        ),
        supports_check_mode=True
    )
    
    info_type = module.params['info_type']
    output_format = module.params['format']
    top_processes = module.params['top_processes']
    include_services = module.params['include_services']
    
    result = {
        'changed': False,
        'system_info': {}
    }
    
    # Always collect basic information
    result['system_info']['basic'] = get_basic_info()
    
    # Collect specific information based on type
    if info_type in ['all', 'hardware']:
        result['system_info']['hardware'] = get_hardware_info()
    
    if info_type in ['all', 'network']:
        result['system_info']['network'] = get_network_info()
    
    if info_type in ['all', 'storage']:
        result['system_info']['storage'] = get_storage_info()
    
    if info_type in ['all', 'processes']:
        result['system_info']['processes'] = get_process_info(top_processes)
    
    if info_type in ['all', 'services'] or include_services:
        result['system_info']['services'] = get_service_info()
    
    # Format output if requested
    if output_format != 'json':
        result['formatted_output'] = format_output(result['system_info'], output_format)
    
    # Add collection metadata
    result['system_info']['collection_info'] = {
        'timestamp': datetime.now().isoformat(),
        'info_type': info_type,
        'format': output_format
    }
    
    module.exit_json(**result)

if __name__ == '__main__':
    main() 