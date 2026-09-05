# AI-DIDSS Module 5: Documented Technical Limitations

**Module:** `module5_explainable_evidence` (Module 5: Explainable Evidence & Anomaly Assessment Engine)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Scope & Decision Support Boundaries

1. **Advisory Decision Support:**
   * Module 5 recommendations (`CLEAR`, `STANDARD_INSPECTION`, `SECONDARY_INSPECTION_RECOMMENDED`, `TECHNICAL_REVIEW_REQUIRED`, `RECAPTURE_REQUIRED`) are strictly advisory and provide transparent evidence checklists.
   * **Border control officers retain full legal authority for passenger admission.**
2. **Missing Module Graceful Degradation:**
   * If any upstream module (e.g., Live camera feed for Module 4) is unavailable, Module 5 flags the missing dimension as an uncertainty and adjusts baseline risk without crashing.
