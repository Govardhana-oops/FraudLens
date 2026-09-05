"""CLI Preprocessing Utility for AI-DIDSS Module 1.

Usage:
    python scripts/preprocess_cli.py --input data/cleaned/sample.png --output outputs/visual_debug/sample_preproc.png --mode standard
"""

import os
import sys
import argparse
import cv2
import json

# Add module root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.pipeline import PreprocessingPipeline

def main():
    parser = argparse.ArgumentParser(description="AI-DIDSS Document Image Preprocessing CLI")
    parser.add_argument("--input", "-i", required=True, help="Path to input image file")
    parser.add_argument("--output", "-o", required=True, help="Path to save preprocessed output image")
    parser.add_argument("--mode", "-m", default="standard", choices=["raw", "standard", "contrast_enhanced", "binarized"], help="Preprocessing mode")
    parser.add_argument("--save-report", action="store_true", help="Print/save JSON quality report")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] Input file does not exist: {args.input}")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    pipeline = PreprocessingPipeline(mode=args.mode)
    result = pipeline.process_image(args.input)

    # Save output image
    cv2.imwrite(args.output, result["processed_image"])
    
    print("=" * 60)
    print(f"PREPROCESSING COMPLETE [{args.mode.upper()}]")
    print("=" * 60)
    print(f"Input:           {args.input}")
    print(f"Output:          {args.output}")
    print(f"Transformations: {result['transformations_applied']}")
    print(f"Quality Status:  {result['quality_assessment']['status']} (Score: {result['quality_assessment']['quality_score']})")
    print(f"Blur Score:      {result['quality_assessment']['blur_score']} (Blurry: {result['quality_assessment']['is_blurry']})")
    print(f"Glare Ratio:     {result['quality_assessment']['glare_ratio']} (Glare: {result['quality_assessment']['has_glare']})")
    print("=" * 60)

if __name__ == "__main__":
    main()
