"""Watchlist Search Route for Module 8."""

from typing import Optional
from fastapi import APIRouter, Query
from module6_database_sync.src.interface import database_sync_service

router = APIRouter(tags=["Watchlist & Revocations"])

@router.get("/watchlist/check/{doc_number}")
async def check_watchlist(doc_number: str, country_code: Optional[str] = Query(None)):
    """Sub-millisecond offline SLTD and revocation watchlist query."""
    res = database_sync_service.lookup_watchlist(doc_number, country_code)
    return res
