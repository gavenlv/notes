# Start Ansible Environment with Custom Images
Write-Host "=== Starting Ansible with Custom Images ===" -ForegroundColor Cyan
Write-Host "Using images from: zlsmshoqvwt6q1.xuanyuan.dev" -ForegroundColor Yellow

# Stop any existing containers
Write-Host "`nStopping existing containers..." -ForegroundColor Yellow
docker-compose -f ../configs/docker-compose.yml down 2>$null
docker-compose -f ../configs/docker-compose-china.yml down 2>$null
docker-compose -f ../configs/docker-compose-simple.yml down 2>$null
docker-compose -f ../configs/docker-compose-offline.yml down 2>$null

# Start the new environment
Write-Host "`nStarting environment with custom images..." -ForegroundColor Green
Set-Location ../configs

try {
    docker-compose -f docker-compose-custom.yml up -d
    
    Write-Host "`nWaiting for services to start..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
    
    Write-Host "`nChecking container status..." -ForegroundColor Cyan
    docker-compose -f docker-compose-custom.yml ps
    
    Write-Host "`nTesting container connectivity..." -ForegroundColor Yellow
    $containers = @("ansible-control", "ansible-node1", "ansible-node2", "ansible-node3")
    
    foreach ($container in $containers) {
        $status = docker exec $container echo "Container $container is running" 2>$null
        if ($status) {
            Write-Host "✓ $container is healthy" -ForegroundColor Green
        } else {
            Write-Host "✗ $container has issues" -ForegroundColor Red
        }
    }
    
    # Test Ansible installation
    Write-Host "`n=== Testing Ansible Installation ===" -ForegroundColor Cyan
    $ansibleTest = docker exec ansible-control ansible --version 2>$null
    if ($ansibleTest) {
        Write-Host "✓ Ansible is available in control node" -ForegroundColor Green
        Write-Host $ansibleTest[0] -ForegroundColor Gray
    } else {
        Write-Host "⚠ Ansible may need to be installed in control node" -ForegroundColor Yellow
        Write-Host "Installing Ansible in control node..." -ForegroundColor Gray
        docker exec ansible-control bash -c "apt-get update -y && apt-get install -y python3-pip && pip3 install ansible" 2>$null
        
        # Test again
        $ansibleTest2 = docker exec ansible-control ansible --version 2>$null
        if ($ansibleTest2) {
            Write-Host "✓ Ansible installed successfully" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install Ansible" -ForegroundColor Red
        }
    }
    
    # Test SSH connectivity
    Write-Host "`n=== Testing SSH Connectivity ===" -ForegroundColor Cyan
    Write-Host "Testing SSH from control to nodes..." -ForegroundColor Gray
    
    $sshTest = docker exec ansible-control bash -c "apt-get install -y sshpass 2>/dev/null && sshpass -p 'ansible' ssh -o StrictHostKeyChecking=no root@ansible-node1 'echo Node1 SSH OK'" 2>$null
    if ($sshTest -eq "Node1 SSH OK") {
        Write-Host "✓ SSH to node1 working" -ForegroundColor Green
    } else {
        Write-Host "⚠ SSH to node1 may need setup" -ForegroundColor Yellow
    }
    
    Write-Host "`n=== Environment Ready! ===" -ForegroundColor Green
    Write-Host "Your Ansible learning environment is now running with custom images!" -ForegroundColor Cyan
    
    Write-Host "`nQuick Start Commands:" -ForegroundColor Yellow
    Write-Host "1. Enter control node:" -ForegroundColor White
    Write-Host "   docker exec -it ansible-control bash" -ForegroundColor Gray
    
    Write-Host "`n2. Test Ansible:" -ForegroundColor White
    Write-Host "   ansible --version" -ForegroundColor Gray
    Write-Host "   ansible all -m ping" -ForegroundColor Gray
    
    Write-Host "`n3. View inventory:" -ForegroundColor White
    Write-Host "   cat /etc/ansible/hosts" -ForegroundColor Gray
    
    Write-Host "`n4. Run basic commands:" -ForegroundColor White
    Write-Host "   ansible all -m setup" -ForegroundColor Gray
    Write-Host "   ansible all -a 'uname -a'" -ForegroundColor Gray
    
    Write-Host "`nConfiguration files:" -ForegroundColor Cyan
    Write-Host "- Inventory: /etc/ansible/hosts" -ForegroundColor White
    Write-Host "- Config: /etc/ansible/ansible.cfg" -ForegroundColor White
    Write-Host "- Working directory: /ansible-code" -ForegroundColor White
    
    # Create a welcome script in the control node
    $welcomeScript = @"
#!/bin/bash
echo "=================================="
echo "Welcome to Ansible Learning Lab!"
echo "=================================="
echo ""
echo "Available commands:"
echo "  ansible --version          # Check Ansible version"
echo "  ansible all -m ping        # Test connectivity to all nodes"
echo "  ansible all -m setup       # Get system facts from all nodes"
echo "  ansible all -a 'uname -a'  # Run command on all nodes"
echo ""
echo "Available nodes:"
echo "  - ansible-node1 (Ubuntu)"
echo "  - ansible-node2 (CentOS)"
echo "  - ansible-node3 (Alpine)"
echo ""
echo "Credentials: root/ansible or ansible/ansible"
echo "=================================="
"@
    
    $welcomeScript | docker exec -i ansible-control tee /ansible-code/welcome.sh > $null
    docker exec ansible-control chmod +x /ansible-code/welcome.sh
    
    Write-Host "`n💡 Tip: Run 'bash welcome.sh' inside the control node for help!" -ForegroundColor Green
    
}
catch {
    Write-Host "❌ Error starting environment: $($_.Exception.Message)" -ForegroundColor Red
    
    Write-Host "`n🔧 Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check if Docker is running" -ForegroundColor White
    Write-Host "2. Verify custom images are accessible" -ForegroundColor White
    Write-Host "3. Check network connectivity to: zlsmshoqvwt6q1.xuanyuan.dev" -ForegroundColor White
    Write-Host "4. Try fallback: .\offline-setup.ps1" -ForegroundColor White
    
    # Show container logs if available
    Write-Host "`nContainer logs:" -ForegroundColor Gray
    docker-compose -f docker-compose-custom.yml logs --tail=10
}

Set-Location ../scripts 