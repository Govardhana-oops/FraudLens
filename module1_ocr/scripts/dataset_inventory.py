"""Dataset Inventory Script for Module 1.

Scans the raw dataset directory and generates both:
1. Machine-readable JSON inventory (outputs/reports/dataset_inventory.json)
2. Human-readable CSV inventory (outputs/reports/dataset_inventory.csv)

Reports dimensions, format, file size, hash, and checks for corrupted or duplicate files.
"""

import os
import sys
import json
import hashlib
from collections import Counter
from PIL import Image

def compute_file_hash(filepath: str) -> str:
    """Computes SHA-256 hash of a file for exact duplicate detection."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def inventory_dataset(raw_dir: str, annotations_file: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    # Load raw annotations if available
    annotations_map = {}
    if os.path.exists(annotations_file):
        with open(annotations_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    annotations_map[data["image_id"]] = data

    inventory_items = []
    seen_hashes = {}
    doc_type_counts = Counter()
    format_counts = Counter()
    status_counts = Counter()

    for root, _, files in os.walk(raw_dir):
        for fname in sorted(files):
            if fname.startswith("."):
                continue
            
            fpath = os.path.join(root, fname)
            file_size = os.path.getsize(fpath)
            
            item = {
                "filename": fname,
                "relative_path": os.path.relpath(fpath, raw_dir),
                "file_size_bytes": file_size,
                "file_hash_sha256": None,
                "format": None,
                "width": None,
                "height": None,
                "channels": None,
                "document_type": "UNKNOWN",
                "document_id": None,
                "has_annotation": fname in annotations_map,
                "is_corrupted": False,
                "is_duplicate": False,
                "status": "VALID",
                "rejection_reason": None
            }
            
            # Check 0-byte
            if file_size == 0:
                item["is_corrupted"] = True
                item["status"] = "REJECTED"
                item["rejection_reason"] = "Zero-byte file"
                status_counts["REJECTED_ZERO_BYTE"] += 1
                inventory_items.append(item)
                continue

            item["file_hash_sha256"] = compute_file_hash(fpath)
            
            # Duplicate check
            if item["file_hash_sha256"] in seen_hashes:
                item["is_duplicate"] = True
                item["status"] = "DUPLICATE"
                item["rejection_reason"] = f"Duplicate of {seen_hashes[item['file_hash_sha256']]}"
                status_counts["DUPLICATE"] += 1
            else:
                seen_hashes[item["file_hash_sha256"]] = fname

            # Image reading & integrity check
            try:
                with Image.open(fpath) as img:
                    item["format"] = img.format
                    item["width"] = img.width
                    item["height"] = img.height
                    item["channels"] = len(img.getbands())
                    format_counts[img.format or "UNKNOWN"] += 1
                    
                    # Check minimum size threshold
                    if img.width < 200 or img.height < 200:
                        item["status"] = "REJECTED"
                        item["rejection_reason"] = f"Dimensions too small ({img.width}x{img.height} < 200x200)"
                        status_counts["REJECTED_TOO_SMALL"] += 1
                    elif not item["is_duplicate"]:
                        status_counts["VALID"] += 1
            except Exception as e:
                item["is_corrupted"] = True
                item["status"] = "REJECTED"
                item["rejection_reason"] = f"Corrupted image header / unreadable ({str(e)})"
                status_counts["REJECTED_CORRUPTED"] += 1

            # Annotation metadata
            if fname in annotations_map:
                ann = annotations_map[fname]
                item["document_type"] = ann.get("document_type", "UNKNOWN")
                item["document_id"] = ann.get("document_id", None)
                doc_type_counts[item["document_type"]] += 1
            else:
                doc_type_counts["NO_ANNOTATION"] += 1

            inventory_items.append(item)

    # Save JSON summary
    summary_report = {
        "total_files_scanned": len(inventory_items),
        "status_breakdown": dict(status_counts),
        "document_type_breakdown": dict(doc_type_counts),
        "format_breakdown": dict(format_counts),
        "inventory": inventory_items
    }
    
    json_path = os.path.join(output_dir, "dataset_inventory.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    # Save CSV summary
    csv_path = os.path.join(output_dir, "dataset_inventory.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        headers = ["filename", "status", "rejection_reason", "document_type", "document_id", "width", "height", "file_size_bytes", "has_annotation"]
        f.write(",".join(headers) + "\n")
        for it in inventory_items:
            row = [
                it["filename"],
                it["status"],
                f'"{it["rejection_reason"] or ""}"',
                it["document_type"],
                str(it["document_id"] or ""),
                str(it["width"] or ""),
                str(it["height"] or ""),
                str(it["file_size_bytes"]),
                str(it["has_annotation"])
            ]
            f.write(",".join(row) + "\n")

    print(f"Dataset Inventory Complete:")
    print(f"  Total scanned: {len(inventory_items)}")
    print(f"  Status breakdown: {dict(status_counts)}")
    print(f"  Doc types: {dict(doc_type_counts)}")
    print(f"  Saved to: {json_path} and {csv_path}")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(base_dir, "data", "raw")
    annotations_file = os.path.join(base_dir, "data", "annotations", "raw_annotations.jsonl")
    output_dir = os.path.join(base_dir, "outputs", "reports")
    inventory_dataset(raw_dir, annotations_file, output_dir)
