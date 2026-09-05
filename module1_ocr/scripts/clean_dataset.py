"""Dataset Cleaning Script for Module 1.

Filters, cleans, and validates raw document images:
- Rejects zero-byte, corrupted, malformed, or undersized images (< 200x200).
- Rejects images missing required ground truth annotations.
- Eliminates exact duplicate files.
- Copies all verified, valid files to data/cleaned/.
- Exports cleaned annotations to data/annotations/cleaned_annotations.jsonl.
- Generates a full audit trail report in outputs/reports/data_cleaning_report.json.
"""

import os
import shutil
import json
import hashlib
from PIL import Image

def compute_file_hash(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def clean_dataset(raw_dir: str, cleaned_dir: str, raw_ann_file: str, cleaned_ann_file: str, report_dir: str):
    os.makedirs(cleaned_dir, exist_ok=True)
    os.makedirs(os.path.dirname(cleaned_ann_file), exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)

    # Load raw annotations
    raw_annotations = {}
    if os.path.exists(raw_ann_file):
        with open(raw_ann_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    raw_annotations[data["image_id"]] = data

    accepted_records = []
    rejected_records = []
    seen_hashes = {}
    
    for root, _, files in os.walk(raw_dir):
        for fname in sorted(files):
            if fname.startswith("."):
                continue
            
            fpath = os.path.join(root, fname)
            file_size = os.path.getsize(fpath)
            
            # Rule 1: Zero-byte file
            if file_size == 0:
                rejected_records.append({
                    "filename": fname,
                    "reason": "Corrupted: Zero-byte file",
                    "file_size": 0
                })
                continue

            # Rule 2: Hash duplicates
            fhash = compute_file_hash(fpath)
            if fhash in seen_hashes:
                rejected_records.append({
                    "filename": fname,
                    "reason": f"Duplicate of {seen_hashes[fhash]}",
                    "file_size": file_size
                })
                continue

            # Rule 3: Image open & dimensions check
            try:
                with Image.open(fpath) as img:
                    img_format = img.format
                    w, h = img.size
                    channels = len(img.getbands())
                    
                    if w < 200 or h < 200:
                        rejected_records.append({
                            "filename": fname,
                            "reason": f"Dimension violation: {w}x{h} is below minimum 200x200",
                            "file_size": file_size
                        })
                        continue
            except Exception as e:
                rejected_records.append({
                    "filename": fname,
                    "reason": f"Image format error / unreadable: {str(e)}",
                    "file_size": file_size
                })
                continue

            # Rule 4: Annotation existence & completeness
            if fname not in raw_annotations:
                rejected_records.append({
                    "filename": fname,
                    "reason": "Missing ground truth annotation record",
                    "file_size": file_size
                })
                continue

            ann = raw_annotations[fname]
            if not ann.get("fields") or len(ann["fields"]) == 0:
                rejected_records.append({
                    "filename": fname,
                    "reason": "Annotation has empty fields dictionary",
                    "file_size": file_size
                })
                continue

            # File passed all cleaning checks!
            seen_hashes[fhash] = fname
            
            # Copy to cleaned directory
            dest_path = os.path.join(cleaned_dir, fname)
            shutil.copy2(fpath, dest_path)
            
            # Record cleaned annotation
            cleaned_record = {
                "image_id": fname,
                "document_id": ann["document_id"],
                "document_type": ann["document_type"],
                "source": ann.get("source", "synth_doc_gen_v1"),
                "variation": ann.get("variation", "standard"),
                "width": w,
                "height": h,
                "channels": channels,
                "file_size_bytes": file_size,
                "sha256": fhash,
                "fields": ann["fields"]
            }
            accepted_records.append(cleaned_record)

    # Save cleaned annotations JSONL
    with open(cleaned_ann_file, "w", encoding="utf-8") as f:
        for r in accepted_records:
            f.write(json.dumps(r) + "\n")

    # Generate cleaning audit report
    cleaning_report = {
        "raw_directory": raw_dir,
        "cleaned_directory": cleaned_dir,
        "total_evaluated": len(accepted_records) + len(rejected_records),
        "total_accepted": len(accepted_records),
        "total_rejected": len(rejected_records),
        "rejection_summary": {
            r["reason"]: sum(1 for x in rejected_records if x["reason"] == r["reason"])
            for r in rejected_records
        },
        "rejected_details": rejected_records
    }

    report_path = os.path.join(report_dir, "data_cleaning_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(cleaning_report, f, indent=2)

    print(f"Data Cleaning Complete:")
    print(f"  Evaluated: {cleaning_report['total_evaluated']}")
    print(f"  Accepted:  {cleaning_report['total_accepted']}")
    print(f"  Rejected:  {cleaning_report['total_rejected']}")
    print(f"  Report saved to: {report_path}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(base_dir, "data", "raw")
    cleaned_dir = os.path.join(base_dir, "data", "cleaned")
    raw_ann = os.path.join(base_dir, "data", "annotations", "raw_annotations.jsonl")
    cleaned_ann = os.path.join(base_dir, "data", "annotations", "cleaned_annotations.jsonl")
    report_dir = os.path.join(base_dir, "outputs", "reports")
    clean_dataset(raw_dir, cleaned_dir, raw_ann, cleaned_ann, report_dir)
