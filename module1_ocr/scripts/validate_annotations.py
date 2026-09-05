"""Annotation Schema Validation Script for Module 1.

Validates that OCR annotations conform to the AI-DIDSS schema:
- Format verification (JSONL structure)
- Bounding box geometry: [xmin, ymin, xmax, ymax] within [0, 0, width, height]
- Non-empty transcribed text strings
- Document type conformance (passport, visa, driver_license, national_id, permit)
- Required field completeness per document type
- Exits with 0 on PASS, 1 on FAIL.
"""

import os
import sys
import json

REQUIRED_FIELDS_BY_DOCTYPE = {
    "passport": ["document_type", "passport_number", "surname", "given_names", "nationality", "date_of_birth", "date_of_expiry", "mrz_line1", "mrz_line2"],
    "visa": ["document_type", "visa_number", "full_name", "passport_number", "issue_date", "expiry_date", "mrz_line1", "mrz_line2"],
    "driver_license": ["document_type", "license_number", "full_name", "address", "date_of_birth", "issue_date", "expiry_date", "vehicle_class"],
    "national_id": ["document_type", "id_number", "full_name", "date_of_birth", "nationality", "expiry_date", "mrz_line1", "mrz_line2", "mrz_line3"],
    "permit": ["document_type", "permit_number", "full_name", "permit_category", "valid_until", "sponsor"]
}

def validate_annotations_file(ann_filepath: str):
    if not os.path.exists(ann_filepath):
        print(f"[FAIL] Annotation file not found: {ann_filepath}")
        return False, []

    errors = []
    record_count = 0

    with open(ann_filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            
            record_count += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Malformed JSON - {str(e)}")
                continue

            img_id = rec.get("image_id", f"Line_{line_num}")
            doc_type = rec.get("document_type")
            doc_id = rec.get("document_id")
            w = rec.get("width")
            h = rec.get("height")
            fields = rec.get("fields", {})

            # 1. Structural checks
            if not doc_type or doc_type not in REQUIRED_FIELDS_BY_DOCTYPE:
                errors.append(f"{img_id}: Unsupported or missing document_type '{doc_type}'")
            if not doc_id:
                errors.append(f"{img_id}: Missing document_id")
            if not isinstance(w, int) or not isinstance(h, int) or w <= 0 or h <= 0:
                errors.append(f"{img_id}: Invalid dimensions ({w}x{h})")

            # 2. Field completeness
            if doc_type in REQUIRED_FIELDS_BY_DOCTYPE:
                req_fields = REQUIRED_FIELDS_BY_DOCTYPE[doc_type]
                for rf in req_fields:
                    if rf not in fields:
                        errors.append(f"{img_id}: Missing required field '{rf}' for document type '{doc_type}'")

            # 3. Geometry & text checks
            for fname, fdata in fields.items():
                if not isinstance(fdata, dict):
                    errors.append(f"{img_id}: Field '{fname}' data must be an object")
                    continue
                
                text = fdata.get("text")
                bbox = fdata.get("bbox")
                
                if text is None or not str(text).strip():
                    errors.append(f"{img_id}: Field '{fname}' text is empty")
                
                if not bbox or len(bbox) != 4:
                    errors.append(f"{img_id}: Field '{fname}' bbox must have 4 coordinates [xmin, ymin, xmax, ymax]")
                else:
                    x1, y1, x2, y2 = bbox
                    if not (isinstance(x1, (int, float)) and isinstance(y1, (int, float)) and isinstance(x2, (int, float)) and isinstance(y2, (int, float))):
                        errors.append(f"{img_id}: Field '{fname}' bbox coordinates must be numbers")
                    elif x1 >= x2 or y1 >= y2:
                        errors.append(f"{img_id}: Field '{fname}' inverted bbox [{x1}, {y1}, {x2}, {y2}]")
                    elif x1 < 0 or y1 < 0 or x2 > w or y2 > h:
                        errors.append(f"{img_id}: Field '{fname}' bbox [{x1}, {y1}, {x2}, {y2}] exceeds image boundaries ({w}x{h})")

    is_valid = len(errors) == 0
    return is_valid, errors, record_count

def run_validation(cleaned_ann_file: str, ext_ann_file: str, report_dir: str):
    os.makedirs(report_dir, exist_ok=True)
    
    print("=" * 60)
    print("RUNNING ANNOTATION SCHEMA VALIDATION")
    print("=" * 60)
    
    val1_pass, errors1, count1 = validate_annotations_file(cleaned_ann_file)
    val2_pass, errors2, count2 = validate_annotations_file(ext_ann_file)
    
    all_pass = val1_pass and val2_pass
    all_errors = errors1 + errors2
    
    report = {
        "status": "PASS" if all_pass else "FAIL",
        "cleaned_annotations_count": count1,
        "external_annotations_count": count2,
        "total_validated": count1 + count2,
        "total_violations": len(all_errors),
        "violations": all_errors
    }
    
    report_file = os.path.join(report_dir, "annotation_validation_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Cleaned Annotations:  {count1} records -> {'PASS' if val1_pass else 'FAIL'}")
    print(f"External Annotations: {count2} records -> {'PASS' if val2_pass else 'FAIL'}")
    print(f"Overall Status:       {'PASS' if all_pass else 'FAIL'} ({len(all_errors)} violations)")
    print(f"Report saved to:      {report_file}")
    print("=" * 60)
    
    return all_pass

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cleaned_ann = os.path.join(base_dir, "data", "annotations", "cleaned_annotations.jsonl")
    ext_ann = os.path.join(base_dir, "data", "annotations", "external_test_annotations.jsonl")
    report_dir = os.path.join(base_dir, "outputs", "reports")
    success = run_validation(cleaned_ann, ext_ann, report_dir)
    sys.exit(0 if success else 1)
