"""Test Matrix Execution Runner for Module 10."""

from typing import Dict, Any, List
from module7_integration_engine.src.interface import screening_orchestrator
from src.generators.scenario_generator import ScenarioGenerator

class SystemTestMatrixRunner:
    """Runs high-level system test batches across multiple scenario permutations."""

    @staticmethod
    def run_scenario(scenario_id: str, doc_num: str = "P12345678", custom_m1: Dict[str, Any] = None) -> Dict[str, Any]:
        doc_img = ScenarioGenerator.create_synthetic_passport_image(doc_num=doc_num)
        live_img = ScenarioGenerator.create_live_probe_face()

        res = screening_orchestrator.process_screening(
            document_image=doc_img,
            live_face_image=live_img,
            extracted_fields_override=custom_m1
        )
        return res
