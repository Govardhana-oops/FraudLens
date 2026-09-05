"""Risk Calculation & Dimension Tests for Module 5."""

import pytest
from src.aggregators.risk_index_calculator import RiskIndexCalculator

@pytest.fixture
def risk_calc():
    return RiskIndexCalculator({
        "weights": {"document_syntactic": 0.35, "physical_tampering": 0.35, "biometric_identity": 0.30}
    })

def test_risk_calc_all_clear(risk_calc):
    m2 = {"overall_status": "VALID", "validation_score": 1.0}
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "anomaly_score": 0.05}
    m4 = {"status": "MATCH", "similarity_score": 0.95}

    dim, risk = risk_calc.calculate_risks(m2, m3, m4)
    assert risk < 0.15
    assert dim.document_syntactic_risk == 0.0
    assert dim.physical_tampering_risk == 0.05

def test_risk_calc_critical_document_invalid(risk_calc):
    m2 = {"overall_status": "INVALID", "validation_score": 0.0}
    m3 = {"status": "NO_TAMPERING_EVIDENCE", "anomaly_score": 0.05}
    m4 = {"status": "MATCH", "similarity_score": 0.95}

    dim, risk = risk_calc.calculate_risks(m2, m3, m4)
    assert dim.document_syntactic_risk == 1.0
    assert risk > 0.30
