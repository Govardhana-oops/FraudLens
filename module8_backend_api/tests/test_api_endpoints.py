"""API Endpoints Tests for Module 8."""

import io
import pytest
from PIL import Image

def _create_dummy_image_bytes():
    img = Image.new("RGB", (150, 150), color=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "module7_integration_engine" in data["modules_ready"]

def test_watchlist_check_endpoint(client):
    response = client.get("/api/v1/watchlist/check/NONEXISTENT123")
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged"] is False

def test_sync_differential_endpoint(client):
    payload = {
        "delta_records": [
            {
                "doc_number": "API_REV_01",
                "country_code": "USA",
                "category": "REVOKED_VISA",
                "record_id": "REV-API-01",
                "reported_date": "2026-03-01",
                "severity": "CRITICAL",
                "officer_instructions": "Stop"
            }
        ]
    }
    response = client.post("/api/v1/sync/differential", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sync_status"] == "SUCCESS"
    assert data["records_pulled"] == 1

def test_screening_inspect_endpoint(client):
    doc_bytes = _create_dummy_image_bytes()
    files = {
        "document_file": ("test_doc.jpg", doc_bytes, "image/jpeg")
    }
    data = {
        "officer_id": "OFFICER-HTTP-TEST",
        "checkpoint_id": "CP-TERMINAL-01"
    }
    response = client.post("/api/v1/screening/inspect", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert "screening_id" in res
    assert "recommended_action" in res
    assert "risk_index" in res
    assert "audit_log" in res

def test_audit_logs_endpoint(client):
    response = client.get("/api/v1/audit/logs?limit=50&verify_integrity=true")
    assert response.status_code == 200
    data = response.json()
    assert data["chain_intact"] is True
    assert isinstance(data["logs"], list)
