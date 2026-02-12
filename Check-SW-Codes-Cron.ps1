#!/usr/bin/env pwsh
# Check if SW_CODES cron job ran today on the server
# Uses credentials from Deploy-to-Docker.ps1

# VPS Configuration (from Deploy-to-Docker.ps1)
$VpsHost = "31.220.111.113"
$VpsUser = "root"
$VpsPassword = "Swa@Adel2022"
$VpsHostKey = "ssh-ed25519 255 SHA256:br5ADDgHrTODqLVxk/qlDPK0qjNr8+awdUExclqzbN0"

Write-Host "Checking SW_CODES cron job status..." -ForegroundColor Cyan
Write-Host "Server: $VpsHost" -ForegroundColor Gray
Write-Host "User: $VpsUser" -ForegroundColor Gray
Write-Host "Time Zone: Asia/Qatar (GMT+3)" -ForegroundColor Gray
Write-Host ""

# Function to execute SSH commands
function Invoke-SshCommand {
    param([string]$Command)
    
    $plinkAvailable = Get-Command plink -ErrorAction SilentlyContinue
    
    try {
        if ($plinkAvailable) {
            $sshCommand = "plink -pw `"$VpsPassword`" -batch -hostkey `"$VpsHostKey`" ${VpsUser}@${VpsHost} `"$Command`""
        } else {
            $sshCommand = "ssh -o StrictHostKeyChecking=no ${VpsUser}@${VpsHost} `"$Command`""
        }
        
        $result = Invoke-Expression $sshCommand 2>&1
        return $result
    } catch {
        Write-Host "SSH command failed: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

try {
    # Get today's date in Qatar timezone
    $QatarTime = [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, "Arab Standard Time")
    $TodayQatar = $QatarTime.ToString("yyyy-MM-dd")
    
    Write-Host "Today in Qatar: $TodayQatar" -ForegroundColor Yellow
    Write-Host "Current Qatar Time: $($QatarTime.ToString('HH:mm:ss'))" -ForegroundColor Yellow
    Write-Host ""
    
    # Check if cron container is running
    Write-Host "1. Checking if SW_CODES_CRON container is running..." -ForegroundColor White
    $cronStatus = Invoke-SshCommand "docker ps --filter name=SW_CODES_CRON --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
    
    if ($cronStatus -match "SW_CODES_CRON") {
        Write-Host "SUCCESS: SW_CODES_CRON container is running" -ForegroundColor Green
        Write-Host $cronStatus -ForegroundColor Gray
    } else {
        Write-Host "ERROR: SW_CODES_CRON container is NOT running" -ForegroundColor Red
        Write-Host "Run: docker-compose -f scrape-sw-codes/docker-compose.yml up -d cron" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    
    # Check cron logs for today
    Write-Host "2. Checking cron logs for today ($TodayQatar)..." -ForegroundColor White
    $cronLogs = Invoke-SshCommand "docker logs SW_CODES_CRON 2>&1 | grep '$TodayQatar' || echo 'No logs found for today'"
    
    if ($cronLogs -ne "No logs found for today") {
        Write-Host "Cron logs for today:" -ForegroundColor Green
        Write-Host $cronLogs -ForegroundColor Gray
    } else {
        Write-Host "WARNING: No cron execution logs found for today" -ForegroundColor Yellow
        Write-Host "This could mean:" -ForegroundColor Yellow
        Write-Host "  - Cron hasn't run yet (scheduled for 8:00 AM Qatar time)" -ForegroundColor Yellow
        Write-Host "  - Cron failed to execute" -ForegroundColor Yellow
        Write-Host "  - Container was restarted and logs were cleared" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Check database for last update
    Write-Host "3. Checking database for last update..." -ForegroundColor White
    $dbCheck = Invoke-SshCommand "curl -s http://localhost:8084/check-update.php | jq -r '.last_update // `"Never`"'"
    
    $lastUpdateDate = ""
    if ($dbCheck -and $dbCheck -ne "Never") {
        try {
            $lastUpdate = [DateTime]::Parse($dbCheck)
            $lastUpdateQatar = [System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId($lastUpdate, "Arab Standard Time")
            $lastUpdateDate = $lastUpdateQatar.ToString("yyyy-MM-dd")
            
            Write-Host "Last database update: $($lastUpdateQatar.ToString('yyyy-MM-dd HH:mm:ss')) Qatar time" -ForegroundColor Gray
            
            if ($lastUpdateDate -eq $TodayQatar) {
                Write-Host "SUCCESS: Database was updated TODAY!" -ForegroundColor Green
            } else {
                Write-Host "WARNING: Database was NOT updated today" -ForegroundColor Yellow
                $daysDiff = ([DateTime]::Parse($TodayQatar) - [DateTime]::Parse($lastUpdateDate)).Days
                Write-Host "   Last update was $daysDiff day(s) ago" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "ERROR: Could not parse last update date: $dbCheck" -ForegroundColor Red
        }
    } else {
        Write-Host "ERROR: Could not retrieve last update info from database" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Check current status
    Write-Host "4. Checking current fetch status..." -ForegroundColor White
    $statusCheck = Invoke-SshCommand "curl -s http://localhost:8084/progress.php | jq -r '.status // `"unknown`"'"
    
    if ($statusCheck) {
        Write-Host "Current status: $statusCheck" -ForegroundColor Gray
        
        if ($statusCheck -eq "completed") {
            Write-Host "SUCCESS: Last fetch completed successfully" -ForegroundColor Green
        } elseif ($statusCheck -eq "running") {
            Write-Host "INFO: Fetch is currently running" -ForegroundColor Blue
        } elseif ($statusCheck -eq "error") {
            Write-Host "ERROR: Last fetch ended with error" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "SUMMARY:" -ForegroundColor Cyan
    Write-Host "=======================================" -ForegroundColor Cyan
    
    if ($cronLogs -ne "No logs found for today" -and $dbCheck -and $lastUpdateDate -eq $TodayQatar) {
        Write-Host "SUCCESS: Cron job appears to have run successfully today" -ForegroundColor Green
    } elseif ($QatarTime.Hour -lt 8) {
        Write-Host "INFO: Cron job hasn't run yet (scheduled for 8:00 AM Qatar time)" -ForegroundColor Yellow
        $timeUntil = (8 - $QatarTime.Hour)
        Write-Host "   Next run in approximately $timeUntil hour(s)" -ForegroundColor Yellow
    } else {
        Write-Host "WARNING: Cron job may have failed or not executed today" -ForegroundColor Yellow
        Write-Host "   Check the logs above for more details" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure the server is accessible and Docker is running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Manual Commands:" -ForegroundColor Cyan
Write-Host "   Check cron logs: docker logs SW_CODES_CRON" -ForegroundColor Gray
Write-Host "   Manual trigger:  curl http://localhost:8084/trigger-fetch-codes.php" -ForegroundColor Gray
Write-Host "   Restart cron:    docker-compose -f scrape-sw-codes/docker-compose.yml restart cron" -ForegroundColor Gray