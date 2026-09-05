# AI-DIDSS Master Turnkey Launcher Script

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " AI-DIDSS: AI-Based Identity & Document Screening System" -ForegroundColor Cyan
Write-Host " Master Release: v1.0.0-PRODUCTION-READY" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Run Subsystem Verification
python -m module13_final_validation.src.cli check

# 2. Start FastAPI Backend API
Write-Host "`nStarting FastAPI Backend API Server on http://localhost:8000..." -ForegroundColor Yellow
$backendJob = Start-Process -FilePath "uvicorn" -ArgumentList "module8_backend_api.src.main:app --host 0.0.0.0 --port 8000" -PassThru

# 3. Serve Officer Web Console
Write-Host "`nServing Inspection Officer Web Console on http://localhost:3000..." -ForegroundColor Green
Write-Host "Open your browser to: http://localhost:3000" -ForegroundColor White
python -m http.server 3000 --directory module9_officer_console
