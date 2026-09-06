# FraudLens / AI-DIDSS — Render Backend Deployment Guide

This guide provides exact, beginner-friendly instructions to deploy the existing Python FastAPI backend (`module8_backend_api` and Modules 1–7) to **Render** using Docker.

---

## Architecture Overview

```
[Browser / Client]
       │
       ▼
[Vercel Frontend] (fraudlens-new-frontend)
       │
       │ (VITE_API_BASE_URL: https://<your-render-service>.onrender.com)
       ▼
[Render Web Service] (Docker: Python 3.11-slim)
       │
       ├─► Module 8 (FastAPI Gateway)
       ├─► Module 7 (Integration Engine Orchestrator)
       │      ├─► Module 1 (Multi-Engine Document OCR: EasyOCR / Tesseract)
       │      ├─► Module 2 (Rule-Based Validation & ICAO 9303 Checksums)
       │      ├─► Module 3 (Forensic ELA & Tamper Neural Networks)
       │      ├─► Module 4 (Biometric 1:1 Face Verification & Liveness)
       │      └─► Module 5 (Explainable Evidence & Dimensional Risk)
       └─► Module 6 (Database Sync, SLTD Watchlist, Cryptographic SHA-256 Ledger)
```

---

## Step-by-Step Render Deployment Instructions

### Step 1: Sign in to Render
1. Open your browser and go to **[https://dashboard.render.com/](https://dashboard.render.com/)**.
2. Sign in with your **GitHub** account (where the repository `Govardhana-oops/FraudLens` is hosted).

---

### Step 2: Create a New Web Service
1. In the top right corner of the Render Dashboard, click the blue **`New +`** button.
2. From the dropdown menu, select **`Web Service`**.

---

### Step 3: Connect Your GitHub Repository
1. Under **Connect a repository**, find **`Govardhana-oops/FraudLens`** (or your repository name).
2. Click the **`Connect`** button next to it.

---

### Step 4: Configure the Web Service Settings
Enter the following exact settings in the configuration form:

| Setting Name | Exact Value to Select / Enter | Why It Is Required |
| :--- | :--- | :--- |
| **Name** | `fraudlens-api` *(or any name you prefer)* | Identifies your backend service URL on Render (e.g. `https://fraudlens-api.onrender.com`). |
| **Region** | `Singapore (Southeast Asia)` or `Frankfurt (EU Central)` | Choose the region closest to your users for lower latency. |
| **Branch** | `main` | Deploys the latest verified code from your main Git branch. |
| **Root Directory** | *(Leave completely blank / empty)* | The root directory contains `Dockerfile` and all submodules. |
| **Runtime / Environment** | **`Docker`** | Render will automatically build the container using the root `Dockerfile`. |
| **Dockerfile Path** | `./Dockerfile` | Points to the production multi-stage Docker container. |
| **Instance Type** | **`Free`** *(or Starter for faster inference)* | Free tier provides 512MB RAM and free monthly hosting. |

---

### Step 5: Configure Health Check Path
1. Scroll down and click **`Advanced`** (if collapsed).
2. Find the **Health Check Path** field.
3. Enter:
   ```text
   /api/v1/health
   ```
4. *Why it is required:* Render continuously verifies that the FastAPI gateway and all 7 submodules are initialized before routing live traffic.

---

### Step 6: Configure Environment Variables
Under the **Environment Variables** section in Render, click **`Add Environment Variable`** and add the following keys:

| Key | Recommended Value | Description |
| :--- | :--- | :--- |
| **`PORT`** | `8000` | Port for the uvicorn ASGI server (Render manages this automatically). |
| **`PYTHONUNBUFFERED`** | `1` | Ensures real-time stdout logs appear in the Render console. |
| **`ALLOWED_ORIGINS`** | `*` *(or your Vercel URL once deployed)* | Allows the Vercel frontend to make secure cross-origin API requests. |
| **`TORCH_HOME`** | `/tmp/.cache/torch` | Writable cache path for PyTorch deep learning weights in the container. |
| **`EASYOCR_MODULE_PATH`** | `/tmp/.EasyOCR` | Writable directory for OCR model checkpoints. |

---

### Step 7: Deploy the Service
1. Click the blue **`Create Web Service`** button at the bottom of the page.
2. Render will begin pulling the repository, building the Docker container, and starting the FastAPI server.
3. Watch the build logs. Within 3–5 minutes, you will see:
   ```text
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:10000 (Press CTRL+C to quit)
   ==> Your service is live 🎉
   ```

---

### Step 8: Verify Your Live Backend
Once Render displays the green **`Live`** badge:

1. **Copy Your Live Render URL**:
   - Locate the URL at the top left under the service name (e.g. `https://fraudlens-api.onrender.com`).

2. **Test Health Endpoint in Your Browser**:
   - Open: `https://<your-render-url>/api/v1/health`
   - You should see:
     ```json
     {
       "status": "HEALTHY",
       "version": "1.0.0",
       "service": "AI-DIDSS Verification Decision Support API",
       "uptime_seconds": 12.4,
       "modules_ready": [
         "module1_ocr",
         "module2_document_validation",
         "module3_tampering_detection",
         "module4_face_verification",
         "module5_explainable_evidence",
         "module6_database_sync",
         "module7_integration_engine"
       ]
     }
     ```

3. **Test Interactive Swagger Documentation**:
   - Open: `https://<your-render-url>/docs`
   - Verify all 5 API endpoints (`/health`, `/screening/inspect`, `/audit/logs`, `/sync/differential`, `/watchlist/check/{doc_number}`) load interactively.

---

### Step 9: Save the URL for Vercel
Keep this Render URL handy. You will paste it as `VITE_API_BASE_URL` in the Vercel frontend deployment settings.
