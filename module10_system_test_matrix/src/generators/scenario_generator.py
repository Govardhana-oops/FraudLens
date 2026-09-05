"""Multi-Modal Scenario Test Generator for Module 10."""

from typing import Dict, Any, Tuple
import numpy as np
import cv2

class ScenarioGenerator:
    """Generates synthetic documents and live probe scenarios for complete matrix testing."""

    @staticmethod
    def create_synthetic_passport_image(doc_num: str = "P12345678", name: str = "DOE JOHN") -> np.ndarray:
        """Generates a structured synthetic document image canvas."""
        img = np.ones((400, 600, 3), dtype=np.uint8) * 240
        # Draw document borders
        cv2.rectangle(img, (20, 20), (580, 380), (70, 70, 90), 2)
        # Draw photo area
        cv2.rectangle(img, (40, 60), (200, 260), (180, 200, 220), -1)
        cv2.ellipse(img, (120, 150), (45, 60), 0, 0, 360, (210, 180, 160), -1)
        cv2.circle(img, (105, 135), 5, (50, 40, 30), -1)
        cv2.circle(img, (135, 135), 5, (50, 40, 30), -1)
        # Draw text lines
        cv2.putText(img, f"PASSPORT - {doc_num}", (230, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 30), 2)
        cv2.putText(img, f"NAME: {name}", (230, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 50), 1)
        cv2.putText(img, "NAT: USA  DOB: 15 MAY 1990", (230, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 50), 1)
        cv2.putText(img, "EXP: 14 MAY 2030  ISS: USA", (230, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 50), 1)
        # MRZ block
        cv2.rectangle(img, (30, 290), (570, 370), (250, 250, 250), -1)
        cv2.putText(img, f"P<USADOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", (40, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (10, 10, 10), 1)
        cv2.putText(img, f"{doc_num}4USA9005156M3005142<<<<<<<<<<<<<<<8", (40, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (10, 10, 10), 1)
        return img

    @staticmethod
    def create_live_probe_face(seed: int = 42) -> np.ndarray:
        """Generates a matching live camera face image."""
        img = np.ones((200, 200, 3), dtype=np.uint8) * 235
        cv2.ellipse(img, (100, 100), (45, 60), 0, 0, 360, (210, 180, 160), -1)
        cv2.circle(img, (85, 85), 5, (50, 40, 30), -1)
        cv2.circle(img, (115, 85), 5, (50, 40, 30), -1)
        cv2.line(img, (100, 95), (100, 115), (150, 120, 100), 2)
        cv2.ellipse(img, (100, 135), (20, 8), 0, 0, 180, (150, 80, 80), 2)
        return img
