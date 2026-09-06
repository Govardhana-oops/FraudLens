# FraudLens / AI-DIDSS — Old Frontend Migration & Replacement Audit

**Date:** September 6, 2026  
**Status:** Audit Complete  
**Replacement Target:** `C:\Users\guvva\OneDrive\Desktop\PROTOTYPE\fraudlens-new-frontend`  

---

## 1. Identified Old Frontend Components

| Component | Location / Files | Role in Previous Architecture | Migration Action |
| :--- | :--- | :--- | :--- |
| **Old Web Console (Module 9)** | `module9_officer_console/` (`index.html`, `app.js`, `index.css`) | Legacy vanilla HTML/JS/CSS frontend | **Deactivated as Production UI.** Replaced by `fraudlens-new-frontend`. Retained only for backwards reference/unit tests. |
| **Streamlit Web App** | `streamlit_app.py`, `.streamlit/` | Temporary standalone Python UI | **Deactivated as Production UI.** Not required by FastAPI backend or Vercel/Render production pipelines. |
| **FastAPI Static Mount** | `module8_backend_api/src/main.py` (`/console` mount) | Previously mounted `module9_officer_console` directory | **Updated** to mount `fraudlens-new-frontend/dist` when compiled, deactivating Module 9 routing. |
| **Root Vercel Deployment Configuration** | `vercel.json` | Previously rewrote requests to `/module9_officer_console/` | **Replaced** with Vite SPA configuration targeting `fraudlens-new-frontend`. |
| **Local Launcher Batch & PowerShell Scripts** | `START_SYSTEM.bat`, `run_aididss_system.bat`, `run_aididss_system.ps1` | Previously spawned `http.server 3000 --directory module9_officer_console` | **Updated** to launch `fraudlens-new-frontend` dev server on port 5174. |

---

## 2. Shared File & Dependency Protection Review

Before making any migration changes, all files were cross-referenced against backend modules (Modules 1–8) and tests:

1. **Frozen Modules 1–7:** Zero dependency on `module9_officer_console` or `streamlit_app.py`. Screening pipelines, OCR engines, validation checksums, forensic tampering neural nets, and biometric verification operate completely independently.
2. **Module 8 Backend API:** Operates as a standalone headless REST API (`/api/v1/health`, `/api/v1/screening/inspect`, `/api/v1/audit/logs`, `/api/v1/sync/differential`, `/api/v1/watchlist/check/{doc_number}`).
3. **Dependencies:** `requirements.txt` does NOT contain `streamlit` or any frontend packages.
4. **Conclusion:** It is completely safe to migrate production routing and launcher scripts to `fraudlens-new-frontend`.

---

## 3. New Production Frontend Specifications

- **Location:** `C:\Users\guvva\OneDrive\Desktop\PROTOTYPE\fraudlens-new-frontend`
- **Technology:** React 18, TypeScript 5.5, Vite 5.4, Tailwind CSS 3.4
- **State Management:** Central `AppContext` with `localStorage` persistence and 100% dynamic KPI calculations.
- **API Client:** RESTful HTTP client targeting `VITE_API_BASE_URL` (Local: `http://localhost:8000`, Production: Render HTTPS URL).
- **Design:** Projector-ready 3D cybersecurity console (`#080D16` deep midnight canvas, `#1A283F` elevated cards, `#2DD4BF` teal glow accents).
- **Pages:** Complete 11-page suite (Landing, Dashboard, Screening, Biometrics, Evidence Dossier, Database, Sync, Audit, Diagnostics, Settings, About).
