# Module 1 OCR: Model & Pipeline Version History

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  

---

## Model Version Registry

| Version Tag | Architecture / Engine | Dataset Version | Validation F1 | Test F1 | Test Exact Match | Mean Latency (CPU) | Status | Key Innovations / Changes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`v1.0.0-baseline`** | DocumentOCR-Baseline (OpenCV Optical Reader + Naive Linear Regex Extractor) | SynthID-Doc v1.0 (240 images) | 20.37% | 17.59% | 12.96% | 60.7ms | **SUPERSEDED** | Initial baseline implementation in Stage 3. Unstructured text extraction with basic linear regex matching. |
| **`v2.0.0-improved`** | LayoutAware-MultiScale-OCR (Multi-Scale ROI Segmentation + Spatial Proximity Extractor + Bidirectional MRZ/VIZ Fusion) | SynthID-Doc v1.0 (240 images) | **30.81%** | **27.13%** | **22.22%** | **55.7ms** | **ACTIVE CANDIDATE** | Stage 4 improvement. Decomposed document ROIs (Header, VIZ, MRZ, Barcode), ISO 3166-1 alpha-3 country dictionaries, standardized ISO date normalization, bidirectional MRZ/VIZ backfilling. |

---

## Detailed Version Changelogs

### Version 2.0.0-improved (Active Candidate)
* **Date:** 2026-09-02
* **Release Objective:** Address baseline multiline bounding box collisions, date format fragmentation, and unsegmented MRZ token confusion.
* **Component Changes:**
  1. `src/preprocessing/roi_extractor.py`: Added 1.5x bicubic upscaling on MRZ zones and functional document partitioning.
  2. `src/extraction/layout_extractor.py`: Implemented multi-region spatial anchoring, ISO date parser (`YYYY-MM-DD`), and bidirectional MRZ-to-VIZ attribute backfilling.
  3. `src/ocr/mrz_parser.py`: Robust padding logic preventing index out-of-bounds on truncated optical reads.
* **Performance Delta vs Baseline:**
  * Field F1 Score: **+9.54% absolute improvement** (+54.2% relative gain)
  * Exact Match Ratio: **+9.26% absolute improvement** (+71.4% relative gain)
  * Latency: Reduced by **-5.0ms** (55.7ms on AMD Ryzen CPU)
* **Known Limitations:**
  * Complex script fonts in unstructured driver's license remarks require deep neural layout transformers for 100% field recovery.
  * Isolated external testing (`data/external_test/`) intentionally preserved for Stage 7.

---

### Version 1.0.0-baseline (Superseded)
* **Date:** 2026-09-02
* **Release Objective:** Establish initial functional baseline and benchmark processing time.
* **Architecture:** Monolithic document OCR with global text line extraction and unanchored regexes.
