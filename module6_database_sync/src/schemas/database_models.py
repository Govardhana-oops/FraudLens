"""Database Data Models & Sync Schemas for Module 6."""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class WatchlistMatchSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    INFORMATIONAL = "INFORMATIONAL"

class WatchlistRecord(BaseModel):
    doc_number: str
    country_code: str
    category: str # 'STOLEN_PASSPORT', 'REVOKED_VISA', 'INTERPOL_ALERT', 'LOST_BLANK'
    record_id: str
    reported_date: str
    severity: WatchlistMatchSeverity = WatchlistMatchSeverity.CRITICAL
    officer_instructions: str
    version_seq: int = 1

class WatchlistLookupResult(BaseModel):
    is_flagged: bool
    record: Optional[WatchlistRecord] = None
    query_doc_number: str
    query_country: Optional[str] = None
    lookup_latency_ms: float

class AuditJournalEntry(BaseModel):
    log_id: str
    timestamp: str
    officer_id: str
    checkpoint_id: str
    doc_number: Optional[str] = None
    recommended_action: str
    risk_index: float
    prev_hash: str
    entry_hash: str
    synced_to_cloud: bool = False

class SyncReport(BaseModel):
    sync_status: str # 'SUCCESS', 'OFFLINE_QUEUED', 'PARTIAL', 'ERROR'
    records_pulled: int = 0
    records_pushed: int = 0
    local_sequence: int = 0
    remote_sequence: int = 0
    timestamp: str
    details: Dict[str, Any] = Field(default_factory=dict)
