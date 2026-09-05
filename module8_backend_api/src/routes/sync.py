from fastapi import APIRouter
from ..schemas.api_models import SyncRequest
from module6_database_sync.src.interface import database_sync_service

router = APIRouter(tags=["Synchronization"])

@router.post("/sync/differential")
async def trigger_differential_sync(payload: SyncRequest):
    """Executes two-way differential synchronization pass with central immigration cloud."""
    report = database_sync_service.sync_with_server(incoming_delta=payload.delta_records)
    return report
