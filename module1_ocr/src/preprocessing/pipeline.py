"""Unified Modular Preprocessing Pipeline for Document Images.

Provides configurable execution modes:
- 'raw': Pass-through original image
- 'standard': Quality check + Boundary Crop + Deskew + CLAHE Illumination
- 'contrast_enhanced': Standard + Dynamic Gamma Correction
- 'binarized': Standard + Adaptive Gaussian / Otsu Thresholding
"""

import cv2
import numpy as np
from PIL import Image

from .quality_check import ImageQualityChecker
from .deskew import DocumentDeskewer
from .crop import DocumentCropper
from .illumination import IlluminationNormalizer

class PreprocessingPipeline:
    def __init__(self, mode: str = "standard", config: dict | None = None):
        self.mode = mode
        self.config = config or {}
        
        self.quality_checker = ImageQualityChecker(
            blur_threshold=self.config.get("blur_threshold", 100.0),
            glare_threshold_ratio=self.config.get("glare_threshold_ratio", 0.05)
        )
        self.deskewer = DocumentDeskewer(
            max_skew_angle=self.config.get("max_skew_angle", 45.0)
        )
        self.cropper = DocumentCropper(
            min_area_ratio=self.config.get("min_area_ratio", 0.20)
        )
        self.illum_normalizer = IlluminationNormalizer(
            clip_limit=self.config.get("clahe_clip_limit", 2.0)
        )

    def process_image(self, image_input: str | np.ndarray | Image.Image) -> dict:
        """Processes a document image according to the configured mode.
        
        Returns:
            dict containing:
                - 'processed_image': np.ndarray (BGR)
                - 'quality_assessment': dict
                - 'transformations_applied': list[str]
                - 'deskew_angle': float
                - 'crop_applied': bool
        """
        # Load / convert to BGR numpy array
        if isinstance(image_input, str):
            image_np = cv2.imread(image_input)
            if image_np is None:
                raise ValueError(f"Could not load image from path: {image_input}")
        elif isinstance(image_input, Image.Image):
            image_np = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        elif isinstance(image_input, np.ndarray):
            image_np = image_input.copy()
        else:
            raise TypeError("Unsupported image input type.")

        # Step 1: Quality check
        quality_report = self.quality_checker.assess(image_np)
        transformations = []
        
        if self.mode == "raw":
            return {
                "processed_image": image_np,
                "quality_assessment": quality_report,
                "transformations_applied": ["none_raw_mode"],
                "deskew_angle": 0.0,
                "crop_applied": False
            }

        # Step 2: Perspective Crop
        warped_img, crop_applied = self.cropper.perspective_crop(image_np)
        if crop_applied:
            transformations.append("perspective_crop")

        # Step 3: Deskew & Rotation Correction
        deskewed_img, angle = self.deskewer.deskew(warped_img)
        if abs(angle) >= 0.5:
            transformations.append(f"deskew_rotate_{angle:.1f}deg")

        # Step 4: Illumination Normalization
        enhanced_img = self.illum_normalizer.normalize(deskewed_img, auto_gamma=(self.mode == "contrast_enhanced"))
        transformations.append("clahe_illumination_norm")

        # Step 5: Binarization / Sharpening if requested
        if self.mode == "binarized":
            gray = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
            # Denoise before threshold
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            binarized = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
            )
            enhanced_img = cv2.cvtColor(binarized, cv2.COLOR_GRAY2BGR)
            transformations.append("adaptive_gaussian_threshold")
        elif self.mode in ["standard", "contrast_enhanced"]:
            # Subtle unsharp masking for crisp text edges
            gaussian = cv2.GaussianBlur(enhanced_img, (0, 0), 2.0)
            enhanced_img = cv2.addWeighted(enhanced_img, 1.25, gaussian, -0.25, 0)
            transformations.append("unsharp_mask_sharpening")

        return {
            "processed_image": enhanced_img,
            "quality_assessment": quality_report,
            "transformations_applied": transformations,
            "deskew_angle": angle,
            "crop_applied": crop_applied
        }
