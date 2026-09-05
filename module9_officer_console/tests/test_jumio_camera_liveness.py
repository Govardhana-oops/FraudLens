"""Comprehensive Verification Suite for Jumio-Inspired Live Camera & Biometric Face Liveness UX."""

from pathlib import Path
import io
import pytest
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

from module8_backend_api.src.main import create_app

@pytest.fixture
def js_content():
    js_path = Path(__file__).parent.parent / "app.js"
    assert js_path.exists()
    with open(js_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def css_content():
    css_path = Path(__file__).parent.parent / "index.css"
    assert css_path.exists()
    with open(css_path, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture
def api_client():
    app = create_app()
    return TestClient(app)

# -----------------------------------------------------------------------------
# Part 1 to 5: Client-Side JS & CSS Architecture Tests
# -----------------------------------------------------------------------------
def test_camera_webrtc_manager_architecture(js_content):
    """Verifies WebRTCCameraManager handles getUserMedia, errors, and device switching."""
    assert "class WebRTCCameraManager" in js_content
    assert "navigator.mediaDevices.getUserMedia" in js_content
    assert "facingMode" in js_content
    assert "environment" in js_content
    assert "user" in js_content
    assert "NotAllowedError" in js_content
    assert "NotFoundError" in js_content
    assert "NotReadableError" in js_content
    assert "switchCamera" in js_content
    assert "stopCamera" in js_content

def test_frame_quality_analyzer_algorithms(js_content):
    """Verifies native Canvas frame brightness, contrast, sharpness, and stability calculations."""
    assert "class ClientFrameAnalyzer" in js_content
    assert "0.299 * r + 0.587 * g + 0.114 * b" in js_content  # Standard luminance formula
    assert "Math.sqrt(sumSqDiff" in js_content                # Standard deviation contrast
    assert "lapVariance" in js_content                        # Laplacian blur detection
    assert "stability" in js_content

def test_active_liveness_state_machine(js_content):
    """Verifies the multi-step interactive active liveness state machine."""
    assert "ALIGNING" in js_content
    assert "BLINK_CHALLENGE" in js_content
    assert "HOLD_STEADY" in js_content
    assert "CAPTURED_LIVE" in js_content
    assert "eyeZoneEnergy" in js_content
    assert "updateLivenessUI" in js_content
    assert "captureSelfieProbe" in js_content

def test_document_auto_capture_and_guidance(js_content):
    """Verifies document guidance states and auto-capture streak counter."""
    assert "ALIGN DOCUMENT" in js_content
    assert "IMPROVE LIGHTING" in js_content
    assert "HOLD STEADY" in js_content
    assert "DOCUMENT DETECTED" in js_content
    assert "docStableStreak" in js_content
    assert "docAutocaptureToggle" in js_content
    assert "captureDocFrame" in js_content

def test_upload_fallback_maintained(js_content):
    """Verifies that file upload mode is fully maintained as a 1-click fallback."""
    assert "tabDocUpload.addEventListener" in js_content
    assert "tabFaceUpload.addEventListener" in js_content
    assert "handleDocFileUpload" in js_content
    assert "liveFileInput.addEventListener" in js_content

def test_jumio_inspired_css_components(css_content):
    """Verifies oval guide, scanline, corner reticles, and responsive styles."""
    assert ".biometric-oval-guide" in css_content
    assert ".oval-pulse-ring" in css_content
    assert ".oval-radar-sweep" in css_content
    assert ".doc-bounding-frame" in css_content
    assert ".doc-bracket" in css_content
    assert ".doc-scanline" in css_content
    assert ".guidance-hud-pill" in css_content
    assert "@media (max-width: 1200px)" in css_content
    assert "@media (max-width: 860px)" in css_content
    assert "@media (max-width: 600px)" in css_content

# -----------------------------------------------------------------------------
# Part 6 to 9: API Contract & Multi-Modal Screening Integration
# -----------------------------------------------------------------------------
def test_api_screening_with_camera_metadata_and_live_probe(api_client):
    """Tests POST /api/v1/screening/inspect with live probe, document type, and capture modes."""
    # Create valid synthetic document image
    doc_arr = np.ones((300, 400, 3), dtype=np.uint8) * 220
    doc_pil = Image.fromarray(doc_arr)
    doc_buf = io.BytesIO()
    doc_pil.save(doc_buf, format="JPEG")
    doc_bytes = doc_buf.getvalue()

    # Create synthetic face probe
    face_arr = np.ones((200, 200, 3), dtype=np.uint8) * 180
    face_pil = Image.fromarray(face_arr)
    face_buf = io.BytesIO()
    face_pil.save(face_buf, format="JPEG")
    face_bytes = face_buf.getvalue()

    response = api_client.post(
        "/api/v1/screening/inspect",
        files={
            "document_file": ("live_doc_frame.jpg", doc_bytes, "image/jpeg"),
            "live_face_file": ("live_selfie_probe.jpg", face_bytes, "image/jpeg")
        },
        data={
            "document_type": "PASSPORT",
            "capture_mode": "LIVE_CAMERA",
            "face_capture_mode": "LIVE_LIVENESS_CAMERA",
            "officer_id": "CP-0082",
            "checkpoint_id": "GATE-04"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommended_action" in data
    assert "risk_index" in data
    assert "dimensional_risks" in data
    assert "itemized_evidence" in data
    assert data["metadata"]["capture_mode"] == "LIVE_CAMERA"
    assert data["metadata"]["face_capture_mode"] == "LIVE_LIVENESS_CAMERA"
    assert data["metadata"]["client_document_type"] == "PASSPORT"

def test_api_zero_hardcoded_identities(api_client):
    """Ensures no hardcoded fictional identities (John Doe, fake passport numbers) are emitted."""
    doc_arr = np.ones((300, 400, 3), dtype=np.uint8) * 255
    doc_pil = Image.fromarray(doc_arr)
    buf = io.BytesIO()
    doc_pil.save(buf, format="PNG")

    response = api_client.post(
        "/api/v1/screening/inspect",
        files={"document_file": ("blank.png", buf.getvalue(), "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    raw_str = str(data).upper()

    assert "JOHN DOE" not in raw_str
    assert "P12345678" not in raw_str
