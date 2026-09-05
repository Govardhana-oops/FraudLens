# Stage 7 Metric Audit: Document Classification Accuracy vs Field Extraction

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Audit Target:** Document Classification Accuracy (40.00%) vs `document_type` Field Score  
**Audit Date:** 2026-09-02  

---

## 1. Root Cause Analysis of the Metric Discrepancy

In `STAGE7_EXTERNAL_METRICS.json`, the multi-class document classification accuracy is reported as:

$$\text{Document Classification Accuracy} = \frac{12 \text{ Correct Images}}{30 \text{ Total Images}} = \mathbf{40.00\%}$$

### Image-Level Multi-Class Confusion Matrix:

| Ground Truth Category | `passport` | `permit` | `driver_license` | `national_id` | `visa` | `unknown_document` | Total Samples | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`passport`** | **6** | 0 | 0 | 0 | 0 | 0 | 6 | **100.0%** |
| **`permit`** | 0 | **6** | 0 | 0 | 0 | 0 | 6 | **100.0%** |
| **`driver_license`** | 1 | 0 | **0** | 0 | 0 | 5 | 6 | **0.0%** |
| **`national_id`** | 6 | 0 | 0 | **0** | 0 | 0 | 6 | **0.0%** |
| **`visa`** | 6 | 0 | 0 | 0 | **0** | 0 | 6 | **0.0%** |
| **Total** | 19 | 6 | 0 | 0 | 0 | 5 | 30 | **40.00%** |

---

## 2. Field-Level vs Image-Level Metric Alignment

In the underlying evaluation JSON (`STAGE7_EXTERNAL_METRICS.json`), the `document_type` field score is:
* **Ground Truth Count ($N_{GT}$):** 30
* **Predictions Count ($N_{Pred}$):** 25 (5 documents were classified as `unknown_document` and had no supported field)
* **True Positives ($TP$):** 12 (6 passports + 6 permits)
* **Precision:** $12 / 25 = \mathbf{48.00\%}$
* **Recall:** $12 / 30 = \mathbf{40.00\%}$
* **Field F1:** $2 \times (0.48 \times 0.40) / (0.48 + 0.40) = \mathbf{43.64\%}$
* **Exact Match Ratio:** $12 / 30 = \mathbf{40.00\%}$

---

## 3. Explaining Classification Confusion

1. **Visas $\rightarrow$ Passport (6/6 misclassified):** Visas contain the label `"PASSPORT NO: P87654321"` and a 2-line MRZ, causing the visual keyword and MRZ classifier to score higher on the `passport` category.
2. **National IDs $\rightarrow$ Passport (6/6 misclassified):** 3-line TD1 MRZ lines were parsed via general MRZ cues, falling back to the default passport parser.
3. **Driver's Licenses $\rightarrow$ Unknown (5/6):** Safely defaulted to `unknown_document` when unanchored, adhering to the zero-hallucination rule.

---

## 4. Audit Conclusion

* **True Document Classification Accuracy:** **`40.00%`** (12 / 30 images).
* **True `document_type` Field F1:** **`43.64%`** (Exact Match = 40.00%).
* **Audit Classification:** **VERIFIED** (Reconciled across image-level and field-level JSON structures).
