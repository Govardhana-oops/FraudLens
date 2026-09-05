"""Global System Test Runner for AI-DIDSS."""

import sys
import subprocess
from pathlib import Path

MODULES = [
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
    "module12_security_audit",
    "module13_final_validation"
]

def main():
    proto_root = Path(__file__).resolve().parent.parent
    all_ok = True
    print("=========================================================================")
    print(" AI-DIDSS FULL SYSTEM TEST CERTIFICATION (MODULES 1 TO 13)")
    print("=========================================================================")

    for mod in MODULES:
        mod_path = proto_root / mod
        if not mod_path.exists():
            print(f"[-] {mod:<35} | MISSING DIRECTORY")
            all_ok = False
            continue

        res = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-p", "no:cacheprovider", "-q"],
            cwd=str(mod_path),
            capture_output=True,
            text=True
        )
        last_line = res.stdout.strip().split("\n")[-1] if res.stdout else res.stderr.strip()
        if res.returncode == 0:
            print(f" [PASS] {mod:<35} | PASSED | {last_line}")
        else:
            print(f" [FAIL] {mod:<35} | FAILED | {last_line}")
            all_ok = False

    print("=========================================================================")
    if all_ok:
        print(" CERTIFICATION RESULT: ALL 13 MODULES PASSED 100% OF TESTS [SUCCESS]")
        return 0
    else:
        print(" CERTIFICATION RESULT: TEST FAILURES DETECTED [FAILURE]")
        return 1

if __name__ == "__main__":
    sys.exit(main())
