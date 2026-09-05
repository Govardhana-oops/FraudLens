import sys
from pathlib import Path

# Add module root to sys.path
module_root = str(Path(__file__).parent.parent)
if module_root not in sys.path:
    sys.path.insert(0, module_root)
