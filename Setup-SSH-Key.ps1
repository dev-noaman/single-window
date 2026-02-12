# Setup SSH Key Authentication for VPS
# This script will create an SSH key and copy it to your VPS for passwordless authentication

$VpsHost = "31.220.111.113"
$VpsUser = "root"
$VpsPassword = "Swa@Adel2022"

Write-Host "`n=== SSH Key Setup for VPS ===" -ForegroundColor Cyan
Write-Host "This will enable passwordless SSH authentication`n" -ForegroundColor Yellow

# Check if SSH key already exists
$sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
if (Test-Path $sshKeyPath) {
    Write-Host "[OK] SSH key already exists at: $sshKeyPath" -ForegroundColor Green
} else {
    Write-Host "[INFO] Generating new SSH key..." -ForegroundColor Yellow
    
    # Create .ssh directory if it doesn't exist
    $sshDir = "$env:USERPROFILE\.ssh"
    if (-not (Test-Path $sshDir)) {
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    }
    
    # Generate SSH key (without passphrase for automation)
    ssh-keygen -t rsa -b 4096 -f $sshKeyPath -N '""' -C "deploy-automation"
    
    if (Test-Path $sshKeyPath) {
        Write-Host "[OK] SSH key generated successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to generate SSH key" -ForegroundColor Red
        exit 1
    }
}

# Read the public key
$publicKeyPath = "$sshKeyPath.pub"
if (-not (Test-Path $publicKeyPath)) {
    Write-Host "[ERROR] Public key not found at: $publicKeyPath" -ForegroundColor Red
    exit 1
}

$publicKey = Get-Content $publicKeyPath -Raw

Write-Host "`n[INFO] Copying public key to VPS..." -ForegroundColor Yellow
Write-Host "[INFO] You will be prompted for the VPS password: $VpsPassword" -ForegroundColor Yellow
Write-Host "`nPlease enter the password when prompted...`n" -ForegroundColor Cyan

# Copy the key to VPS using ssh-copy-id equivalent
$command = @"
mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo 'SSH key added successfully'
"@

try {
    $result = ssh -o StrictHostKeyChecking=no "$VpsUser@$VpsHost" $command 2>&1
    
    if ($result -match "SSH key added successfully") {
        Write-Host "`n[SUCCESS] SSH key has been copied to VPS!" -ForegroundColor Green
        Write-Host "[INFO] Testing passwordless connection..." -ForegroundColor Yellow
        
        # Test the connection
        $testResult = ssh -o StrictHostKeyChecking=no "$VpsUser@$VpsHost" "echo 'Connection successful'" 2>&1
        
        if ($testResult -match "Connection successful") {
            Write-Host "[SUCCESS] Passwordless SSH authentication is working!" -ForegroundColor Green
            Write-Host "`nYou can now run Deploy-to-Docker.ps1 without password prompts.`n" -ForegroundColor Cyan
        } else {
            Write-Host "[WARNING] Key was copied but test connection failed" -ForegroundColor Yellow
            Write-Host "Result: $testResult" -ForegroundColor Gray
        }
    } else {
        Write-Host "[ERROR] Failed to copy SSH key" -ForegroundColor Red
        Write-Host "Result: $result" -ForegroundColor Gray
    }
}
catch {
    Write-Host "[ERROR] Failed to connect to VPS: $_" -ForegroundColor Red
    Write-Host "`nMake sure:" -ForegroundColor Yellow
    Write-Host "  1. VPS is accessible at $VpsHost" -ForegroundColor White
    Write-Host "  2. SSH service is running on the VPS" -ForegroundColor White
    Write-Host "  3. Password is correct: $VpsPassword" -ForegroundColor White
}
