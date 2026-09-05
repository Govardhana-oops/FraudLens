# AI-DIDSS Module 1: Standardized Field Extraction & Document Understanding Schema

**Standard Version:** 2.0.0  
**Specification:** ISO/IEC 19794, ICAO Doc 9303, AAMVA DL Standards  
**JSON Output Specification**

---

## 1. Top-Level Extraction Payload Schema

```json
{
  "document_type": "passport",
  "document_type_confidence": 0.99,
  "raw_text": "PASSPORT / PASSEPORT ...",
  "fields": {
    "full_name": {
      "value": "JOHN MICHAEL SMITH",
      "raw_value": "JOHN MICHAEL SMITH",
      "confidence": 0.95,
      "source": "visual_text",
      "extraction_method": "spatial_label_value",
      "validation_status": "VALID",
      "bounding_box": [300, 195, 750, 235],
      "warnings": [],
      "corrections": []
    },
    "passport_number": {
      "value": "P91823746",
      "raw_value": "P91823746",
      "confidence": 1.0,
      "source": "mrz",
      "extraction_method": "mrz_checksum_verified",
      "validation_status": "VALID",
      "bounding_box": [40, 620, 960, 670],
      "warnings": [],
      "corrections": []
    }
  },
  "mrz_validation": {
    "mrz_format": "TD3",
    "lines": [
      "P<UTOSMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<",
      "P918237464UTO8504128M3004121<<<<<<<<<<<<<<02"
    ],
    "document_number_checksum": true,
    "dob_checksum": true,
    "expiry_checksum": true,
    "composite_checksum": true,
    "all_checksums_pass": true,
    "status": "VALID"
  },
  "cross_field_conflicts": [],
  "validation_summary": {
    "all_valid": true,
    "valid_fields_count": 8,
    "invalid_fields_count": 0,
    "unknown_fields_count": 0,
    "conflict_fields_count": 0
  },
  "processing_metadata": {
    "preprocessing_mode": "roi_multiscale_standard",
    "model_version": "v2.0.0-improved",
    "quality_score": 1.0,
    "quality_status": "ACCEPTABLE"
  },
  "status": "SUCCESS",
  "review_required": false
}
```

---

## 2. Field Object Attribute Definitions

| Attribute | Type | Description |
| :--- | :--- | :--- |
| **`value`** | `str` | Normalized, standard representation (e.g. `YYYY-MM-DD` for dates, uppercase trimmed for names). |
| **`raw_value`** | `str` | Exact unnormalized OCR string extracted prior to corrections. |
| **`confidence`** | `float` ($0.0 - 1.0$) | Weighted confidence score based on OCR quality, spatial proximity, and checksum verification. |
| **`source`** | `str` | Extraction origin: `visual_text`, `mrz`, `barcode_pdf417`, or `cross_fused`. |
| **`extraction_method`** | `str` | Mechanism used: `spatial_label_value`, `mrz_checksum_verified`, `regex_pattern`, or `layout_anchor`. |
| **`validation_status`** | `str` | Status code: `VALID`, `INVALID`, `UNKNOWN`, or `NOT_APPLICABLE`. |
| **`bounding_box`** | `list[int]` | `[xmin, ymin, xmax, ymax]` pixel coordinates, or `null` if derived globally. |
| **`warnings`** | `list[str]` | Operational advisory notes (e.g. `"Near expiry document"`, `"Character disambiguated"`). |
| **`corrections`** | `list[dict]` | Audit trail of character or format adjustments made during normalization. |

---

## 3. Cross-Field Conflict Object Schema

When visual text and MRZ data disagree on a specific attribute:

```json
{
  "field": "date_of_birth",
  "status": "CONFLICT",
  "visual_value": "1985-04-12",
  "mrz_value": "1986-04-12",
  "confidence_visual": 0.85,
  "confidence_mrz": 1.0,
  "resolution_recommendation": "REVIEW_REQUIRED"
}
```
