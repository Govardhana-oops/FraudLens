"""Local Embedded SQLite Data Store for Offline Border Screening."""

import sqlite3
import time
import os
from typing import Dict, Any, Optional, List, Tuple
from ..schemas.database_models import (
    WatchlistRecord,
    WatchlistLookupResult,
    AuditJournalEntry,
    WatchlistMatchSeverity
)
from ..security.hash_integrity import TamperEvidentHasher

class SQLiteOfflineStore:
    """Thread-safe ACID local SQLite store for watchlists, revocations, and audit trails."""

    def __init__(self, db_path: str, genesis_hash: str = "0000000000000000000000000000000000000000000000000000000000000000"):
        self.db_path = db_path
        self.genesis_hash = genesis_hash
        self.in_memory_watchlist: Dict[str, WatchlistRecord] = {}

        self._init_db()
        self._load_memory_index()

    def _get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            return conn
        except sqlite3.DatabaseError as e:
            if "malformed" in str(e).lower() or "disk image" in str(e).lower():
                # Recover from corrupt database file by removing corrupt file
                try:
                    conn.close()
                except Exception:
                    pass
                for ext in ["", "-wal", "-shm"]:
                    fpath = f"{self.db_path}{ext}"
                    if os.path.exists(fpath):
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass
                conn = sqlite3.connect(self.db_path, timeout=5.0)
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                return conn
            raise

    def _init_db(self):
        """Initializes database schema and indexes."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self._get_connection() as conn:
            # 1. Watchlist / Stolen Travel Documents Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS watchlist_records (
                    doc_number TEXT NOT NULL,
                    country_code TEXT NOT NULL,
                    category TEXT NOT NULL,
                    record_id TEXT PRIMARY KEY,
                    reported_date TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    officer_instructions TEXT NOT NULL,
                    version_seq INTEGER NOT NULL DEFAULT 1
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_doc ON watchlist_records (doc_number, country_code);")

            # 2. Tamper-Evident Chained Audit Journal Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_journal (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    officer_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    doc_number TEXT,
                    recommended_action TEXT NOT NULL,
                    risk_index REAL NOT NULL,
                    prev_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL,
                    synced_to_cloud INTEGER NOT NULL DEFAULT 0
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_synced ON audit_journal (synced_to_cloud);")

    def _load_memory_index(self):
        """Pre-loads watchlist records into in-memory dictionary for sub-millisecond lookups."""
        self.in_memory_watchlist.clear()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT doc_number, country_code, category, record_id, reported_date, severity, officer_instructions, version_seq FROM watchlist_records;")
            for row in cursor.fetchall():
                rec = WatchlistRecord(
                    doc_number=row[0],
                    country_code=row[1],
                    category=row[2],
                    record_id=row[3],
                    reported_date=row[4],
                    severity=WatchlistMatchSeverity(row[5]),
                    officer_instructions=row[6],
                    version_seq=row[7]
                )
                # Key by normalized document number and doc+country
                clean_num = row[0].replace(" ", "").upper()
                self.in_memory_watchlist[clean_num] = rec
                self.in_memory_watchlist[f"{clean_num}::{row[1].upper()}"] = rec

    def upsert_watchlist_records(self, records: List[WatchlistRecord]) -> int:
        """Upserts a batch of watchlist records from synchronization."""
        with self._get_connection() as conn:
            for r in records:
                conn.execute("""
                    INSERT INTO watchlist_records (doc_number, country_code, category, record_id, reported_date, severity, officer_instructions, version_seq)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(record_id) DO UPDATE SET
                        doc_number=excluded.doc_number,
                        country_code=excluded.country_code,
                        category=excluded.category,
                        reported_date=excluded.reported_date,
                        severity=excluded.severity,
                        officer_instructions=excluded.officer_instructions,
                        version_seq=excluded.version_seq;
                """, (r.doc_number, r.country_code, r.category, r.record_id, r.reported_date, r.severity.value, r.officer_instructions, r.version_seq))
        self._load_memory_index()
        return len(records)

    def lookup_watchlist(self, doc_number: str, country_code: Optional[str] = None) -> WatchlistLookupResult:
        """Sub-millisecond offline in-memory watchlist lookup."""
        t0 = time.perf_counter()
        if not doc_number:
            return WatchlistLookupResult(
                is_flagged=False,
                query_doc_number="",
                query_country=country_code,
                lookup_latency_ms=0.01
            )

        clean_num = doc_number.replace(" ", "").upper()
        rec = None

        if country_code:
            rec = self.in_memory_watchlist.get(f"{clean_num}::{country_code.upper()}")

        if rec is None:
            rec = self.in_memory_watchlist.get(clean_num)

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        return WatchlistLookupResult(
            is_flagged=(rec is not None),
            record=rec,
            query_doc_number=clean_num,
            query_country=country_code,
            lookup_latency_ms=round(latency_ms, 3)
        )

    def append_audit_entry(
        self,
        log_id: str,
        timestamp: str,
        officer_id: str,
        checkpoint_id: str,
        doc_number: Optional[str],
        recommended_action: str,
        risk_index: float
    ) -> AuditJournalEntry:
        """Atomically computes chained SHA-256 hash and appends entry to local journal."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT entry_hash FROM audit_journal ORDER BY rowid DESC LIMIT 1;")
            row = cursor.fetchone()
            prev_hash = row[0] if row else self.genesis_hash

            payload_data = {
                "log_id": log_id,
                "timestamp": timestamp,
                "officer_id": officer_id,
                "checkpoint_id": checkpoint_id,
                "doc_number": doc_number,
                "recommended_action": recommended_action,
                "risk_index": risk_index
            }
            entry_hash = TamperEvidentHasher.compute_entry_hash(prev_hash, payload_data)

            conn.execute("""
                INSERT INTO audit_journal (log_id, timestamp, officer_id, checkpoint_id, doc_number, recommended_action, risk_index, prev_hash, entry_hash, synced_to_cloud)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0);
            """, (log_id, timestamp, officer_id, checkpoint_id, doc_number, recommended_action, risk_index, prev_hash, entry_hash))

            return AuditJournalEntry(
                log_id=log_id,
                timestamp=timestamp,
                officer_id=officer_id,
                checkpoint_id=checkpoint_id,
                doc_number=doc_number,
                recommended_action=recommended_action,
                risk_index=risk_index,
                prev_hash=prev_hash,
                entry_hash=entry_hash,
                synced_to_cloud=False
            )

    def get_unsynced_audit_entries(self, limit: int = 500) -> List[AuditJournalEntry]:
        """Retrieves un-pushed local audit logs for cloud sync."""
        entries = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT log_id, timestamp, officer_id, checkpoint_id, doc_number, recommended_action, risk_index, prev_hash, entry_hash, synced_to_cloud
                FROM audit_journal WHERE synced_to_cloud = 0 ORDER BY rowid ASC LIMIT ?;
            """, (limit,))
            for row in cursor.fetchall():
                entries.append(AuditJournalEntry(
                    log_id=row[0],
                    timestamp=row[1],
                    officer_id=row[2],
                    checkpoint_id=row[3],
                    doc_number=row[4],
                    recommended_action=row[5],
                    risk_index=row[6],
                    prev_hash=row[7],
                    entry_hash=row[8],
                    synced_to_cloud=bool(row[9])
                ))
        return entries

    def mark_audit_entries_synced(self, log_ids: List[str]):
        """Marks audit entries as acknowledged by central cloud server."""
        if not log_ids:
            return
        with self._get_connection() as conn:
            conn.executemany("UPDATE audit_journal SET synced_to_cloud = 1 WHERE log_id = ?;", [(lid,) for lid in log_ids])
