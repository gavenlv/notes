# Simple Ansible Environment Startup
param(
    [switch]$Force
)

Write-Host "=== Simple Ansible Environment Setup ===" -ForegroundColor Cyan

if ($Force) {
    Write-Host "Force mode: Cleaning all containers..." -ForegroundColor Yellow
    docker stop $(docker ps -aq) 2>$null
    docker rm $(docker ps -aq) 2>$null
}

# Create the simplest possible setup
Write-Host "Creating minimal Ansible environment..." -ForegroundColor Green

# Simple docker-compose content
$simpleSetup = @"
version: '3.8'
services:
  control:
    image: python:3.11
    container_name: ansible-control
    working_dir: /work
    volumes:
      - ../code:/work
      - ../examples:/examples
    command: >
      bash -c "
      pip install ansible &&
      apt-get update && apt-get install -y openssh-client sshpass &&
      echo '[test]' > /etc/ansible/hosts &&
      echo 'localhost ansible_connection=local' >> /etc/ansible/hosts &&
      echo '[defaults]' > /etc/ansible/ansible.cfg &&
      echo 'host_key_checking = False' >> /etc/ansible/ansible.cfg &&
      echo 'Ansible ready! Try: ansible localhost -m ping' &&
      tail -f /dev/null
      "
    restart: unless-stopped
"@

# Write and start
Set-Location ../configs
$simpleSetup | Out-File -FilePath "docker-compose-simple-test.yml" -Encoding UTF8

Write-Host "Starting control node..." -ForegroundColor Yellow
docker-compose -f docker-compose-simple-test.yml up -d

Write-Host "Waiting for setup..." -ForegroundColor Gray
Start-Sleep -Seconds 20

Write-Host "`nTesting Ansible..." -ForegroundColor Cyan
$result = docker exec ansible-control ansible --version 2>$null
if ($result) {
    Write-Host "✓ Ansible is working!" -ForegroundColor Green
    Write-Host $result[0] -ForegroundColor Gray
    
    Write-Host "`nTesting localhost connection..." -ForegroundColor Yellow
    $pingTest = docker exec ansible-control ansible localhost -m ping 2>$null
    if ($pingTest -match "SUCCESS") {
        Write-Host "✓ Ansible can connect to localhost!" -ForegroundColor Green
    }
} else {
    Write-Host "✗ Ansible setup failed" -ForegroundColor Red
}

Write-Host "`n=== Quick Start ===" -ForegroundColor Green
Write-Host "Enter the environment:" -ForegroundColor White
Write-Host "  docker exec -it ansible-control bash" -ForegroundColor Gray
Write-Host "`nTest commands:" -ForegroundColor White
Write-Host "  ansible --version" -ForegroundColor Gray
Write-Host "  ansible localhost -m ping" -ForegroundColor Gray
Write-Host "  ansible localhost -m setup" -ForegroundColor Gray

Write-Host "`n💡 This is a minimal setup for learning Ansible basics!" -ForegroundColor Yellow

Set-Location ../scripts 