# AI-DIDSS Module 5: Explainable Evidence & Anomaly Assessment Architecture

**Module:** `module5_explainable_evidence` (Module 5: Explainable Evidence & Anomaly Assessment Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Stage:** Stage 1 — Architecture & Multi-Source Evidence Fusion  
**Date:** 2026-09-03  

---

## 1. Executive Summary & Philosophy

Module 5 is the holistic evidence aggregation, cross-modal anomaly correlation, and explainable decision-support reasoning engine. It ingests outputs from:
* **Module 1 (OCR & Document Understanding):** Extracted text, confidence scores, visual fields.
* **Module 2 (Document Validation):** Schema syntax, calendar math, chronology, ICAO MRZ checksums.
* **Module 3 (Tampering Detection):** ELA, noise inconsistency, edge gradient clipping, moiré lattices.
* **Module 4 (Biometric Verification):** Facial match score, ICAO portrait quality, PAD liveness.

### Strict Decision-Support Mandate
> [!IMPORTANT]
> **Module 5 synthesizes forensic evidence for human border control officers. It does NOT issue autonomous legal or detention decisions.**  
> Module 5 **NEVER outputs `FRAUD`, `CRIMINAL`, `DETAIN`, `ARREST`, `FORGER`, or `REJECT`**. All recommendations are formulated as decision support (`CLEAR`, `STANDARD_INSPECTION`, `SECONDARY_INSPECTION_RECOMMENDED`, `TECHNICAL_REVIEW_REQUIRED`, `RECAPTURE_REQUIRED`).

---

## 2. Multi-Source Evidence Fusion Architecture

```
   [ M1: OCR Payload ]    [ M2: Validation ]    [ M3: Tampering ]    [ M4: Biometrics ]
            │                     │                     │                    │
            └─────────────────────┼─────────────────────┴────────────────────┘
                                  ▼
                   [ Multi-Source Ingestion & Gating ]
                   ├── Schema Validation & Uncertainty Parsing
                   └── Missing Module Fallback Handlers
                                  │
                                  ▼
                   [ Cross-Modal Anomaly Correlator ]
                   ├── Correlate M3 Spliced Photo with M4 Biometric Mismatch
                   ├── Correlate M1 Low Confidence with M2 Rule Failures
                   └── Correlate M3 Altered Digits with M2 MRZ Checksum Mismatch
                                  │
                                  ▼
                   [ Explainable Risk Index Calculator ]
                   ├── Document Syntactic Risk Score [0.0, 1.0]
                   ├── Physical Tampering Risk Score [0.0, 1.0]
                   ├── Biometric Identity Risk Score [0.0, 1.0]
                   └── Overall Calibrated Risk Index [0.0, 1.0]
                                  │
                                  ▼
                   [ Explainable Narrative Engine ]
                   ├── Deterministic Natural Language Summary
                   ├── Itemized Evidence Checklist (Positive & Negative)
                   └── Actionable Inspection Guidance
                                  │
                                  ▼
                   [ Comprehensive Decision Support Dossier ]
```

---

## 3. Recommended Officer Action Taxonomy

| Recommended Action | Condition | Operational Meaning |
| :--- | :--- | :--- |
| **`CLEAR`** | All modules `VALID` / `NO_TAMPERING` / `MATCH`, Risk Index $< 0.20$. | Proceed with standard clearance. |
| **`STANDARD_INSPECTION`** | Minor informational warnings, expired document, Risk Index $\in [0.20, 0.45)$. | Normal document inspection flow. |
| **`SECONDARY_INSPECTION_RECOMMENDED`**| High tampering anomaly, biometric mismatch, or MRZ checksum failure, Risk Index $\ge 0.70$. | Refer bearer to secondary inspection station with itemized evidence dossier. |
| **`TECHNICAL_REVIEW_REQUIRED`** | OCR ambiguity, visual vs MRZ conflict, or borderline biometric similarity. | Officer manual review of highlighted fields. |
| **`RECAPTURE_REQUIRED`** | Poor image resolution, dark lighting, or no face detected. | Re-scan document or re-take live photo. |
