# AI-DIDSS Module 2: Documented Technical Limitations

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Scope & Domain Boundaries

1. **Optical Consistency vs. Physical Authenticity:**
   * A valid MRZ checksum, correct format syntax, and valid calendar dates demonstrate mathematical and layout consistency of the extracted text.
   * **Module 2 does NOT evaluate physical substrate security, microprinting, holograms, or optical variable ink.** Physical tampering verification is performed by Module 3.
2. **Database Verification Absence:**
   * Module 2 operates as a standalone offline mathematical and syntactic validator. It does NOT query government backend immigration databases (handled by Module 6).
3. **Synthetic Rule Scope:**
   * Certain alphanumeric regex rules (e.g. `FORMAT_PASSPORT_NUMBER_SYNTAX`, `FORMAT_DRIVER_LICENSE_SYNTAX`) are calibrated to the project's multi-jurisdiction prototype schema and should be updated if deploying to specific national authorities with non-standard numbering schemes.
4. **Offline ISO Country Tables:**
   * Uses an embedded ISO 3166-1 alpha-3 country directory.
