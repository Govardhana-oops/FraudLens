# AI-DIDSS Module 1: Field Validation & Normalization Rules

**Module:** Module 1 (OCR Extraction & Document Data Understanding)  
**Standard Compliance:** ICAO Doc 9303, AAMVA DL/ID Card Standard, ISO 8601  

---

## 1. Document Format & Pattern Validation Rules

| Field Name | Target Document | Expected Regex / Structural Format | Validation Check |
| :--- | :--- | :--- | :--- |
| **`passport_number`** | Passport | `^[A-Z0-9]{8,10}$` | ICAO Modulo-10 checksum ($[7, 3, 1]$ weights) |
| **`visa_number`** | Visa | `^V[A-Z0-9]{7,9}$` or `^[A-Z0-9]{8,10}$` | ICAO Modulo-10 check digit |
| **`license_number`** | Driver's License | `^DL-[A-Z0-9]+$` or `^[A-Z0-9]{8,12}$` | Alphanumeric string structure |
| **`id_number`** | National ID | `^ID-[A-Z0-9]+$` or `^[A-Z0-9]{8,12}$` | Alphanumeric string structure |
| **`permit_number`** | Residence Permit | `^RP-[A-Z0-9]+$` or `^[A-Z0-9]{8,12}$` | Alphanumeric string structure |
| **`nationality`** | All | `^[A-Z]{3}$` (ISO 3166-1 alpha-3) | Membership in international country code registry |
| **`gender`** | All | `^[MFU]$` | Normalized to `M` (Male), `F` (Female), or `U` (Unspecified) |

---

## 2. Chronological & Relational Validation Rules

1. **Date Format Standard:** All dates normalized to ISO 8601 `YYYY-MM-DD`.
2. **Chronological Ordering:**
   $$\text{Date of Birth} < \text{Date of Issue} < \text{Date of Expiry}$$
3. **Biological Age Constraint:**
   $$\text{Current Date} - \text{Date of Birth} \ge 0 \text{ (Age is non-negative)}$$
4. **Visa Validity Constraint:**
   $$\text{Visa Valid From} \le \text{Visa Valid Until}$$

---

## 3. Cross-Field Visual vs MRZ Consistency Matrix

| Visual Field (VIZ) | MRZ Field | Consistency Rule | Handling on Discrepancy |
| :--- | :--- | :--- | :--- |
| `passport_number` | `doc_number` (MRZ Line 2) | Identical Alphanumeric Match | Flag `CONFLICT`, record both values, mark `REVIEW_REQUIRED` |
| `full_name` | `surname` + `given_names` | Token Substring Inclusion | Flag `WARNING` if partial, `CONFLICT` if mismatched |
| `date_of_birth` | `dob_mrz` (MRZ Line 2) | Exact Year/Month/Day Equivalence | Flag `CONFLICT`, mark `REVIEW_REQUIRED` |
| `date_of_expiry` | `expiry_mrz` (MRZ Line 2) | Exact Year/Month/Day Equivalence | Flag `CONFLICT`, mark `REVIEW_REQUIRED` |
| `nationality` | `country_code` (MRZ Line 2) | Exact ISO Code Match | Flag `CONFLICT`, mark `REVIEW_REQUIRED` |

*Important Principle:* A cross-field mismatch is recorded as an explicit **evidentiary conflict**, **never** as an automatic fraud determination.
