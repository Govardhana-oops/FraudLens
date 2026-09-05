# Stage 7: External Dataset Independence & Anti-Leakage Audit Report

**Module:** Module 1 (OCR Extraction & Multi-Type Identity Data Understanding)  
**Audit Timestamp:** 2026-09-02  
**Dataset Version:** `SynthID-Doc-External v1.0`  

---

## 1. Executive Summary of Audit Findings

A comprehensive cryptographic, document identity, and filename audit was performed across all dataset partitions before executing Stage 7 external evaluation.

| Audit Dimension | Development Partitions (`train` + `val` + `test`) | External Test Partition (`external_test`) | Overlap Detected | Audit Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **Total Image Files** | 240 files | 30 files | **0 files** | **PASSED (100% Unique)** |
| **Document Identity Groups** | 120 unique IDs | 30 unique IDs | **0 IDs** | **PASSED (Zero Identity Leakage)** |
| **Cryptographic SHA-256 Hashes** | 240 unique hashes | 30 unique hashes | **0 hashes** | **PASSED (Zero Duplicate Images)** |
| **Annotation Records** | 240 records | 30 records | **0 records** | **PASSED (Independent Ground Truth)** |

---

## 2. Document Class Distribution (External Partition)

* **Passport (ICAO TD3):** 6 samples (100% unseen traveler identities)
* **Travel Visa (ICAO MRV-A):** 6 samples (100% unseen visa holders)
* **Driver's License (AAMVA):** 6 samples (100% unseen driver records)
* **National ID (ICAO TD1):** 6 samples (100% unseen citizen cards)
* **Residence Permit:** 6 samples (100% unseen resident records)

---

## 3. Certification of Independence

It is certified that:
1. No sample from `data/external_test/` was ever used during Stage 1 through Stage 6 for training, spatial template fitting, threshold tuning, or debugging.
2. The external partition is completely isolated, quarantined, and cryptographically distinct from all development data.
3. The evaluation procedure in Stage 7 is a true blind evaluation of generalization capability.
