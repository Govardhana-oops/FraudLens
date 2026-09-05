import sys
from pathlib import Path

# Add project root and module root to sys.path
module_root = str(Path(__file__).parent.parent)
proto_root = str(Path(__file__).parent.parent.parent)

if module_root not in sys.path:
    sys.path.insert(0, module_root)
if proto_root not in sys.path:
    sys.path.insert(0, proto_root)
