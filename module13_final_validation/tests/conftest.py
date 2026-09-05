import sys
from pathlib import Path

module_root = str(Path(__file__).parent.parent)
proto_root = str(Path(__file__).parent.parent.parent)

if module_root in sys.path:
    sys.path.remove(module_root)
sys.path.insert(0, module_root)

if proto_root in sys.path:
    sys.path.remove(proto_root)
sys.path.insert(0, proto_root)
