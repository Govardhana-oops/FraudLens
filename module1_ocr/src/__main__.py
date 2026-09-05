"""Command Line Interface for Module 1 OCR & Document Understanding.

Usage:
    python -m src --input sample.png --output result.json
    python -m src --server --port 8000
"""

import sys
import json
import argparse
from pathlib import Path
from .interface import document_ocr

def main():
    parser = argparse.ArgumentParser(description="AI-DIDSS Module 1: Document OCR & Understanding CLI")
    parser.add_argument("--input", "-i", type=str, help="Path to input identity or travel document image")
    parser.add_argument("--output", "-o", type=str, help="Optional output JSON file path to save structured results")
    parser.add_argument("--server", action="store_true", help="Start the FastAPI REST service on specified port")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the REST service (default: 8000)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")

    args = parser.parse_args()

    if args.server:
        import uvicorn
        from .api import app
        print(f"Starting Module 1 OCR REST Service on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    result = document_ocr.process(args.input)
    json_str = json.dumps(result, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"Extraction result successfully saved to: {args.output}")
    else:
        print(json_str)

if __name__ == "__main__":
    main()
