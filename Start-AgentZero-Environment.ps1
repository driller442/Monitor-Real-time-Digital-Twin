#Requires -RunAsAdministrator # Docker commands often need admin rights

<#
.SYNOPSIS
Script to streamline the startup of the Agent Zero environment.
Launches LM Studio and restarts the Agent Zero Docker container.
Creates baseline settings.json and .env files.
MANUAL UI CONFIGURATION WILL BE REQUIRED for LLM settings. (Attempt 9)
Uses frdel/agent-zero-run:hacking image.
#>

# --- Configuration ---
$lmStudioExecutablePath = "C:\Users\aiaio\AppData\Local\Programs\LM Studio\LM Studio.exe"
$containerName = "agent-zero"
$imageName = "frdel/agent-zero-run:hacking"
$hostDataPath = "C:\Projects\AgentZeroData" # Base for all persistent data
$hostPort = 80

# Paths for generated config files on HOST
$hostTmpPath = Join-Path -Path $hostDataPath -ChildPath "tmp"
$settingsJsonPath = Join-Path -Path $hostTmpPath -ChildPath "settings.json"
$envFilePath = Join-Path -Path $hostDataPath -ChildPath "runtime.env" # For LM_STUDIO_BASE_URL & API_KEY as fallback

# --- Desired Settings for settings.json (as a baseline) ---
$ChatModelProvider = "LMSTUDIO" 
$ChatModelName = "dolphin3.0-llama3.1-8b"
$ChatModelCtxLength = 4096 
$ChatModelCtxHistory = 0.7
$ChatModelVision = $false
$ChatModelKwargs = @{ temperature = "0" }
$UtilModelProvider = "LMSTUDIO" 
$UtilModelName = "dolphin3.0-llama3.1-8b" 
$UtilModelCtxLength = 4096
$UtilModelCtxInput = 0.7
$UtilModelKwargs = @{ temperature = "0" }
$EmbedModelProvider = "LMSTUDIO" 
$EmbedModelName = "dolphin3.0-llama3.1-8b" 
$EmbedModelKwargs = @{}
$BrowserModelProvider = "LMSTUDIO"
$BrowserModelName = "dolphin3.0-llama3.1-8b"
$BrowserModelVision = $false
$BrowserModelKwargs = @{ temperature = "0" }
$OpenAIApiKey = "none" 
$LMStudioBaseUrl = "http://127.0.0.1:1234/v1" 

$settingsObject = @{
    chat_model_provider = $ChatModelProvider; chat_model_name = $ChatModelName; chat_model_kwargs = $ChatModelKwargs; chat_model_ctx_length = $ChatModelCtxLength; chat_model_ctx_history = $ChatModelCtxHistory; chat_model_vision = $ChatModelVision; chat_model_rl_requests = 0; chat_model_rl_input = 0; chat_model_rl_output = 0;
    util_model_provider = $UtilModelProvider; util_model_name = $UtilModelName; util_model_kwargs = $UtilModelKwargs; util_model_ctx_length = $UtilModelCtxLength; util_model_ctx_input = $UtilModelCtxInput; util_model_rl_requests = 0; util_model_rl_input = 0; util_model_rl_output = 0;
    embed_model_provider = $EmbedModelProvider; embed_model_name = $EmbedModelName; embed_model_kwargs = $EmbedModelKwargs; embed_model_rl_requests = 0; embed_model_rl_input = 0;
    browser_model_provider = $BrowserModelProvider; browser_model_name = $BrowserModelName; browser_model_vision = $BrowserModelVision; browser_model_kwargs = $BrowserModelKwargs;
    api_keys = @{ openai = $OpenAIApiKey };
    auth_login = ""; auth_password = ""; root_password = ""; agent_prompts_subdir = "default"; agent_memory_subdir = "default"; agent_knowledge_subdir = "custom"; rfc_auto_docker = $true; rfc_url = "localhost"; rfc_password = ""; rfc_port_http = 55080; rfc_port_ssh = 55022;
    stt_model_size = "base"; stt_language = "en"; stt_silence_threshold = 0.3; stt_silence_duration = 1000; stt_waiting_timeout = 2000
}
$settingsJsonContent = $settingsObject | ConvertTo-Json -Depth 5
$envFileContent = @"
LM_STUDIO_BASE_URL="$LMStudioBaseUrl"
OPENAI_API_KEY="$OpenAIApiKey"
CUSTOM_ENV_LOADED="true_from_host_script_v9_final"
"@

# --- Pre-checks & config file creation ---
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (-not (Test-Path $lmStudioExecutablePath -PathType Leaf)) { Write-Error "LM Studio executable not found: '$lmStudioExecutablePath'."; exit 1 } else { Write-Host "[OK] LM Studio path valid." -FG Green }
if (-not (Test-Path $hostDataPath)) { Write-Host "Base data directory '$hostDataPath' not found. Creating it..."; try { New-Item $hostDataPath -ItemType Directory -EA Stop|Out-Null; Write-Host "[OK] Created directory." -FG Green } catch { Write-Error "Failed to create '$hostDataPath': $($_.Exception.Message)"; exit 1 } } else { Write-Host "[OK] Base data directory exists." -FG Green }
if (-not (Test-Path $hostTmpPath)) { Write-Host "Host tmp directory '$hostTmpPath' not found. Creating it..."; try { New-Item $hostTmpPath -ItemType Directory -EA Stop|Out-Null; Write-Host "[OK] Created directory." -FG Green } catch { Write-Error "Failed to create '$hostTmpPath': $($_.Exception.Message)"; exit 1 } }
Write-Host "Creating/Updating '$settingsJsonPath'..."
try { Set-Content -Path $settingsJsonPath -Value $settingsJsonContent -Encoding UTF8 -Force; Write-Host "[OK] settings.json prepared." -FG Green } catch { Write-Error "Failed to create '$settingsJsonPath': $($_.Exception.Message)"; exit 1 }
Write-Host "Creating/Updating '$envFilePath'..."
try { Set-Content -Path $envFilePath -Value $envFileContent -Encoding UTF8 -Force; Write-Host "[OK] runtime.env prepared." -FG Green } catch { Write-Error "Failed to create '$envFilePath': $($_.Exception.Message)"; exit 1 }

# --- Step 1: Launch LM Studio ---
Write-Host "Attempting to launch LM Studio..." -ForegroundColor Cyan
try { Start-Process -FilePath $lmStudioExecutablePath; Write-Host "[OK] LM Studio launched." -ForegroundColor Green }
catch { Write-Error "Failed to launch LM Studio. Error: $($_.Exception.Message)" }

# --- Step 2: Manual LM Studio Server Start ---
Write-Host "*** USER ACTION REQUIRED ***"
Write-Host "1. Wait for LM Studio." -FG Yellow; Write-Host "2. Select model '$($settingsObject.chat_model_name)'." -FG Yellow; Write-Host "3. Go to 'Local Server' tab." -FG Yellow; Write-Host "4. Click 'Start Server'." -FG Yellow; Write-Host "5. Wait for server." -FG Yellow
Read-Host -Prompt "Press Enter ONLY AFTER LM Studio server is running..."

# --- Step 3: Restart Agent Zero Container ---
Write-Host "Proceeding to restart Agent Zero (Attempt 9 - Final)..." -ForegroundColor Cyan
docker stop $containerName -t 2 | Out-Null; docker stop "agent-zero-insta" -t 2 | Out-Null
docker rm -f $containerName | Out-Null; docker rm -f "agent-zero-insta" | Out-Null
Start-Sleep -Seconds 2
Write-Host "Pulling image '$imageName'..."
try { docker pull $imageName } catch { Write-Error "Failed to pull '$imageName': $($_.Exception.Message)"; exit 1 }
Write-Host "Starting Agent Zero container..."
try {
    $dockerRunParams = @(
        "run", "-d", "--name", $containerName, "-p", "${hostPort}:80", "--restart", "unless-stopped",
        "-v", "${hostDataPath}\config:/app/config", "-v", "${hostDataPath}\knowledge:/app/knowledge",
        "-v", "${hostDataPath}\memory:/app/memory", "-v", "${hostDataPath}\database:/app/database",
        "-v", "${hostDataPath}\logs:/app/logs", "-v", "${hostTmpPath}:/app/tmp",
        "-v", "${envFilePath}:/app/.env:ro", "-e", "OPENAI_API_KEY=$OpenAIApiKey", # Explicitly pass API key also
        $imageName 
    )
    docker @dockerRunParams
     Start-Sleep -Seconds 3
     $status = docker ps -f "name=$containerName" --format "{{.Status}}"
     if ($status -like "Up*") { Write-Host "[OK] Container '$containerName' started. Status: $status" -FG Green }
     else { Write-Warning "Container '$containerName' not started. Status: $status"; docker logs $containerName }
} catch { Write-Error "Failed to start '$containerName': $($_.Exception.Message)"; docker logs $containerName 2>$null; exit 1 }

Write-Host "--------------------------------------------------" -ForegroundColor Green
Write-Host "Startup Script Completed." -ForegroundColor Green
Write-Host "Agent Zero Docker container '$containerName' should be running."
Write-Host "Access Agent Zero UI at http://localhost:$hostPort."
Write-Host ""
Write-Host "IMPORTANT MANUAL STEPS REQUIRED IN AGENT ZERO UI:" -ForegroundColor Yellow
Write-Host "1. Go to Settings." -ForegroundColor Yellow
Write-Host "2. For Chat, Utility, and Web Browser models:" -ForegroundColor Yellow
Write-Host "   - Select Provider: LMSTUDIO (or OpenAI if LMSTUDIO not available)." -ForegroundColor Yellow
Write-Host "   - Set Base URL: $LMStudioBaseUrl" -ForegroundColor Yellow
Write-Host "   - Set API Key: $OpenAIApiKey (or leave blank if LM Studio provider ignores it)." -ForegroundColor Yellow
Write-Host "   - Set Model Name: $($settingsObject.chat_model_name)" -ForegroundColor Yellow
Write-Host "3. For Embedding Model:" -ForegroundColor Yellow
Write-Host "   - Select Provider: LMSTUDIO (if using main model for embeddings) or OpenAI." -ForegroundColor Yellow
Write-Host "   - Set Model Name: $($settingsObject.embed_model_name) (or your preferred embedding model)." -ForegroundColor Yellow
Write-Host "4. Click SAVE in the Agent Zero settings page." -ForegroundColor Yellow
Write-Host "--------------------------------------------------"
