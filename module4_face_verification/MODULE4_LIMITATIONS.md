# AI-DIDSS Module 4: Documented Technical Limitations

**Module:** `module4_face_verification` (Module 4: Biometric Face Verification & Match Quality Engine)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Scope & Biometric Boundaries

1. **Aging & Temporal Drift:**
   * Passports issued 10 years prior may exhibit significant facial aging, weight change, or hairstyle differences relative to a live adult probe capture.
   * Moderate similarity drops ($0.50 \le \text{Score} < 0.72$) safely route to **`REVIEW_REQUIRED`** to allow manual officer inspection rather than false rejection.
2. **Cosmetic Surgery & Severe Occlusion:**
   * Full facial veils, large medical bandages, or heavy sunglasses occluding eyes/nose/mouth will fail minimum facial feature visibility thresholds and route to **`POOR_QUALITY`**.
3. **Multi-Person Probes:**
   * The live capture interface expects a single primary subject in frame. If multiple individuals appear, the largest detected face is selected.
