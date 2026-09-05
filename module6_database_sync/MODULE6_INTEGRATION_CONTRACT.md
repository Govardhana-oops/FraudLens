# AI-DIDSS Module 6: Interface Contract & Integration Specification

**Module:** `module6_database_sync` (Module 6: Online/Offline Database & Synchronization Subsystem)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Public API Interface

```python
from src.interface import database_sync_service

# 1. High-speed offline watchlist lookup (< 0.1 ms)
alert = database_sync_service.lookup_watchlist(doc_number="P12345678", country="USA")

# 2. Append-only inspection audit logging
log_entry = database_sync_service.log_inspection(dossier_data)

# 3. Trigger manual or automatic differential sync
sync_report = database_sync_service.sync_with_server(server_endpoint="https://border.gov/sync")
```

---

## 2. Watchlist Query Response Schema

```json
{
  "is_flagged": true,
  "match_type": "EXACT_DOCUMENT_NUMBER",
  "record_id": "SLTD-USA-2025-9921",
  "category": "STOLEN_BLANK_PASSPORT",
  "issuing_authority": "US Department of State",
  "reported_date": "2025-11-14",
  "severity": "CRITICAL",
  "officer_instructions": "Document reported stolen. Refer bearer for immediate secondary inspection."
}
```
