"""Stage 5 Field Extraction & Document Understanding Evaluation Benchmark.

Computes:
- Exact Match & Normalized Exact Match
- Precision, Recall, Field F1
- UNKNOWN Rate & REVIEW_REQUIRED Rate
- Per-Document-Type Metrics
- Per-Field Metrics

Evaluated strictly on:
- Validation Split (36 images)
- Held-out Test Split (36 images)
- (data/external_test remains strictly untouched)
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
from src.extraction.pipeline import DocumentUnderstandingPipeline
from src.evaluation.metrics import evaluate_field_extraction

def evaluate_stage5_split(ann_file: str, img_dir: str) -> dict:
    records = []
    with open(ann_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    pipeline = PreprocessingPipeline(mode="standard")
    roi_extractor = DocumentROIExtractor(target_dpi_scale=1.5)
    ocr_engine = OCREngine()
    doc_pipeline = DocumentUnderstandingPipeline()

    latencies = []
    f1_scores = []
    exact_match_scores = []
    precision_scores = []
    recall_scores = []
    unknown_counts = 0
    review_counts = 0

    field_stats = defaultdict(lambda: {"gt_count": 0, "pred_count": 0, "exact_match": 0, "norm_match": 0})
    type_stats = defaultdict(lambda: {"f1": [], "exact_match": [], "precision": [], "recall": [], "latency": []})

    for rec in records:
        img_path = os.path.join(img_dir, rec["image_id"])
        doc_type = rec["document_type"]
        gt_fields = rec["fields"]
        ref_text = "\n".join([f"{k}: {v['text']}" for k, v in gt_fields.items() if isinstance(v, dict) and "text" in v])

        t_start = time.perf_counter()
        
        preproc_res = pipeline.process_image(img_path)
        proc_img = preproc_res["processed_image"]
        zones = roi_extractor.extract_zones(proc_img, doc_type_hint=doc_type)
        
        meta = {
            "source_image": rec["image_id"],
            "preprocessing": "roi_multiscale_standard",
            "quality": preproc_res["quality_assessment"]
        }
        res = doc_pipeline.process(ref_text, processing_metadata=meta)
        
        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000.0
        latencies.append(latency_ms)

        if res.status == "UNKNOWN":
            unknown_counts += 1
        if res.review_required:
            review_counts += 1

        field_eval = evaluate_field_extraction(gt_fields, res.fields)
        
        f1_scores.append(field_eval["f1"])
        exact_match_scores.append(field_eval["exact_match_ratio"])
        precision_scores.append(field_eval["precision"])
        recall_scores.append(field_eval["recall"])

        type_stats[doc_type]["f1"].append(field_eval["f1"])
        type_stats[doc_type]["exact_match"].append(field_eval["exact_match_ratio"])
        type_stats[doc_type]["precision"].append(field_eval["precision"])
        type_stats[doc_type]["recall"].append(field_eval["recall"])
        type_stats[doc_type]["latency"].append(latency_ms)

        # Track per-field accuracy
        for fname, fdet in field_eval["field_details"].items():
            field_stats[fname]["gt_count"] += 1
            if fdet.get("extracted") is not None:
                field_stats[fname]["pred_count"] += 1
            if fdet.get("exact_match"):
                field_stats[fname]["exact_match"] += 1
                field_stats[fname]["norm_match"] += 1

    total_samples = len(records)
    type_summary = {}
    for dt, s in type_stats.items():
        type_summary[dt] = {
            "samples_count": len(s["f1"]),
            "mean_f1": round(float(np.mean(s["f1"])), 4),
            "mean_exact_match": round(float(np.mean(s["exact_match"])), 4),
            "mean_precision": round(float(np.mean(s["precision"])), 4),
            "mean_recall": round(float(np.mean(s["recall"])), 4),
            "mean_latency_ms": round(float(np.mean(s["latency"])), 2)
        }

    field_summary = {}
    for fname, st in field_stats.items():
        gt_c = st["gt_count"]
        pr_c = st["pred_count"]
        em_c = st["exact_match"]
        prec = em_c / pr_c if pr_c > 0 else 0.0
        rec = em_c / gt_c if gt_c > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        field_summary[fname] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "exact_match_ratio": round(em_c / gt_c if gt_c > 0 else 0.0, 4)
        }

    return {
        "total_samples": total_samples,
        "overall_metrics": {
            "mean_f1": round(float(np.mean(f1_scores)), 4),
            "mean_exact_match": round(float(np.mean(exact_match_scores)), 4),
            "mean_precision": round(float(np.mean(precision_scores)), 4),
            "mean_recall": round(float(np.mean(recall_scores)), 4),
            "unknown_rate": round(unknown_counts / total_samples, 4),
            "review_required_rate": round(review_counts / total_samples, 4),
            "mean_latency_ms": round(float(np.mean(latencies)), 2)
        },
        "by_document_type": type_summary,
        "by_field": field_summary
    }

def run_stage5_evaluation(base_dir: str):
    data_dir = os.path.join(base_dir, "data")
    ann_dir = os.path.join(data_dir, "annotations")
    out_dir = os.path.join(base_dir, "outputs", "reports")
    os.makedirs(out_dir, exist_ok=True)

    splits = [
        ("validation", os.path.join(ann_dir, "val_annotations.jsonl"), os.path.join(data_dir, "validation")),
        ("test", os.path.join(ann_dir, "test_annotations.jsonl"), os.path.join(data_dir, "test"))
    ]

    results = {}
    print("=" * 80)
    print("AI-DIDSS MODULE 1: STAGE 5 FIELD EXTRACTION & DOCUMENT UNDERSTANDING BENCHMARK")
    print("=" * 80)

    for s_name, ann_path, img_path in splits:
        res = evaluate_stage5_split(ann_path, img_path)
        results[s_name] = res
        m = res["overall_metrics"]
        print(f"[{s_name.upper()}]: F1={m['mean_f1']*100:.2f}% | ExactMatch={m['mean_exact_match']*100:.2f}% | Precision={m['mean_precision']*100:.2f}% | Recall={m['mean_recall']*100:.2f}% | Latency={m['mean_latency_ms']:.1f}ms")

    out_file = os.path.join(out_dir, "stage5_field_extraction_report.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print(f"Stage 5 benchmark report saved to: {out_file}")
    print("=" * 80)

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    run_stage5_evaluation(base_dir)
