# AI-DIDSS Module 4: Biometric Face Verification & Match Quality Engine

**Module:** `module4_face_verification` (Module 4: Biometric Face Verification & Match Quality Engine)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Release Version:** `v1.0.0-FROZEN`  
**Status:** **`FROZEN (28/28 TESTS PASSED - 100%)`**  

---

## 1. Overview & Operational Philosophy

Module 4 performs 1:1 facial biometric matching and ICAO Doc 9303 / ISO/IEC 19794-5 image quality evaluation. It compares bearer portraits extracted from physical documents against live camera capture probes.

### Strict Non-Exclusion Invariant
> [!IMPORTANT]
> **Module 4 is a biometric decision-support tool for border control officers, NOT an autonomous deportation system.**  
> A biometric mismatch indicates low statistical facial feature similarity for officer review. Module 4 **NEVER outputs `IMPOSTER`, `CRIMINAL`, `DETAIN`, or `REJECT`**.

---

## 2. Core Capabilities

1. **ICAO 9303 Quality Assessment:** Laplacian sharpness, horizontal illumination symmetry, contrast dynamic range, specular glare.
2. **Presentation Attack Detection (PAD):** 2D FFT spectral lattice moiré analysis and skin texture energy evaluation.
3. **Discriminative Representation:** 128-dimensional multi-scale spatial gradient and morphology embedding.
4. **Calibrated Cosine Matching:** Normalized similarity score in $[0.0, 1.0]$ with an operating match threshold of $\ge 0.72$.

---

## 3. How to Run Module 4

```powershell
cd module4_face_verification
pytest tests/ -v -p no:cacheprovider
```
