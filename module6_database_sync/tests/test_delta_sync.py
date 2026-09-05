"""Two-Way Differential Delta Sync Tests."""

import pytest

def test_differential_sync_push_and_pull(test_sync_service):
    # 1. Log two offline inspections
    test_sync_service.log_inspection("CLEAR", 0.05, "DOC_OFFLINE_1")
    test_sync_service.log_inspection("CLEAR", 0.08, "DOC_OFFLINE_2")

    # 2. Sync with incoming delta
    delta_payload = [
        {
            "doc_number": "REVOKED999",
            "country_code": "CAN",
            "category": "REVOKED_VISA",
            "record_id": "REV-CAN-999",
            "reported_date": "2026-02-01",
            "severity": "CRITICAL",
            "officer_instructions": "Visa cancelled by issuing consulate."
        }
    ]

    report = test_sync_service.sync_with_server(incoming_delta=delta_payload)
    assert report["sync_status"] == "SUCCESS"
    assert report["records_pulled"] == 1
    assert report["records_pushed"] == 2

    # Verify that the pulled record is now immediately searchable offline
    lookup = test_sync_service.lookup_watchlist("REVOKED999")
    assert lookup["is_flagged"] is True
    assert lookup["record"]["category"] == "REVOKED_VISA"
