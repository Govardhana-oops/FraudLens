# AI-DIDSS Deployment Guide: GitHub + Streamlit Community Cloud

**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Main Streamlit Deployment Entrypoint:** `streamlit_app.py`  
**Status:** `READY FOR DEPLOYMENT`

---

## 1. What is the Main File to Deploy in Streamlit?

> [!IMPORTANT]
> The **MAIN FILE** to enter when deploying on Streamlit Community Cloud is:
> ```
> streamlit_app.py
> ```
> This file is located at the root of the repository and boots the full multi-modal screening pipeline across Modules 1–7 with the **exact 3-column cybersecurity dark-mode border workstation console**.

---

## 2. Streamlit Cloud Configuration Settings

When you click **"Create App"** or **"New App"** on [share.streamlit.io](https://share.streamlit.io):

| Deployment Field | Exact Value to Enter | Notes |
| :--- | :--- | :--- |
| **Repository** | `YOUR_USERNAME/AI-DIDSS` | Select your GitHub repo |
| **Branch** | `main` | Default production branch |
| **Main file path** | `streamlit_app.py` | Root deployment entrypoint |
| **App URL (Optional)** | `ai-didss-screening` | Or custom subdomain of choice |
| **Python Version** | `3.11` or `3.12` | Under *Advanced Settings* |

### Automatic Cloud Dependency Handling:
* **Linux System Packages ([`packages.txt`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/packages.txt)):**
  * `libgl1`
  * `libglib2.0-0` (Ensures headless OpenCV runs seamlessly on Linux containers)
* **Python Runtime Packages ([`requirements.txt`](file:///c:/Users/guvva/OneDrive/Desktop/PROTOTYPE/requirements.txt)):**
  * Automatically installs `streamlit`, `torch`, `torchvision`, `easyocr`, `opencv-python-headless`, `pydantic`, `pyyaml`, `numpy`, `pillow`.

---

## 3. Step-by-Step Commands to Push to GitHub

Run these commands in your terminal from the project folder:

```bash
# Step 1: Initialize Git (if not already done)
git init

# Step 2: Stage all project files
git add .

# Step 3: Commit the production release
git commit -m "feat: AI-DIDSS production release with Streamlit Community Cloud web interface"

# Step 4: Ensure default branch is main
git branch -M main

# Step 5: Link your GitHub repository
# (Create an empty repo on https://github.com/new first)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git

# Step 6: Push to GitHub
git push -u origin main
```

---

## 4. Deploying on Streamlit Community Cloud (Step-by-Step)

1. Open your browser and go to **[share.streamlit.io](https://share.streamlit.io)**.
2. Sign in with your **GitHub account**.
3. Click the **"New app"** button.
4. Fill in the deployment form:
   * **Repository:** `YOUR_USERNAME/AI-DIDSS`
   * **Branch:** `main`
   * **Main file path:** `streamlit_app.py`
5. Click **"Deploy!"**.
6. Streamlit Cloud will build the container, install packages from `packages.txt` and `requirements.txt`, and launch your live public AI-DIDSS Screening Console!

---

## 5. Local Workstation Testing (Optional)

To test locally before pushing:

* **Run Streamlit Console:**
  ```bash
  streamlit run streamlit_app.py
  ```
  *(Opens automatically at `http://localhost:8501`)*

* **Or run the Dual-Window Launcher (FastAPI Backend + Officer UI):**
  ```cmd
  START_SYSTEM.bat
  ```
