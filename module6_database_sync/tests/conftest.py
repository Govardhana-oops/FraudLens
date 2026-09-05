import sys
import tempfile
import os
from pathlib import Path
import pytest
from src.interface import DatabaseSyncService

# Add module root to sys.path
module_root = str(Path(__file__).parent.parent)
if module_root not in sys.path:
    sys.path.insert(0, module_root)

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
