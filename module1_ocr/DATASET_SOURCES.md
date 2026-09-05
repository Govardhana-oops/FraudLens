# Dataset Sources & Licensing Specification

**Project:** AI-Based Fake Identity & Travel Document Screening System (AI-DIDSS)  
**Module:** Module 1 (OCR Extraction & Document Data Understanding)  
**Compliance Standard:** ISO/IEC 19794, ICAO Doc 9303, AAMVA DL/ID Card Standard, GDPR/Privacy-by-Design  

---

## 1. Authorized Data Sources Policy

To prevent privacy violations and adhere to ethical AI practices:
* **Zero Real Document Ingestion:** No real, non-consented identity documents (passports, national IDs, driver's licenses) are collected, downloaded, or stored.
* **Synthetic & Benchmark Ground Truth:** All data utilized in Module 1 originates from verified synthetic generators, publicly licensed research benchmarks, or authorized procedural generators modeled on international standards.

---

## 2. Dataset Registry

| Dataset Name | Source / Origin | License | Supported Document Types | Sample Count | Annotation Availability | Allowed Usage | Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AI-DIDSS Synthetic Generator (SynthID-Doc)** | Internal Procedural Document Generation Engine (PIL / OpenCV) | MIT / Open Research | Passports (TD3), Visas (MRV-A), Driver's Licenses (PDF417), National IDs (TD1/TD2), Residence Permits | 600 unique document identities (1,200 total captures with camera & scanner variations) | Full Ground Truth (JSONL): Word/Field bboxes, normalized text, MRZ checksums, barcode payloads | Development, Training, Validation, and Benchmarking | Synthetic visual texture; requires real-world benchmark cross-validation |
| **MIDV-500 Benchmark Subset** | Institute for Information Transmission Problems (IITP RAS) | CC BY-SA 4.0 | International Passports, Identity Cards, Driver's Licenses | 50 distinct identity types captured under 10 camera conditions | Full Ground Truth: 4-corner document boundaries, text fields, OCR transcripts | Academic & Non-Commercial Research Benchmarking | Fixed template layouts; primarily physical camera clips converted to frames |
| **MIDV-2019 Extended Subset** | IITP RAS / Smart Engines | CC BY-SA 4.0 | Modern Travel & Identity Documents with varied fonts and security patterns | 50 distinct identity templates with extreme perspective distortion | Bounding boxes, document type labels, text field transcriptions | Academic & Non-Commercial Research Benchmarking | Limited variation in biometric facial demographics |
| **SynthDoG Multilingual Benchmark** | NAVER Clova AI / Donut Document Benchmark | MIT License | Textual and tabular documents with synthetic rendering | Reference synthetic benchmark samples | Character and word-level coordinates, transcriptions | Pre-training and text recognition evaluation | General document layout rather than strict identity card templates |
| **AI-DIDSS Isolated External Test Suite** | Dedicated out-of-distribution synthetic generator with unseen fonts, noise, and foreign layout templates | MIT / Research Isolated | Passports, Visas, National IDs, Driver's Licenses | 100 unique, completely unseen document identities | Separate ground truth JSONL preserved strictly for blind evaluation | Zero-training evaluation only | Must never be accessed during training or threshold tuning |

---

## 3. Data Integrity & Privacy Verification

* **PII Risk:** **ZERO.** All names, passport numbers, dates of birth, addresses, and barcode payloads are procedurally generated using synthetic name/address dictionaries and random algorithmic seed patterns.
* **Photographs:** Synthetic face avatars generated procedurally or sourced from royalty-free public domain / synthetic face repositories.
* **Barcode & MRZ Compliance:** Generated MRZ lines and PDF417 byte streams strictly follow ICAO 9303 and AAMVA specifications with valid modulo-10 and Reed-Solomon check digits.
