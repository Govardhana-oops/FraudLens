"""Global Master Module Verification Suite for Module 13."""

from pathlib import Path
import pytest
from module13_final_validation.src.master_runner import MasterSystemRunner

def test_all_modules_exist_and_have_tests():
    proto_root = Path(__file__).resolve().parent.parent.parent
    for m_dir in MasterSystemRunner.MODULE_DIRS:
        mod_path = proto_root / m_dir
        assert mod_path.exists(), f"Module directory {m_dir} does not exist"
        assert (mod_path / "tests").exists(), f"Tests directory for {m_dir} does not exist"
        manifest_exists = (mod_path / "configs" / "frozen_manifest.json").exists() or (mod_path / "models" / "frozen_manifest.json").exists()
        assert manifest_exists, f"Frozen manifest for {m_dir} missing"
