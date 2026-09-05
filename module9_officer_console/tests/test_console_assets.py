"""CSS and JS Assets Verification for Module 9 Web Console."""

from pathlib import Path
import pytest

def test_css_design_tokens_present():
    css_path = Path(__file__).parent.parent / "index.css"
    assert css_path.exists()
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Design tokens
    assert "--bg-base" in content
    assert "--bg-card" in content
    assert "--status-clear" in content
    assert "--status-danger" in content
    assert "backdrop-filter" in content
    assert "Outfit" in content
    assert "JetBrains Mono" in content

def test_js_event_listeners_and_api_calls():
    js_path = Path(__file__).parent.parent / "app.js"
    assert js_path.exists()
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "DOMContentLoaded" in content
    assert "/api/v1/screening/inspect" in content
    assert "renderDossier" in content
    assert "docDropzone.addEventListener" in content
