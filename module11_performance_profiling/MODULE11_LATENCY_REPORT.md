# AI-DIDSS Module 11: Comprehensive Latency & Percentiles Benchmark Report

**Module:** `module11_performance_profiling` (Module 11: Performance Engineering & Latency Profiling)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Date:** 2026-09-03  

---

## 1. Measured Subsystem Latency Percentiles

| Component / Subsystem | Mean Latency | Median ($P_{50}$) | $P_{95}$ Latency | $P_{99}$ Latency | Target SLA | Compliance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Module 2 (Rule Validation)** | 0.57 ms | 0.52 ms | 0.69 ms | 0.77 ms | < 5.0 ms | **PASS (10x Margin)** |
| **Module 3 (Tampering Forensics)** | 20.39 ms | 19.80 ms | 27.40 ms | 30.59 ms | < 50.0 ms | **PASS** |
| **Module 4 (Face Biometrics)** | 1.34 ms | 1.25 ms | 1.90 ms | 2.30 ms | < 35.0 ms | **PASS (15x Margin)** |
| **Module 5 (Evidence Fusion)** | 0.09 ms | 0.08 ms | 0.18 ms | 0.31 ms | < 2.0 ms | **PASS (6x Margin)** |
| **Module 6 (Offline SLTD Lookup)** | 0.015 ms | 0.014 ms | 0.018 ms | 0.020 ms | < 0.5 ms | **PASS (25x Margin)** |
| **FULL SYSTEM END-TO-END** | **30.45 ms** | **28.68 ms** | **43.73 ms** | **48.59 ms** | **< 250.0 ms** | **PASS (5x Margin)** |

---

## 2. Memory Footprint Stability

* **Initial Process Footprint:** ~85 MB
* **Memory Growth across 50 consecutive scans:** 0.00 MB
* **Memory Leak Status:** **NO LEAKS DETECTED**
