"""CLI Tool for Field Extraction & Document Understanding (AI-DIDSS Module 1).

Usage:
    python scripts/extract_fields.py --input data/cleaned/DOC_PASSPORT_0001_v1.png
    python scripts/extract_fields.py --input data/cleaned/DOC_PASSPORT_0001_v1.png --output outputs/extraction_results/
"""

import os
import sys
import json
import argparse

# Add module root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.pipeline import PreprocessingPipeline
from src.preprocessing.roi_extractor import DocumentROIExtractor
from src.ocr.engine import OCREngine
from src.extraction.pipeline import DocumentUnderstandingPipeline

def process_document(image_path: str, output_dir: str = None) -> dict:
    if not os.path.exists(image_path):
        print(f"Error: Input image file '{image_path}' not found.", file=sys.stderr)
        sys.exit(1)

    preproc = PreprocessingPipeline(mode="standard")
    roi_ext = DocumentROIExtractor(target_dpi_scale=1.5)
    ocr_eng = OCREngine()
    doc_pipeline = DocumentUnderstandingPipeline()

    # 1. Preprocess
    preproc_res = preproc.process_image(image_path)
    proc_img = preproc_res["processed_image"]

    # 2. Extract Zones & OCR
    zones = roi_ext.extract_zones(proc_img)
    ocr_res = ocr_eng.extract_text(zones["full_document"])

    # 3. Document Understanding & Field Extraction
    metadata = {
        "source_image": os.path.basename(image_path),
        "preprocessing_mode": "roi_multiscale_standard",
        "quality_assessment": preproc_res["quality_assessment"]
    }
    result = doc_pipeline.process(ocr_res["raw_text"], processing_metadata=metadata)
    output_dict = result.to_dict()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        out_file = os.path.join(output_dir, f"{base_name}_fields.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output_dict, f, indent=2)
        print(f"Saved extraction result to: {out_file}")

    return output_dict

def main():
    parser = argparse.ArgumentParser(description="AI-DIDSS Module 1: Document Field Extraction CLI")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input document image")
    parser.add_argument("--output", "-o", type=str, default="outputs/extraction_results", help="Directory to save JSON output")
    args = parser.parse_args()

    res = process_document(args.input, args.output)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
