"""Cross-Modal Anomaly Correlation Tests for Module 5."""

import pytest
from src.aggregators.anomaly_correlator import AnomalyCorrelator

@pytest.fixture
def correlator():
    return AnomalyCorrelator({
        "thresholds": {"compound_boost_photo_bio": 0.20, "compound_boost_text_mrz": 0.15}
    })

def test_photo_tampering_plus_bio_mismatch_boost(correlator):
    m3 = {"status": "POTENTIAL_TAMPERING", "tampering_types_detected": ["compression_splicing_inconsistency"]}
    m4 = {"status": "NO_MATCH", "similarity_score": 0.30}

    boost, correlations = correlator.correlate(None, None, m3, m4)
    assert boost >= 0.20
    assert len(correlations) > 0
    assert "Photo-Substitution Probability" in correlations[0]

def test_no_correlation_on_clean_inputs(correlator):
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "tampering_types_detected": []}
    m4 = {"status": "MATCH", "similarity_score": 0.90}

    boost, correlations = correlator.correlate(None, None, m3, m4)
    assert boost == 0.0
    assert len(correlations) == 0
