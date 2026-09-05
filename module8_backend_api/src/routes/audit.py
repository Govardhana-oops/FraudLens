from fastapi import APIRouter, Query
from ..schemas.api_models import AuditVerificationResponse
from module6_database_sync.src.interface import database_sync_service
from module6_database_sync.src.security.hash_integrity import TamperEvidentHasher

router = APIRouter(tags=["Audit Logs"])

@router.get("/audit/logs", response_model=AuditVerificationResponse)
async def get_audit_logs(limit: int = Query(100, ge=1, le=1000), verify_integrity: bool = Query(True)):
    """Retrieves audit journal records and verifies SHA-256 cryptographic chain integrity."""
    entries = database_sync_service.store.get_unsynced_audit_entries(limit=limit)

    chain_valid = True
    if verify_integrity and entries:
        for i, entry in enumerate(entries):
            payload_data = {
                "log_id": entry.log_id,
                "timestamp": entry.timestamp,
                "officer_id": entry.officer_id,
                "checkpoint_id": entry.checkpoint_id,
                "doc_number": entry.doc_number,
                "recommended_action": entry.recommended_action,
                "risk_index": entry.risk_index
            }
            # 1. Verify that this entry's hash matches its own payload + prev_hash
            if not TamperEvidentHasher.verify_chain_link(entry.prev_hash, payload_data, entry.entry_hash):
                chain_valid = False
                break
            # 2. Verify contiguous continuity with the preceding entry in the slice
            if i > 0 and entry.prev_hash != entries[i-1].entry_hash:
                chain_valid = False
                break

    return AuditVerificationResponse(
        total_logs=len(entries),
        chain_intact=chain_valid,
        logs=[e.model_dump() for e in entries]
    )
