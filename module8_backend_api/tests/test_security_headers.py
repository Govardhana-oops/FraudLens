"""Security Headers and OWASP Standards Tests for Module 8."""

import pytest

def test_security_headers_present_on_response(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "max-age" in headers.get("Strict-Transport-Security", "")
    assert headers.get("Referrer-Policy") == "no-referrer"
