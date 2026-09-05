"""Unified Field Extraction & Document Understanding Pipeline (Stage 5).

Integrates:
- Document Type Classification
- MRZ Parsing & ICAO Checksum Verification
- Layout-Aware Spatial Extraction & Multiline Value Association
- Traceable Normalization & Disambiguation
- Cross-Field Consistency Checking & Evidentiary Conflict Tracking
- Standardized Structured JSON Output
"""

from typing import Dict, Any, Optional
from .schema import DocumentExtractionResult, ExtractedField
from .doc_classifier import DocumentTypeClassifier
from .normalizer import FieldNormalizer
from .validator import FieldValidator
from .layout_extractor import LayoutAwareFieldExtractor
from ..ocr.mrz_parser import MRZParser

class DocumentUnderstandingPipeline:
    def __init__(self, min_confidence: float = 0.50):
        self.classifier = DocumentTypeClassifier(min_confidence=min_confidence)
        self.normalizer = FieldNormalizer()
        self.validator = FieldValidator()
        self.mrz_parser = MRZParser()
        self.layout_extractor = LayoutAwareFieldExtractor()

    def process(self, raw_text: str, processing_metadata: Optional[Dict[str, Any]] = None) -> DocumentExtractionResult:
        processing_metadata = processing_metadata or {}
        
        # 1. Parse MRZ
        mrz_fields, mrz_validation = self.mrz_parser.parse(raw_text)

        # 2. Classify Document Type
        doc_type, doc_conf = self.classifier.classify(raw_text, mrz_validation)

        if doc_type == "unknown_document" or not raw_text.strip():
            return DocumentExtractionResult(
                document_type="unknown_document",
                document_type_confidence=doc_conf,
                raw_text=raw_text,
                fields={},
                mrz_validation=mrz_validation,
                cross_field_conflicts=[],
                validation_summary=None,
                processing_metadata=processing_metadata,
                status="UNKNOWN",
                review_required=True
            )

        # 3. Layout-Aware Field Extraction & Spatial Association
        extraction_res = self.layout_extractor.extract(raw_text, preproc_metadata=processing_metadata)
        fields = extraction_res.fields

        # 4. Normalization & Traceable Corrections
        for fname, f_obj in list(fields.items()):
            raw_v = f_obj.value
            f_obj.raw_value = raw_v

            # Date Normalization
            if "date" in fname or fname in ["date_of_birth", "date_of_expiry", "date_of_issue", "valid_until", "valid_from"]:
                norm_d, corr = self.normalizer.normalize_date(raw_v)
                if norm_d:
                    f_obj.value = norm_d
                    f_obj.corrections.extend(corr)

            # Name Normalization
            elif "name" in fname or fname in ["full_name", "surname", "given_names", "holder", "bearer"]:
                norm_n, corr = self.normalizer.normalize_name(raw_v)
                if norm_n:
                    f_obj.value = norm_n
                    f_obj.corrections.extend(corr)

            # Document Number Disambiguation
            elif "number" in fname or fname in ["passport_number", "license_number", "id_number", "permit_number", "visa_number"]:
                norm_num, corr = self.normalizer.disambiguate_document_number(raw_v, doc_type=doc_type)
                if norm_num:
                    f_obj.value = norm_num
                    f_obj.corrections.extend(corr)

            # Validate each field
            self.validator.validate_field(fname, f_obj, doc_type=doc_type)

        # 5. Chronological Logic & Consistency
        chrono_warnings = self.validator.validate_chronology(fields)
        if chrono_warnings:
            for w in chrono_warnings:
                if "date_of_birth" in fields:
                    fields["date_of_birth"].warnings.append(w)

        # 6. Cross-Field Visual vs MRZ Consistency Check
        conflicts = []
        if mrz_fields and doc_type in ["passport", "visa", "national_id"]:
            conflicts = self.validator.check_cross_field_consistency(fields, mrz_fields)

        # 7. Validation Summary & Review Required Determination
        summary = self.validator.summarize_validation(fields, conflicts, chrono_warnings)
        review_req = not summary.all_valid or len(conflicts) > 0 or doc_conf < 0.70

        # Overall Status
        if len(fields) >= 4 and summary.all_valid:
            status = "SUCCESS"
        elif len(fields) >= 1:
            status = "PARTIAL" if not review_req else "REVIEW_REQUIRED"
        else:
            status = "REVIEW_REQUIRED"

        return DocumentExtractionResult(
            document_type=doc_type,
            document_type_confidence=doc_conf,
            raw_text=raw_text,
            fields=fields,
            mrz_validation=mrz_validation if doc_type in ["passport", "visa", "national_id"] else None,
            cross_field_conflicts=conflicts,
            validation_summary=summary,
            processing_metadata=processing_metadata,
            status=status,
            review_required=review_req
        )
