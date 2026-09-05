# AI-DIDSS Module 5: Explainable Evidence & Anomaly Assessment Engine

**Module:** `module5_explainable_evidence` (Module 5: Explainable Evidence & Anomaly Assessment Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Status:** **`FROZEN (26/26 TESTS PASSED - 100%)`**  

---

## 1. Overview & Operational Philosophy

Module 5 synthesizes multi-source findings from OCR (Module 1), Rule Validation (Module 2), Physical Tampering Detection (Module 3), and Facial Biometrics (Module 4) into a unified, explainable risk assessment dossier.

### Strict Decision-Support Invariant
> [!IMPORTANT]
> **Module 5 provides structured, transparent decision support for human border inspection officers.**  
> It **NEVER outputs `FRAUD`, `CRIMINAL`, `DETAIN`, `REJECT`, or `ARREST`**. All conclusions are formatted as actionable operational recommendations (`CLEAR`, `STANDARD_INSPECTION`, `SECONDARY_INSPECTION_RECOMMENDED`, `TECHNICAL_REVIEW_REQUIRED`, `RECAPTURE_REQUIRED`).

---

## 2. Dimensional Risk Indices

1. **Document Syntactic Risk ($R_{\text{doc}}$):** Schema, calendar, chronology, and ICAO MRZ checksum integrity.
2. **Physical Tampering Risk ($R_{\text{tamp}}$):** ELA, noise inconsistency, edge gradient, moiré, font texture.
3. **Biometric Identity Risk ($R_{\text{bio}}$):** Facial match similarity, portrait quality, presentation attack detection.
4. **Cross-Modal Boost ($B_{\text{cross}}$):** Compound risk weighting for correlated multi-module anomalies.

---

## 3. How to Run Module 5

```powershell
cd module5_explainable_evidence
pytest tests/ -v -p no:cacheprovider
```
