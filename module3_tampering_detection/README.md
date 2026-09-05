# AI-DIDSS Module 3: Document Tampering & Physical Anomaly Detection Engine

**Module:** `module3_tampering_detection` (Module 3: Document Forensic & Tampering Detection Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Status:** **`FROZEN (32/32 TESTS PASSED - 100%)`**  

---

## 1. Overview & Operational Philosophy

Module 3 is a multi-modal digital image forensics engine. It evaluates input document images and crops to detect statistical, spectral, and compression inconsistencies indicating photo substitution, altered digits, copy-paste border splicing, or screen replay captures.

### Strict Non-Fraud Invariant
> [!IMPORTANT]
> **Module 3 is a forensic evidence extraction engine, NOT a judicial tribunal.**  
> A high anomaly score triggers a `REVIEW_REQUIRED` or `POTENTIAL_TAMPERING` decision-support flag with localized heatmaps for human forensic officers. Module 3 **NEVER outputs `FRAUD`, `CRIMINAL`, `DETAIN`, `REJECT`, or `FORGERY`**.

---

## 2. Forensic Indicators

1. **Error Level Analysis (ELA):** JPEG compression error variance across different compression grids.
2. **Noise Inconsistency Analysis:** High-frequency spatial noise residual variance across document patches.
3. **Edge & Gradient Discontinuity:** Artificial rectangular line gradients and copy-move border clipping.
4. **Font & Character Texture:** Character stroke sharpness and blur discrepancies.
5. **2D FFT Frequency & Spectral:** Periodic moiré patterns and screen replay refresh lattices.

---

## 3. How to Run Module 3

```powershell
cd module3_tampering_detection
pytest tests/ -v -p no:cacheprovider
```
