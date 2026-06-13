# Pro3duct Startup & Diagnostic Script
# Automatically launches Docker Desktop if offline, checks dependencies, and spins up the platform.

Clear-Host
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host "          ◈ Pro3duct Interactive Digital Twin ◈" -ForegroundColor Magenta
Write-Host "              Startup & Diagnostics Runner" -ForegroundColor Magenta
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host ""

$DockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
$DockerIsReady = $false

# 1. Check if Docker Daemon is running
Write-Host "[*] Checking Docker daemon status..." -ForegroundColor Cyan
try {
    $dockerInfo = docker info --format '{{.Name}}' 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] Docker is online and running." -ForegroundColor Green
        $DockerIsReady = $true
    }
} catch {
    # Docker not running or not installed
}

# 2. Attempt to start Docker Desktop if it's offline
if (-not $DockerIsReady) {
    Write-Host "[!] Docker daemon is not responding." -ForegroundColor Yellow
    if (Test-Path $DockerPath) {
        Write-Host "[*] Launching Docker Desktop automatically at: $DockerPath" -ForegroundColor Cyan
        Start-Process $DockerPath
        
        Write-Host "[*] Waiting for Docker daemon to initialize (this can take up to 45s)..." -ForegroundColor Cyan
        for ($i = 1; $i -le 45; $i++) {
            Write-Progress -Activity "Initializing Docker Daemon" -Status "Attempt $i / 45" -PercentComplete (($i / 45) * 100)
            Start-Sleep -Seconds 1
            
            try {
                $check = docker info --format '{{.Name}}' 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $DockerIsReady = $true
                    Write-Progress -Activity "Initializing Docker Daemon" -Completed
                    Write-Host "`n[+] Docker daemon is now online!" -ForegroundColor Green
                    break
                }
            } catch {}
        }
    } else {
        Write-Host "[-] Docker Desktop executable not found at typical path: $DockerPath" -ForegroundColor Red
        Write-Host "[-] Please ensure Docker Desktop is installed and running." -ForegroundColor Red
    }
}

# 3. Spin up environment
if ($DockerIsReady) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Magenta
    Write-Host "[*] Launching all services via Docker Compose..." -ForegroundColor Cyan
    Write-Host "========================================================" -ForegroundColor Magenta
    Write-Host ""
    docker compose up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[+] Pro3duct is running in the background." -ForegroundColor Green
        Write-Host "[+] Application: http://localhost:3000" -ForegroundColor Green
        Write-Host "[+] API docs:    http://localhost:8000/api/docs" -ForegroundColor Green
        Write-Host "[+] Temporal UI: http://localhost:8233" -ForegroundColor Green
        Write-Host ""
        docker compose ps
    } else {
        Write-Host "[-] Docker Compose failed to start Pro3duct." -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Red
    Write-Host "[-] Critical Error: Docker is unavailable." -ForegroundColor Red
    Write-Host "========================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "WOULD YOU LIKE TO START FRONTEND AND BACKEND LOCALLY WITHOUT DOCKER?" -ForegroundColor Yellow
    Write-Host "(Note: DB, Redis, MinIO, and Temporal must be started manually if you run locally)" -ForegroundColor Yellow
    Write-Host ""
    $choice = Read-Host "Start local development servers? (Y/N)"
    
    if ($choice -eq "Y" -or $choice -eq "y") {
        Write-Host "[*] Bootstrapping local dev servers..." -ForegroundColor Cyan
        
        # Start backend in a new PowerShell window
        Write-Host "[*] Starting FastAPI Backend on port 8000..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        
        # Start frontend in a new PowerShell window
        Write-Host "[*] Starting Next.js Frontend on port 3000..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; pnpm install; pnpm dev"
        
        Write-Host "[+] Local windows initialized. Check separate prompt instances." -ForegroundColor Green
    } else {
        Write-Host "[*] Exiting. Please turn on Docker Desktop and try again." -ForegroundColor Yellow
    }
}
