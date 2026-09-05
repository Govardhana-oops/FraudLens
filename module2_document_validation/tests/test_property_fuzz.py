"""Property-based & Invariant Fuzz Testing for Module 2 Document Validation."""

import random
import pytest
from src.interface import document_validator

# Property Invariant 1: Score is strictly bounded in [0.0, 1.0] for any arbitrary payload
@pytest.mark.parametrize("iteration", range(20))
def test_score_bounded_in_range_under_random_inputs(iteration):
    doc_types = ["passport", "visa", "driver_license", "national_id", "permit", "unknown_document", "voter_card"]
    random_doc_type = random.choice(doc_types)
    random_conf = random.random()
    
    payload = {
        "status": random.choice(["SUCCESS", "PARTIAL", "UNKNOWN", "REVIEW_REQUIRED"]),
        "document_type": {"value": random_doc_type, "confidence": random_conf},
        "fields": {
            "passport_number": {"value": f"P{random.randint(100000, 9999999)}", "confidence": random.random()},
            "date_of_birth": {"value": f"{random.randint(1950, 2024):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"},
            "date_of_expiry": {"value": f"{random.randint(2020, 2035):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": random.choice([True, False])
    }
    
    res = document_validator.validate(payload)
    score = res["validation_score"]
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0, f"Score {score} violated bounds on iteration {iteration}"

# Property Invariant 2: Deterministic Invariance (F(x) == F(x))
def test_determinism_invariant():
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "nationality": {"value": "USA", "status": "VALID"},
            "date_of_birth": {"value": "1985-04-12", "status": "VALID"},
            "date_of_expiry": {"value": "2030-08-25", "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    
    res1 = document_validator.validate(payload)
    res2 = document_validator.validate(payload)
    assert res1["overall_status"] == res2["overall_status"]
    assert res1["validation_score"] == res2["validation_score"]
    assert len(res1["checks"]) == len(res2["checks"])

# Property Invariant 3: Impossible calendar date ALWAYS yields INVALID or UNKNOWN, NEVER VALID
@pytest.mark.parametrize("invalid_date_str", [
    "2023-02-29", "1900-02-29", "2020-04-31", "2020-00-15", "2020-13-15", "2020-05-00", "2020-05-32"
])
def test_impossible_calendar_date_never_valid(invalid_date_str):
    payload = {
        "status": "SUCCESS",
        "document_type": {"value": "passport", "confidence": 0.99},
        "fields": {
            "passport_number": {"value": "P12345678", "status": "VALID"},
            "full_name": {"value": "JOHN SMITH", "status": "VALID"},
            "date_of_birth": {"value": invalid_date_str, "status": "VALID"}
        },
        "mrz": None,
        "consistency": {"status": "CONSISTENT", "conflicts": []},
        "review_required": False
    }
    res = document_validator.validate(payload)
    assert res["overall_status"] != "VALID"
    assert res["overall_status"] == "INVALID"
