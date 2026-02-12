<#
.SYNOPSIS
    Remote VPS deployment script for Docker and host services (API-php, API-node, API-CR, Portal, SW_GSHEET, SW_CODES, officernd-bff)

.DESCRIPTION
    This script automates remote VPS deployment of all services.
    Docker services: cleanup, archive (ZIP), transfer, extraction, Docker build, container startup.
    Host services: archive, transfer, extraction, npm install/build, PM2 process management.

.PARAMETER TestCode
    Activity code to test the APIs with after deployment (default: "013001")

.PARAMETER SkipTests
    Skip the API testing step after deployment

.PARAMETER ForceRebuild
    Force rebuild of Docker images without using cache

.EXAMPLE
    .\Deploy-to-Docker.ps1
    Deploy to VPS with default settings and test with code 013001

.EXAMPLE
    .\Deploy-to-Docker.ps1 -TestCode "2005172" -ForceRebuild
    Deploy to VPS with specific test code and force rebuild

.EXAMPLE
    .\Deploy-to-Docker.ps1 -SkipTests -ForceRebuild
    Deploy to VPS with force rebuild and skip tests
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$TestCode = "013001",

    [Parameter(Mandatory=$false)]
    [switch]$SkipTests,

    [Parameter(Mandatory=$false)]
    [switch]$ForceRebuild
)

# Script configuration
$ErrorActionPreference = "Stop"
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = $null

# VPS Configuration (reads from environment variables, prompts if not set)
$VpsHost = if ($env:VPS_HOST) { $env:VPS_HOST } else { Read-Host "Enter VPS host" }
$VpsUser = if ($env:VPS_USER) { $env:VPS_USER } else { Read-Host "Enter VPS username" }
$VpsPassword = if ($env:VPS_PASS) { $env:VPS_PASS } else { Read-Host "Enter VPS password" }
$VpsPath = "/root/scrapers"
$VpsHostKey = if ($env:VPS_HOST_KEY) { $env:VPS_HOST_KEY } else { "ssh-ed25519 255 SHA256:br5ADDgHrTODqLVxk/qlDPK0qjNr8+awdUExclqzbN0" }

# Color configuration for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Step = "Magenta"
}

# Service definitions
$Services = @(
    @{
        Name = "API-php"
        ContainerName = "API-PHP"
        Port = 8080
        Endpoint = "/SW_GSHEET.php"
        Type = "API"
    },
    @{
        Name = "API-node"
        ContainerName = "API-NODE"
        Port = 8081
        Endpoint = "/scrape"
        Type = "API"
    },
    @{
        Name = "API-CR"
        ContainerName = "API-CR"
        Port = 8086
        Endpoint = "/health"
        Type = "API"
    },
    @{
        Name = "Portal"
        ContainerName = "PORTAL"
        Port = 8082
        Endpoint = "/"
        Type = "Web"
    },
    @{
        Name = "scrape-sw-gsheet"
        ContainerName = "SW_GSHEET"
        Port = $null
        Endpoint = $null
        Type = "Background"
    },
    @{
        Name = "scrape-sw-codes"
        ContainerName = "SW_CODES_PYTHON"
        Port = 8084
        Endpoint = "/"
        Type = "Web"
    },
    @{
        Name = "officernd-api"
        LocalDir = "officernd"
        RemoteDir = "officernd"
        ContainerName = $null
        Port = 8087
        Endpoint = "/health"
        Type = "HostService"
        Runtime = "python"
        ProcessName = "officernd-api"
        StartCommand = "uvicorn api.main:app --host 0.0.0.0 --port 8087"
        ExcludeDirs = @("bff", "data", "__pycache__")
        PreserveEnv = $true
        EnvPath = "config/.env"
        DefaultEnv = @"
OFFICERND_ORG_SLUG=arafat-business-centers
OFFICERND_CLIENT_ID=CHANGE_ME
OFFICERND_CLIENT_SECRET=CHANGE_ME
OFFICERND_GRANT_TYPE=client_credentials
OFFICERND_SCOPE=flex.billing.payments.read flex.community.members.read flex.community.companies.read flex.space.locations.read flex.space.resources.read flex.settings.webhooks.read
DATABASE_URL=postgresql://officernd_user:OfficerndPass2024@localhost:5432/officernd
LOCAL_API_KEY=dev-api-key-change-in-production
LOCAL_API_PORT=8087
"@
    },
    @{
        Name = "officernd-bff"
        LocalDir = "officernd\bff"
        RemoteDir = "officernd/bff"
        ContainerName = $null
        Port = 8088
        Endpoint = "/api/officernd/status"
        Type = "HostService"
        ProcessName = "officernd-bff"
    }
)

#region Helper Functions

function Write-Log {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    
    Write-Host $logMessage -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-Log "Validating prerequisites..." -Color $Colors.Step
    
    # Check for SSH tools
    $pscpAvailable = Get-Command pscp -ErrorAction SilentlyContinue
    $plinkAvailable = Get-Command plink -ErrorAction SilentlyContinue
    $sshAvailable = Get-Command ssh -ErrorAction SilentlyContinue
    
    if (-not ($pscpAvailable -and $plinkAvailable) -and -not $sshAvailable) {
        Write-Log "ERROR: Neither PuTTY tools nor OpenSSH found. Please install one of them." -Color $Colors.Error
        return $false
    }
    
    if ($pscpAvailable -and $plinkAvailable) {
        Write-Log "Using PuTTY tools for SSH/SCP" -Color $Colors.Success
    } else {
        Write-Log "Using OpenSSH for SSH/SCP" -Color $Colors.Success
    }
    
    # Validate service directories
    foreach ($service in $Services) {
        if ($service.Name -eq "SW_GSHEET") { continue } # Optional
        $localDir = if ($service.LocalDir) { $service.LocalDir } else { $service.Name }
        $servicePath = Join-Path $ScriptPath $localDir
        if (-not (Test-Path $servicePath)) {
            if ($service.Type -eq "HostService") {
                Write-Log "Host service directory not found (will skip): $servicePath" -Color $Colors.Warning
                continue
            }
            Write-Log "ERROR: Service directory not found: $servicePath" -Color $Colors.Error
            return $false
        }
    }
    
    Write-Log "Prerequisites validated successfully" -Color $Colors.Success
    return $true
}

function Test-SshConnection {
    Write-Log "Testing SSH connection to VPS..." -Color $Colors.Info
    
    $plinkAvailable = Get-Command plink -ErrorAction SilentlyContinue
    
    try {
        if ($plinkAvailable) {
            $testCommand = 'plink -pw "' + $VpsPassword + '" -batch -hostkey "' + $VpsHostKey + '" ' + $VpsUser + '@' + $VpsHost + ' "echo OK"'
        }
        else {
            $testCommand = 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 ' + $VpsUser + '@' + $VpsHost + ' "echo OK"'
        }
        
        $result = Invoke-Expression $testCommand 2>&1 | Out-String
        
        # Check if "OK" is in the output (ignore warnings about host keys)
        if ($result -match "OK") {
            Write-Log "SSH connection test successful" -Color $Colors.Success
            return $true
        }
        else {
            # Filter out common SSH warnings that don't indicate failure
            $filteredResult = $result -split "`n" | Where-Object { 
                $_ -notmatch "Warning: Permanently added" -and 
                $_ -notmatch "Pseudo-terminal will not be allocated" -and
                $_.Trim() -ne ""
            } | Select-Object -First 3
            
            if ($filteredResult) {
                Write-Log "SSH connection test failed: $($filteredResult -join '; ')" -Color $Colors.Error
            } else {
                Write-Log "SSH connection test failed: No response received" -Color $Colors.Error
            }
            return $false
        }
    }
    catch {
        # Filter the error message to remove SSH warnings
        $errorMsg = $_.Exception.Message
        if ($errorMsg -notmatch "Warning: Permanently added") {
            Write-Log "Error testing SSH connection: $errorMsg" -Color $Colors.Error
        } else {
            Write-Log "SSH connection established (with host key warning)" -Color $Colors.Success
            return $true
        }
        return $false
    }
}

function Initialize-RemoteEnvironment {
    Write-Log "Initializing remote environment..." -Color $Colors.Step
    
    try {
        # Check if unzip is installed
        Write-Log "Checking for unzip on VPS..." -Color $Colors.Info
        $unzipCheck = Invoke-VpsCommand -Command 'which unzip 2>/dev/null || echo "not found"' -ReturnOutput
        
        if (-not $unzipCheck -or $unzipCheck -match "not found") {
            Write-Log "unzip not found, installing..." -Color $Colors.Warning
            Invoke-VpsCommand -Command "apt-get update -qq && apt-get install -y unzip" | Out-Null
            Write-Log "unzip installed successfully" -Color $Colors.Success
        } else {
            Write-Log "unzip is available" -Color $Colors.Success
        }

        # Check for Node.js and PM2 if any HostService is defined
        $hasHostServices = $Services | Where-Object { $_.Type -eq "HostService" }
        if ($hasHostServices) {
            Write-Log "Checking Node.js for host services..." -Color $Colors.Info
            $nodeCheck = Invoke-VpsCommand -Command 'node --version 2>/dev/null || echo "not found"' -ReturnOutput
            if ($nodeCheck -match "not found") {
                Write-Log "Node.js not found, installing via NodeSource..." -Color $Colors.Warning
                Invoke-VpsCommand -Command "(curl -fsSL https://deb.nodesource.com/setup_20.x | bash -) 2>&1 && apt-get install -y nodejs 2>&1" | Out-Null
                Write-Log "Node.js installed successfully" -Color $Colors.Success
            } else {
                Write-Log "Node.js is available ($($nodeCheck.Trim()))" -Color $Colors.Success
            }

            Write-Log "Checking PM2 for host services..." -Color $Colors.Info
            $pm2Check = Invoke-VpsCommand -Command 'which pm2 2>/dev/null || echo "not found"' -ReturnOutput
            if ($pm2Check -match "not found") {
                Write-Log "PM2 not found, installing globally..." -Color $Colors.Warning
                Invoke-VpsCommand -Command "npm install -g pm2 2>&1 && (pm2 startup 2>/dev/null ; true)" | Out-Null
                Write-Log "PM2 installed successfully" -Color $Colors.Success
            } else {
                Write-Log "PM2 is available" -Color $Colors.Success
            }
        }

        # Check for Python and pip3 if any Python HostService is defined
        $hasPythonServices = $Services | Where-Object { $_.Runtime -eq "python" }
        if ($hasPythonServices) {
            Write-Log "Checking Python3 for Python host services..." -Color $Colors.Info
            $pythonCheck = Invoke-VpsCommand -Command 'python3 --version 2>/dev/null || echo "not found"' -ReturnOutput
            if ($pythonCheck -match "not found") {
                Write-Log "Python3 not found, installing..." -Color $Colors.Warning
                Invoke-VpsCommand -Command "apt-get update -qq && apt-get install -y python3 python3-pip 2>&1" | Out-Null
                Write-Log "Python3 installed successfully" -Color $Colors.Success
            } else {
                Write-Log "Python3 is available ($($pythonCheck.Trim()))" -Color $Colors.Success
            }

            Write-Log "Checking pip3..." -Color $Colors.Info
            $pipCheck = Invoke-VpsCommand -Command 'python3 -m pip --version 2>/dev/null || echo "not found"' -ReturnOutput
            if ($pipCheck -match "not found") {
                Write-Log "pip3 not found, installing..." -Color $Colors.Warning
                Invoke-VpsCommand -Command "apt-get install -y python3-pip 2>&1" | Out-Null
                Write-Log "pip3 installed successfully" -Color $Colors.Success
            } else {
                Write-Log "pip3 is available" -Color $Colors.Success
            }

            # Check for PostgreSQL (required for officernd)
            Write-Log "Checking PostgreSQL..." -Color $Colors.Info
            $pgCheck = Invoke-VpsCommand -Command 'systemctl is-active postgresql 2>/dev/null || echo "not found"' -ReturnOutput
            if ($pgCheck -match "not found" -or $pgCheck -match "inactive" -or $pgCheck -match "failed") {
                Write-Log "PostgreSQL not running, installing and configuring..." -Color $Colors.Warning
                Invoke-VpsCommand -Command "apt-get install -y postgresql postgresql-contrib 2>&1 | tail -1" | Out-Null
                Invoke-VpsCommand -Command "systemctl start postgresql && systemctl enable postgresql" | Out-Null

                # Configure listen_addresses for Docker container access
                $pgConfPath = Invoke-VpsCommand -Command "find /etc/postgresql -name postgresql.conf 2>/dev/null | head -1" -ReturnOutput
                $pgConfPath = $pgConfPath.Trim()
                if ($pgConfPath) {
                    Invoke-VpsCommand -Command "sed -i `"s/#listen_addresses = 'localhost'/listen_addresses = '*'/`" $pgConfPath" | Out-Null
                }

                # Allow Docker network connections in pg_hba.conf
                $pgHbaPath = Invoke-VpsCommand -Command "find /etc/postgresql -name pg_hba.conf 2>/dev/null | head -1" -ReturnOutput
                $pgHbaPath = $pgHbaPath.Trim()
                if ($pgHbaPath) {
                    $hbaCheck = Invoke-VpsCommand -Command "grep '172.16.0.0/12' $pgHbaPath 2>/dev/null || echo 'NOT_FOUND'" -ReturnOutput
                    if ($hbaCheck -match "NOT_FOUND") {
                        Invoke-VpsCommand -Command "echo 'host    all             all             172.16.0.0/12           scram-sha-256' >> $pgHbaPath" | Out-Null
                    }
                }

                Invoke-VpsCommand -Command "systemctl restart postgresql" | Out-Null
                Write-Log "PostgreSQL installed and configured" -Color $Colors.Success
            } else {
                Write-Log "PostgreSQL is running" -Color $Colors.Success
            }

            # Create databases and users if they don't exist (via dedicated script)
            Write-Log "Ensuring databases exist..." -Color $Colors.Info
            $setupDbScript = Join-Path $ScriptPath "scripts\setup-databases.py"
            if (Test-Path $setupDbScript) {
                Copy-FileToVps -LocalPath $setupDbScript -RemotePath "/tmp/setup-databases.py" | Out-Null
                Invoke-VpsCommand -Command "python3 /tmp/setup-databases.py" | Out-Null
                Invoke-VpsCommand -Command "rm -f /tmp/setup-databases.py" | Out-Null
            } else {
                Write-Log "scripts/setup-databases.py not found, skipping database setup" -Color $Colors.Warning
            }
            Write-Log "Databases ready" -Color $Colors.Success
        }

        # Create base directory
        Invoke-VpsCommand -Command ('mkdir -p ' + $VpsPath) | Out-Null
        Write-Log "Remote environment initialized" -Color $Colors.Success
        return $true
    }
    catch {
        Write-Log "Failed to initialize remote environment: $_" -Color $Colors.Error
        return $false
    }
}

function Invoke-VpsCommand {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        [switch]$ReturnOutput
    )
    
    Write-Log "Executing on VPS: $Command" -Color $Colors.Info
    
    $plinkAvailable = Get-Command plink -ErrorAction SilentlyContinue
    
    # For docker compose commands, we need special handling because they output progress to stderr
    $isDockerCommand = $Command -match 'docker compose|docker-compose'
    
    try {
        if ($plinkAvailable) {
            $sshCommand = "plink -pw `"$VpsPassword`" -batch -hostkey `"$VpsHostKey`" ${VpsUser}@${VpsHost} `"$Command`""
        }
        else {
            $sshCommand = "ssh -o StrictHostKeyChecking=no ${VpsUser}@${VpsHost} `"$Command`""
        }
        
        # For docker commands, temporarily set error action to continue to avoid stderr throwing
        if ($isDockerCommand) {
            $previousErrorAction = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
        }
        
        $result = Invoke-Expression $sshCommand 2>&1
        $exitCode = $LASTEXITCODE
        
        # Restore error action preference
        if ($isDockerCommand) {
            $ErrorActionPreference = $previousErrorAction
        }
        
        # Convert result to string for easier handling
        $resultString = if ($result) { $result | Out-String } else { "" }
        
        # Don't fail on non-zero exit codes if command contains || true, ; true, or docker compose commands
        # For npm install: some npm versions exit 1 when printing deprecation warnings; only fail on real errors (ERR!)
        $isNpmInstall = $Command -match 'npm install'
        $npmOnlyWarnings = $isNpmInstall -and $exitCode -ne 0 -and $resultString -and $resultString -notmatch 'ERR!'
        if ($exitCode -ne 0 -and $Command -notmatch '\|\| true|\; true|docker compose|docker-compose' -and -not $npmOnlyWarnings) {
            $errMsg = "Command failed with exit code $exitCode"
            if ($resultString -and $resultString.Trim().Length -gt 0) {
                $errMsg += "`n" + $resultString.Trim()
            }
            throw $errMsg
        }
        if ($npmOnlyWarnings) {
            Write-Log "npm install completed with warnings (exit code $exitCode), continuing..." -Color $Colors.Warning
        }
        
        if ($ReturnOutput) {
            return $resultString
        }
        
        return $true
    }
    catch {
        # For docker commands, only log as error if it's a real failure (not just stderr output)
        if ($isDockerCommand -and $_ -notmatch 'error|failed|cannot|unable') {
            Write-Log "Docker command output: $_" -Color $Colors.Info
            if ($ReturnOutput) {
                return $_
            }
            return $true
        }
        Write-Log "Error executing command: $_" -Color $Colors.Error
        throw
    }
}

function Copy-FileToVps {
    param(
        [Parameter(Mandatory=$true)]
        [string]$LocalPath,
        [Parameter(Mandatory=$true)]
        [string]$RemotePath,
        [int]$MaxRetries = 3
    )
    
    Write-Log "Transferring file to VPS: $(Split-Path $LocalPath -Leaf)" -Color $Colors.Info
    
    if (-not (Test-Path $LocalPath)) {
        throw "Local file not found: $LocalPath"
    }
    
    $pscpAvailable = Get-Command pscp -ErrorAction SilentlyContinue
    $retryCount = 0
    $success = $false
    
    while (-not $success -and $retryCount -lt $MaxRetries) {
        $retryCount++
        
        if ($retryCount -gt 1) {
            Write-Log "Retry $retryCount of $MaxRetries..." -Color $Colors.Warning
            Start-Sleep -Seconds 5
        }
        
        try {
            if ($pscpAvailable) {
                $scpCommand = "pscp -pw `"$VpsPassword`" -batch -hostkey `"$VpsHostKey`" `"$LocalPath`" ${VpsUser}@${VpsHost}:$RemotePath"
            }
            else {
                $scpCommand = "scp -o StrictHostKeyChecking=no `"$LocalPath`" ${VpsUser}@${VpsHost}:$RemotePath"
            }
            
            $result = Invoke-Expression $scpCommand 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "File transferred successfully" -Color $Colors.Success
                $success = $true
            }
            else {
                Write-Log "Transfer failed (attempt $retryCount): $result" -Color $Colors.Warning
            }
        }
        catch {
            Write-Log "Transfer error (attempt $retryCount): $_" -Color $Colors.Warning
        }
    }
    
    if (-not $success) {
        throw "Failed to transfer file after $MaxRetries attempts"
    }
    
    return $true
}

#endregion

#region Cleanup Functions

function Clear-AllRemoteResources {
    param(
        [Parameter(Mandatory=$true)]
        [array]$ServiceList
    )
    
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "Cleaning up remote resources" -Color $Colors.Step
    Write-Log "========================================" -Color $Colors.Step
    
    # Phase 1: Stop services (docker-compose for Docker, PM2 for host services)
    Write-Log "Phase 1: Stopping services..." -Color $Colors.Step
    foreach ($service in $ServiceList) {
        $serviceName = $service.Name
        $remoteDir = if ($service.RemoteDir) { $service.RemoteDir } else { $service.Name }
        $remoteServicePath = "$VpsPath/$remoteDir"

        # Handle HostService (PM2-managed)
        if ($service.Type -eq "HostService") {
            $processName = $service.ProcessName
            Write-Log "  Stopping $serviceName PM2 process..." -Color $Colors.Info
            try {
                Invoke-VpsCommand -Command "(pm2 delete $processName 2>/dev/null ; true)" | Out-Null
                Write-Log "  $serviceName PM2 process stopped" -Color $Colors.Success
            }
            catch {
                Write-Log "  ${serviceName}: PM2 process not running or not found" -Color $Colors.Info
            }
            continue
        }

        # Docker services: check if directory and docker-compose.yml exist
        $checkComposeCommand = '[ -d "' + $remoteServicePath + '" ] && [ -f "' + $remoteServicePath + '/docker-compose.yml" ] && echo "EXISTS" || echo "NOT_EXISTS"'

        try {
            $composeExists = Invoke-VpsCommand -Command $checkComposeCommand -ReturnOutput

            if ($composeExists -match "EXISTS") {
                Write-Log "  Stopping $serviceName with docker-compose down..." -Color $Colors.Info
                $composeDownCommand = 'cd "' + $remoteServicePath + '" && docker compose down --volumes --remove-orphans 2>/dev/null || true'
                Invoke-VpsCommand -Command $composeDownCommand | Out-Null
                Write-Log "  $serviceName stopped and cleaned up" -Color $Colors.Success
            } else {
                Write-Log "  ${serviceName}: Directory or docker-compose.yml not found, will use manual cleanup" -Color $Colors.Info
            }
        }
        catch {
            Write-Log "  ${serviceName}: Could not check/stop service, will use manual cleanup" -Color $Colors.Info
        }
    }
    
    # Phase 2: Manual cleanup for any remaining containers (Docker services only)
    Write-Log "Phase 2: Manual cleanup of remaining containers..." -Color $Colors.Step
    $containerNames = $ServiceList | Where-Object { $_.ContainerName -ne $null } | ForEach-Object { $_.ContainerName }
    
    # Stop any remaining containers
    $containerList = $containerNames -join ' '
    $stopCommand = '(docker stop ' + $containerList + ' 2>/dev/null ; true)'
    Invoke-VpsCommand -Command $stopCommand | Out-Null
    
    # Remove any remaining containers
    $removeCommand = '(docker rm -f ' + $containerList + ' 2>/dev/null ; true)'
    Invoke-VpsCommand -Command $removeCommand | Out-Null
    
    # PostgreSQL runs on host (not Docker) - no database container cleanup
    
    Write-Log "Container cleanup completed" -Color $Colors.Success
    
    # Phase 3: Backup preserved configs, then remove service directories
    Write-Log "Phase 3: Removing service directories..." -Color $Colors.Step

    # Backup config/.env for services with PreserveEnv
    $preserveServices = $ServiceList | Where-Object { $_.PreserveEnv -eq $true }
    foreach ($svc in $preserveServices) {
        $svcDir = if ($svc.RemoteDir) { $svc.RemoteDir } else { $svc.Name }
        $envPath = if ($svc.EnvPath) { $svc.EnvPath } else { ".env" }
        $fullEnvPath = "$VpsPath/$svcDir/$envPath"
        $backupCmd = "test -f $fullEnvPath && cp $fullEnvPath /tmp/deploy-backup-$(($svc.Name)) 2>/dev/null ; true"
        Invoke-VpsCommand -Command $backupCmd | Out-Null
    }

    $remoteDirs = $ServiceList | ForEach-Object { if ($_.RemoteDir) { $_.RemoteDir } else { $_.Name } } | Select-Object -Unique
    $removeDirsCommand = ($remoteDirs | ForEach-Object { 'rm -rf ' + $VpsPath + '/' + $_ }) -join ' && '
    Invoke-VpsCommand -Command $removeDirsCommand | Out-Null
    Write-Log "Directories removed" -Color $Colors.Success

    # Phase 4: Recreate clean directories and restore preserved configs
    Write-Log "Phase 4: Recreating clean directories..." -Color $Colors.Step
    $mkdirCommand = ($remoteDirs | ForEach-Object { 'mkdir -p ' + $VpsPath + '/' + $_ }) -join ' && '
    Invoke-VpsCommand -Command $mkdirCommand | Out-Null

    # Restore preserved configs
    foreach ($svc in $preserveServices) {
        $svcDir = if ($svc.RemoteDir) { $svc.RemoteDir } else { $svc.Name }
        $envPath = if ($svc.EnvPath) { $svc.EnvPath } else { ".env" }
        $fullEnvPath = "$VpsPath/$svcDir/$envPath"
        $envDir = $fullEnvPath -replace '/[^/]+$', ''
        $restoreCmd = "mkdir -p $envDir && test -f /tmp/deploy-backup-$(($svc.Name)) && mv /tmp/deploy-backup-$(($svc.Name)) $fullEnvPath 2>/dev/null ; true"
        Invoke-VpsCommand -Command $restoreCmd | Out-Null
    }

    Write-Log "Directories created" -Color $Colors.Success
    
    # Phase 5: Clean up unused Docker resources
    Write-Log "Phase 5: Cleaning up unused Docker resources..." -Color $Colors.Step
    $dockerCleanupCommand = "(docker system prune -f --volumes 2>/dev/null ; true)"
    Invoke-VpsCommand -Command $dockerCleanupCommand | Out-Null
    Write-Log "Docker cleanup completed" -Color $Colors.Success
    
    Write-Log "Cleanup completed successfully" -Color $Colors.Success
    Write-Log ""
}

#endregion

#region Archive Functions

function New-ArchiveForDeployment {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SourcePath,
        [Parameter(Mandatory=$true)]
        [string]$ServiceName,
        [string[]]$ExcludeDirs = @()
    )

    Write-Log "Creating ZIP archive for $ServiceName..." -Color $Colors.Info

    $archiveName = "${ServiceName}.zip"
    $archivePath = Join-Path $ScriptPath $archiveName

    # Remove old archive if exists
    if (Test-Path $archivePath) {
        Remove-Item $archivePath -Force
    }

    try {
        # Get all items to archive, excluding logs directory, log files, and custom exclude dirs
        $itemsToArchive = Get-ChildItem -Path $SourcePath -Recurse | Where-Object {
            $relativePath = $_.FullName.Substring($SourcePath.Length)
            # Exclude logs directory, .log files, node_modules, and __pycache__
            $excluded = ($relativePath -match '\\logs\\' -or $relativePath -match '\\logs$' -or $_.Extension -eq '.log' -or $relativePath -match '\\node_modules\\' -or $relativePath -match '\\node_modules$' -or $relativePath -match '\\__pycache__\\' -or $relativePath -match '\\__pycache__$')
            # Exclude custom directories
            foreach ($dir in $ExcludeDirs) {
                if ($relativePath -match "\\$dir\\" -or $relativePath -match "\\$dir$") {
                    $excluded = $true
                }
            }
            -not $excluded
        }
        
        if ($itemsToArchive.Count -eq 0) {
            throw "No files found to archive after exclusions"
        }
        
        # Create a temporary directory for staging
        $tempDir = Join-Path $env:TEMP "deploy-$ServiceName-$(Get-Random)"
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        
        try {
            # Copy files to temp directory maintaining structure
            foreach ($item in $itemsToArchive) {
                $relativePath = $item.FullName.Substring($SourcePath.Length + 1)
                $destPath = Join-Path $tempDir $relativePath
                
                if ($item.PSIsContainer) {
                    New-Item -ItemType Directory -Path $destPath -Force | Out-Null
                } else {
                    $destDir = Split-Path $destPath -Parent
                    if (-not (Test-Path $destDir)) {
                        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                    }
                    Copy-Item -Path $item.FullName -Destination $destPath -Force
                }
            }
            
            # Create archive from temp directory
            Compress-Archive -Path "$tempDir\*" -DestinationPath $archivePath -Force -CompressionLevel Optimal
        }
        finally {
            # Clean up temp directory
            if (Test-Path $tempDir) {
                Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        
        # Verify archive was created
        if (-not (Test-Path $archivePath)) {
            throw "Archive file was not created"
        }
        
        $archiveSize = (Get-Item $archivePath).Length / 1MB
        Write-Log "Archive created successfully: $archiveName ($([math]::Round($archiveSize, 2)) MB)" -Color $Colors.Success
        return $archivePath
    }
    catch {
        Write-Log "Failed to create archive: $_" -Color $Colors.Error
        throw
    }
}

#endregion

#region Deployment Functions

function Deploy-ServiceToVps {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Service
    )
    
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "Deploying $($Service.Name) to VPS" -Color $Colors.Step
    Write-Log "========================================" -Color $Colors.Step
    
    # Map service name to local directory (support LocalDir/RemoteDir overrides)
    $localDir = if ($Service.LocalDir) { $Service.LocalDir } else { $Service.Name }
    $servicePath = Join-Path $ScriptPath $localDir
    $serviceName = $Service.Name
    $remoteDir = if ($Service.RemoteDir) { $Service.RemoteDir } else { $Service.Name }
    $remoteServicePath = "$VpsPath/$remoteDir"
    
    try {
        # Step 1: Create ZIP archive
        Write-Log "Step 1/6: Creating archive..." -Color $Colors.Info
        $excludeDirs = if ($Service.ExcludeDirs) { $Service.ExcludeDirs } else { @() }
        $archivePath = New-ArchiveForDeployment -SourcePath $servicePath -ServiceName $serviceName -ExcludeDirs $excludeDirs
        $archiveName = Split-Path $archivePath -Leaf
        
        # Step 2: Transfer to VPS
        Write-Log "Step 2/6: Transferring archive to VPS..." -Color $Colors.Info
        $remoteArchivePath = "/tmp/$archiveName"
        Copy-FileToVps -LocalPath $archivePath -RemotePath $remoteArchivePath | Out-Null
        
        # Step 3: Extract on VPS (using unzip for ZIP files)
        # Note: unzip returns exit code 1 for warnings (like Windows backslash paths) even though extraction succeeds
        # We use ; true to ignore the exit code, then separately verify extraction and clean up
        Write-Log "Step 3/6: Extracting archive on VPS..." -Color $Colors.Info
        $extractCommand = "cd $remoteServicePath && (unzip -o $remoteArchivePath 2>&1 || true) && rm -f $remoteArchivePath"
        Invoke-VpsCommand -Command $extractCommand | Out-Null
        Write-Log "Archive extracted successfully" -Color $Colors.Success
        
        # Host service deployment (no Docker)
        if ($Service.Type -eq "HostService") {
            $processName = $Service.ProcessName
            $runtime = if ($Service.Runtime) { $Service.Runtime } else { "node" }

            # Step 4: Configure environment
            Write-Log "Step 4/6: Configuring environment..." -Color $Colors.Info
            $envRelPath = if ($Service.EnvPath) { $Service.EnvPath } else { ".env" }
            $envFullPath = "$remoteServicePath/$envRelPath"
            $envCheckCommand = "test -f $envFullPath && echo 'EXISTS' || echo 'NOT_EXISTS'"
            $envExists = Invoke-VpsCommand -Command $envCheckCommand -ReturnOutput
            if ($envExists -match "NOT_EXISTS") {
                if ($Service.DefaultEnv) {
                    $envDir = $envFullPath -replace '/[^/]+$', ''
                    Invoke-VpsCommand -Command "mkdir -p $envDir" | Out-Null
                    $escapedEnv = $Service.DefaultEnv -replace "'", "'\\''"
                    Invoke-VpsCommand -Command "cat > $envFullPath << 'ENVEOF'`n$($Service.DefaultEnv)`nENVEOF" | Out-Null
                    Write-Log ".env created with defaults at $envRelPath" -Color $Colors.Success
                } else {
                    $envCopyCommand = "cd $remoteServicePath && cp .env.example .env 2>/dev/null || printf 'OFFICERND_API_URL=http://localhost:8087\nOFFICERND_ORG_SLUG=arafat-business-centers\nPORT=8088\n' > .env"
                    Invoke-VpsCommand -Command $envCopyCommand | Out-Null
                    Write-Log ".env created from .env.example" -Color $Colors.Success
                }
            } else {
                Write-Log ".env already exists at $envRelPath, keeping current configuration" -Color $Colors.Info
            }

            # Host services run directly on the host, not in Docker.
            # Fix any host.docker.internal references (only valid inside Docker containers).
            Invoke-VpsCommand -Command "sed -i 's/host\.docker\.internal/localhost/g' $envFullPath" | Out-Null

            # Step 5: Install dependencies and build
            Write-Log "Step 5/6: Installing dependencies and building..." -Color $Colors.Info

            if ($runtime -eq "python") {
                # Python service: pip install
                $reqPath = "$remoteServicePath/config/requirements.txt"
                $reqCheck = Invoke-VpsCommand -Command "test -f $reqPath && echo 'EXISTS' || echo 'NOT_EXISTS'" -ReturnOutput
                if ($reqCheck -match "EXISTS") {
                    $pipCommand = "cd $remoteServicePath && bash -c 'set -o pipefail && pip3 install --break-system-packages -r config/requirements.txt 2>&1 | tail -5'"
                    Invoke-VpsCommand -Command $pipCommand | Out-Null
                    Write-Log "Python dependencies installed" -Color $Colors.Success
                } else {
                    Write-Log "No requirements.txt found, skipping pip install" -Color $Colors.Info
                }

                # Create database tables if needed (non-fatal: tables may already exist)
                Write-Log "Ensuring database tables exist..." -Color $Colors.Info
                $setupDbScript = Join-Path $ScriptPath "scripts\setup-databases.py"
                if (Test-Path $setupDbScript) {
                    Copy-FileToVps -LocalPath $setupDbScript -RemotePath "/tmp/setup-databases.py" | Out-Null
                    Invoke-VpsCommand -Command "sed -i 's/\r$//' /tmp/setup-databases.py" | Out-Null
                    try {
                        $dbSetupResult = Invoke-VpsCommand -Command "python3 /tmp/setup-databases.py $remoteServicePath 2>&1" -ReturnOutput
                        if ($dbSetupResult -match "Error:|Traceback|ModuleNotFoundError|ImportError") {
                            Write-Log "Database setup warnings: $($dbSetupResult.Trim())" -Color $Colors.Warning
                        } else {
                            Write-Log "Database tables ready" -Color $Colors.Success
                        }
                    }
                    catch {
                        Write-Log "Database table setup failed (non-fatal): $_" -Color $Colors.Warning
                        Write-Log "Tables may already exist from a previous deployment" -Color $Colors.Info
                    }
                    Invoke-VpsCommand -Command "rm -f /tmp/setup-databases.py" | Out-Null
                } else {
                    Write-Log "scripts/setup-databases.py not found, skipping table creation" -Color $Colors.Warning
                }
            } else {
                # Node.js service: npm install + build
                $installCommand = "cd $remoteServicePath && npm install --loglevel=error --no-audit --no-fund 2>&1"
                Invoke-VpsCommand -Command $installCommand | Out-Null
                Write-Log "Backend dependencies installed" -Color $Colors.Success

                # Check for frontend directory
                $frontendCheck = Invoke-VpsCommand -Command "test -d $remoteServicePath/frontend && echo 'EXISTS' || echo 'NOT_EXISTS'" -ReturnOutput
                if ($frontendCheck -match "EXISTS") {
                    $frontendBuildCommand = "cd $remoteServicePath/frontend && npm install --loglevel=error --no-audit --no-fund 2>&1 && npm run build"
                    Invoke-VpsCommand -Command $frontendBuildCommand | Out-Null
                    Write-Log "Frontend built successfully" -Color $Colors.Success
                }

                $backendBuildCommand = "cd $remoteServicePath && npm run build"
                Invoke-VpsCommand -Command $backendBuildCommand | Out-Null
                Write-Log "Backend built successfully" -Color $Colors.Success
            }

            # Step 6: Start with PM2
            Write-Log "Step 6/6: Starting service with PM2..." -Color $Colors.Info
            Invoke-VpsCommand -Command "(pm2 delete $processName 2>/dev/null ; true)" | Out-Null
            if ($Service.StartCommand) {
                $pm2StartCommand = "cd $remoteServicePath && pm2 start '$($Service.StartCommand)' --name $processName"
            } else {
                $pm2StartCommand = "cd $remoteServicePath && pm2 start dist/main.js --name $processName"
            }
            Invoke-VpsCommand -Command $pm2StartCommand | Out-Null
            Invoke-VpsCommand -Command "pm2 save" | Out-Null
            Write-Log "Service started with PM2 as '$processName'" -Color $Colors.Success

            # Cleanup local archive
            Remove-Item -Path $archivePath -Force -ErrorAction SilentlyContinue

            Write-Log "Deployment of $serviceName completed" -Color $Colors.Success
            Write-Log ""
            return $true
        }

        # Step 4: Check if docker-compose.yml exists
        Write-Log "Step 4/6: Checking service configuration..." -Color $Colors.Info
        $checkComposeCommand = "test -f $remoteServicePath/docker-compose.yml && echo 'EXISTS' || echo 'NOT_EXISTS'"
        $composeExists = Invoke-VpsCommand -Command $checkComposeCommand -ReturnOutput
        
        if ($composeExists -match "NOT_EXISTS") {
            Write-Log "No docker-compose.yml found for $serviceName - skipping Docker build/start" -Color $Colors.Warning
            Write-Log "Service $serviceName requires manual setup or docker-compose.yml file" -Color $Colors.Info
            throw "docker-compose.yml not found"
        }
        
        # Step 5: Build Docker image
        Write-Log "Step 5/6: Building Docker images..." -Color $Colors.Info
        $buildCommand = "cd $remoteServicePath && docker compose build$(if ($ForceRebuild) { ' --no-cache' }) 2>&1"
        $buildResult = Invoke-VpsCommand -Command $buildCommand -ReturnOutput
        
        if ($buildResult -match "Successfully built|DONE|Successfully tagged|Built|exporting to image") {
            # Check for actual build errors (not text inside echo/COPY commands)
            # Only match ERROR at line start or after specific error patterns
            if ($buildResult -match "(?m)^#\d+\s+ERROR|failed to solve|error: process|did not complete successfully|exit code:") {
                Write-Log "Build completed with errors:" -Color $Colors.Warning
                # Extract and show actual error lines
                $errorLines = ($buildResult -split "`n" | Where-Object { $_ -match "^#\d+\s+ERROR|failed to solve|error: process|did not complete successfully|exit code:" }) -join "`n"
                if ($errorLines) {
                    Write-Log "  $errorLines" -Color $Colors.Error
                }
            } else {
                Write-Log "Docker images built successfully" -Color $Colors.Success
            }
        } elseif ($buildResult -match "(?m)^#\d+\s+ERROR|failed to solve|error: process|did not complete successfully|exit code:") {
            Write-Log "Build FAILED:" -Color $Colors.Error
            $errorLines = ($buildResult -split "`n" | Where-Object { $_ -match "ERROR|error:|failed" }) -join "`n"
            Write-Log "  $errorLines" -Color $Colors.Error
        } else {
            Write-Log "Build completed (no clear status message)" -Color $Colors.Warning
        }
        
        # Step 6: Start services
        Write-Log "Step 6/6: Starting services..." -Color $Colors.Info
        $startCommand = "cd $remoteServicePath && docker compose up -d"
        $startResult = Invoke-VpsCommand -Command $startCommand -ReturnOutput
        
        # Enhanced verification for scrape-sw-codes (PostgreSQL on host, no DB container)
        if ($Service.Name -eq "scrape-sw-codes") {
            Write-Log "Verifying scrape-sw-codes (PostgreSQL on host)..." -Color $Colors.Info
            Start-Sleep -Seconds 10
            $fetchCodesStatus = Invoke-VpsCommand -Command "docker ps --filter name=SW_CODES_PYTHON --format '{{.Status}}'" -ReturnOutput
            if ($fetchCodesStatus -match "Up") {
                Write-Log "[OK] scrape-sw-codes container is running" -Color $Colors.Success
            } else {
                Write-Log "[WARN] scrape-sw-codes container status: $fetchCodesStatus" -Color $Colors.Warning
                $logs = Invoke-VpsCommand -Command "docker logs SW_CODES_PYTHON --tail 5 2>&1 ; true" -ReturnOutput
                Write-Log "Container logs: $logs" -Color $Colors.Info
            }
        }
        
        if ($startResult -match "Started|Running|done") {
            Write-Log "Services started successfully" -Color $Colors.Success
        } else {
            Write-Log "Services may have started - check container status manually" -Color $Colors.Warning
        }
        
        # Cleanup local archive
        Remove-Item -Path $archivePath -Force -ErrorAction SilentlyContinue
        
        Write-Log "Deployment of $serviceName completed" -Color $Colors.Success
        Write-Log ""
        return $true
    }
    catch {
        Write-Log "Deployment of $serviceName failed: $_" -Color $Colors.Error
        Write-Log ""
        
        # Show additional debugging info for scrape-sw-codes (PostgreSQL on host)
        if ($Service.Name -eq "scrape-sw-codes") {
            Write-Log "scrape-sw-codes debugging information:" -Color $Colors.Info
            try {
                $containerLogs = Invoke-VpsCommand -Command 'docker logs SW_CODES_PYTHON --tail 10 2>&1 || echo "Container not found"' -ReturnOutput
                Write-Log "Container logs: $containerLogs" -Color $Colors.Info
            }
            catch {
                Write-Log "Could not retrieve debugging logs" -Color $Colors.Warning
            }
        }
        
        # Cleanup local archive on failure
        if ($archivePath -and (Test-Path $archivePath)) {
            Remove-Item -Path $archivePath -Force -ErrorAction SilentlyContinue
        }
        
        return $false
    }
}

#endregion

#region Testing Functions

function Invoke-VpsCommandSilent {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        [switch]$ReturnOutput
    )
    
    # Silent version without logging
    $plinkAvailable = Get-Command plink -ErrorAction SilentlyContinue
    $isDockerCommand = $Command -match 'docker compose|docker-compose|docker '
    
    try {
        if ($plinkAvailable) {
            $sshCommand = "plink -pw `"$VpsPassword`" -batch -hostkey `"$VpsHostKey`" ${VpsUser}@${VpsHost} `"$Command`""
        }
        else {
            $sshCommand = "ssh -o StrictHostKeyChecking=no ${VpsUser}@${VpsHost} `"$Command`""
        }
        
        # For docker commands, temporarily set error action to continue
        if ($isDockerCommand) {
            $previousErrorAction = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
        }
        
        $result = Invoke-Expression $sshCommand 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($isDockerCommand) {
            $ErrorActionPreference = $previousErrorAction
        }
        
        # Convert result to string
        $resultString = if ($result) { $result | Out-String } else { "" }
        
        # Don't fail for docker commands - they may return non-zero when no containers found
        if ($exitCode -ne 0 -and -not $isDockerCommand -and $Command -notmatch '; true\)') {
            throw "Command failed with exit code $exitCode"
        }
        
        if ($ReturnOutput) {
            return $resultString
        }
        
        return $true
    }
    catch {
        # For docker commands, don't throw - just return empty/error info
        if ($isDockerCommand) {
            if ($ReturnOutput) {
                return ""
            }
            return $true
        }
        throw
    }
}

function Test-RemoteContainerHealth {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Service,
        [int]$TimeoutSeconds = 30
    )
    
    # Skip health check for Web/Portal services
    if ($Service.Type -eq "Web") {
        Write-Log "$($Service.Name) is a web service - skipping health check" -Color $Colors.Info
        return $true
    }

    # Host service health check (PM2 process + port listening)
    if ($Service.Type -eq "HostService") {
        Write-Log "Checking health of $($Service.Name) host service..." -Color $Colors.Info
        $processName = $Service.ProcessName
        $port = $Service.Port

        $startTime = Get-Date
        $timeout = [TimeSpan]::FromSeconds($TimeoutSeconds)

        while ((Get-Date) - $startTime -lt $timeout) {
            # Check if PM2 process is running (pm2 pid returns PID or 0)
            $pm2Pid = Invoke-VpsCommandSilent -Command "pm2 pid $processName 2>/dev/null || echo ''" -ReturnOutput
            $pm2Pid = $pm2Pid.Trim()

            if ($pm2Pid -and $pm2Pid -ne "0" -and $pm2Pid -ne "") {
                # Check if port is listening
                $portCheck = Invoke-VpsCommandSilent -Command "ss -tuln | grep ':${port} ' || echo 'NOT_LISTENING'" -ReturnOutput
                if ($portCheck -notmatch "NOT_LISTENING") {
                    Write-Log "$($Service.Name) is running (PID: $pm2Pid, port $port)" -Color $Colors.Success
                    return $true
                }
            }

            Start-Sleep -Seconds 2
        }

        Write-Log "$($Service.Name) host service health check timed out" -Color $Colors.Warning
        try {
            $logs = Invoke-VpsCommandSilent -Command "pm2 logs $processName --lines 5 --nostream 2>&1 ; true" -ReturnOutput
            Write-Log "PM2 logs: $logs" -Color $Colors.Info
        } catch {}
        return $false
    }
    
    Write-Log "Checking health of $($Service.Name) container..." -Color $Colors.Info
    
    $startTime = Get-Date
    $timeout = [TimeSpan]::FromSeconds($TimeoutSeconds)
    $containerName = $Service.ContainerName
    
    # Special handling for scrape-sw-codes (PostgreSQL on host, no DB container)
    if ($Service.Name -eq "scrape-sw-codes") {
        Write-Log "Health check for scrape-sw-codes (PostgreSQL on host)..." -Color $Colors.Info
        while ((Get-Date) - $startTime -lt $timeout) {
            $fetchStatus = Invoke-VpsCommandSilent -Command "docker ps --filter name=SW_CODES_PYTHON --format '{{.Status}}'" -ReturnOutput
            if ($fetchStatus -match "Up") {
                Write-Log "scrape-sw-codes container is running" -Color $Colors.Success
                Start-Sleep -Seconds 5
                return $true
            }
            if ($fetchStatus -match "Exited") {
                Write-Log "scrape-sw-codes container has exited unexpectedly" -Color $Colors.Error
                return $false
            }
            Start-Sleep -Seconds 3
        }
        Write-Log "scrape-sw-codes health check timed out" -Color $Colors.Warning
        return $false
    }
    
    # Standard health check for other services
    while ((Get-Date) - $startTime -lt $timeout) {
        $statusCommand = "docker ps --filter name=$containerName --format '{{.Status}}'"
        $status = Invoke-VpsCommandSilent -Command $statusCommand -ReturnOutput
        
        if ($status -match "Up") {
            Write-Log "$($Service.Name) container is running" -Color $Colors.Success
            
            # For API services, wait a bit longer for the service to be ready
            if ($Service.Type -eq "API") {
                Write-Log "Waiting for API service to be ready..." -Color $Colors.Info
                Start-Sleep -Seconds 5
            }
            
            return $true
        }
        
        if ($status -match "Exited") {
            Write-Log "$($Service.Name) container has exited unexpectedly" -Color $Colors.Error
            return $false
        }
        
        Start-Sleep -Seconds 3
    }
    
    Write-Log "$($Service.Name) container health check timed out" -Color $Colors.Warning
    return $false
}

function Test-RemoteApiEndpoint {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Service
    )
    
    Write-Log "Testing $($Service.Name) API endpoint..." -Color $Colors.Info
    
    # Build test URL based on service type
    if ($Service.Type -eq "HostService") {
        $testUrl = "http://${VpsHost}:$($Service.Port)$($Service.Endpoint)"
    } elseif ($Service.Endpoint -eq "/health") {
        $testUrl = "http://${VpsHost}:$($Service.Port)$($Service.Endpoint)"
    } elseif ($Service.Endpoint -eq "/scrape") {
        # API-node uses /scrape?code=XXXXXX format
        $testUrl = "http://${VpsHost}:$($Service.Port)$($Service.Endpoint)?code=${TestCode}"
    } else {
        $testUrl = "http://${VpsHost}:$($Service.Port)$($Service.Endpoint)?code=${TestCode}"
    }
    
    try {
        # First check if port is listening on VPS
        $port = $Service.Port
        $portCheckCommand = 'netstat -tuln | grep ":' + $port + ' " 2>/dev/null || ss -tuln | grep ":' + $port + ' " 2>/dev/null || echo "PORT_NOT_LISTENING"'
        $portStatus = Invoke-VpsCommandSilent -Command $portCheckCommand -ReturnOutput
        
        if ($portStatus -match "PORT_NOT_LISTENING") {
            Write-Log "$($Service.Name) API test SKIPPED: Port $($Service.Port) not listening on VPS" -Color $Colors.Warning
            Write-Log "  Container may still be starting or port mapping issue" -Color $Colors.Info
            return $false
        }
        
        $response = Invoke-WebRequest -Uri $testUrl -Method Get -TimeoutSec 30 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            $content = $response.Content | ConvertFrom-Json
            
            # Handle different response formats
            if ($Service.Type -eq "HostService") {
                # HostService endpoints return {success: true/false, ...}
                if ($content.success -eq $true) {
                    Write-Log "$($Service.Name) API test PASSED" -Color $Colors.Success
                    Write-Log "  API Status: $($content.api_status)" -Color $Colors.Info
                    Write-Log "  Companies: $($content.companies)" -Color $Colors.Info
                    return $true
                } else {
                    Write-Log "$($Service.Name) API responding (upstream may be down): $($content.message)" -Color $Colors.Warning
                    return $true  # Service itself is working
                }
            }
            elseif ($Service.Endpoint -eq "/health") {
                # scrape-sw-codes health endpoint returns {"ok": true}
                if ($content.ok -eq $true) {
                    Write-Log "$($Service.Name) API test PASSED" -Color $Colors.Success
                    Write-Log "  Health check: OK" -Color $Colors.Info
                    return $true
                } else {
                    Write-Log "$($Service.Name) API returned unexpected health response" -Color $Colors.Warning
                    return $false
                }
            }
            elseif ($content.status -eq "success" -and $content.data) {
                Write-Log "$($Service.Name) API test PASSED" -Color $Colors.Success
                Write-Log "  Activity Code: $($content.data.activity_code)" -Color $Colors.Info
                Write-Log "  Name (EN): $($content.data.name_en)" -Color $Colors.Info
                Write-Log "  Status: $($content.data.status)" -Color $Colors.Info
                return $true
            }
            else {
                Write-Log "$($Service.Name) API returned unexpected response" -Color $Colors.Warning
                return $false
            }
        }
        else {
            Write-Log "$($Service.Name) API returned status code: $($response.StatusCode)" -Color $Colors.Error
            return $false
        }
    }
    catch {
        Write-Log "$($Service.Name) API test FAILED: $_" -Color $Colors.Warning
        Write-Log "  This may be due to firewall rules or the service still starting" -Color $Colors.Info
        return $false
    }
}

function Test-RemotePortalEndpoint {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Service
    )
    
    Write-Log "Testing $($Service.Name) endpoint..." -Color $Colors.Info
    
    $testUrl = "http://${VpsHost}:$($Service.Port)$($Service.Endpoint)"
    
    try {
        $response = Invoke-WebRequest -Uri $testUrl -Method Get -TimeoutSec 30 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            if ($response.Content -match "noaman.cloud" -or $response.Content -match "Premium Data Extraction") {
                Write-Log "$($Service.Name) endpoint test PASSED" -Color $Colors.Success
                return $true
            }
            else {
                Write-Log "$($Service.Name) returned unexpected content" -Color $Colors.Warning
                return $false
            }
        }
        else {
            Write-Log "$($Service.Name) returned status code: $($response.StatusCode)" -Color $Colors.Error
            return $false
        }
    }
    catch {
        Write-Log "$($Service.Name) endpoint test FAILED: $_" -Color $Colors.Error
        return $false
    }
}

#endregion

#region Main Deployment Function

function Start-Deployment {
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "VPS Deployment Script" -Color $Colors.Step
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "VPS Host: $VpsHost" -Color $Colors.Info
    Write-Log "VPS User: $VpsUser" -Color $Colors.Info
    Write-Log "VPS Path: $VpsPath" -Color $Colors.Info
    Write-Log "Force Rebuild: $ForceRebuild" -Color $Colors.Info
    Write-Log "Skip Tests: $SkipTests" -Color $Colors.Info
    Write-Log ""
    
    # Validate prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Log "Prerequisites validation failed. Exiting." -Color $Colors.Error
        exit 1
    }
    Write-Log ""
    
    # Test SSH connection
    if (-not (Test-SshConnection)) {
        Write-Log "Cannot establish SSH connection to VPS." -Color $Colors.Error
        Write-Log "Please ensure:" -Color $Colors.Info
        Write-Log "1. VPS is accessible and SSH service is running" -Color $Colors.Info
        Write-Log "2. Firewall allows SSH connections (port 22)" -Color $Colors.Info
        Write-Log "3. Credentials are correct" -Color $Colors.Info
        Write-Log ""
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 1
        }
    }
    Write-Log ""
    
    # Initialize remote environment (install unzip if needed)
    if (-not (Initialize-RemoteEnvironment)) {
        Write-Log "Failed to initialize remote environment. Exiting." -Color $Colors.Error
        exit 1
    }
    Write-Log ""
    
    # Configure Nginx reverse proxy for noaman.cloud
    Write-Log "Configuring Nginx reverse proxy..." -Color $Colors.Step
    try {
        # Check if Nginx is installed and running
        $nginxStatus = Invoke-VpsCommand -Command 'systemctl is-active nginx 2>/dev/null || echo "inactive"' -ReturnOutput
        
        if ($nginxStatus -match "active") {
            Write-Log "Nginx is running, deploying reverse proxy configuration..." -Color $Colors.Info
            
            # Check if noaman.cloud.nginx.conf exists in Portal directory
            $nginxConfigPath = Join-Path $ScriptPath "Portal/noaman.cloud.nginx.conf"
            if (Test-Path $nginxConfigPath) {
                # Backup existing configuration
                Invoke-VpsCommand -Command 'cp /etc/nginx/sites-available/noaman.cloud /etc/nginx/sites-available/noaman.cloud.backup.`$(date +%Y%m%d_%H%M%S) 2>/dev/null ; true' | Out-Null
                
                # Copy new configuration to VPS
                Copy-FileToVps -LocalPath $nginxConfigPath -RemotePath "/etc/nginx/sites-available/noaman.cloud" | Out-Null
                
                # Test Nginx configuration
                $nginxTest = Invoke-VpsCommand -Command "nginx -t 2>&1" -ReturnOutput
                if ($nginxTest -match "syntax is ok") {
                    # Reload Nginx
                    Invoke-VpsCommand -Command "systemctl reload nginx" | Out-Null
                    Write-Log "Nginx reverse proxy configuration deployed and reloaded successfully" -Color $Colors.Success
                } else {
                    Write-Log "Nginx configuration test failed: $nginxTest" -Color $Colors.Warning
                    Write-Log "Restoring backup configuration..." -Color $Colors.Info
                    Invoke-VpsCommand -Command 'cp /etc/nginx/sites-available/noaman.cloud.backup.* /etc/nginx/sites-available/noaman.cloud 2>/dev/null ; true' | Out-Null
                }
            } else {
                Write-Log "Nginx configuration file not found, skipping reverse proxy setup" -Color $Colors.Info
            }
        } else {
            Write-Log "Nginx not running, skipping reverse proxy configuration" -Color $Colors.Info
        }
    }
    catch {
        Write-Log "Error configuring Nginx: $_" -Color $Colors.Warning
        Write-Log "Continuing with deployment..." -Color $Colors.Info
    }
    Write-Log ""
    
    # Filter services (skip if directory doesn't exist)
    $servicesToDeploy = $Services | Where-Object {
        if ($_.Name -eq "scrape-sw-gsheet") {
            $SW_GSHEETPath = Join-Path $ScriptPath "scrape-sw-gsheet"
            if (-not (Test-Path $SW_GSHEETPath)) {
                Write-Log "Skipping scrape-sw-gsheet (directory not found)" -Color $Colors.Warning
                return $false
            }
        }
        if ($_.Type -eq "HostService") {
            $localDir = if ($_.LocalDir) { $_.LocalDir } else { $_.Name }
            $hostPath = Join-Path $ScriptPath $localDir
            if (-not (Test-Path $hostPath)) {
                Write-Log "Skipping $($_.Name) (directory not found)" -Color $Colors.Warning
                return $false
            }
        }
        return $true
    }
    
    # Clean up all remote resources
    Clear-AllRemoteResources -ServiceList $servicesToDeploy
    
    # Deploy each service
    $successCount = 0
    $failedServices = @()
    
    foreach ($service in $servicesToDeploy) {
        if (Deploy-ServiceToVps -Service $service) {
            $successCount++
        } else {
            $failedServices += $service.Name
        }
    }
    
    # Verify deployments
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "Verifying Deployments" -Color $Colors.Step
    Write-Log "========================================" -Color $Colors.Step
    Write-Log ""
    
    foreach ($service in $servicesToDeploy) {
        if ($service.Name -in $failedServices) {
            continue
        }
        
        # Check container health
        $containerHealthy = Test-RemoteContainerHealth -Service $service
        if (-not $containerHealthy) {
            Write-Log "$($service.Name) health check failed" -Color $Colors.Warning

            # Show logs for debugging
            Write-Log "Fetching logs for debugging..." -Color $Colors.Info
            try {
                if ($service.Type -eq "HostService") {
                    $logs = Invoke-VpsCommandSilent -Command "pm2 logs $($service.ProcessName) --lines 10 --nostream 2>&1 || echo 'No logs available'" -ReturnOutput
                } else {
                    $logs = Invoke-VpsCommandSilent -Command "docker logs $($service.ContainerName) --tail 10 2>&1 || echo 'No logs available'" -ReturnOutput
                }
                Write-Log "  Last 10 log lines: $logs" -Color $Colors.Info
            } catch {
                Write-Log "  Could not fetch logs" -Color $Colors.Info
            }
        }
        
        if ($containerHealthy) {
            Write-Log "$($service.Name) deployment verified (container running)" -Color $Colors.Success
        }
        
        Write-Log ""
    }
    
    # Summary
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "Deployment Summary" -Color $Colors.Step
    Write-Log "========================================" -Color $Colors.Step
    Write-Log "VPS: $VpsHost" -Color $Colors.Info
    Write-Log "Total services: $($servicesToDeploy.Count)" -Color $Colors.Info
    Write-Log "Successfully deployed: $successCount" -Color $Colors.Success
    Write-Log "Failed: $($servicesToDeploy.Count - $successCount)" -Color $(if ($failedServices.Count -gt 0) { $Colors.Error } else { $Colors.Success })
    
    if ($failedServices.Count -gt 0) {
        Write-Log "Failed services: $($failedServices -join ', ')" -Color $Colors.Error
    }
    
    Write-Log ""
    
    if ($successCount -eq $servicesToDeploy.Count) {
        Write-Log "Deployment completed successfully!" -Color $Colors.Success
        exit 0
    }
    else {
        Write-Log "Deployment completed with errors" -Color $Colors.Error
        exit 1
    }
}

#endregion

# Run deployment
Start-Deployment
