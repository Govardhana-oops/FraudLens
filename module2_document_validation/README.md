# AI-DIDSS Module 2: Document Validation Engine

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Status:** **`FROZEN (161/161 TESTS PASSED - 100%)`**  

---

## 1. Overview & Operational Philosophy

Module 2 is an independent, deterministic document verification engine designed to evaluate structured optical character data emitted by Module 1 OCR. It assesses structural integrity, syntax compliance, calendar accuracy, temporal chronology, ICAO Doc 9303 modulo-10 checksums (TD1, TD2, TD3, MRV-A, MRV-B), and cross-field agreement between Visual Inspection Zones (VIZ) and Machine Readable Zones (MRZ).

### The Zero Autonomous Fraud Rule
> [!IMPORTANT]
> **Module 2 is an evidence collection and validation engine, NOT a judicial fraud determination system.**  
> A validation failure constitutes structured evidence for human officer review. Module 2 **NEVER outputs `FRAUD`, `CRIMINAL`, `DETAIN`, or `REJECT`** as autonomous conclusions.

---

## 2. Supported Document Types & MRZ Standards

1. **Passports (`passport`):** ICAO Doc 9303 TD3 ($2 \times 44$ chars), ISO 3166-1 alpha-3 country codes, validity span $\le 10.5$ years.
2. **Travel Visas (`visa`):** ICAO Doc 9303 MRV-A ($2 \times 44$) / MRV-B ($2 \times 36$), visa category, validity window, stay duration.
3. **Driver's Licenses (`driver_license`):** AAMVA standards, alphanumeric license syntax, minimum driving age ($\ge 16$ years), vehicle classes.
4. **National Identity Cards (`national_id`):** ICAO Doc 9303 TD1 ($3 \times 30$) / TD2 ($2 \times 36$), national ID structure.
5. **Residence / Work Permits (`permit`):** Permit registration code format, authorized immigration categories, sponsor documentation.
6. **Unknown / Ambiguous Documents (`unknown_document`):** Safe fallback routing to `UNKNOWN` or `REVIEW_REQUIRED`.

---

## 3. Precedence Hierarchy

$$\text{INVALID\_INPUT} \succ \text{UNSUPPORTED\_DOCUMENT} \succ \text{INVALID} \succ \text{UNKNOWN} \succ \text{REVIEW\_REQUIRED} \succ \text{EXPIRED} \succ \text{VALID}$$

---

## 4. How to Run Module 2 Independently

```powershell
# 1. Navigate to Module 2 directory
cd module2_document_validation

# 2. Run automated test suite (161 tests)
pytest tests/ -v -p no:cacheprovider
```

---

## 5. Performance Metrics

* **Average Latency:** **0.25 ms / document**
* **Throughput:** **~4,000 documents / second**
* **Memory Overhead:** **< 12 MB**
