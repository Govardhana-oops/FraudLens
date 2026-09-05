"""HTML Markup and DOM Structure Verification for Module 9 Web Console."""

import os
from pathlib import Path
import pytest

@pytest.fixture
def html_content():
    html_path = Path(__file__).parent.parent / "index.html"
    assert html_path.exists(), "index.html must exist in module9"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

def test_html_essential_elements(html_content):
    # Unique interactive and telemetry IDs
    essential_ids = [
        # Document Section & Camera
        "tab-doc-camera", "tab-doc-upload", "doc-type-select", "btn-side-front", "btn-side-back",
        "doc-camera-container", "doc-video", "doc-canvas", "doc-bounding-frame",
        "doc-guidance-badge", "doc-guidance-text", "doc-lighting-indicator", "doc-stability-indicator",
        "btn-doc-switch-cam", "btn-doc-capture", "btn-doc-retake", "doc-autocapture-toggle",
        "doc-dropzone", "doc-file-input", "doc-preview-img", "doc-type-badge",
        
        # Biometrics & Active Liveness
        "tab-face-liveness", "tab-face-upload", "doc-face-crop",
        "selfie-camera-container", "selfie-video", "selfie-canvas", "biometric-oval-guide",
        "liveness-challenge-banner", "liveness-step-badge", "liveness-step-prompt", "liveness-progress-fill",
        "selfie-lighting-badge", "selfie-sharpness-badge",
        "btn-selfie-switch-cam", "btn-selfie-capture", "btn-selfie-retake",
        "live-face-box", "live-file-input", "live-face-crop",
        "bio-status-badge", "bio-similarity-val", "bio-progress-fill",
        "pad-status-text", "pad-badge",
        
        # Execution & Dossier
        "run-screen-btn", "sync-btn",
        "decision-banner", "decision-title",
        "risk-index-val", "risk-doc-fill", "risk-tamp-fill", "risk-bio-fill",
        "evidence-list", "guidance-text", "audit-hash-display", "latency-val"
    ]
    for element_id in essential_ids:
        assert f'id="{element_id}"' in html_content, f"Missing essential element ID: {element_id}"

def test_html_accessibility_and_seo(html_content):
    assert "<!DOCTYPE html>" in html_content
    assert '<html lang="en">' in html_content
    assert '<meta name="viewport"' in html_content
    assert '<meta name="description"' in html_content
    assert "<title>" in html_content
    assert "<h1" in html_content
    assert 'alt="Document Preview"' in html_content
    assert 'alt="Extracted Portrait"' in html_content
    assert 'alt="Live Probe"' in html_content

