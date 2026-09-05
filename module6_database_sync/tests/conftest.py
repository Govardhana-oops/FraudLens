import sys
import tempfile
import os
from pathlib import Path
import pytest
# Add module root and prototype root to sys.path
module_root = str(Path(__file__).parent.parent)
proto_root = str(Path(__file__).parent.parent.parent)
if module_root not in sys.path:
    sys.path.insert(0, module_root)
if proto_root not in sys.path:
    sys.path.insert(0, proto_root)

try:
    from src.interface import DatabaseSyncService
except (ImportError, ModuleNotFoundError):
    from module6_database_sync.src.interface import DatabaseSyncService

@pytest.fixture
def test_sync_service():
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tf:
        db_path = tf.name
    service = DatabaseSyncService(db_override_path=db_path)
    yield service
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
