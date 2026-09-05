# AI-DIDSS: Module 1 to Module 2 Integration Contract

**Source Module:** `module1_ocr` (Module 1: OCR Extraction & Document Understanding)  
**Consumer Module:** `module2_validation` (Module 2: Document Rule & Security Logic Validation)  
**Contract Version:** `1.0.0-FROZEN`  
**Interface Mechanism:** Python Direct Class (`document_ocr.process()`) OR REST Endpoint (`POST /ocr/analyze`)  

---

## 1. Architectural Responsibility Separation

* **Module 1 Responsibility:** Visual text reading, image quality verification, MRZ parsing, modulo-10 check digit math, character normalization, spatial label-value extraction, and evidentiary consistency comparison.
* **Module 2 Responsibility:** Cross-referencing extracted fields against government/ICAO rule engines, issuing authority blacklists, geographic jurisdiction logic, validity duration bounds, and travel requirement policies.
* **Strict Boundary Rule:** Module 2 consumes the normalized structured JSON without needing to know internal optical filters, Hough deskewing transforms, or OCR regex implementations.

---

## 2. Standardized JSON Output Contract

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
      "confidence": 1.0,
      "status": "VALID",
      "source": "mrz",
      "extraction_method": "mrz_checksum_verified",
      "warnings": [],
      "corrections": []
    },
    "full_name": {
      "value": "JOHN MICHAEL SMITH",
      "raw_value": "JOHN MICHAEL SMITH",
      "confidence": 0.95,
      "status": "VALID",
      "source": "visual_text",
      "extraction_method": "spatial_label_value",
      "warnings": [],
      "corrections": []
    },
    "date_of_birth": {
      "value": "1985-04-12",
      "raw_value": "1985-04-12",
      "confidence": 0.95,
      "status": "VALID",
      "source": "visual_text",
      "extraction_method": "spatial_label_value",
      "warnings": [],
      "corrections": []
    },
    "date_of_expiry": {
      "value": "2030-08-25",
      "raw_value": "2030-08-25",
      "confidence": 0.95,
      "status": "VALID",
      "source": "visual_text",
      "extraction_method": "spatial_label_value",
      "warnings": [],
      "corrections": []
    },
    "nationality": {
      "value": "UTO",
      "raw_value": "UTO",
      "confidence": 0.98,
      "status": "VALID",
      "source": "visual_text",
      "extraction_method": "spatial_label_value",
      "warnings": [],
      "corrections": []
    }
  },
  "mrz": {
    "status": "VALID",
    "mrz_format": "TD3",
    "lines": [
      "P<UTOSMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<",
      "P123456789UTO8504124M3008258<<<<<<<<<<<<<<<8"
    ],
    "checksum_valid": true,
    "checks": {
      "document_number": true,
      "date_of_birth": true,
      "date_of_expiry": true,
      "composite": true
    }
  },
  "consistency": {
    "status": "CONSISTENT",
    "conflicts": []
  },
  "review_required": false,
  "warnings": [],
  "processing_metadata": {
    "module": "module1_ocr",
    "module_version": "1.0.0",
    "model_version": "LayoutAware-MultiScale-OCR-v2.0",
    "quality_assessment": {
      "is_valid": true,
      "quality_score": 1.0,
      "status": "ACCEPTABLE"
    }
  }
}
```

---

## 3. Allowed Top-Level Status Enum Values

| Status Value | Meaning | Module 2 Action |
| :--- | :--- | :--- |
| **`SUCCESS`** | All essential fields extracted with high confidence ($\ge 0.70$) and consistent evidence. | Proceed with full automated rule validation. |
| **`PARTIAL`** | Non-critical fields missing or partially extracted; core document number present. | Execute rules on available fields; mark missing attributes as `UNVERIFIED`. |
| **`UNKNOWN`** | Document type or key fields unidentifiable from optical capture. | Flag `MANUAL_REVIEW_REQUIRED` without declaring fraud. |
| **`REVIEW_REQUIRED`** | Low confidence, cross-field conflict, or chronological warning detected. | Forward conflicting evidence to officer dashboard. |
| **`INVALID_INPUT`** | Corrupted image, empty byte buffer, or resolution $< 100\times 100$. | Return input rejection error to submission interface. |
| **`UNSUPPORTED_DOCUMENT`**| Document format not part of supported specifications. | Route to generalized document review queue. |
| **`PROCESSING_ERROR`** | Internal exception handled safely without crashing. | Log diagnostic traceback and prompt user re-upload. |

---

## 4. Evidentiary Cross-Field Conflict Object Schema

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
