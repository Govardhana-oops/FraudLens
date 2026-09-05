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
        "doc-dropzone", "doc-file-input", "doc-preview-img",
        "live-face-box", "live-file-input", "live-face-crop",
        "run-screen-btn", "sync-btn",
        "decision-banner", "decision-title",
        "risk-index-val", "risk-doc-fill", "risk-tamp-fill", "risk-bio-fill",
        "bio-similarity-val", "bio-progress-fill",
        "evidence-list", "guidance-text", "audit-hash-display"
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
