# Offline Ansible Learning Environment Setup
Write-Host "=== Offline Ansible Environment Setup ===" -ForegroundColor Cyan

# Stop any running containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker stop $(docker ps -aq) 2>$null
docker rm $(docker ps -aq) 2>$null

# Create a simple setup without package updates
$offlineCompose = @"
version: '3.8'

networks:
  ansible-network:
    driver: bridge

services:
  ansible-control:
    image: python:3.11-slim
    container_name: ansible-control
    hostname: control
    networks:
      - ansible-network
    volumes:
      - ../code:/ansible-code
      - ../examples:/ansible-examples
    working_dir: /ansible-code
    command: >
      bash -c "
      echo 'Setting up Ansible control node...' &&
      pip install ansible --no-warn-script-location &&
      echo 'Ansible installed successfully' &&
      mkdir -p /etc/ansible &&
      echo '[nodes]' > /etc/ansible/hosts &&
      echo 'node1 ansible_host=ansible-node1 ansible_user=root ansible_password=ansible' >> /etc/ansible/hosts &&
      echo 'node2 ansible_host=ansible-node2 ansible_user=root ansible_password=ansible' >> /etc/ansible/hosts &&
      echo '[defaults]' > /etc/ansible/ansible.cfg &&
      echo 'host_key_checking = False' >> /etc/ansible/ansible.cfg &&
      echo 'timeout = 30' >> /etc/ansible/ansible.cfg &&
      apt-get update -y --allow-releaseinfo-change || true &&
      apt-get install -y openssh-client sshpass || true &&
      echo 'Environment ready!' &&
      tail -f /dev/null
      "
    restart: unless-stopped

  node1:
    image: python:3.11-slim
    container_name: ansible-node1
    hostname: node1
    networks:
      - ansible-network
    command: >
      bash -c "
      echo 'Setting up node1...' &&
      apt-get update -y --allow-releaseinfo-change || true &&
      apt-get install -y openssh-server sudo || true &&
      mkdir -p /var/run/sshd || true &&
      echo 'root:ansible' | chpasswd &&
      sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config 2>/dev/null || true &&
      sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config 2>/dev/null || true &&
      ssh-keygen -A 2>/dev/null || true &&
      useradd -m ansible 2>/dev/null || true &&
      echo 'ansible:ansible' | chpasswd &&
      echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 2>/dev/null || true &&
      echo 'Node1 ready!' &&
      /usr/sbin/sshd -D -e 2>/dev/null || sleep infinity
      "
    restart: unless-stopped

  node2:
    image: python:3.11-slim
    container_name: ansible-node2  
    hostname: node2
    networks:
      - ansible-network
    command: >
      bash -c "
      echo 'Setting up node2...' &&
      apt-get update -y --allow-releaseinfo-change || true &&
      apt-get install -y openssh-server sudo || true &&
      mkdir -p /var/run/sshd || true &&
      echo 'root:ansible' | chpasswd &&
      sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config 2>/dev/null || true &&
      sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config 2>/dev/null || true &&
      ssh-keygen -A 2>/dev/null || true &&
      useradd -m ansible 2>/dev/null || true &&
      echo 'ansible:ansible' | chpasswd &&
      echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers 2>/dev/null || true &&
      echo 'Node2 ready!' &&
      /usr/sbin/sshd -D -e 2>/dev/null || sleep infinity
      "
    restart: unless-stopped
"@

# Write the offline compose file
$offlineCompose | Out-File -FilePath "../configs/docker-compose-offline.yml" -Encoding UTF8

Write-Host "Starting offline environment..." -ForegroundColor Yellow
Set-Location ../configs
docker-compose -f docker-compose-offline.yml up -d

Write-Host "Waiting for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 45

Write-Host "`nChecking container status..." -ForegroundColor Cyan
docker-compose -f docker-compose-offline.yml ps

Write-Host "`nTesting connectivity..." -ForegroundColor Yellow
$containers = @("ansible-control", "ansible-node1", "ansible-node2")

foreach ($container in $containers) {
    $status = docker exec $container echo "Container $container is running" 2>$null
    if ($status) {
        Write-Host "✓ $container is healthy" -ForegroundColor Green
    } else {
        Write-Host "✗ $container has issues" -ForegroundColor Red
    }
}

Write-Host "`n=== Testing Ansible Setup ===" -ForegroundColor Cyan

# Test if Ansible is installed
Write-Host "Testing Ansible installation..." -ForegroundColor Yellow
$ansibleVersion = docker exec ansible-control ansible --version 2>$null
if ($ansibleVersion) {
    Write-Host "✓ Ansible is installed" -ForegroundColor Green
    Write-Host $ansibleVersion[0] -ForegroundColor Gray
} else {
    Write-Host "✗ Ansible installation failed" -ForegroundColor Red
}

Write-Host "`n=== Environment Ready ===" -ForegroundColor Green
Write-Host "Enter the control node with:" -ForegroundColor Cyan
Write-Host "docker exec -it ansible-control bash" -ForegroundColor White

Write-Host "`nQuick test commands:" -ForegroundColor Cyan
Write-Host "ansible --version" -ForegroundColor White
Write-Host "ansible all -m ping" -ForegroundColor White
Write-Host "ansible all -m setup" -ForegroundColor White

Write-Host "`nInventory file location: /etc/ansible/hosts" -ForegroundColor Cyan
Write-Host "Config file location: /etc/ansible/ansible.cfg" -ForegroundColor Cyan

# Create a quick test script
$testScript = @"
#!/bin/bash
echo "=== Ansible Quick Test ==="
echo "Ansible Version:"
ansible --version

echo ""
echo "Testing connectivity to all nodes:"
ansible all -m ping

echo ""
echo "Getting system info from all nodes:"
ansible all -m setup -a "filter=ansible_os_family"
"@

$testScript | Out-File -FilePath "../code/test-ansible.sh" -Encoding UTF8

Write-Host "`nCreated test script: /ansible-code/test-ansible.sh" -ForegroundColor Green
Write-Host "Run it inside the control node with: bash test-ansible.sh" -ForegroundColor White

Set-Location ../scripts 