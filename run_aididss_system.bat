@echo off
echo =========================================================
echo  AI-DIDSS: AI-Based Identity & Document Screening System
echo  Master Release: v1.0.0-PRODUCTION-READY
echo =========================================================
echo.
echo Running Submodule Operational Verification...
python -m module13_final_validation.src.cli check
echo.
echo Starting FastAPI Backend API on port 8000...
start /b uvicorn module8_backend_api.src.main:app --host 0.0.0.0 --port 8000
echo.
echo Starting FraudLens Web Console UI on port 5174...
echo Visit http://localhost:5174 in your browser.
cd /d "%~dp0\fraudlens-new-frontend" && npm run dev -- --port 5174
