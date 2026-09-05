import os
from pathlib import Path
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, Optional, List
import yaml
from .storage.sqlite_store import SQLiteOfflineStore
from .sync.delta_sync_engine import DeltaSyncEngine
from .schemas.database_models import (
    WatchlistLookupResult,
    AuditJournalEntry,
    SyncReport
)

class DatabaseSyncService:
    """Public high-level singleton API for Module 6 local database & offline sync."""

    def __init__(self, config_path: Optional[str] = None, db_override_path: Optional[str] = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "configs" / "database_config.yaml")

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        if db_override_path:
            db_path = db_override_path
        else:
            filename = self.config.get("storage", {}).get("database_filename", "offline_border_store.sqlite3")
            db_path = str(Path(__file__).parent.parent / "data" / filename)

        genesis = self.config.get("security", {}).get("chain_genesis_hash", "0000000000000000000000000000000000000000000000000000000000000000")
        self.store = SQLiteOfflineStore(db_path, genesis_hash=genesis)
        self.sync_engine = DeltaSyncEngine(self.store, self.config)

    def lookup_watchlist(self, doc_number: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """Performs sub-millisecond offline watchlist search."""
        res = self.store.lookup_watchlist(doc_number, country_code)
        return res.model_dump()

    def log_inspection(
        self,
        recommended_action: str,
        risk_index: float,
        doc_number: Optional[str] = None,
        officer_id: Optional[str] = None,
        checkpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Appends a tamper-evident chained audit entry to the local SQLite journal."""
        log_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        off_id = officer_id or self.config.get("sync", {}).get("officer_default_id", "OFFICER-DEFAULT")
        cp_id = checkpoint_id or self.config.get("sync", {}).get("checkpoint_id", "CP-TERMINAL-01")

        entry = self.store.append_audit_entry(
            log_id=log_id,
            timestamp=now_iso,
            officer_id=off_id,
            checkpoint_id=cp_id,
            doc_number=doc_number,
            recommended_action=recommended_action,
            risk_index=risk_index
        )
        return entry.model_dump()

    def sync_with_server(self, incoming_delta: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Triggers differential two-way sync pass."""
        report = self.sync_engine.sync(incoming_watchlist_delta=incoming_delta)
        return report.model_dump()

# Global singleton
database_sync_service = DatabaseSyncService()
