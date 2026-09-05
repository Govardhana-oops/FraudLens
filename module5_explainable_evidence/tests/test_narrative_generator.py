"""Narrative Generator Tests for Module 5."""

import pytest
from src.explainer.narrative_generator import NarrativeGenerator

@pytest.fixture
def generator():
    return NarrativeGenerator({})

def test_clear_narrative_generation(generator):
    m1 = {"document_type": {"value": "passport", "confidence": 0.99}}
    m2 = {"overall_status": "VALID"}
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "anomaly_score": 0.05}
    m4 = {"status": "MATCH", "similarity_score": 0.95}

    action, summary, itemized, guidance = generator.generate(0.05, m1, m2, m3, m4, [])
    assert action == "CLEAR"
    assert "Standard clearance" in guidance
    assert len(itemized.negative_findings) == 0

def test_secondary_inspection_narrative(generator):
    m2 = {"overall_status": "INVALID", "errors": ["Invalid calendar date 2023-02-29"]}
    m3 = {"status": "POTENTIAL_TAMPERING", "anomaly_score": 0.85, "tampering_types_detected": ["copy_paste_edge_clipping"]}

    action, summary, itemized, guidance = generator.generate(0.78, None, m2, m3, None, ["Critical anomaly"])
    assert action == "SECONDARY_INSPECTION_RECOMMENDED"
    assert "Secondary Inspection Station" in guidance
    assert len(itemized.negative_findings) > 0
