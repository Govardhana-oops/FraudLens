"""Property & Fuzz Testing for Module 8 API."""

import io
import random
import pytest
from PIL import Image

@pytest.mark.parametrize("seed", range(5))
def test_fuzz_random_image_uploads(client, seed):
    random.seed(seed)
    w = random.randint(80, 200)
    h = random.randint(80, 200)
    img = Image.new("RGB", (w, h), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    files = {"document_file": ("fuzz.jpg", buf.getvalue(), "image/jpeg")}
    response = client.post("/api/v1/screening/inspect", files=files)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["risk_index"] <= 1.0

def test_fuzz_invalid_empty_upload_400(client):
    files = {"document_file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/api/v1/screening/inspect", files=files)
    assert response.status_code == 400
