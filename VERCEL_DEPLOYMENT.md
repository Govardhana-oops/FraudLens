# FraudLens / AI-DIDSS — Vercel Frontend Deployment Guide

This guide provides exact, beginner-friendly instructions to deploy the new **FraudLens Officer Web Console** (`fraudlens-new-frontend`) to **Vercel**.

---

## Deployment Architecture

```
[Vercel Global Edge Network]
       │
       ▼
[React 18 + Vite Production SPA] (fraudlens-new-frontend)
       │
       │ (Calls Render Backend via VITE_API_BASE_URL)
       ▼
[Render FastAPI Backend] (https://<your-render-service>.onrender.com)
```

> **IMPORTANT:** Vercel hosts ONLY the new React frontend. The Python backend (Modules 1–8) runs independently on Render.

---

## Step-by-Step Vercel Deployment Instructions

### Step 1: Sign in to Vercel
1. Open your browser and go to **[https://vercel.com/](https://vercel.com/)**.
2. Sign in with your **GitHub** account.

---

### Step 2: Add New Project
1. On your Vercel Dashboard, click the **`Add New...`** button in the top right corner.
2. Select **`Project`** from the dropdown list.

---

### Step 3: Import Your GitHub Repository
1. In the **Import Git Repository** list, find your project: **`Govardhana-oops/FraudLens`**.
2. Click the **`Import`** button next to it.

---

### Step 4: Configure Project Settings (CRITICAL)
In the **Configure Project** screen, enter the following exact settings:

| Field Name | What to Click / Enter | Explanation / Why It Is Required |
| :--- | :--- | :--- |
| **Project Name** | `fraudlens-console` *(or default)* | Your application name on Vercel. |
| **Framework Preset** | **`Vite`** | Tells Vercel how to bundle the React + Vite frontend. |
| **Root Directory** | Click **`Edit`** and enter: **`fraudlens-new-frontend`** | **CRITICAL:** Tells Vercel to build only the new frontend directory and ignore backend Python folders. |
| **Build Command** | `npm run build` *(or leave default toggle off)* | Executes `tsc -b && vite build` to generate `dist/`. |
| **Output Directory** | `dist` *(or leave default toggle off)* | Points to the compiled HTML/CSS/JS assets. |
| **Install Command** | `npm install` *(or leave default toggle off)* | Installs React, Lucide icons, Tailwind, and dependencies. |

---

### Step 5: Add Environment Variables
Before clicking Deploy, expand the **`Environment Variables`** section:

1. In the **Key / Name** field, enter:
   ```text
   VITE_API_BASE_URL
   ```
2. In the **Value** field, paste your **Live Render Backend URL** from Step 8 of the Render guide:
   ```text
   https://<your-render-service-name>.onrender.com
   ```
   *(e.g., `https://fraudlens-api.onrender.com` — do NOT include a trailing slash)*
3. Click the **`Add`** button to save the variable.

---

### Step 6: Click Deploy
1. Click the blue **`Deploy`** button at the bottom of the screen.
2. Vercel will clone the `fraudlens-new-frontend` folder, install npm packages, run `vite build`, and deploy the production bundle to its global CDN.
3. Within 1–2 minutes, you will see the **"Congratulations! What's next?"** screen with live preview confetti.

---

### Step 7: Open & Verify Your Production Deployment
1. Click on the live deployment snapshot or the domain link (e.g. `https://fraudlens-console.vercel.app`).
2. Verify all pages:
   - **`/`**: Landing Portal loads with active "FastAPI Online" indicator.
   - **`/dashboard`**: Operational Dashboard displays real 0 initial counters.
   - **`/screening`**: Upload a test document image; verify real OCR fields, ICAO checks, and tampering risk score appear.
   - **`/evidence`**: Interactive 3D evidence relationship graph and field matrix display.
   - **`/database`**: Record appears in the searchable database.
   - **`/audit`**: Cryptographic SHA-256 chained audit logs display.
   - **`/health`**: Subsystem telemetry reports 7/7 ready submodules.

---

## Client-Side Route Rewrites (`vercel.json`)
The file `fraudlens-new-frontend/vercel.json` is already configured with:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
This ensures that direct browser refreshes or bookmarking URLs like `/screening` or `/evidence` work smoothly on Vercel without 404 errors.
