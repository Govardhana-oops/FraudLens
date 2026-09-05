import sys
from pathlib import Path
import pytest

module_root = str(Path(__file__).parent.parent)
proto_root = str(Path(__file__).parent.parent.parent)

if module_root not in sys.path:
    sys.path.insert(0, module_root)
if proto_root not in sys.path:
    sys.path.insert(0, proto_root)

for m_dir in [
    "module1_ocr",
    "module2_document_validation",
    "module3_tampering_detection",
    "module4_face_verification",
    "module5_explainable_evidence",
    "module6_database_sync",
    "module7_integration_engine",
    "module8_backend_api",
    "module9_officer_console"
]:
    p = str(Path(proto_root) / m_dir)
    if p not in sys.path:
        sys.path.insert(0, p)
