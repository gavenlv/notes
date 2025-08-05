# Quick Fix for Ansible Day 1 Network Issues
Write-Host "=== Quick Fix for Network Issues ===" -ForegroundColor Cyan

# Stop any running containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f ../configs/docker-compose.yml down 2>$null

# Use lightweight approach with existing images
Write-Host "Creating simple environment..." -ForegroundColor Yellow

# Create temporary docker-compose with minimal config
$simpleCompose = @"
version: '3.8'

networks:
  ansible-network:
    driver: bridge

services:
  ansible-control:
    image: ubuntu:22.04
    container_name: ansible-control
    hostname: control
    networks:
      - ansible-network
    volumes:
      - ../code:/ansible-code
      - ../examples:/ansible-examples
      - ./ansible.cfg:/tmp/ansible.cfg
      - ./inventory.ini:/tmp/inventory.ini
    working_dir: /ansible-code
    command: >
      bash -c "
      apt-get update -y && 
      apt-get install -y python3 python3-pip openssh-client sshpass curl &&
      pip3 install ansible &&
      cp /tmp/ansible.cfg /etc/ansible/ansible.cfg 2>/dev/null || true &&
      cp /tmp/inventory.ini /etc/ansible/hosts 2>/dev/null || true &&
      tail -f /dev/null
      "
    restart: unless-stopped

  node1:
    image: ubuntu:22.04
    container_name: ansible-node1
    hostname: node1
    networks:
      - ansible-network
    command: >
      bash -c "
      apt-get update -y &&
      apt-get install -y openssh-server python3 sudo &&
      mkdir -p /var/run/sshd &&
      echo 'root:ansible' | chpasswd &&
      sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config &&
      sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config &&
      useradd -m ansible &&
      echo 'ansible:ansible' | chpasswd &&
      echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers &&
      /usr/sbin/sshd -D
      "
    restart: unless-stopped

  node2:
    image: ubuntu:22.04
    container_name: ansible-node2  
    hostname: node2
    networks:
      - ansible-network
    command: >
      bash -c "
      apt-get update -y &&
      apt-get install -y openssh-server python3 sudo &&
      mkdir -p /var/run/sshd &&
      echo 'root:ansible' | chpasswd &&
      sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config &&
      sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config &&
      useradd -m ansible &&
      echo 'ansible:ansible' | chpasswd &&
      echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers &&
      /usr/sbin/sshd -D
      "
    restart: unless-stopped
"@

# Write the simple compose file
$simpleCompose | Out-File -FilePath "../configs/docker-compose-simple.yml" -Encoding UTF8

Write-Host "Starting simple environment..." -ForegroundColor Yellow
Set-Location ../configs
docker-compose -f docker-compose-simple.yml up -d

Write-Host "Waiting for services to start..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host "`nChecking container status..." -ForegroundColor Cyan
docker-compose -f docker-compose-simple.yml ps

Write-Host "`nTesting connections..." -ForegroundColor Yellow
$containers = @("ansible-control", "ansible-node1", "ansible-node2")

foreach ($container in $containers) {
    $status = docker exec $container echo "OK" 2>$null
    if ($status -eq "OK") {
        Write-Host "✓ $container is running" -ForegroundColor Green
    } else {
        Write-Host "✗ $container has issues" -ForegroundColor Red
    }
}

Write-Host "`n=== Environment Ready ===" -ForegroundColor Green
Write-Host "Enter the control node with:" -ForegroundColor Cyan
Write-Host "docker exec -it ansible-control bash" -ForegroundColor White
Write-Host "`nOnce inside, test Ansible with:" -ForegroundColor Cyan
Write-Host "ansible --version" -ForegroundColor White
Write-Host "ansible all -m ping" -ForegroundColor White

Set-Location ../scripts 