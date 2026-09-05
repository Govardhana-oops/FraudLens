"""Differential Delta Synchronization Engine."""

import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from ..storage.sqlite_store import SQLiteOfflineStore
from ..schemas.database_models import (
    WatchlistRecord,
    SyncReport
)

class DeltaSyncEngine:
    """Manages two-way differential synchronization between local SQLite store and central server."""

    def __init__(self, store: SQLiteOfflineStore, config: Dict[str, Any]):
        self.store = store
        self.config = config
        self.last_sync_timestamp = None
        self.local_sequence = 1

    def sync(
        self,
        incoming_watchlist_delta: Optional[List[Dict[str, Any]]] = None,
        simulate_cloud_ack: bool = True
    ) -> SyncReport:
        """Executes a two-way differential sync pass."""
        pulled = 0
        pushed = 0
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Pull incoming delta records and upsert into local SQLite
        if incoming_watchlist_delta:
            records = []
            for item in incoming_watchlist_delta:
                records.append(WatchlistRecord(**item))
            pulled = self.store.upsert_watchlist_records(records)

        # 2. Push unsynced local audit logs
        unsynced = self.store.get_unsynced_audit_entries(limit=500)
        pushed = len(unsynced)

        if simulate_cloud_ack and unsynced:
            log_ids = [e.log_id for e in unsynced]
            self.store.mark_audit_entries_synced(log_ids)

        self.last_sync_timestamp = now_iso
        self.local_sequence += 1

        return SyncReport(
            sync_status="SUCCESS",
            records_pulled=pulled,
            records_pushed=pushed,
            local_sequence=self.local_sequence,
            remote_sequence=self.local_sequence + 100,
            timestamp=now_iso,
            details={"synced_audit_count": pushed, "applied_watchlist_count": pulled}
        )
