# AI-DIDSS Module 2: Interface Contract & Integration Specification

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Public API Interface

```python
from src.interface import document_validator

# Input can be a dictionary, JSON string, or Module1InputPayload object
result = document_validator.validate(module1_ocr_output)
```

---

## 2. Input Contract Schema (from Module 1)

```json
{
  "status": "SUCCESS",
  "document_type": {
    "value": "passport",
    "confidence": 0.99
  },
  "fields": {
    "passport_number": {
      "value": "P12345678",
      "raw_value": "P12345678",
      "confidence": 0.98,
      "status": "VALID",
      "source": "visual_text",
      "extraction_method": "spatial_label_value",
      "warnings": [],
      "corrections": []
    },
    "date_of_expiry": {
      "value": "2030-08-25",
      "confidence": 0.95,
      "status": "VALID"
    }
  },
  "mrz": {
    "status": "VALID",
    "mrz_format": "TD3",
    "lines": [
      "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
      "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
    ],
    "checksum_valid": true,
    "checks": {
      "doc_number": true,
      "dob": true,
      "expiry": true,
      "composite": true
    }
  },
  "consistency": {
    "status": "CONSISTENT",
    "conflicts": []
  },
  "review_required": false,
  "warnings": [],
  "processing_metadata": {}
}
```

---

## 3. Output Contract Schema (to Downstream Modules 5, 7, 8)

```json
{
  "module": "module2_document_validation",
  "module_version": "1.0.0",
  "document_type": "passport",
  "overall_status": "VALID",
  "validation_score": 1.0,
  "checks": [
    {
      "rule_id": "DATE_CALENDAR_VALIDITY",
      "category": "DATE",
      "status": "PASS",
      "severity": "CRITICAL",
      "message": "Date 'date_of_expiry' is a valid calendar date (2030-08-25)",
      "field_name": "date_of_expiry",
      "expected": null,
      "actual": "2030-08-25",
      "details": {}
    }
  ],
  "field_results": {
    "passport_number": {
      "field_name": "passport_number",
      "value": "P12345678",
      "status": "VALID",
      "checks_passed": 2,
      "checks_failed": 0,
      "messages": []
    }
  },
  "cross_field_conflicts": [],
  "mrz_validation": {
    "format": "TD3",
    "lines": [
      "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
      "P123456789USA8504124M3008258<<<<<<<<<<<<<<<8"
    ],
    "checksum_valid": true,
    "checks": {
      "doc_number": true,
      "dob": true,
      "expiry": true,
      "composite": true
    }
  },
  "warnings": [],
  "errors": [],
  "review_required": false,
  "validation_metadata": {
    "total_checks": 10,
    "checks_passed": 10,
    "checks_failed": 0,
    "checks_warning": 0,
    "checks_unknown": 0,
    "doc_type_confidence": 0.99,
    "is_doc_type_ambiguous": false
  }
}
```

---

## 4. Status Taxonomy & Downstream Interpretation Contract

| Status Code | Downstream Meaning (Module 5 & UI) | Automated Action Allowed? |
| :--- | :--- | :---: |
| **`VALID`** | High structural & syntactic consistency across optical data | Yes (Aggregated with Modules 3 & 4) |
| **`INVALID`** | Substantive physical/calendar/chronological impossibility | Flagged for officer inspection |
| **`EXPIRED`** | Structurally valid document past validity expiration | Flagged for officer inspection |
| **`REVIEW_REQUIRED`** | OCR uncertainty, optical ambiguity, or Visual/MRZ discrepancy | Requires human officer review |
| **`UNKNOWN`** | Unidentifiable document or missing primary key | Requires manual capture or rescanning |
| **`UNSUPPORTED_DOCUMENT`**| Document class outside supported identity types | Requires alternative manual inspection |
| **`INVALID_INPUT`** | Corrupted image stream or decode failure | Prompt user for resubmission |
| **`PROCESSING_ERROR`** | Internal exception handled safely | Logged in system diagnostic telemetry |
