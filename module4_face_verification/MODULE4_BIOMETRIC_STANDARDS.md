# AI-DIDSS Module 4: ICAO Doc 9303 & ISO/IEC 19794-5 Biometric Standards

**Module:** `module4_face_verification` (Module 4: Biometric Face Verification & Match Quality Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Compliance Matrix

| Standard Metric | ISO/IEC 19794-5 Recommendation | Module 4 Verification Rule | Action on Failure |
| :--- | :--- | :--- | :--- |
| **Minimum Face Size** | $\ge 90 \times 90$ pixels | Inter-eye distance $\ge 30$ px, crop $\ge 100 \times 100$ px | Routes to `POOR_QUALITY` |
| **Image Sharpness** | Focused, no motion blur | Laplacian variance $\ge 25.0$ | Routes to `POOR_QUALITY` |
| **Illumination Uniformity** | Symmetrical lighting without deep shadows | Left-right facial luminance delta $\le 35\%$ | Emits warning / `REVIEW_REQUIRED` |
| **Head Pose Orientation** | Frontal within $\pm 15^\circ$ yaw/pitch | Symmetry ratio $\in [0.75, 1.30]$ | Emits warning / `REVIEW_REQUIRED` |
| **Eye Occlusion / Gaze** | Eyes open and visible | Eye region aspect ratio $\ge 0.15$ | Routes to `POOR_QUALITY` |
| **Overexposure / Glare** | No specular saturation | Pixels with value $= 255$ must be $< 3\%$ | Emits warning |
