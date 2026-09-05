"""Document Region of Interest (ROI) Extractor & Multi-Scale Segmenter.

Decomposes standard document layouts into specialized functional zones:
1. Header Zone: Document type, issuing authority
2. Visual Inspection Zone (VIZ): Form fields, biographical data
3. Machine Readable Zone (MRZ): Bottom 25% zone, upscaled for high-DPI OCR
4. Barcode Zone: 2D PDF417 / QR region
5. Photo Zone: Traveler facial portrait
"""

import cv2
import numpy as np

class DocumentROIExtractor:
    def __init__(self, target_dpi_scale: float = 1.5):
        self.target_dpi_scale = target_dpi_scale

    def extract_zones(self, document_bgr: np.ndarray, doc_type_hint: str = "passport") -> dict:
        """Extracts localized ROIs and applies high-DPI scaling on dense text zones."""
        h, w = document_bgr.shape[:2]
        
        # 1. Header Zone (Top 15%)
        header_h = int(h * 0.15)
        header_roi = document_bgr[0:header_h, 0:w]
        
        # 2. MRZ Zone (Bottom 26% for TD3 / TD1 / MRV)
        mrz_start_y = int(h * 0.74)
        mrz_roi = document_bgr[mrz_start_y:h, 0:w]
        # 1.5x upscaling for crisp character boundary isolation
        mrz_high_dpi = cv2.resize(mrz_roi, (0, 0), fx=self.target_dpi_scale, fy=self.target_dpi_scale, interpolation=cv2.INTER_CUBIC)
        
        # 3. VIZ Central Zone
        viz_roi = document_bgr[header_h:mrz_start_y, 0:w]
        
        # 4. Portrait / Photo Zone (Left 30%, central vertical)
        photo_x2 = int(w * 0.32)
        photo_y1 = int(h * 0.12)
        photo_y2 = int(h * 0.65)
        photo_roi = document_bgr[photo_y1:photo_y2, 0:photo_x2]
        
        # 5. Right-side VIZ Text Zone
        viz_text_roi = document_bgr[header_h:mrz_start_y, photo_x2:w]

        return {
            "full_document": document_bgr,
            "header_roi": header_roi,
            "mrz_roi": mrz_roi,
            "mrz_high_dpi": mrz_high_dpi,
            "viz_roi": viz_roi,
            "viz_text_roi": viz_text_roi,
            "photo_roi": photo_roi,
            "dimensions": {"width": w, "height": h}
        }
