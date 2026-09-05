# AI-DIDSS Module 8: Documented Technical Limitations

**Module:** `module8_backend_api` (Module 8: Verification Decision Support Backend API)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Scope & Network Boundaries

1. **Payload Size Limits:**
   * High-resolution passport scans up to 25MB are accepted. Files exceeding 25MB are rejected with HTTP 413.
2. **Localhost & Edge Deployment:**
   * Designed for in-process or local area network (LAN) edge terminal operations at e-Gates and inspection counters.
