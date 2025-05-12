#Requires -RunAsAdministrator # Docker commands often need admin rights

<#
.SYNOPSIS
Script to streamline the startup of the Agent Zero environment.
Launches LM Studio and restarts the Agent Zero Docker container.

.DESCRIPTION
1. Defines necessary variables (paths, names).
2. Specifies the path to LM Studio (NEEDS TO BE EDITED BY USER).
3. Attempts to launch LM Studio.
4. Pauses and prompts the user to manually load the model and start the server in LM Studio.
5. Stops and removes any existing Agent Zero containers.
6. Pulls the latest image (optional, ensures availability).
7. Starts the new Agent Zero container with persistent volume mappings.
8. Provides access details.

.NOTES
- Requires PowerShell to be run as Administrator for Docker commands.
- USER MUST EDIT the $lmStudioExecutablePath variable below.
- User MUST manually interact with LM Studio to load the model and start the server when prompted.
- Assumes Docker Desktop is already running or configured to start with Windows.
- Assumes Agent Zero UI settings persist via the volume mount (verification still needed).
#>

# --- Configuration ---
$lmStudioExecutablePath = "C:\Path\To\Your\LM Studio\LM Studio.exe" # <-- IMPORTANT: EDIT THIS PATH
$containerName = "agent-zero"
$imageName = "frdel/agent-zero-run:hacking"
$hostDataPath = "C:\Projects\AgentZeroData" # Make sure this parent folder exists
$hostPort = 80

# --- Pre-checks ---
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check if LM Studio path is valid
if (-not (Test-Path $lmStudioExecutablePath -PathType Leaf)) {
    Write-Error "LM Studio executable not found at '$lmStudioExecutablePath'. Please edit the script with the correct path."
    # Optional: Pause script if path is wrong, or just exit
    # Read-Host "Press Enter to exit script..."
    exit 1
} else {
    Write-Host "[OK] LM Studio path seems valid: $lmStudioExecutablePath" -ForegroundColor Green
}

# Ensure base data directory exists (Docker needs it for volume mounts)
if (-not (Test-Path $hostDataPath -PathType Container)) {
    Write-Host "Base data directory '$hostDataPath' not found. Creating it..." -ForegroundColor Yellow
    try {
        New-Item -Path $hostDataPath -ItemType Directory -ErrorAction Stop | Out-Null
        Write-Host "[OK] Created directory: $hostDataPath" -ForegroundColor Green
    } catch {
        # Standard PowerShell error handling, will work correctly now
        Write-Error "Failed to create base data directory '$hostDataPath'. Please create it manually. Error: $($_.Exception.Message)"
        exit 1
    }
} else {
     Write-Host "[OK] Base data directory exists: $hostDataPath" -ForegroundColor Green
}


# --- Step 1: Launch LM Studio ---
Write-Host "Attempting to launch LM Studio..." -ForegroundColor Cyan
try {
    Start-Process -FilePath $lmStudioExecutablePath
    Write-Host "[OK] LM Studio launched." -ForegroundColor Green
} catch {
    # Standard PowerShell error handling, will work correctly now
    Write-Error "Failed to launch LM Studio. Error: $($_.Exception.Message)"
    # Consider whether to exit or continue if LM Studio fails to launch
    # exit 1
}

# --- Step 2: Manual LM Studio Server Start ---
Write-Host "*** USER ACTION REQUIRED ***" -ForegroundColor Yellow
Write-Host "1. Wait for LM Studio to open." -ForegroundColor Yellow
Write-Host "2. Select your desired AI model." -ForegroundColor Yellow
Write-Host "3. Go to the 'Local Server' tab (or equivalent)." -ForegroundColor Yellow
Write-Host "4. Click 'Start Server'." -ForegroundColor Yellow
Write-Host "5. Wait for the server to indicate it is running." -ForegroundColor Yellow
Read-Host -Prompt "Press Enter ONLY AFTER you have started the LM Studio server..."

# --- Step 3: Restart Agent Zero Container ---
Write-Host "Proceeding to restart Agent Zero Docker container..." -ForegroundColor Cyan

Write-Host "Attempting to stop existing container '$containerName'..."
docker stop $containerName | Out-Null # Suppress output if command fails when container doesn't exist
docker stop "agent-zero-insta" | Out-Null # Old name, just in case

Write-Host "Attempting to forcefully remove existing container '$containerName'..."
docker rm -f $containerName | Out-Null
docker rm -f "agent-zero-insta" | Out-Null

# Short delay to allow Docker daemon to release resources
Start-Sleep -Seconds 3

Write-Host "Pulling the Hacking Edition image '$imageName' (to ensure it's up-to-date)..."
try {
     docker pull $imageName -ErrorAction Stop
} catch {
    # Standard PowerShell error handling, will work correctly now
    Write-Error "Failed to pull image '$imageName'. Check Docker connection and image name. Error: $($_.Exception.Message)"
    exit 1
}


Write-Host "Starting new Agent Zero Hacking Edition container '$containerName'..."
try {
    # Note: Using ${hostPort} and ${hostDataPath} for clarity in docker run - these will expand correctly
    docker run -d --name $containerName -p ${hostPort}:80 --restart unless-stopped `
        -v "${hostDataPath}\config:/app/config" `
        -v "${hostDataPath}\knowledge:/app/knowledge" `
        -v "${hostDataPath}\memory:/app/memory" `
        -v "${hostDataPath}\database:/app/database" `
        -v "${hostDataPath}\logs:/app/logs" `
        $imageName -ErrorAction Stop

     Start-Sleep -Seconds 3 # Give container a moment to initialize
     # Optional: Check if container is running
     $status = docker ps -f "name=$containerName" --format "{{.Status}}"
     if ($status -like "Up*") {
        Write-Host "[OK] Container '$containerName' started successfully." -ForegroundColor Green
     } else {
        Write-Warning "Container '$containerName' may not have started correctly. Status: $status"
        docker logs $containerName # Show logs if it failed
     }

} catch {
     # Standard PowerShell error handling, will work correctly now
     Write-Error "Failed to start container '$containerName'. Error: $($_.Exception.Message)"
     # Attempt to show logs if the container was created but failed to run
     docker logs $containerName 2>$null
     exit 1
}


Write-Host "--------------------------------------------------" -ForegroundColor Green
Write-Host "Startup Script Completed." -ForegroundColor Green
Write-Host "LM Studio should be running with the server started (Manual Step)." -ForegroundColor Green
Write-Host "Agent Zero Hacking Edition container '$containerName' should be running." -ForegroundColor Green
Write-Host "Access Agent Zero UI at http://localhost:$hostPort." -ForegroundColor Green
# Standard PowerShell variable expansion, will work correctly now
Write-Host "Verify Agent Zero settings in UI - hoping they persisted from '$($hostDataPath)\config'." -ForegroundColor Yellow
Write-Host "--------------------------------------------------"

