from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import cv2
from ..schemas.output_schema import PortraitQualityAssessment

class PortraitQualityEvaluator:
    """Evaluates facial image compliance against ICAO Doc 9303 / ISO/IEC 19794-5 standards."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_sharpness = config.get("thresholds", {}).get("min_sharpness_score", 20.0)
        self.min_illum = config.get("thresholds", {}).get("min_illumination_uniformity", 0.60)
        self.max_glare = config.get("thresholds", {}).get("max_glare_percentage", 5.0)

        self.has_cascade = hasattr(cv2, 'CascadeClassifier')
        self.face_cascade = None
        if self.has_cascade:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                self.face_cascade = None

    def detect_face(self, image: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[List[int]]]:
        """Detects the primary frontal face bounding box [ymin, xmin, ymax, xmax]."""
        if image is None or image.size == 0:
            return None, None

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY if image.shape[2] == 3 else cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        h, w = gray.shape

        # 1. Try Cascade Classifier if available
        if self.face_cascade is not None:
            try:
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50))
                if len(faces) > 0:
                    largest_face = max(faces, key=lambda b: b[2] * b[3])
                    x, y, w_f, h_f = largest_face
                    return gray[y:y+h_f, x:x+w_f], [int(y), int(x), int(y + h_f), int(x + w_f)]
            except Exception:
                pass

        # 2. Robust Skin-Tone / Morphology Facial Component Locator
        if len(image.shape) == 3 and image.shape[2] >= 3:
            hsv = cv2.cvtColor(image[:, :, :3], cv2.COLOR_RGB2HSV)
            # Standard human skin color range in HSV
            lower_skin = np.array([0, 20, 50], dtype=np.uint8)
            upper_skin = np.array([30, 255, 255], dtype=np.uint8)
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

            # Morphological closing
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            valid_faces = []
            for cnt in contours:
                x, y, w_c, h_c = cv2.boundingRect(cnt)
                area = w_c * h_c
                aspect = h_c / float(w_c) if w_c > 0 else 0
                if area >= (h * w * 0.05) and 0.8 <= aspect <= 2.2:
                    valid_faces.append((area, [y, x, y + h_c, x + w_c]))

            if valid_faces:
                best_bbox = max(valid_faces, key=lambda f: f[0])[1]
                y1, x1, y2, x2 = best_bbox
                return gray[y1:y2, x1:x2], best_bbox

        # 3. Direct portrait crop fallback (if image aspect ratio is portrait)
        if 0.5 <= (w / float(h)) <= 1.6 and min(h, w) >= 50:
            # Check if there is contrast / variance (not blank uniform white)
            if float(np.std(gray)) > 5.0:
                return gray, [0, 0, h, w]

        return None, None

    def evaluate(self, image: np.ndarray) -> Tuple[PortraitQualityAssessment, Optional[np.ndarray]]:
        """Evaluates image quality metrics and returns quality assessment along with the cropped face."""
        if image is None or image.size == 0:
            return PortraitQualityAssessment(
                is_compliant=False,
                overall_quality_score=0.0,
                sharpness=0.0,
                illumination_uniformity=0.0,
                contrast_score=0.0,
                glare_percentage=0.0,
                warnings=["Null or empty image buffer"]
            ), None

        face_crop, bbox = self.detect_face(image)
        if face_crop is None:
            return PortraitQualityAssessment(
                is_compliant=False,
                overall_quality_score=0.0,
                sharpness=0.0,
                illumination_uniformity=0.0,
                contrast_score=0.0,
                glare_percentage=0.0,
                warnings=["No frontal face detected"]
            ), None

        warnings = []

        # 1. Sharpness (Laplacian variance)
        lap_var = float(cv2.Laplacian(face_crop, cv2.CV_64F).var())
        if lap_var < self.min_sharpness:
            warnings.append(f"Low facial sharpness ({lap_var:.1f} < {self.min_sharpness})")

        # 2. Illumination Uniformity (Left vs Right half mean luminance delta)
        h, w = face_crop.shape
        mid_x = w // 2
        left_mean = float(np.mean(face_crop[:, :mid_x]))
        right_mean = float(np.mean(face_crop[:, mid_x:]))
        illum_ratio = min(left_mean, right_mean) / (max(left_mean, right_mean) + 1e-4)

        if illum_ratio < self.min_illum:
            warnings.append(f"Asymmetric facial lighting (uniformity ratio: {illum_ratio:.2f})")

        # 3. Contrast (Dynamic range)
        contrast = float(np.std(face_crop))
        if contrast < 25.0:
            warnings.append(f"Low image contrast (std: {contrast:.1f})")

        # 4. Glare / Specular reflection
        overexposed_pixels = np.sum(face_crop >= 250)
        glare_pct = float((overexposed_pixels / float(face_crop.size)) * 100.0)
        if glare_pct > self.max_glare:
            warnings.append(f"High specular glare ({glare_pct:.1f}% > {self.max_glare}%)")

        # Compute composite quality score [0.0, 1.0]
        sharp_score = float(np.clip(lap_var / 100.0, 0.0, 1.0))
        illum_score = float(np.clip(illum_ratio, 0.0, 1.0))
        contrast_score = float(np.clip(contrast / 60.0, 0.0, 1.0))
        glare_score = float(np.clip(1.0 - (glare_pct / 10.0), 0.0, 1.0))

        overall_quality = (sharp_score * 0.40) + (illum_score * 0.30) + (contrast_score * 0.15) + (glare_score * 0.15)
        overall_quality = float(np.clip(overall_quality, 0.0, 1.0))

        is_compliant = (lap_var >= self.min_sharpness) and (illum_ratio >= 0.50) and (glare_pct <= 10.0)

        return PortraitQualityAssessment(
            is_compliant=is_compliant,
            overall_quality_score=round(overall_quality, 3),
            sharpness=round(lap_var, 2),
            illumination_uniformity=round(illum_ratio, 3),
            contrast_score=round(contrast, 2),
            glare_percentage=round(glare_pct, 2),
            face_bbox=bbox,
            warnings=warnings
        ), face_crop
