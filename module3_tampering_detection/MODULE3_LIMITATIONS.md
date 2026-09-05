# AI-DIDSS Module 3: Documented Technical Limitations

**Module:** `module3_tampering_detection` (Module 3: Document Forensic & Tampering Detection Engine)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Forensic Boundaries & Scope Limitations

1. **Digital vs Physical Substrate Forensics:**
   * Module 3 operates strictly on 2D digital image representations. It analyzes compression artifacts, gradient steps, noise variance, and spectral patterns.
   * **Module 3 cannot verify physical physical-security features (e.g., tactile laser engraving, UV fluorescent fibers, holograms, micro-perforations) that require dedicated specialized hardware optical readers.**
2. **Analog Print-Scan Recapture:**
   * If an attacker creates a forged physical document, prints it, and re-scans it on a uniform flatbed scanner, the analog recapture step naturally blurs digital ELA discrepancies. Module 3 counters this via spectral moiré analysis and font texture inconsistencies, but manual officer review remains mandatory (`REVIEW_REQUIRED`).
3. **Severe Resolution Limits:**
   * Document crops below $150 \times 150$ pixels do not contain sufficient spatial pixel density for high-frequency noise variance estimation and safely route to `UNKNOWN`.
