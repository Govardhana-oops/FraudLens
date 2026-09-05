"""Dataset Partitioning & Data Leakage Prevention Script for Module 1.

Performs document/source-level grouped splitting:
- Groups samples strictly by unique document identity (`document_id`).
- Partitions document groups into:
    * 70% Training
    * 15% Validation
    * 15% Test
- Preserves `data/external_test/` completely isolated.
- Copies image files into data/train/, data/validation/, and data/test/.
- Emits split manifests into data/annotations/train_annotations.jsonl, val_annotations.jsonl, test_annotations.jsonl.
- Executes automated mathematical set intersection tests to certify 0% data leakage.
"""

import os
import shutil
import json
import random
from collections import defaultdict, Counter

# Fixed seed for reproducible partitions
random.seed(42)

def partition_and_copy(cleaned_ann_file: str, cleaned_img_dir: str, base_data_dir: str, report_dir: str):
    # 1. Load cleaned annotations
    records = []
    with open(cleaned_ann_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    # 2. Group records by document_id
    doc_groups = defaultdict(list)
    for r in records:
        doc_groups[r["document_id"]].append(r)

    unique_doc_ids = sorted(list(doc_groups.keys()))
    random.shuffle(unique_doc_ids)

    total_groups = len(unique_doc_ids)
    train_end = int(total_groups * 0.70)
    val_end = train_end + int(total_groups * 0.15)

    train_ids = set(unique_doc_ids[:train_end])
    val_ids = set(unique_doc_ids[train_end:val_end])
    test_ids = set(unique_doc_ids[val_end:])

    # 3. Data Leakage Verification Check
    inter_train_val = train_ids.intersection(val_ids)
    inter_train_test = train_ids.intersection(test_ids)
    inter_val_test = val_ids.intersection(test_ids)

    assert len(inter_train_val) == 0, f"DATA LEAKAGE DETECTED between Train and Val: {inter_train_val}"
    assert len(inter_train_test) == 0, f"DATA LEAKAGE DETECTED between Train and Test: {inter_train_test}"
    assert len(inter_val_test) == 0, f"DATA LEAKAGE DETECTED between Val and Test: {inter_val_test}"

    # Check external test isolation
    ext_ann_file = os.path.join(base_data_dir, "annotations", "external_test_annotations.jsonl")
    ext_ids = set()
    if os.path.exists(ext_ann_file):
        with open(ext_ann_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    ext_ids.add(json.loads(line)["document_id"])
        
        inter_ext_train = ext_ids.intersection(train_ids)
        inter_ext_val = ext_ids.intersection(val_ids)
        inter_ext_test = ext_ids.intersection(test_ids)
        assert len(inter_ext_train) == 0, f"DATA LEAKAGE DETECTED between External Test and Train: {inter_ext_train}"
        assert len(inter_ext_val) == 0, f"DATA LEAKAGE DETECTED between External Test and Val: {inter_ext_val}"
        assert len(inter_ext_test) == 0, f"DATA LEAKAGE DETECTED between External Test and Test: {inter_ext_test}"

    # 4. Prepare directories and copy files
    splits = {
        "train": (train_ids, os.path.join(base_data_dir, "train"), os.path.join(base_data_dir, "annotations", "train_annotations.jsonl")),
        "validation": (val_ids, os.path.join(base_data_dir, "validation"), os.path.join(base_data_dir, "annotations", "val_annotations.jsonl")),
        "test": (test_ids, os.path.join(base_data_dir, "test"), os.path.join(base_data_dir, "annotations", "test_annotations.jsonl"))
    }

    split_stats = {}

    for split_name, (id_set, target_dir, target_ann_file) in splits.items():
        os.makedirs(target_dir, exist_ok=True)
        split_records = []
        doc_type_counts = Counter()

        for doc_id in id_set:
            for rec in doc_groups[doc_id]:
                split_records.append(rec)
                doc_type_counts[rec["document_type"]] += 1
                
                # Copy image file
                src_img = os.path.join(cleaned_img_dir, rec["image_id"])
                dst_img = os.path.join(target_dir, rec["image_id"])
                shutil.copy2(src_img, dst_img)

        # Write split JSONL
        with open(target_ann_file, "w", encoding="utf-8") as f:
            for r in split_records:
                f.write(json.dumps(r) + "\n")

        split_stats[split_name] = {
            "document_groups_count": len(id_set),
            "total_images_count": len(split_records),
            "percentage_of_total_groups": round(len(id_set) / total_groups * 100, 2),
            "document_type_distribution": dict(doc_type_counts)
        }

    split_report = {
        "total_unique_document_identities": total_groups,
        "total_cleaned_images": len(records),
        "external_test_isolated_identities": len(ext_ids),
        "leakage_verification": {
            "train_val_overlap": len(inter_train_val),
            "train_test_overlap": len(inter_train_test),
            "val_test_overlap": len(inter_val_test),
            "external_train_overlap": len(inter_ext_train) if os.path.exists(ext_ann_file) else 0,
            "leakage_status": "ZERO_LEAKAGE_CERTIFIED"
        },
        "split_breakdown": split_stats
    }

    report_path = os.path.join(report_dir, "dataset_split_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(split_report, f, indent=2)

    print("=" * 60)
    print("DATASET SPLIT COMPLETE (GROUPED BY DOCUMENT IDENTITY)")
    print("=" * 60)
    print(f"Total Unique Document Identities: {total_groups}")
    for s_name, stats in split_stats.items():
        print(f"  [{s_name.upper()}]: {stats['document_groups_count']} doc groups ({stats['percentage_of_total_groups']}%) -> {stats['total_images_count']} images. Distribution: {stats['document_type_distribution']}")
    print(f"  [EXTERNAL TEST]: {len(ext_ids)} completely isolated document identities")
    print(f"Leakage Check: {split_report['leakage_verification']['leakage_status']}")
    print(f"Report saved to: {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cleaned_ann = os.path.join(base_dir, "data", "annotations", "cleaned_annotations.jsonl")
    cleaned_img = os.path.join(base_dir, "data", "cleaned")
    data_dir = os.path.join(base_dir, "data")
    report_dir = os.path.join(base_dir, "outputs", "reports")
    partition_and_copy(cleaned_ann, cleaned_img, data_dir, report_dir)
