# AI-DIDSS: Beginner's Guide to Running the System

Welcome to the **AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)**. This guide provides simple, step-by-step instructions for running the complete application on Windows.

---

## STEP 1: Start the System

1. Open your project folder:
   ```
   C:\Users\guvva\OneDrive\Desktop\PROTOTYPE
   ```
2. **Double-click** on the file named:
   ```
   START_SYSTEM.bat
   ```

---

## STEP 2: Wait for the Service Windows

The startup script will automatically open **two separate command windows**:
1. **`AI-DIDSS Backend API [Port 8000]`** (FastAPI REST service)
2. **`AI-DIDSS Web Console [Port 3000]`** (Officer workstation web server)

> [!NOTE]
> Keep both of these windows open while using the system.

---

## STEP 3: Open the Website in Your Browser

Your default web browser should open automatically. If it does not, open your browser (Chrome, Edge, Firefox, or Safari) and go to:

* **Officer Web Console (UI):** [http://localhost:3000](http://localhost:3000)
* **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## STEP 4: How to Test with a Sample Document

1. On the **Officer Web Console** ([http://localhost:3000](http://localhost:3000)):
2. Under **"1. Document Optical Scanner"**, click the drag-and-drop box or drop a sample passport image.
   * *Sample image location:* You can use any test image from `module1_ocr/data/raw/` or `module1_ocr/data/test/`.
3. (Optional) Under **"2. Biometric Face Verification"**, click the live probe box to upload a selfie photo.
4. Click the blue button: **"Execute Multi-Modal Screening"**.
5. The system will process the document across all 6 forensic engines and display:
   * **Recommended Action** (`CLEAR`, `STANDARD_INSPECTION`, or `SECONDARY_INSPECTION_RECOMMENDED`)
   * **Risk Index Breakdown** (Syntactic, Tampering, and Biometric risk gauges)
   * **Forensic Audit Trail** (Detailed explainable checklist)
   * **ICAO Doc 9303 MRZ Checksums**
   * **Tamper-Evident SHA-256 Audit Hash**

---

## STEP 5: How to Stop the System

To stop the system completely:
1. Close the browser tab.
2. Close the two opened command windows (`AI-DIDSS Backend API` and `AI-DIDSS Web Console`).

---

## STEP 6: Common Errors & Simple Fixes

| Issue / Error | Cause | Simple Fix |
| :--- | :--- | :--- |
| **"Python is not found"** | Python is not added to Windows PATH. | Re-run the Python installer and check the box **"Add Python to PATH"**. |
| **"Port 8000 or 3000 already in use"** | An old instance of the server is still running. | Close any existing Python/Uvicorn terminal windows and re-run `START_SYSTEM.bat`. |
| **"API fetch failed; running local simulation mode"** | The backend API window was closed or is starting up. | Make sure the `AI-DIDSS Backend API` window is open and showing `Uvicorn running on http://0.0.0.0:8000`. |
| **Camera input on desktop** | Desktop browsers open a file picker for photo selection. | Select a face image from your computer to simulate the live camera probe. |
