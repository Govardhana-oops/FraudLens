# AI-DIDSS Module 6: Two-Way Differential Synchronization Protocol

**Module:** `module6_database_sync` (Module 6: Online/Offline Database & Synchronization Subsystem)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Synchronization Flow

```
   [ Local Edge Node ]                                [ Central Authority ]
            │                                                    │
            │ ── 1. Handshake (Edge ID, Last Synced Seq No) ───► │
            │                                                    │
            │ ◄─ 2. Delta Payload (New Revocations / Alerts) ─── │
            │                                                    │
            │ (Apply Delta in Atomic SQLite Transaction)         │
            │                                                    │
            │ ── 3. Push Local Offline Audit Logs Chained ─────► │
            │                                                    │
            │ ◄─ 4. Sync Acknowledgment (New Sequence No) ────── │
```

---

## 2. Conflict Resolution Invariants

1. **Watchlist & Revocations:** Central server is the authoritative single source of truth. Edge caches overwrite local watchlist records based on timestamp version.
2. **Audit Logs:** Edge inspection logs are immutable and append-only. They are queued locally during offline periods and pushed sequentially upon reconnect.
3. **Idempotency:** Re-transmitting an already acknowledged sync packet produces no side effects.
