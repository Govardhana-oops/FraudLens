"""Top-Level CLI Utility for Module 1 OCR (AI-DIDSS).

Usage:
    python scripts/ocr_cli.py --input data/cleaned/DOC_PASSPORT_0001_v1.png
    python scripts/ocr_cli.py --input data/cleaned/DOC_PASSPORT_0001_v1.png --output outputs/sample_result.json
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.interface import document_ocr

def main():
    parser = argparse.ArgumentParser(description="AI-DIDSS Module 1: Document OCR Production CLI")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input identity document image")
    parser.add_argument("--output", "-o", type=str, help="Optional output JSON file path to save structured results")
    args = parser.parse_args()

    res = document_ocr.process(args.input)
    json_output = json.dumps(res, indent=2)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as fp:
            fp.write(json_output)
        print(f"Extraction result saved to: {args.output}")
    else:
        print(json_output)

if __name__ == "__main__":
    main()
