"""Master System Test Suite & Certification Runner for AI-DIDSS."""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class MasterSystemRunner:
    """Discovers and runs test suites across all project modules."""

    MODULE_DIRS = [
        "module1_ocr",
        "module2_document_validation",
        "module3_tampering_detection",
        "module4_face_verification",
        "module5_explainable_evidence",
        "module6_database_sync",
        "module7_integration_engine",
        "module8_backend_api",
        "module9_officer_console",
        "module10_system_test_matrix",
        "module11_performance_profiling",
        "module12_security_audit"
    ]

    @classmethod
    def run_all_module_tests(cls, base_dir: Path) -> Dict[str, Any]:
        results = {}
        total_passed = 0
        total_failed = 0

        for m_dir in cls.MODULE_DIRS:
            target_path = base_dir / m_dir
            if not target_path.exists():
                results[m_dir] = {"status": "SKIPPED", "passed": 0, "failed": 0}
                continue

            cmd = [sys.executable, "-m", "pytest", "tests/", "-p", "no:cacheprovider", "-q"]
            proc = subprocess.run(cmd, cwd=str(target_path), capture_output=True, text=True)
            status = "PASS" if proc.returncode == 0 else "FAIL"
            results[m_dir] = {
                "status": status,
                "output": proc.stdout + proc.stderr
            }

        return results
