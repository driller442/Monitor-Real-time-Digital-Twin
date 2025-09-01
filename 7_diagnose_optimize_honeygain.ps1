# Script: 7_diagnose_optimize_honeygain.ps1
# Purpose: Combines Honeygain diagnostics (finding traces) and optimization (maximizing uptime/bandwidth).
# Usage: Run as Administrator.

# --- Configuration ---
$logPath = "$env:USERPROFILE\Desktop\Honeygain_Combined_Report.txt"
$honeygainExePath = "C:\Program Files (x86)\Honeygain\Honeygain.exe" # Standard installation path

# --- Initial Logging ---
"--- Honeygain Combined Diagnostic & Optimization Report ---" | Out-File $logPath -Encoding UTF8

# Add a timestamp to the existing file or create if missing
"Script file saved/committed on: $($(Get-Date))" | Tee-Object -FilePath $logPath -Append
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 1: Installation Check ---
"1. Checking Honeygain Installation..." | Tee-Object -FilePath $logPath -Append
if (Test-Path $honeygainExePath) {
    "   [OK] Honeygain executable found at: $honeygainExePath" | Tee-Object -FilePath $logPath -Append
} else {
    "   [ERROR] Honeygain executable not found at: $honeygainExePath" | Tee-Object -FilePath $logPath -Append
    "   Please install Honeygain from https://www.honeygain.com/ and run this script again." | Tee-Object -FilePath $logPath -Append
    Write-Host "ERROR: Honeygain not found. Check $logPath for details. Halting optimization steps." -ForegroundColor Red
    # Stop further optimization if not installed, but allow diagnostic checks to continue
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 2: Running Process Check ---
"2. Checking Running Honeygain Processes..." | Tee-Object -FilePath $logPath -Append
$hgProcesses = Get-Process | Where-Object { $_.ProcessName -like "*honeygain*" } -ErrorAction SilentlyContinue
if ($hgProcesses) {
    "   [INFO] Found running Honeygain process(es):" | Tee-Object -FilePath $logPath -Append
    $hgProcesses | Select-Object ProcessName, Id, StartTime | Format-Table -AutoSize | Out-String | Tee-Object -FilePath $logPath -Append
    if ($hgProcesses.Count -gt 1) {
        "   [WARNING] Multiple Honeygain processes detected. This can cause 'Network Overused' issues and is not recommended." | Tee-Object -FilePath $logPath -Append
        # Optional: Consider adding logic to stop extras if needed, but manual intervention might be safer.
    }
} else {
    "   [INFO] No running Honeygain process found." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 3: Autostart Configuration Check & Setup ---
"3. Checking/Configuring Autostart (Run Key)..." | Tee-Object -FilePath $logPath -Append
if (Test-Path $honeygainExePath) {
    $runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
    $regEntryName = "Honeygain"
    # Ensure quotes around path, then add -silent
    $expectedRegValue = ""$honeygainExePath"" -silent"

    try {
        # Ensure the Run key path exists
        if (-not (Test-Path $runKey)) {
             New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion" -Name "Run" -Force | Out-Null
             "   [INFO] Created missing Run key: $runKey" | Tee-Object -FilePath $logPath -Append
        }

        $currentRegValue = Get-ItemPropertyValue -Path $runKey -Name $regEntryName -ErrorAction SilentlyContinue
        if ($currentRegValue -eq $expectedRegValue) {
            "   [OK] Honeygain autostart entry found and correctly configured with '-silent'." | Tee-Object -FilePath $logPath -Append
        } else {
            if ($currentRegValue) {
                "   [WARNING] Honeygain autostart entry found but value is incorrect: '$currentRegValue'." | Tee-Object -FilePath $logPath -Append
            } else {
                "   [INFO] Honeygain autostart entry not found." | Tee-Object -FilePath $logPath -Append
            }
            "   Setting/Updating autostart entry to: $expectedRegValue" | Tee-Object -FilePath $logPath -Append
            Set-ItemProperty -Path $runKey -Name $regEntryName -Value $expectedRegValue -Force -ErrorAction Stop
            "   [OK] Autostart entry configured." | Tee-Object -FilePath $logPath -Append
        }
    } catch {
        "   [ERROR] Failed to configure autostart entry: $($_.Exception.Message). Requires Admin rights or registry access." | Tee-Object -FilePath $logPath -Append
    }
} else {
    "   [INFO] Skipping autostart configuration as Honeygain is not installed." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 4: Task Scheduler Check (Alternative Autostart) ---
"4. Checking Task Scheduler for Honeygain Entries..." | Tee-Object -FilePath $logPath -Append
try {
    $scheduledTasks = Get-ScheduledTask | Where-Object { $_.TaskName -like "*honeygain*" -or $_.TaskPath -like "*honeygain*" -or ($_.Actions.Execute -like "*Honeygain.exe*") } -ErrorAction SilentlyContinue
    if ($scheduledTasks) {
        "   [INFO] Found Honeygain-related scheduled task(s):" | Tee-Object -FilePath $logPath -Append
        $scheduledTasks | Format-List TaskName, TaskPath, State, Actions | Out-String | Tee-Object -FilePath $logPath -Append
    } else {
        "   [INFO] No Honeygain-related scheduled tasks found." | Tee-Object -FilePath $logPath -Append
    }
} catch {
     "   [ERROR] Failed to query Task Scheduler: $($_.Exception.Message)." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 5: Sleep Mode Configuration (Optimize for Uptime) ---
"5. Configuring Power Settings (Disabling Sleep)..." | Tee-Object -FilePath $logPath -Append
try {
    # Requires Administrator privileges
    powercfg -change -standby-timeout-ac 0
    powercfg -change -standby-timeout-dc 0
    "   [OK] Sleep timeouts set to 'Never' for AC and DC power to maximize uptime." | Tee-Object -FilePath $logPath -Append
} catch {
    "   [ERROR] Failed to set power settings: $($_.Exception.Message). Run script as Administrator." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 6: IPv6 Configuration (Optimize for Connectivity) ---
"6. Configuring Network Adapters (Disabling IPv6)..." | Tee-Object -FilePath $logPath -Append
try {
    # Requires Administrator privileges
    $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    $ipv6DisabledCount = 0
    if ($adapters) {
        foreach ($adapter in $adapters) {
            $binding = Get-NetAdapterBinding -Name $adapter.Name -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue
            if ($binding -and $binding.Enabled) {
                Disable-NetAdapterBinding -Name $adapter.Name -ComponentID ms_tcpip6 -PassThru -ErrorAction SilentlyContinue
                "   [OK] Disabled IPv6 on active adapter: $($adapter.Name)" | Tee-Object -FilePath $logPath -Append
                $ipv6DisabledCount++
            } elseif ($binding -and -not $binding.Enabled) {
                "   [INFO] IPv6 already disabled on active adapter: $($adapter.Name)" | Tee-Object -FilePath $logPath -Append
            }
            # Ignore if binding doesn't exist
        }
        if ($ipv6DisabledCount -eq 0) {
              "   [INFO] No active adapters required IPv6 disabling or were already disabled." | Tee-Object -FilePath $logPath -Append
         }
    } else {
         "   [INFO] No active network adapters found to check for IPv6." | Tee-Object -FilePath $logPath -Append
    }
} catch {
    "   [ERROR] Failed during IPv6 configuration: $($_.Exception.Message). Run script as Administrator." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 7: Ensure Honeygain is Running Silently ---
"7. Ensuring Honeygain is Running..." | Tee-Object -FilePath $logPath -Append
if (Test-Path $honeygainExePath) {
    $hgProcesses = Get-Process | Where-Object { $_.ProcessName -like "*honeygain*" } -ErrorAction SilentlyContinue # Re-check processes
    if (-not $hgProcesses) {
        "   [INFO] Honeygain is not running. Starting it silently..." | Tee-Object -FilePath $logPath -Append
        try {
            Start-Process -FilePath $honeygainExePath -ArgumentList "-silent" -ErrorAction Stop
            "   [OK] Honeygain started silently." | Tee-Object -FilePath $logPath -Append
        } catch {
            "   [ERROR] Failed to start Honeygain: $($_.Exception.Message)" | Tee-Object -FilePath $logPath -Append
        }
    } else {
        "   [INFO] Honeygain is already running." | Tee-Object -FilePath $logPath -Append
    }
} else {
     "   [INFO] Cannot start Honeygain as it's not installed." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 8: Log Current Bandwidth Usage ---
"8. Logging Current Network Adapter Statistics..." | Tee-Object -FilePath $logPath -Append
try {
    Get-NetAdapterStatistics | Select-Object Name, InterfaceDescription, ReceivedBytes, SentBytes | Format-Table -AutoSize | Out-String | Tee-Object -FilePath $logPath -Append
} catch {
    "   [ERROR] Failed to get network statistics: $($_.Exception.Message)." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append

# --- Step 9: File Evidence Search (Diagnostic) ---
"9. Searching for Honeygain Related Files (Logs, DBs, Configs)..." | Tee-Object -FilePath $logPath -Append
$searchPaths = @(
    "$env:USERPROFILE\AppData\Roaming\Honeygain",
    "$env:USERPROFILE\AppData\Local\Honeygain",
    "C:\ProgramData\Honeygain" # Common location for service data/logs
    # Add other likely locations if needed
)
$includePatterns = @('*honeygain*', '*.sqlite*', '*.log', 'uptime*', 'config*') # Added config
$foundFiles = @()

foreach ($path in $searchPaths) {
     if (Test-Path $path) {
         "   Searching in $path ..." | Tee-Object -FilePath $logPath -Append
         $filesInPath = Get-ChildItem -Path $path -Recurse -Include $includePatterns -File -ErrorAction SilentlyContinue
         if ($filesInPath) {
             $foundFiles += $filesInPath
             $filesInPath | Select-Object FullName, LastWriteTime, Length | Format-Table -AutoSize | Out-String | Tee-Object -FilePath $logPath -Append
         } else {
             "   No relevant files found in $path." | Tee-Object -FilePath $logPath -Append
         }
     } else {
          "   [INFO] Search path not found, skipping: $path" | Tee-Object -FilePath $logPath -Append
     }
}
if ($foundFiles.Count -eq 0) {
    "   [INFO] No Honeygain-related files found in common locations." | Tee-Object -FilePath $logPath -Append
}
"
" | Tee-Object -FilePath $logPath -Append


# --- Final Message ---
"[OK] Script finished. Comprehensive report saved to: $logPath" | Tee-Object -FilePath $logPath -Append
Write-Host "
[OK] Script finished. Review the detailed report at: $logPath" -ForegroundColor Green
Write-Host "Reminder: For maximum potential earnings (Content Delivery), ensure 'Content Delivery' is enabled manually in the Honeygain application settings." -ForegroundColor Yellow
