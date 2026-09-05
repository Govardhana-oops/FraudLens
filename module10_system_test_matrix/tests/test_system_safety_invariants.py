"""System-Wide Safety Invariants & Non-Exclusion Test for Module 10."""

import pytest
import numpy as np
from module7_integration_engine.src.interface import screening_orchestrator
from module10_system_test_matrix.src.generators.scenario_generator import ScenarioGenerator

FORBIDDEN_TAGS = ["FRAUD", "CRIMINAL", "DETAIN", "REJECT", "FORGERY", "IMPOSTER", "ARREST", "ILLEGAL"]

def test_system_wide_zero_criminal_label_safety_invariant():
    # Test multiple adversarial scenarios
    for seed in range(10):
        # Degraded/adversarial document
        doc_img = ScenarioGenerator.create_synthetic_passport_image(f"ADV{seed:03d}")
        # Add destructive noise
        doc_img[50:150, 50:150] = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        res = screening_orchestrator.process_screening(doc_img)

        # 1. Check recommended action
        assert res["recommended_action"] not in FORBIDDEN_TAGS, f"Forbidden action emitted: {res['recommended_action']}"

        # 2. Check executive summary and guidance for autonomous criminal decisions
        summary = res["executive_summary"].upper()
        guidance = res["actionable_guidance"].upper()

        for tag in ["YOU ARE A CRIMINAL", "ARREST THIS PERSON", "DEFINITIVE FORGER"]:
            assert tag not in summary
            assert tag not in guidance
