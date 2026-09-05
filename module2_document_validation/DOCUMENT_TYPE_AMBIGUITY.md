# AI-DIDSS Module 2: Document-Type Ambiguity Specification

**Module:** `module2_document_validation` (Module 2: Document Rule & Security Logic Validation)  
**System:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Version:** `v0.3.0-STAGE3`  
**Date:** 2026-09-03  

---

## 1. Threat Model & Problem Statement

Module 1 OCR performs layout-aware document classification, but may encounter degraded images, partial crops, or unfamiliar document variants where document classification confidence is borderline (e.g. $\text{confidence} < 0.70$).

### Core Principle
> [!IMPORTANT]
> **Never force an ambiguous document into a strict document class simply to continue processing.**  
> Demanding passport-specific fields (e.g. passport number) on a document that might actually be a national ID card causes false `INVALID` decisions.

---

## 2. Decision Logic Matrix

| Classification State | Optical Confidence | Rule Engine Execution Policy | Overall Status Outcome | Review Flag |
| :--- | :---: | :--- | :---: | :---: |
| **High-Confidence Known Type** | $\ge 0.70$ | Executes universal checks + dedicated document validator (`passport`, `visa`, `driver_license`, etc.) | Follows standard precedence (`VALID`, `INVALID`, `EXPIRED`, `REVIEW_REQUIRED`) | Based on check results |
| **Borderline / Low Confidence** | $< 0.70$ | **Restricts execution to Universal Rules only** (Calendar math, temporal chronology, MRZ math, cross-field consistency). Skips document-specific mandatory field enforcement. | **`REVIEW_REQUIRED`** (or `INVALID` if universal calendar/chronology math is violated) | `true` |
| **Unknown Document** (`unknown_document`) | Any | Universal checks only. | **`UNKNOWN`** | `true` |
| **Unsupported Document** (`voter_card`, etc.) | Any | Universal checks only. Emits `SCHEMA_UNSUPPORTED_DOCUMENT` warning. | **`UNSUPPORTED_DOCUMENT`** | `true` |

---

## 3. Substantive Failures in Ambiguous Contexts

Even when a document's classification is ambiguous, **fundamental universal physical and mathematical violations remain fatal**:
* Impossible calendar date (e.g. `1990-02-30`) $\rightarrow$ **`INVALID`**.
* Chronology inversion ($\text{Issue Date} > \text{Expiry Date}$) $\rightarrow$ **`INVALID`**.
* ICAO Modulo-10 checksum failure on detected MRZ $\rightarrow$ **`INVALID`**.
