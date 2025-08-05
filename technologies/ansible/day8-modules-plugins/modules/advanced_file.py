#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Learning Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
---
module: advanced_file
short_description: Advanced file management with backup and validation
description:
    - Provides advanced file management capabilities
    - Supports template rendering and content validation
    - Includes backup functionality and permission management
    - Validates file content before applying changes
version_added: "1.0.0"
author:
    - "Ansible Learning Project"
options:
    path:
        description:
            - Path to the file to manage
        type: path
        required: true
    content:
        description:
            - Content to write to the file
            - Mutually exclusive with template
        type: str
        required: false
    template:
        description:
            - Path to Jinja2 template file
            - Mutually exclusive with content
        type: path
        required: false
    backup:
        description:
            - Create backup of existing file before modification
        type: bool
        default: false
    mode:
        description:
            - File permissions in octal format
        type: str
        required: false
    owner:
        description:
            - Name of user that should own the file
        type: str
        required: false
    group:
        description:
            - Name of group that should own the file
        type: str
        required: false
    state:
        description:
            - Desired state of the file
        type: str
        choices: ['present', 'absent', 'touch']
        default: present
    validate:
        description:
            - Command to validate file content
            - Use %s as placeholder for file path
        type: str
        required: false
    variables:
        description:
            - Variables to pass to template rendering
        type: dict
        default: {}
requirements:
    - python >= 3.6
notes:
    - Requires Jinja2 for template rendering
    - Backup files are created with timestamp suffix
seealso:
    - module: ansible.builtin.file
    - module: ansible.builtin.template
'''

EXAMPLES = '''
# Create a simple file
- name: Create configuration file
  advanced_file:
    path: /etc/myapp/config.conf
    content: |
      server_name = {{ ansible_hostname }}
      port = 8080
      debug = false
    mode: '0644'
    owner: root
    group: root
    backup: true

# Use template with variables
- name: Create from template
  advanced_file:
    path: /etc/nginx/sites-available/mysite
    template: templates/nginx.conf.j2
    variables:
      server_name: example.com
      port: 80
      ssl_enabled: true
    mode: '0644'
    validate: 'nginx -t -c %s'
    backup: true

# Remove file
- name: Remove temporary file
  advanced_file:
    path: /tmp/temp_file
    state: absent

# Touch file (create empty)
- name: Create empty file
  advanced_file:
    path: /var/log/myapp.log
    state: touch
    mode: '0644'
    owner: myapp
    group: myapp
'''

RETURN = '''
path:
    description: Path to the managed file
    returned: always
    type: str
    sample: /etc/myapp/config.conf
changed:
    description: Whether the file was modified
    returned: always
    type: bool
    sample: true
backup_file:
    description: Path to backup file if created
    returned: when backup is true and file existed
    type: str
    sample: /etc/myapp/config.conf.backup.20231201_143022
msg:
    description: Human readable message about the operation
    returned: always
    type: str
    sample: File /etc/myapp/config.conf updated successfully
size:
    description: Size of the file in bytes
    returned: when state is present
    type: int
    sample: 1024
checksum:
    description: SHA1 checksum of the file
    returned: when state is present
    type: str
    sample: da39a3ee5e6b4b0d3255bfef95601890afd80709
'''

import os
import shutil
import tempfile
import subprocess
import hashlib
import pwd
import grp
import stat
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native

def get_file_checksum(path):
    """Calculate SHA1 checksum of file"""
    if not os.path.exists(path):
        return None
    
    hash_sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

def backup_file(path):
    """Create backup of existing file"""
    if not os.path.exists(path):
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{path}.backup.{timestamp}"
    
    try:
        shutil.copy2(path, backup_path)
        return backup_path
    except IOError as e:
        raise Exception(f"Failed to create backup: {to_native(e)}")

def validate_file(path, validate_cmd):
    """Validate file using provided command"""
    if not validate_cmd:
        return True, ""
    
    cmd = validate_cmd.replace('%s', path)
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def render_template(template_path, variables):
    """Render Jinja2 template"""
    try:
        from jinja2 import Template, FileSystemLoader, Environment
        
        # Get template directory and filename
        template_dir = os.path.dirname(template_path)
        template_name = os.path.basename(template_path)
        
        # Create Jinja2 environment
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        
        # Render template
        return template.render(variables)
        
    except ImportError:
        raise Exception("Jinja2 is required for template rendering")
    except Exception as e:
        raise Exception(f"Template rendering failed: {to_native(e)}")

def set_file_attributes(path, mode=None, owner=None, group=None):
    """Set file attributes (permissions, owner, group)"""
    changed = False
    
    # Set permissions
    if mode:
        try:
            current_mode = oct(stat.S_IMODE(os.stat(path).st_mode))
            desired_mode = oct(int(mode, 8))
            if current_mode != desired_mode:
                os.chmod(path, int(mode, 8))
                changed = True
        except (OSError, ValueError) as e:
            raise Exception(f"Failed to set file mode: {to_native(e)}")
    
    # Set owner and group
    if owner or group:
        try:
            current_stat = os.stat(path)
            uid = pwd.getpwnam(owner).pw_uid if owner else current_stat.st_uid
            gid = grp.getgrnam(group).gr_gid if group else current_stat.st_gid
            
            if uid != current_stat.st_uid or gid != current_stat.st_gid:
                os.chown(path, uid, gid)
                changed = True
        except (KeyError, OSError) as e:
            raise Exception(f"Failed to set file ownership: {to_native(e)}")
    
    return changed

def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            content=dict(type='str'),
            template=dict(type='path'),
            backup=dict(type='bool', default=False),
            mode=dict(type='str'),
            owner=dict(type='str'),
            group=dict(type='str'),
            state=dict(type='str', default='present', 
                      choices=['present', 'absent', 'touch']),
            validate=dict(type='str'),
            variables=dict(type='dict', default={})
        ),
        mutually_exclusive=[['content', 'template']],
        supports_check_mode=True
    )
    
    # Get parameters
    path = module.params['path']
    content = module.params['content']
    template = module.params['template']
    backup = module.params['backup']
    mode = module.params['mode']
    owner = module.params['owner']
    group = module.params['group']
    state = module.params['state']
    validate_cmd = module.params['validate']
    variables = module.params['variables']
    
    # Initialize result
    result = dict(
        changed=False,
        path=path
    )
    
    # Check if file exists
    file_exists = os.path.exists(path)
    
    try:
        if state == 'absent':
            if file_exists:
                if not module.check_mode:
                    os.remove(path)
                result['changed'] = True
                result['msg'] = f"File {path} removed"
            else:
                result['msg'] = f"File {path} does not exist"
        
        elif state == 'touch':
            if not file_exists:
                if not module.check_mode:
                    # Create empty file
                    open(path, 'a').close()
                    # Set attributes
                    if mode or owner or group:
                        set_file_attributes(path, mode, owner, group)
                result['changed'] = True
                result['msg'] = f"File {path} created"
            else:
                # File exists, just update attributes if needed
                if not module.check_mode:
                    attr_changed = set_file_attributes(path, mode, owner, group)
                    if attr_changed:
                        result['changed'] = True
                        result['msg'] = f"File {path} attributes updated"
                    else:
                        result['msg'] = f"File {path} already exists"
        
        elif state == 'present':
            # Create backup if requested and file exists
            backup_path = None
            if backup and file_exists:
                if not module.check_mode:
                    backup_path = backup_file(path)
                    result['backup_file'] = backup_path
            
            # Prepare content
            if template:
                # Add common variables
                template_vars = variables.copy()
                template_vars.update({
                    'ansible_hostname': os.uname().nodename,
                    'ansible_date_time': datetime.now().isoformat()
                })
                file_content = render_template(template, template_vars)
            elif content:
                file_content = content
            else:
                file_content = ""
            
            # Check if content needs to be updated
            needs_update = True
            if file_exists:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                    needs_update = current_content != file_content
                except (IOError, UnicodeDecodeError):
                    needs_update = True
            
            if needs_update:
                if not module.check_mode:
                    # Write content to temporary file first
                    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(path))
                    try:
                        with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        
                        # Validate temporary file
                        if validate_cmd:
                            valid, error = validate_file(temp_path, validate_cmd)
                            if not valid:
                                os.unlink(temp_path)
                                # Restore backup if validation fails
                                if backup_path and os.path.exists(backup_path):
                                    shutil.copy2(backup_path, path)
                                module.fail_json(msg=f"Validation failed: {error}")
                        
                        # Move temporary file to final location
                        shutil.move(temp_path, path)
                        
                        # Set file attributes
                        set_file_attributes(path, mode, owner, group)
                        
                    except Exception as e:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        raise e
                
                result['changed'] = True
                result['msg'] = f"File {path} updated"
            else:
                # Content is the same, but check attributes
                if not module.check_mode:
                    attr_changed = set_file_attributes(path, mode, owner, group)
                    if attr_changed:
                        result['changed'] = True
                        result['msg'] = f"File {path} attributes updated"
                    else:
                        result['msg'] = f"File {path} is already up to date"
            
            # Add file information to result
            if not module.check_mode and os.path.exists(path):
                file_stat = os.stat(path)
                result['size'] = file_stat.st_size
                result['checksum'] = get_file_checksum(path)
    
    except Exception as e:
        module.fail_json(msg=f"Operation failed: {to_native(e)}")
    
    module.exit_json(**result)

if __name__ == '__main__':
    main() 