import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add module root and prototype root to sys.path
module_root = str(Path(__file__).parent.parent)
proto_root = str(Path(__file__).parent.parent.parent)

if module_root not in sys.path:
    sys.path.insert(0, module_root)
if proto_root not in sys.path:
    sys.path.insert(0, proto_root)

try:
    from src.main import create_app
except ModuleNotFoundError:
    from module8_backend_api.src.main import create_app

@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c
