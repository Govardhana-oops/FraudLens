# AI-DIDSS Module 3: Forensic Threat Model & Tampering Taxonomy

**Module:** `module3_tampering_detection` (Module 3: Document Forensic & Tampering Detection Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Threat Taxonomy

Module 3 is designed to detect and categorize the following adversarial manipulation modalities:

| Threat Category | Description | Forensic Signatures |
| :--- | :--- | :--- |
| **Photo Substitution / Splicing** | Replacing original bearer photo with an imposter portrait. | Splicing edge discontinuity, ELA compression discrepancy between photo and card body, noise variance mismatch. |
| **Text Modification (Altered DOB / Dates)** | Overwriting or modifying digits in date of birth, expiration, or document numbers. | Localized font blur, baseline misalignment, micro-pattern disruption, double-JPEG artifacts. |
| **Copy-Paste / Clone Tampering** | Cloning background security textures or numbers from another document region. | High correlation of identical noise patterns, identical DCT coefficient distribution. |
| **Screen Replay / Moiré Capture** | Capturing an identity document displayed on a monitor/phone screen. | 2D FFT periodic spectral peaks, lattice frequency spikes, high-frequency moiré patterns. |
| **Re-compression / Spliced Saving** | Pasting elements and saving with different JPEG quality factor. | ELA residual differential, distinct block boundary artifacts. |

---

## 2. Benign vs Malicious Transformations

To prevent false alarms, Module 3 explicitly models and normalizes benign environmental transformations:
* **Benign JPEG Recompression ($Q \ge 60$):** Global compression without localized variance is classified as normal.
* **Benign Illumination Gradients:** Camera flash and room shadows are handled by illumination normalization.
* **Benign Aspect Ratio / Scaling:** Uniform downscaling is distinguished from localized resampling.
