# AI-DIDSS Module 6: Documented Technical Limitations

**Module:** `module6_database_sync` (Module 6: Online/Offline Database & Synchronization Subsystem)  
**Version:** `v1.0.0-FROZEN`  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Scope & Operational Limitations

1. **Watchlist Currency During Prolonged Offline Windows:**
   * If a border workstation remains disconnected from the central immigration network for days, it relies on the last synchronized SLTD database snapshot.
   * New revocations issued during the offline period will be detected immediately upon delta sync.
2. **Local Disk Space:**
   * The local SQLite store utilizes WAL mode and automatic compaction. Audit entries are marked as synced and can be archived based on local retention policies.
