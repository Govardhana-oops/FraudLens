# AI-DIDSS Module 6: Online/Offline Database & Sync Subsystem

**Module:** `module6_database_sync` (Module 6: Online/Offline Database & Synchronization Subsystem)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Status:** **`FROZEN (17/17 TESTS PASSED - 100%)`**  

---

## 1. Overview & Operational Philosophy

Module 6 provides offline-first, resilient data storage and two-way differential synchronization for border control workstations.

### Core Capabilities

1. **Sub-Millisecond Offline SLTD Watchlist Lookup:** In-memory indexed SQLite search ($0.0103$ ms).
2. **Tamper-Evident Audit Journaling:** SHA-256 cryptographically chained inspection events.
3. **Two-Way Differential Sync:** Seamless delta exchange with central immigration servers upon network reconnect.

---

## 2. How to Run Module 6

```powershell
cd module6_database_sync
pytest tests/ -v -p no:cacheprovider
```
