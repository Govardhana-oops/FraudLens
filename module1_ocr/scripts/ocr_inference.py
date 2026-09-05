"""CLI OCR Inference Utility for AI-DIDSS Module 1.

Usage:
    python scripts/ocr_inference.py --input data/cleaned/DOC_PASSPORT_0001_v1.png --mode standard
"""

import os
import sys
import argparse
import json

# Add module root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.pipeline import PreprocessingPipeline
from src.ocr.engine import OCREngine
from src.extraction.field_extractor import FieldExtractor

def run_inference(image_path: str, preproc_mode: str = "standard") -> dict:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Input image not found: {image_path}")

    # 1. Preprocessing
    pipeline = PreprocessingPipeline(mode=preproc_mode)
    preproc_res = pipeline.process_image(image_path)
    proc_img = preproc_res["processed_image"]

    # 2. OCR Recognition
    ocr_engine = OCREngine()
    ocr_res = ocr_engine.extract_text(proc_img)

    # 3. Field & MRZ Extraction
    extractor = FieldExtractor()
    meta = {
        "preprocessing_mode": preproc_mode,
        "transformations": preproc_res["transformations_applied"],
        "quality_score": preproc_res["quality_assessment"]["quality_score"],
        "quality_status": preproc_res["quality_assessment"]["status"]
    }
    
    # Try reading from raw image annotations or OCR text
    extraction_res = extractor.extract(ocr_res["raw_text"], preproc_metadata=meta)
    
    return extraction_res.to_dict()

def main():
    parser = argparse.ArgumentParser(description="AI-DIDSS Module 1 OCR Inference CLI")
    parser.add_argument("--input", "-i", required=True, help="Path to input document image")
    parser.add_argument("--mode", "-m", default="standard", choices=["raw", "standard", "contrast_enhanced", "binarized"], help="Preprocessing mode")
    parser.add_argument("--output", "-o", help="Optional JSON file path to save output")

    args = parser.parse_args()

    try:
        res = run_inference(args.input, preproc_mode=args.mode)
        json_output = json.dumps(res, indent=2)
        print(json_output)

        if args.output:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"\n[Saved inference result to {args.output}]")
    except Exception as e:
        print(f"[ERROR] Inference failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
