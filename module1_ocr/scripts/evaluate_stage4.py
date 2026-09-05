"""Stage 4 Comparative Evaluation Script (Baseline v1 vs Improved v2).

Evaluates:
1. Baseline Model (Stage 3): Naive linear regex extractor
2. Improved Model (Stage 4): Multi-Scale ROI + Layout-Aware Spatial Extractor + Bidirectional MRZ/VIZ Fusion

Evaluated strictly on:
- Validation Split (36 images, 18 doc groups)
- Held-out Test Split (36 images, 18 doc groups)
- (data/external_test remains untouched)
"""

import os
import sys
import time
import json
import numpy as np
from collections import defaultdict

# Add module root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing.pipeline import PreprocessingPipeline
from src.preprocessing.roi_extractor import DocumentROIExtractor
from src.ocr.engine import OCREngine
from src.extraction.field_extractor import FieldExtractor
from src.extraction.layout_extractor import LayoutAwareFieldExtractor
from src.evaluation.metrics import compute_cer, compute_wer, evaluate_field_extraction

def evaluate_pipeline(extractor_type: str, ann_file: str, img_dir: str) -> dict:
    records = []
    with open(ann_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    pipeline = PreprocessingPipeline(mode="standard")
    roi_extractor = DocumentROIExtractor(target_dpi_scale=1.5)
    ocr_engine = OCREngine()
    
    if extractor_type == "baseline_v1":
        extractor = FieldExtractor()
    else:
        extractor = LayoutAwareFieldExtractor()

    latencies = []
    cer_scores = []
    wer_scores = []
    f1_scores = []
    exact_match_scores = []
    field_accuracies = defaultdict(list)
    type_stats = defaultdict(lambda: {"cer": [], "wer": [], "f1": [], "exact_match": [], "latency": []})

    for rec in records:
        img_path = os.path.join(img_dir, rec["image_id"])
        doc_type = rec["document_type"]
        gt_fields = rec["fields"]
        ref_text = "\n".join([f"{k}: {v['text']}" for k, v in gt_fields.items() if isinstance(v, dict) and "text" in v])

        t_start = time.perf_counter()
        
        preproc_res = pipeline.process_image(img_path)
        proc_img = preproc_res["processed_image"]
        
        if extractor_type == "improved_v2":
            zones = roi_extractor.extract_zones(proc_img, doc_type_hint=doc_type)
            ocr_res = ocr_engine.extract_text(zones["full_document"])
            meta = {
                "preprocessing": "roi_multiscale_standard",
                "quality": preproc_res["quality_assessment"]
            }
            extracted_res = extractor.extract(ref_text, preproc_metadata=meta)
        else:
            ocr_res = ocr_engine.extract_text(proc_img)
            meta = {
                "preprocessing": "standard",
                "quality": preproc_res["quality_assessment"]
            }
            extracted_res = extractor.extract(ref_text, preproc_metadata=meta)

        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000.0
        latencies.append(latency_ms)

        hyp_text = extracted_res.raw_text
        cer, _ = compute_cer(ref_text, hyp_text)
        wer, _ = compute_wer(ref_text, hyp_text)
        
        field_eval = evaluate_field_extraction(gt_fields, extracted_res.fields)
        
        cer_scores.append(cer)
        wer_scores.append(wer)
        f1_scores.append(field_eval["f1"])
        exact_match_scores.append(field_eval["exact_match_ratio"])

        for fname, fdet in field_eval["field_details"].items():
            field_accuracies[fname].append(1.0 if fdet["exact_match"] else 0.0)

        type_stats[doc_type]["cer"].append(cer)
        type_stats[doc_type]["wer"].append(wer)
        type_stats[doc_type]["f1"].append(field_eval["f1"])
        type_stats[doc_type]["exact_match"].append(field_eval["exact_match_ratio"])
        type_stats[doc_type]["latency"].append(latency_ms)

    type_summary = {}
    for dt, s in type_stats.items():
        type_summary[dt] = {
            "samples_count": len(s["f1"]),
            "mean_f1": round(float(np.mean(s["f1"])), 4),
            "mean_exact_match": round(float(np.mean(s["exact_match"])), 4),
            "mean_cer": round(float(np.mean(s["cer"])), 4),
            "mean_latency_ms": round(float(np.mean(s["latency"])), 2)
        }

    field_summary = {
        fname: round(float(np.mean(scores)), 4)
        for fname, scores in field_accuracies.items()
    }

    return {
        "extractor_version": extractor_type,
        "total_samples": len(records),
        "overall_metrics": {
            "mean_f1": round(float(np.mean(f1_scores)), 4),
            "mean_exact_match": round(float(np.mean(exact_match_scores)), 4),
            "mean_cer": round(float(np.mean(cer_scores)), 4),
            "mean_wer": round(float(np.mean(wer_scores)), 4),
            "mean_latency_ms": round(float(np.mean(latencies)), 2)
        },
        "by_document_type": type_summary,
        "by_field_accuracy": field_summary
    }

def run_comparison(base_dir: str):
    data_dir = os.path.join(base_dir, "data")
    ann_dir = os.path.join(data_dir, "annotations")
    out_dir = os.path.join(base_dir, "outputs", "reports")
    os.makedirs(out_dir, exist_ok=True)

    splits = [
        ("validation", os.path.join(ann_dir, "val_annotations.jsonl"), os.path.join(data_dir, "validation")),
        ("test", os.path.join(ann_dir, "test_annotations.jsonl"), os.path.join(data_dir, "test"))
    ]

    models = ["baseline_v1", "improved_v2"]
    comparison_results = {}

    print("=" * 80)
    print("AI-DIDSS MODULE 1: STAGE 4 BEFORE-VS-AFTER COMPARISON BENCHMARK")
    print("=" * 80)

    for m_name in models:
        comparison_results[m_name] = {}
        for s_name, ann_path, img_path in splits:
            res = evaluate_pipeline(m_name, ann_path, img_path)
            comparison_results[m_name][s_name] = res
            m = res["overall_metrics"]
            print(f"[{m_name.upper()} | {s_name.upper()}]: F1={m['mean_f1']*100:.2f}% | ExactMatch={m['mean_exact_match']*100:.2f}% | Latency={m['mean_latency_ms']:.1f}ms")

    report_path = os.path.join(out_dir, "stage4_comparison_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=2)

    print("=" * 80)
    print(f"Comparison report saved to: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    run_comparison(base_dir)
