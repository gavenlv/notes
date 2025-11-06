#!/usr/bin/python
# Custom Ansible Module Example

from ansible.module_utils.basic import AnsibleModule
import json
import os

def main():
    # 定义模块参数
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True),
            content=dict(type='str', required=False),
            state=dict(type='str', default='file', choices=['file', 'directory', 'absent']),
            owner=dict(type='str', required=False),
            group=dict(type='str', required=False),
            mode=dict(type='str', required=False),
        ),
        supports_check_mode=True
    )

    # 获取参数
    path = module.params['path']
    content = module.params['content']
    state = module.params['state']
    owner = module.params['owner']
    group = module.params['group']
    mode = module.params['mode']

    # 检查模式下直接返回
    if module.check_mode:
        module.exit_json(changed=True)

    # 根据状态执行操作
    if state == 'absent':
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    os.rmdir(path)
                module.exit_json(changed=True, msg=f"Removed {path}")
            except Exception as e:
                module.fail_json(msg=f"Failed to remove {path}: {str(e)}")
        else:
            module.exit_json(changed=False, msg=f"{path} does not exist")

    elif state == 'file':
        if not os.path.exists(path):
            try:
                # 创建文件
                with open(path, 'w') as f:
                    if content:
                        f.write(content)
                
                # 设置权限
                if mode:
                    os.chmod(path, int(mode, 8))
                
                # 设置所有者
                if owner or group:
                    import pwd
                    import grp
                    uid = pwd.getpwnam(owner).pw_uid if owner else -1
                    gid = grp.getgrnam(group).gr_gid if group else -1
                    os.chown(path, uid, gid)
                
                module.exit_json(changed=True, msg=f"Created file {path}")
            except Exception as e:
                module.fail_json(msg=f"Failed to create file {path}: {str(e)}")
        else:
            # 检查文件内容是否需要更新
            try:
                with open(path, 'r') as f:
                    current_content = f.read()
                
                if content and current_content != content:
                    with open(path, 'w') as f:
                        f.write(content)
                    module.exit_json(changed=True, msg=f"Updated file {path}")
                else:
                    module.exit_json(changed=False, msg=f"File {path} already exists with correct content")
            except Exception as e:
                module.fail_json(msg=f"Failed to check/update file {path}: {str(e)}")

    elif state == 'directory':
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                
                # 设置权限
                if mode:
                    os.chmod(path, int(mode, 8))
                
                # 设置所有者
                if owner or group:
                    import pwd
                    import grp
                    uid = pwd.getpwnam(owner).pw_uid if owner else -1
                    gid = grp.getgrnam(group).gr_gid if group else -1
                    os.chown(path, uid, gid)
                
                module.exit_json(changed=True, msg=f"Created directory {path}")
            except Exception as e:
                module.fail_json(msg=f"Failed to create directory {path}: {str(e)}")
        else:
            module.exit_json(changed=False, msg=f"Directory {path} already exists")

if __name__ == '__main__':
    main()