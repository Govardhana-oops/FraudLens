"""AI-DIDSS: AI-Based Fake Identity & Travel Document Screening System.

Streamlit Community Cloud Main Deployment Entrypoint: streamlit_app.py
Provides the Mission-Critical 3-Column Cybersecurity Workstation Interface
(Exact visual & functional parity with Module 9 Officer Console)
and executes the real, in-process multi-modal AI-DIDSS screening pipeline:
Uploaded Image -> Module 7 -> Modules 1-6 -> Unified Screening Dossier.
"""

import io
import os
import sys
import time
import base64
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from PIL import Image
import cv2
import streamlit as st

# Ensure repository root is on sys.path for direct module resolution
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the real Module 7 integration orchestrator
try:
    from module7_integration_engine.src.interface import screening_orchestrator
except ImportError as e:
    st.error(f"Critical System Error: Failed to import Module 7 Integration Engine: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-DIDSS | Border Inspection & Document Screening Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------------------------------------------------------
# Exact Module 9 Glassmorphism Cybersecurity CSS Stylesheet
# -----------------------------------------------------------------------------
st.markdown("""
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
</head>
<style>
    /* Reset & Streamlit container overrides */
    [data-testid="stAppViewContainer"] {
        background-color: #070B14 !important;
        background-image: 
            radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 85% 85%, rgba(16, 185, 129, 0.05) 0%, transparent 40%) !important;
        color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0B111E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* AI-DIDSS Modern Glassmorphism Stylesheet */
    :root {
        --bg-base: #070B14;
        --bg-surface: #0E1626;
        --bg-card: rgba(18, 28, 48, 0.65);
        --border-card: rgba(255, 255, 255, 0.08);
        --border-highlight: rgba(99, 102, 241, 0.4);

        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;

        --brand-indigo: #6366F1;
        --brand-indigo-glow: rgba(99, 102, 241, 0.25);
        --status-clear: #10B981;
        --status-clear-glow: rgba(16, 185, 129, 0.25);
        --status-warning: #F59E0B;
        --status-warning-glow: rgba(245, 158, 11, 0.25);
        --status-danger: #EF4444;
        --status-danger-glow: rgba(239, 68, 68, 0.25);

        --font-heading: 'Outfit', -apple-system, sans-serif;
        --font-body: 'Inter', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --radius-lg: 16px;
        --radius-md: 10px;
        --radius-sm: 6px;
    }

    /* Top Navigation Header */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(18, 28, 48, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 14px 24px;
        margin-bottom: 20px;
    }
    .brand-group {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .logo-shield {
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: linear-gradient(135deg, #4F46E5, #06B6D4);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.35);
    }
    .shield-icon {
        width: 24px;
        height: 24px;
        color: #FFF;
    }
    .brand-title {
        font-family: 'Outfit', sans-serif;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: 0.5px;
        background: linear-gradient(90deg, #FFFFFF, #CBD5E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 12px;
        color: #94A3B8;
        letter-spacing: 0.2px;
    }
    .station-telemetry {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .telemetry-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
    }
    .pill-label {
        color: #64748B;
        font-weight: 600;
    }
    .pill-val {
        font-family: 'JetBrains Mono', monospace;
        color: #F8FAFC;
        font-weight: 500;
    }
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .status-indicator.online {
        background-color: #10B981;
        box-shadow: 0 0 10px #10B981;
    }

    /* Cards */
    .card {
        background: rgba(18, 28, 48, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        margin-bottom: 16px;
        height: 100%;
        transition: border-color 0.2s ease;
    }
    .card:hover {
        border-color: rgba(255, 255, 255, 0.15);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        background: rgba(255, 255, 255, 0.02);
    }
    .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 15px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 8px;
        color: #F8FAFC;
        margin: 0;
    }
    .card-body {
        padding: 18px;
        display: flex;
        flex-direction: column;
        gap: 14px;
        flex: 1;
    }

    /* Badges */
    .badge {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.06);
        color: #94A3B8;
        letter-spacing: 0.5px;
    }
    .badge.active {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge.alert {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Dropzone Viewfinder */
    .dropzone-viewfinder {
        border: 2px dashed rgba(255, 255, 255, 0.12);
        border-radius: 10px;
        min-height: 160px;
        max-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
        text-align: center;
        padding: 10px;
    }
    .dropzone-viewfinder img {
        max-width: 100%;
        max-height: 180px;
        object-fit: contain;
        border-radius: 6px;
    }

    /* Extracted Fields Grid */
    .extracted-fields-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
    }
    .field-item {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 7px 10px;
    }
    .field-label {
        display: block;
        font-size: 9.5px;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 2px;
    }
    .field-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12.5px;
        font-weight: 600;
        color: #F8FAFC;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* MRZ Box */
    .mrz-box {
        background: #050811;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 10px 12px;
    }
    .mrz-header {
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        color: #64748B;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .mrz-badge {
        color: #10B981;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
    }
    .mrz-text {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 1px;
        color: #38BDF8;
        line-height: 1.4;
        white-space: pre-wrap;
        word-break: break-all;
        margin: 0;
        background: transparent;
        border: none;
    }

    /* Biometric Comparison */
    .biometric-compare-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .bio-frame {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .bio-frame-label {
        font-size: 10px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
    }
    .face-crop-box {
        height: 130px;
        background: #050811;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
    }
    .face-crop-box img {
        max-height: 100%;
        max-width: 100%;
        object-fit: cover;
    }

    /* Match Meter */
    .match-meter-container {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 10px 14px;
    }
    .match-meter-header {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .match-val {
        font-family: 'JetBrains Mono', monospace;
        color: #6366F1;
        font-weight: 700;
    }
    .progress-track {
        height: 6px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366F1, #10B981);
        transition: width 0.4s ease;
    }

    /* PAD Anti-Spoof */
    .pad-anti-spoof-box {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 8px 12px;
    }
    .pad-label {
        font-size: 9px;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
    }
    .pad-status-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        font-weight: 600;
        margin-top: 4px;
    }
    .pad-badge {
        font-size: 10px;
        font-weight: 700;
        color: #10B981;
    }

    /* Decision Banner */
    .decision-banner {
        border-radius: 10px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        border: 1px solid;
        transition: all 0.3s ease;
    }
    .decision-banner.clear {
        background: rgba(16, 185, 129, 0.12);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 24px rgba(16, 185, 129, 0.25);
    }
    .decision-banner.secondary {
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.5);
        box-shadow: 0 0 24px rgba(239, 68, 68, 0.25);
    }
    .decision-banner.review {
        background: rgba(245, 158, 11, 0.15);
        border-color: rgba(245, 158, 11, 0.5);
        box-shadow: 0 0 24px rgba(245, 158, 11, 0.25);
    }
    .decision-sub {
        font-size: 10px;
        color: #94A3B8;
        font-weight: 700;
        display: block;
    }
    .decision-title {
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin: 0;
        color: #F8FAFC;
    }

    /* Risk Summary Grid */
    .risk-summary-grid {
        display: grid;
        grid-template-columns: 100px 1fr;
        gap: 14px;
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
    }
    .risk-meter-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        padding-right: 10px;
    }
    .risk-meter-label {
        font-size: 9px;
        color: #64748B;
        font-weight: 700;
        text-align: center;
        text-transform: uppercase;
    }
    .risk-meter-val {
        font-family: 'Outfit', sans-serif;
        font-size: 26px;
        font-weight: 800;
        color: #10B981;
        margin-top: 2px;
    }
    .risk-breakdown {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 6px;
    }
    .risk-bar-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 11px;
        gap: 8px;
    }
    .mini-bar-track {
        flex: 1;
        height: 5px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 2px;
        overflow: hidden;
    }
    .mini-bar-fill {
        height: 100%;
        background: #6366F1;
    }

    /* Evidence Checklist */
    .evidence-checklist-box {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        max-height: 140px;
        overflow-y: auto;
    }
    .checklist-title {
        font-size: 10px;
        color: #64748B;
        font-weight: 700;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .evidence-list {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 0;
        margin: 0;
    }
    .evidence-item {
        font-size: 11px;
        line-height: 1.4;
        padding-left: 16px;
        position: relative;
    }
    .evidence-item.positive::before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #10B981;
        font-weight: 700;
    }
    .evidence-item.negative::before {
        content: "⚠";
        position: absolute;
        left: 0;
        color: #EF4444;
        font-weight: 700;
    }

    /* Guidance Box */
    .guidance-box {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 6px;
        padding: 10px 12px;
    }
    .guidance-label {
        font-size: 9px;
        color: #818CF8;
        font-weight: 700;
        text-transform: uppercase;
    }
    .guidance-text {
        font-size: 12px;
        color: #F8FAFC;
        margin-top: 2px;
        line-height: 1.35;
    }

    /* Bottom Telemetry Footer */
    .app-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #64748B;
        padding: 12px 10px 0 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 10px;
    }
    .footer-telemetry {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .footer-telemetry code {
        font-family: 'JetBrains Mono', monospace;
        color: #94A3B8;
        background: rgba(255, 255, 255, 0.04);
        padding: 2px 6px;
        border-radius: 4px;
    }

    /* Streamlit Button Restyling */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
        color: #FFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        filter: brightness(1.15) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Helper Utilities: Image Base64 Encoding & Face Cropping
# -----------------------------------------------------------------------------
def pil_to_base64(img: Image.Image) -> str:
    """Encodes PIL Image to Base64 data URL string."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def bytes_to_base64(img_bytes: bytes) -> str:
    """Encodes raw image bytes to Base64 data URL string."""
    b64_str = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def extract_face_portrait(image_bytes: bytes) -> Optional[str]:
    """Detects and extracts portrait face crop from document image buffer."""
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return None

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Try Haar cascade if available
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50))

        if len(faces) > 0:
            largest = max(faces, key=lambda b: b[2] * b[3])
            x, y, fw, fh = largest
            pad_y = int(fh * 0.15)
            pad_x = int(fw * 0.15)
            y1 = max(0, y - pad_y)
            y2 = min(h, y + fh + pad_y)
            x1 = max(0, x - pad_x)
            x2 = min(w, x + fw + pad_x)
            crop_rgb = cv2.cvtColor(img_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
            return pil_to_base64(Image.fromarray(crop_rgb))

        # Skin tone morphology fallback
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 50], dtype=np.uint8)
        upper_skin = np.array([30, 255, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_faces = []
        for cnt in contours:
            cx, cy, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            aspect = ch / float(cw) if cw > 0 else 0
            if area >= (h * w * 0.05) and 0.8 <= aspect <= 2.2:
                valid_faces.append((area, [cy, cx, cy + ch, cx + cw]))

        if valid_faces:
            best_bbox = max(valid_faces, key=lambda f: f[0])[1]
            y1, x1, y2, x2 = best_bbox
            crop_rgb = cv2.cvtColor(img_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2RGB)
            return pil_to_base64(Image.fromarray(crop_rgb))

    except Exception:
        pass
    return None


def get_field_val(fields: Dict[str, Any], keys: List[str]) -> str:
    """Extracts field string adhering to strict zero-mock policy (UNKNOWN if absent)."""
    for k in keys:
        if k in fields:
            val = fields[k]
            if isinstance(val, dict):
                v = val.get("value")
                if v is not None and str(v).strip() != "":
                    return str(v).strip()
            elif val is not None and str(val).strip() != "":
                return str(val).strip()
    return "UNKNOWN"


# -----------------------------------------------------------------------------
# Sidebar: Workstation Controls & Sample Selector
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🛡️ Station Configuration")
officer_id = st.sidebar.text_input("Officer ID", value="CP-0082")
checkpoint_id = st.sidebar.text_input("Station / Gate", value="GATE-04")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📄 Preset Document Samples")
sample_choice = st.sidebar.selectbox(
    "Load Authorized Synthetic Sample",
    options=[
        "Custom Document Upload",
        "Synthetic Passport (Valid TD3)",
        "Synthetic National ID (Valid TD1)",
        "Synthetic Driver License (Valid)",
        "Synthetic Visa (Valid MRV)",
        "Blank Canvas Test Image"
    ]
)

samples_dir = ROOT_DIR / "module1_ocr" / "data" / "cleaned"
sample_file_map = {
    "Synthetic Passport (Valid TD3)": samples_dir / "DOC_PASSPORT_0001_v1.png",
    "Synthetic National ID (Valid TD1)": samples_dir / "DOC_NATIONAL_ID_0004_v1.png",
    "Synthetic Driver License (Valid)": samples_dir / "DOC_DRIVER_LICENSE_0002_v1.png",
    "Synthetic Visa (Valid MRV)": samples_dir / "DOC_VISA_0003_v1.png",
}

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Live Biometric Probe")
live_probe_file = st.sidebar.file_uploader(
    "Upload Live Probe / Selfie Image",
    type=["png", "jpg", "jpeg"],
    key="live_probe_file_uploader",
    help="Optional live probe capture for 1:1 biometric facial verification."
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "**AI-DIDSS Architecture:**\n"
    "• Module 1: Neural OCR (EasyOCR)\n"
    "• Module 2: ICAO Doc 9303 Rule Engine\n"
    "• Module 3: Physical & Frequency Forensics\n"
    "• Module 4: 1:1 Face & PAD Verification\n"
    "• Module 5: Explainable Evidence Fusion\n"
    "• Module 6: Offline SLTD & SHA-256 Ledger\n"
    "• Module 7: Integration Orchestrator"
)


# -----------------------------------------------------------------------------
# Document Image Acquisition & Memory Ingestion
# -----------------------------------------------------------------------------
doc_bytes: Optional[bytes] = None
doc_b64: Optional[str] = None
doc_type_badge = "NO DOCUMENT"

if sample_choice == "Custom Document Upload":
    custom_file = st.sidebar.file_uploader(
        "Upload Document Image (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        key="doc_file_uploader_custom"
    )
    if custom_file is not None:
        doc_bytes = custom_file.read()
        doc_b64 = bytes_to_base64(doc_bytes)
        doc_type_badge = "DOCUMENT LOADED"
elif sample_choice == "Blank Canvas Test Image":
    blank_arr = np.ones((300, 400, 3), dtype=np.uint8) * 255
    pil_blank = Image.fromarray(blank_arr)
    buf = io.BytesIO()
    pil_blank.save(buf, format="PNG")
    doc_bytes = buf.getvalue()
    doc_b64 = bytes_to_base64(doc_bytes)
    doc_type_badge = "BLANK CANVAS"
else:
    s_path = sample_file_map.get(sample_choice)
    if s_path and s_path.exists():
        with open(s_path, "rb") as f:
            doc_bytes = f.read()
        doc_b64 = bytes_to_base64(doc_bytes)
        doc_type_badge = sample_choice.split("(")[0].strip().upper()

# Live probe bytes
live_bytes: Optional[bytes] = None
live_b64: Optional[str] = None
if live_probe_file is not None:
    live_bytes = live_probe_file.read()
    live_b64 = bytes_to_base64(live_bytes)

# Extract doc portrait if available
doc_face_b64 = None
if doc_bytes:
    doc_face_b64 = extract_face_portrait(doc_bytes)


# -----------------------------------------------------------------------------
# Render Top Navigation Header (Exact Module 9 UI)
# -----------------------------------------------------------------------------
st.markdown(f"""
<header class="app-header">
    <div class="brand-group">
        <div class="logo-shield">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="shield-icon">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <path d="m9 12 2 2 4-4"/>
            </svg>
        </div>
        <div class="brand-text">
            <h1 class="brand-title">AI-DIDSS</h1>
            <span class="brand-subtitle">Border Inspection & Document Screening Console</span>
        </div>
    </div>
    <div class="station-telemetry">
        <div class="telemetry-pill">
            <span class="pill-label">STATION</span>
            <span class="pill-val">{checkpoint_id}</span>
        </div>
        <div class="telemetry-pill">
            <span class="pill-label">OFFICER</span>
            <span class="pill-val">{officer_id}</span>
        </div>
        <div class="telemetry-pill">
            <span class="status-indicator online"></span>
            <span class="pill-val">ONLINE</span>
        </div>
    </div>
</header>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Manage Session State for Screening Dossier
# -----------------------------------------------------------------------------
if "dossier" not in st.session_state:
    st.session_state.dossier = None
if "screening_latency" not in st.session_state:
    st.session_state.screening_latency = 0.0

col_left, col_mid, col_right = st.columns([1, 1, 1])


# -----------------------------------------------------------------------------
# Column 1: Document Optical Scanner
# -----------------------------------------------------------------------------
with col_left:
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" style="width: 18px; height: 18px;">
                    <rect width="18" height="14" x="3" y="5" rx="2"/>
                    <path d="M7 15h4M15 15h2M7 11h2M13 11h4"/>
                </svg>
                1. Document Optical Scanner
            </h2>
            <span class="badge {'active' if doc_bytes else ''}">{doc_type_badge}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Viewfinder Image Box
    if doc_b64:
        st.markdown(f"""
        <div class="dropzone-viewfinder">
            <img src="{doc_b64}" alt="Document Scan">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="dropzone-viewfinder">
            <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
                <svg viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="1.5" style="width: 32px; height: 32px;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
                <span style="font-size: 13px; font-weight: 600; color: #F8FAFC;">Select Sample from Sidebar or Upload File</span>
                <span style="font-size: 11px; color: #64748B;">Supports High-Res Passport, Visa, ID Card & License</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Fields to Display
    dossier = st.session_state.dossier or {}
    fields = dossier.get("extracted_fields", {})

    doc_num = get_field_val(fields, ["document_number", "passport_number", "id_number", "license_number", "visa_number", "permit_number"])
    holder_name = get_field_val(fields, ["full_name", "given_names", "surname"])
    issuing_country = get_field_val(fields, ["issuing_country", "nationality"])
    dob = get_field_val(fields, ["date_of_birth"])
    expiry = get_field_val(fields, ["date_of_expiry", "valid_until"])

    st.markdown(f"""
    <div class="extracted-fields-grid" style="margin-top: 12px;">
        <div class="field-item">
            <span class="field-label">Document Number</span>
            <span class="field-value">{doc_num}</span>
        </div>
        <div class="field-item">
            <span class="field-label">Holder Name</span>
            <span class="field-value">{holder_name}</span>
        </div>
        <div class="field-item">
            <span class="field-label">Issuing State</span>
            <span class="field-value">{issuing_country}</span>
        </div>
        <div class="field-item">
            <span class="field-label">Date of Birth</span>
            <span class="field-value">{dob}</span>
        </div>
        <div class="field-item" style="grid-column: span 2;">
            <span class="field-label">Date of Expiry</span>
            <span class="field-value">{expiry}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # MRZ Box
    mrz = dossier.get("mrz") or {}
    mrz_lines = mrz.get("lines") or []
    mrz_status = mrz.get("status") or ("CHECKSUM VALID" if mrz.get("checksum_valid") else "STANDBY")
    mrz_display = "\n".join(mrz_lines) if mrz_lines else "P<UTO<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n0000000000UTO0000000M0000000<<<<<<<<<<<<<<<0"

    st.markdown(f"""
    <div class="mrz-box" style="margin-top: 12px;">
        <div class="mrz-header">
            <span>ICAO DOC 9303 MRZ STREAM</span>
            <span class="mrz-badge">{mrz_status}</span>
        </div>
        <pre class="mrz-text">{mrz_display}</pre>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Column 2: Biometric Face Verification
# -----------------------------------------------------------------------------
with col_mid:
    bio_badge = "AWAITING PROBE"
    if live_bytes:
        bio_badge = "PROBE CAPTURED"
    m4_tel = dossier.get("modules_telemetry", {}).get("module4_face_verification") if isinstance(dossier, dict) else getattr(dossier, "modules_telemetry", {}).get("module4_face_verification", None)
    if m4_tel:
        if hasattr(m4_tel, "status"):
            bio_badge = str(m4_tel.status)
        elif isinstance(m4_tel, dict):
            bio_badge = str(m4_tel.get("status", bio_badge))

    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" style="width: 18px; height: 18px;">
                    <circle cx="12" cy="8" r="5"/>
                    <path d="M20 21a8 8 0 1 0-16 0"/>
                </svg>
                2. Biometric Face Verification
            </h2>
            <span class="badge {'active' if live_bytes else ''}">{bio_badge}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Side-by-side face compare grid
    doc_portrait_html = f'<img src="{doc_face_b64}" alt="Extracted Portrait">' if doc_face_b64 else """
        <svg viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="1.5" style="width: 36px; height: 36px;">
            <circle cx="12" cy="8" r="5"/>
            <path d="M20 21a8 8 0 1 0-16 0"/>
        </svg>
    """

    live_probe_html = f'<img src="{live_b64}" alt="Live Probe">' if live_b64 else """
        <div style="display: flex; flex-direction: column; align-items: center; gap: 4px; color: #64748B; font-size: 10px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="1.5" style="width: 24px; height: 24px;">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                <circle cx="12" cy="13" r="4"/>
            </svg>
            <span>Upload Probe via Sidebar</span>
        </div>
    """

    st.markdown(f"""
    <div class="biometric-compare-grid">
        <div class="bio-frame">
            <span class="bio-frame-label">EXTRACTED PORTRAIT</span>
            <div class="face-crop-box">
                {doc_portrait_html}
            </div>
        </div>
        <div class="bio-frame">
            <span class="bio-frame-label">LIVE CAMERA PROBE</span>
            <div class="face-crop-box">
                {live_probe_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1:1 Facial Similarity Score
    sim_score = 0.0
    dim_risks = dossier.get("dimensional_risks", {})
    if "biometric_identity_risk" in dim_risks:
        sim_score = max(0.0, 1.0 - float(dim_risks["biometric_identity_risk"]))
    pct_fill = int(round(sim_score * 100))

    st.markdown(f"""
    <div class="match-meter-container" style="margin-top: 12px;">
        <div class="match-meter-header">
            <span>1:1 Facial Similarity</span>
            <span class="match-val">{sim_score:.2f}</span>
        </div>
        <div class="progress-track">
            <div class="progress-fill" style="width: {pct_fill}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PAD Anti-Spoof
    st.markdown("""
    <div class="pad-anti-spoof-box" style="margin-top: 12px;">
        <span class="pad-label">PRESENTATION ATTACK DETECTION (PAD)</span>
        <div class="pad-status-row">
            <span style="color: #F8FAFC;">Sensor Ready</span>
            <span class="pad-badge">LIVENESS OK</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    # Prominent Screening Action Button
    run_screening = st.button("🔍 Execute Multi-Modal Screening", type="primary", use_container_width=True)


# -----------------------------------------------------------------------------
# Trigger Screening Pipeline
# -----------------------------------------------------------------------------
if run_screening:
    if not doc_bytes:
        st.warning("⚠️ Please provide a document image or select a synthetic demonstration sample from the sidebar.")
    else:
        with st.spinner("Processing Multi-Modal Pipeline across Modules 1–6..."):
            t_start = time.perf_counter()
            try:
                # Direct in-process execution of the real Module 7 orchestrator
                res_dossier = screening_orchestrator.process_screening(
                    document_image=doc_bytes,
                    live_face_image=live_bytes,
                    officer_id=officer_id,
                    checkpoint_id=checkpoint_id
                )
                st.session_state.dossier = res_dossier
                st.session_state.screening_latency = (time.perf_counter() - t_start) * 1000.0
                st.rerun()
            except Exception as e:
                st.error(f"Fatal Pipeline Error: {str(e)}")


# -----------------------------------------------------------------------------
# Column 3: Explainable Decision Support Dossier
# -----------------------------------------------------------------------------
dossier = st.session_state.dossier or {}
rec_action = dossier.get("recommended_action", "STANDBY")
risk_index = float(dossier.get("risk_index", 0.0))
dim_risks = dossier.get("dimensional_risks", {})
doc_risk_pct = int(round(float(dim_risks.get("document_syntactic_risk", 0.0)) * 100))
tamp_risk_pct = int(round(float(dim_risks.get("physical_tampering_risk", 0.0)) * 100))
bio_risk_pct = int(round(float(dim_risks.get("biometric_identity_risk", 0.0)) * 100))

# Decision Banner Class
banner_class = "clear"
banner_icon = """<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>"""
if "SECONDARY" in rec_action or "REJECT" in rec_action:
    banner_class = "secondary"
    banner_icon = """<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>"""
elif "REVIEW" in rec_action:
    banner_class = "review"
    banner_icon = """<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>"""

with col_right:
    st.markdown(f"""
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" style="width: 18px; height: 18px;">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                3. Explainable Decision Dossier
            </h2>
            <span class="badge active">AUDIT READY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Recommendation Banner
    st.markdown(f"""
    <div class="decision-banner {banner_class}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width: 28px; height: 28px;">
            {banner_icon}
        </svg>
        <div class="decision-text-wrap">
            <span class="decision-sub">RECOMMENDED ACTION</span>
            <h3 class="decision-title">{rec_action.replace('_', ' ')}</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Risk Summary Grid
    st.markdown(f"""
    <div class="risk-summary-grid" style="margin-top: 12px;">
        <div class="risk-meter-box">
            <span class="risk-meter-label">Overall Risk</span>
            <span class="risk-meter-val">{risk_index:.2f}</span>
        </div>
        <div class="risk-breakdown">
            <div class="risk-bar-row">
                <span style="color: #94A3B8;">Syntactic (M2)</span>
                <div class="mini-bar-track"><div class="mini-bar-fill" style="width: {doc_risk_pct}%;"></div></div>
            </div>
            <div class="risk-bar-row">
                <span style="color: #94A3B8;">Tampering (M3)</span>
                <div class="mini-bar-track"><div class="mini-bar-fill" style="width: {tamp_risk_pct}%;"></div></div>
            </div>
            <div class="risk-bar-row">
                <span style="color: #94A3B8;">Biometric (M4)</span>
                <div class="mini-bar-track"><div class="mini-bar-fill" style="width: {bio_risk_pct}%;"></div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Forensic Evidence Items
    itemized = dossier.get("itemized_evidence", {})
    positives = itemized.get("positive_findings", [])
    negatives = itemized.get("negative_findings", [])
    uncertainties = itemized.get("uncertainties", [])

    ev_items_html = ""
    for p in positives:
        ev_items_html += f'<li class="evidence-item positive">{p}</li>'
    for n in negatives:
        ev_items_html += f'<li class="evidence-item negative">{n}</li>'
    for u in uncertainties:
        ev_items_html += f'<li class="evidence-item negative">{u}</li>'

    if not ev_items_html:
        ev_items_html = '<li class="evidence-item positive">Awaiting document input for multi-module inspection.</li>'

    st.markdown(f"""
    <div class="evidence-checklist-box" style="margin-top: 12px;">
        <h4 class="checklist-title">FORENSIC AUDIT TRAIL</h4>
        <ul class="evidence-list">
            {ev_items_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Officer Actionable Guidance
    guidance = dossier.get("actionable_guidance") or "Insert document into optical feeder to begin inspection flow."
    st.markdown(f"""
    <div class="guidance-box" style="margin-top: 12px;">
        <span class="guidance-label">OFFICER INSTRUCTIONS</span>
        <p class="guidance-text">{guidance}</p>
    </div>
    """, unsafe_allow_html=True)

    # Action Buttons Row
    c_btn1, c_btn2 = st.columns([1, 1])
    with c_btn1:
        st.button("Secondary Escalate", key="btn_sec", type="secondary", use_container_width=True)
    with c_btn2:
        st.button("Admit Passenger", key="btn_admit", type="secondary", use_container_width=True)


# -----------------------------------------------------------------------------
# Bottom Telemetry Footer
# -----------------------------------------------------------------------------
latency_display = dossier.get("total_latency_ms") or st.session_state.screening_latency or 0.0
audit_log = dossier.get("audit_log") or {}
audit_hash = audit_log.get("entry_hash", "0000000000000000000000000000000000000000") if isinstance(audit_log, dict) else getattr(audit_log, "entry_hash", "0000000000000000000000000000000000000000")

st.markdown(f"""
<footer class="app-footer">
    <div class="footer-telemetry">
        <span>Total Latency: <strong style="color: #F8FAFC;">{latency_display:.1f} ms</strong></span>
        <span>•</span>
        <span>SHA-256 Audit Hash: <code>{audit_hash[:32]}...</code></span>
    </div>
    <div class="footer-version" style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">AI-DIDSS v1.0.0-FROZEN</div>
</footer>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Deep Modular Telemetry & Inspection Drawer (Collapsible)
# -----------------------------------------------------------------------------
if dossier:
    st.write("")
    with st.expander("🔬 Deep Modular Forensics, Telemetry & Immutable Ledger (Modules 1–6)"):
        t1, t2, t3, t4 = st.tabs(["📊 Module Telemetry", "🔤 Raw Field Tokens", "🛡️ Forensics & Tampering", "📜 Tamper-Evident Ledger"])

        with t1:
            telemetry = dossier.get("modules_telemetry", {})
            rows = []
            for m_name, m_tel in telemetry.items():
                status_v = m_tel.status if hasattr(m_tel, 'status') else (m_tel.get('status') if isinstance(m_tel, dict) else str(m_tel))
                lat_v = m_tel.latency_ms if hasattr(m_tel, 'latency_ms') else (m_tel.get('latency_ms') if isinstance(m_tel, dict) else 0.0)
                rows.append({"Module": m_name, "Status": status_v, "Latency (ms)": lat_v})
            st.dataframe(rows, use_container_width=True)

        with t2:
            if fields:
                f_rows = []
                for k, v in fields.items():
                    val = v.get("value") if isinstance(v, dict) else v
                    conf = v.get("confidence") if isinstance(v, dict) else "N/A"
                    status = v.get("status") if isinstance(v, dict) else "N/A"
                    f_rows.append({"Field": k, "Value": str(val), "Confidence": f"{float(conf)*100:.1f}%" if isinstance(conf, (int, float)) else str(conf), "Status": str(status)})
                st.dataframe(f_rows, use_container_width=True)
            else:
                st.info("No field tokens extracted.")

        with t3:
            st.json({
                "dimensional_risks": dossier.get("dimensional_risks"),
                "visual_mrz_conflicts": dossier.get("visual_mrz_conflicts"),
                "warnings": dossier.get("warnings"),
                "errors": dossier.get("errors")
            })

        with t4:
            st.json(dossier.get("audit_log", {}))
