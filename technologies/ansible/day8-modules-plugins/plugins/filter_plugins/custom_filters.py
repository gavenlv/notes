# -*- coding: utf-8 -*-

"""
Custom filter plugins for Ansible
Provides additional filters for data manipulation and formatting
"""

import re
import json
import base64
from datetime import datetime, timedelta
from ansible.errors import AnsibleFilterError

def to_title_case(value):
    """Convert string to title case"""
    if not isinstance(value, str):
        raise AnsibleFilterError("to_title_case filter requires a string")
    return value.title()

def extract_domain(email):
    """Extract domain from email address"""
    if not isinstance(email, str):
        raise AnsibleFilterError("extract_domain filter requires a string")
    
    if '@' not in email:
        raise AnsibleFilterError("Invalid email format")
    
    return email.split('@')[1]

def format_bytes(bytes_value):
    """Format bytes into human readable format"""
    try:
        bytes_value = float(bytes_value)
    except (ValueError, TypeError):
        raise AnsibleFilterError("format_bytes filter requires a numeric value")
    
    if bytes_value < 0:
        raise AnsibleFilterError("format_bytes filter requires a positive value")
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} EB"

def json_query_extended(data, query):
    """Extended JSON query using JMESPath"""
    try:
        import jmespath
        return jmespath.search(query, data)
    except ImportError:
        raise AnsibleFilterError("jmespath library is required for json_query_extended filter")
    except Exception as e:
        raise AnsibleFilterError(f"JSON query failed: {str(e)}")

def regex_findall_named(value, pattern):
    """Find all matches with named groups"""
    if not isinstance(value, str):
        raise AnsibleFilterError("regex_findall_named filter requires a string")
    
    try:
        matches = re.finditer(pattern, value)
        results = []
        for match in matches:
            if match.groupdict():
                results.append(match.groupdict())
            else:
                results.append(match.groups())
        return results
    except re.error as e:
        raise AnsibleFilterError(f"Invalid regex pattern: {str(e)}")

def base64_encode_safe(value):
    """Base64 encode with URL-safe characters"""
    if not isinstance(value, str):
        raise AnsibleFilterError("base64_encode_safe filter requires a string")
    
    try:
        encoded = base64.urlsafe_b64encode(value.encode('utf-8'))
        return encoded.decode('utf-8')
    except Exception as e:
        raise AnsibleFilterError(f"Base64 encoding failed: {str(e)}")

def base64_decode_safe(value):
    """Base64 decode with URL-safe characters"""
    if not isinstance(value, str):
        raise AnsibleFilterError("base64_decode_safe filter requires a string")
    
    try:
        # Add padding if necessary
        missing_padding = len(value) % 4
        if missing_padding:
            value += '=' * (4 - missing_padding)
        
        decoded = base64.urlsafe_b64decode(value.encode('utf-8'))
        return decoded.decode('utf-8')
    except Exception as e:
        raise AnsibleFilterError(f"Base64 decoding failed: {str(e)}")

def calculate_age(date_string, format='%Y-%m-%d'):
    """Calculate age in days from date string"""
    try:
        date_obj = datetime.strptime(date_string, format)
        today = datetime.now()
        age = today - date_obj
        return age.days
    except ValueError as e:
        raise AnsibleFilterError(f"Date parsing failed: {str(e)}")

def add_days(date_string, days, format='%Y-%m-%d'):
    """Add days to a date string"""
    try:
        date_obj = datetime.strptime(date_string, format)
        new_date = date_obj + timedelta(days=int(days))
        return new_date.strftime(format)
    except (ValueError, TypeError) as e:
        raise AnsibleFilterError(f"Date calculation failed: {str(e)}")

def flatten_dict(data, separator='.'):
    """Flatten nested dictionary"""
    if not isinstance(data, dict):
        raise AnsibleFilterError("flatten_dict filter requires a dictionary")
    
    def _flatten(obj, parent_key=''):
        items = []
        for key, value in obj.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(_flatten(value, new_key).items())
            else:
                items.append((new_key, value))
        return dict(items)
    
    return _flatten(data)

def unflatten_dict(data, separator='.'):
    """Unflatten dictionary"""
    if not isinstance(data, dict):
        raise AnsibleFilterError("unflatten_dict filter requires a dictionary")
    
    result = {}
    for key, value in data.items():
        keys = key.split(separator)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    
    return result

def group_by_key(items, key):
    """Group list of dictionaries by a key"""
    if not isinstance(items, list):
        raise AnsibleFilterError("group_by_key filter requires a list")
    
    groups = {}
    for item in items:
        if not isinstance(item, dict):
            raise AnsibleFilterError("group_by_key filter requires a list of dictionaries")
        
        group_key = item.get(key)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(item)
    
    return groups

def sort_by_key(items, key, reverse=False):
    """Sort list of dictionaries by a key"""
    if not isinstance(items, list):
        raise AnsibleFilterError("sort_by_key filter requires a list")
    
    try:
        return sorted(items, key=lambda x: x.get(key, ''), reverse=bool(reverse))
    except Exception as e:
        raise AnsibleFilterError(f"Sorting failed: {str(e)}")

def mask_sensitive(value, mask_char='*', show_last=4):
    """Mask sensitive information"""
    if not isinstance(value, str):
        raise AnsibleFilterError("mask_sensitive filter requires a string")
    
    if len(value) <= show_last:
        return mask_char * len(value)
    
    masked_length = len(value) - show_last
    return mask_char * masked_length + value[-show_last:]

def validate_email(email):
    """Validate email format"""
    if not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_ip(ip):
    """Validate IP address format"""
    if not isinstance(ip, str):
        return False
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    # IPv6 pattern (simplified)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    return bool(re.match(ipv6_pattern, ip))

def generate_password(length=12, include_special=True):
    """Generate random password"""
    import random
    import string
    
    try:
        length = int(length)
        if length < 4:
            raise AnsibleFilterError("Password length must be at least 4")
        
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += '!@#$%^&*'
        
        password = ''.join(random.choice(chars) for _ in range(length))
        return password
    except ValueError:
        raise AnsibleFilterError("Invalid password length")

class FilterModule(object):
    """Custom filter module"""
    
    def filters(self):
        return {
            # String manipulation
            'to_title_case': to_title_case,
            'extract_domain': extract_domain,
            'mask_sensitive': mask_sensitive,
            
            # Data formatting
            'format_bytes': format_bytes,
            'base64_encode_safe': base64_encode_safe,
            'base64_decode_safe': base64_decode_safe,
            
            # Date/time operations
            'calculate_age': calculate_age,
            'add_days': add_days,
            
            # Dictionary operations
            'flatten_dict': flatten_dict,
            'unflatten_dict': unflatten_dict,
            
            # List operations
            'group_by_key': group_by_key,
            'sort_by_key': sort_by_key,
            
            # Advanced queries
            'json_query_extended': json_query_extended,
            'regex_findall_named': regex_findall_named,
            
            # Validation
            'validate_email': validate_email,
            'validate_ip': validate_ip,
            
            # Utilities
            'generate_password': generate_password
        } 