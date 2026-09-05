# AI-DIDSS Module 5: Evidence Aggregation & Risk Index Mathematical Model

**Module:** `module5_explainable_evidence` (Module 5: Explainable Evidence & Anomaly Assessment Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Dimensional Risk Score Formulations

1. **Document Syntactic Risk ($R_{\text{doc}} \in [0.0, 1.0]$):**
   $$R_{\text{doc}} = 1.0 - \text{validation\_score}_{\text{M2}}$$
   * Critical check failure (e.g. invalid calendar date, MRZ checksum error) sets $R_{\text{doc}} = 1.0$.

2. **Physical Tampering Risk ($R_{\text{tamp}} \in [0.0, 1.0]$):**
   $$R_{\text{tamp}} = \text{anomaly\_score}_{\text{M3}}$$

3. **Biometric Identity Risk ($R_{\text{bio}} \in [0.0, 1.0]$):**
   $$R_{\text{bio}} = 1.0 - \text{similarity\_score}_{\text{M4}}$$
   * Presentation attack or spoof detection sets $R_{\text{bio}} = 1.0$.

4. **Compound Cross-Modal Boost ($B_{\text{cross}} \in [0.0, 0.25]$):**
   * If both $R_{\text{tamp}} \ge 0.60$ and $R_{\text{bio}} \ge 0.50$ (correlated photo tampering + face mismatch):
     $$B_{\text{cross}} = 0.20$$
   * If both $R_{\text{doc}} \ge 0.60$ and $R_{\text{tamp}} \ge 0.60$ (altered text + checksum failure):
     $$B_{\text{cross}} = 0.15$$

5. **Overall Calibrated Risk Index ($R_{\text{total}} \in [0.0, 1.0]$):**
   $$R_{\text{total}} = \min\left(1.0, w_{\text{doc}} R_{\text{doc}} + w_{\text{tamp}} R_{\text{tamp}} + w_{\text{bio}} R_{\text{bio}} + B_{\text{cross}}\right)$$
   *(Default weights: $w_{\text{doc}} = 0.35, w_{\text{tamp}} = 0.35, w_{\text{bio}} = 0.30$)*
