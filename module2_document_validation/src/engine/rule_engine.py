"""Rule Engine Orchestrator for Module 2 Document Validation.

Coordinates OCR normalization, modular validators, aggregates check results,
calculates deterministic validation scores, and handles document-type and field-level
confidence ambiguities conservatively.
"""

from typing import Dict, Any, List, Optional
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import (
    DocumentValidationResult,
    ValidationCheckResult,
    FieldValidationResult,
    ValidationStatusEnum,
    RuleSeverityEnum
)
from ..normalizers.ocr_normalizer import OCRNormalizer
from ..validators.date_validator import DateValidator
from ..validators.mrz_validator import MRZValidator
from ..validators.consistency_validator import ConsistencyValidator
from ..validators.passport_validator import PassportValidator
from ..validators.visa_validator import VisaValidator
from ..validators.license_validator import LicenseValidator
from ..validators.national_id_validator import NationalIDValidator
from ..validators.permit_validator import PermitValidator

class RuleEngine:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.normalizer = OCRNormalizer(self.config)
        self.date_validator = DateValidator(self.config)
        self.mrz_validator = MRZValidator(self.config)
        self.consistency_validator = ConsistencyValidator(self.config)
        self.passport_validator = PassportValidator(self.config)
        self.visa_validator = VisaValidator(self.config)
        self.license_validator = LicenseValidator(self.config)
        self.national_id_validator = NationalIDValidator(self.config)
        self.permit_validator = PermitValidator(self.config)

        # Thresholds
        self.doc_type_confidence_threshold = self.config.get("thresholds", {}).get("doc_type_confidence_threshold", 0.70)
        self.field_confidence_threshold = self.config.get("thresholds", {}).get("field_confidence_threshold", 0.60)

        # Severity weights for deterministic score calculation
        self.severity_weights = {
            RuleSeverityEnum.CRITICAL.value: 1.0,
            RuleSeverityEnum.HIGH.value: 0.75,
            RuleSeverityEnum.MEDIUM.value: 0.50,
            RuleSeverityEnum.LOW.value: 0.25,
            RuleSeverityEnum.INFO.value: 0.0
        }

    def _get_document_validator(self, doc_type: str):
        clean_type = doc_type.lower().strip()
        if clean_type in ["passport"]:
            return self.passport_validator
        elif clean_type in ["visa"]:
            return self.visa_validator
        elif clean_type in ["driver_license", "driver_licence", "license"]:
            return self.license_validator
        elif clean_type in ["national_id", "id_card", "identity_card"]:
            return self.national_id_validator
        elif clean_type in ["permit", "residence_permit"]:
            return self.permit_validator
        return None

    def validate(self, payload: Module1InputPayload) -> DocumentValidationResult:
        """Executes full validation pipeline across input payload."""
        checks: List[ValidationCheckResult] = []
        warnings: List[str] = list(payload.warnings)
        errors: List[str] = []

        raw_type = payload.document_type.value if payload.document_type else "unknown_document"
        doc_type = raw_type.lower().strip()
        doc_type_conf = payload.document_type.confidence if payload.document_type else 0.0
        
        # 1. Handle Upstream Invalid Input or Processing Errors
        if payload.status in ["INVALID_INPUT", "PROCESSING_ERROR"]:
            err_msg = payload.error_details.get("message", "Upstream invalid input") if payload.error_details else "Invalid input"
            checks.append(ValidationCheckResult(
                rule_id="SCHEMA_INPUT_VALIDITY",
                category="SCHEMA",
                status="FAIL",
                severity=RuleSeverityEnum.CRITICAL.value,
                message=f"Module 1 reported input error: {err_msg}"
            ))
            return DocumentValidationResult(
                document_type=doc_type,
                overall_status=ValidationStatusEnum.INVALID_INPUT.value,
                validation_score=0.0,
                checks=checks,
                errors=[err_msg],
                review_required=True
            )

        # 2. Stage 3 Pre-Validation OCR Normalization
        norm_res = self.normalizer.normalize_payload_fields(payload.fields)
        if norm_res.warnings:
            warnings.extend(norm_res.warnings)

        # 3. Universal Date & Chronology Validation
        date_checks = self.date_validator.validate(payload)
        checks.extend(date_checks)

        # 4. Universal MRZ Checksum Validation
        mrz_checks = self.mrz_validator.validate(payload)
        checks.extend(mrz_checks)

        # 5. Universal Consistency & Conflict Validation
        consistency_checks = self.consistency_validator.validate(payload)
        checks.extend(consistency_checks)

        # 6. Document-Type Ambiguity Evaluation
        is_doc_type_ambiguous = (doc_type_conf < self.doc_type_confidence_threshold) and (doc_type != "unknown_document")
        if is_doc_type_ambiguous:
            checks.append(ValidationCheckResult(
                rule_id="AMBIGUITY_DOCUMENT_TYPE_CONFIDENCE",
                category="SCHEMA",
                status="WARNING",
                severity=RuleSeverityEnum.HIGH.value,
                message=f"Document type '{doc_type}' has low classification confidence ({doc_type_conf:.2f} < {self.doc_type_confidence_threshold:.2f}); restricting to universal verification",
                field_name="document_type",
                expected=f">= {self.doc_type_confidence_threshold:.2f}",
                actual=f"{doc_type_conf:.2f}"
            ))

        # 7. Document-Specific Rules (Executed only if classification is confident)
        doc_validator = self._get_document_validator(doc_type)
        if doc_validator and not is_doc_type_ambiguous:
            doc_checks = doc_validator.validate(payload)
            checks.extend(doc_checks)
        elif doc_validator and is_doc_type_ambiguous:
            # When ambiguous, skip strict document-specific mandatory rules to prevent false invalids
            pass
        elif doc_type not in ["unknown_document"]:
            checks.append(ValidationCheckResult(
                rule_id="SCHEMA_UNSUPPORTED_DOCUMENT",
                category="SCHEMA",
                status="WARNING",
                severity=RuleSeverityEnum.MEDIUM.value,
                message=f"Document type '{doc_type}' does not have a dedicated validation rule set"
            ))

        # 8. Field-Level Confidence Inspection (Flags review for critical low-confidence fields)
        critical_fields = {
            "passport_number", "visa_number", "license_number", "id_number",
            "permit_number", "date_of_expiry", "expiry_date", "valid_until", "date_of_birth", "dob"
        }
        has_low_confidence_critical_field = False
        for fname, fobj in payload.fields.items():
            if fobj.confidence < self.field_confidence_threshold and fobj.value:
                if fname.lower() in critical_fields:
                    has_low_confidence_critical_field = True
                    checks.append(ValidationCheckResult(
                        rule_id="AMBIGUITY_FIELD_OPTICAL_CONFIDENCE",
                        category="SCHEMA",
                        status="WARNING",
                        severity=RuleSeverityEnum.HIGH.value,
                        message=f"Critical field '{fname}' extracted with low optical confidence ({fobj.confidence:.2f} < {self.field_confidence_threshold:.2f})",
                        field_name=fname,
                        expected=f">= {self.field_confidence_threshold:.2f}",
                        actual=f"{fobj.confidence:.2f}"
                    ))
                else:
                    checks.append(ValidationCheckResult(
                        rule_id="AMBIGUITY_FIELD_OPTICAL_CONFIDENCE",
                        category="SCHEMA",
                        status="WARNING",
                        severity=RuleSeverityEnum.LOW.value,
                        message=f"Optional field '{fname}' extracted with low optical confidence ({fobj.confidence:.2f})",
                        field_name=fname,
                        actual=f"{fobj.confidence:.2f}"
                    ))

        # 9. Granular Field Validation Results Compilation
        field_results: Dict[str, FieldValidationResult] = {}
        for fname, fobj in payload.fields.items():
            f_checks = [c for c in checks if c.field_name == fname]
            f_pass = sum(1 for c in f_checks if c.status == "PASS")
            f_fail = sum(1 for c in f_checks if c.status == "FAIL")
            f_msgs = [c.message for c in f_checks]
            
            if f_fail > 0:
                f_status = "INVALID"
            elif f_pass > 0:
                f_status = "VALID"
            elif fobj.value:
                f_status = "VALID"
            else:
                f_status = "UNKNOWN"

            field_results[fname] = FieldValidationResult(
                field_name=fname,
                value=fobj.value,
                status=f_status,
                checks_passed=f_pass,
                checks_failed=f_fail,
                messages=f_msgs
            )

        # 10. Check for Missing Mandatory Primary Identifiers
        primary_id_missing = any(
            c.rule_id == "REQ_FIELD_PRESENCE" and c.status == "UNKNOWN" and c.field_name in [
                "passport_number", "visa_number", "license_number", "id_number", "permit_number", "date_of_expiry", "valid_until", "expiry_date"
            ] for c in checks
        )

        # 11. Deterministic Score Calculation (Excludes UNKNOWN / NOT_APPLICABLE)
        total_weight = 0.0
        passed_weight = 0.0

        for c in checks:
            w = self.severity_weights.get(c.severity, 0.5)
            if c.status in ["PASS", "FAIL", "WARNING"]:
                total_weight += w
                if c.status == "PASS":
                    passed_weight += w
                elif c.status == "WARNING":
                    passed_weight += (w * 0.8) # Non-blocking warning multiplier

        if doc_type in ["unknown_document", "voter_registration_card", "voter_card"] or primary_id_missing or is_doc_type_ambiguous:
            validation_score = 0.50
        elif total_weight > 0.0:
            validation_score = min(1.0, max(0.0, passed_weight / total_weight))
        else:
            validation_score = 0.0

        # 12. Overall Status Determination (Semantic Hierarchy)
        has_critical_fail = any(c.status == "FAIL" and c.severity == RuleSeverityEnum.CRITICAL.value for c in checks)
        has_high_fail = any(c.status == "FAIL" and c.severity == RuleSeverityEnum.HIGH.value for c in checks)
        is_expired = any(c.rule_id == "CHRONO_EXPIRATION_STATUS" and c.status == "FAIL" for c in checks)
        has_conflicts = any(c.category == "CONSISTENCY" and c.status == "FAIL" for c in checks)

        for c in checks:
            if c.status == "FAIL":
                errors.append(f"[{c.rule_id}] {c.message}")
            elif c.status == "WARNING":
                warnings.append(f"[{c.rule_id}] {c.message}")

        if doc_type == "unknown_document":
            overall_status = ValidationStatusEnum.UNKNOWN.value
            review_required = True
        elif doc_validator is None and doc_type != "unknown_document":
            overall_status = ValidationStatusEnum.UNSUPPORTED_DOCUMENT.value
            review_required = True
        elif has_critical_fail:
            overall_status = ValidationStatusEnum.INVALID.value
            review_required = True
        elif primary_id_missing:
            overall_status = ValidationStatusEnum.UNKNOWN.value
            review_required = True
        elif is_doc_type_ambiguous:
            overall_status = ValidationStatusEnum.REVIEW_REQUIRED.value
            review_required = True
        elif is_expired:
            overall_status = ValidationStatusEnum.EXPIRED.value
            review_required = True
        elif has_high_fail or has_conflicts or payload.review_required or has_low_confidence_critical_field:
            overall_status = ValidationStatusEnum.REVIEW_REQUIRED.value
            review_required = True
        else:
            overall_status = ValidationStatusEnum.VALID.value
            review_required = False

        mrz_summary = None
        if payload.mrz:
            mrz_summary = {
                "format": payload.mrz.mrz_format,
                "lines": payload.mrz.lines,
                "checksum_valid": payload.mrz.checksum_valid,
                "checks": payload.mrz.checks
            }

        return DocumentValidationResult(
            document_type=doc_type,
            overall_status=overall_status,
            validation_score=round(validation_score, 4),
            checks=checks,
            field_results=field_results,
            cross_field_conflicts=payload.consistency.get("conflicts", []),
            mrz_validation=mrz_summary,
            warnings=warnings,
            errors=errors,
            review_required=review_required,
            validation_metadata={
                "total_checks": len(checks),
                "checks_passed": sum(1 for c in checks if c.status == "PASS"),
                "checks_failed": sum(1 for c in checks if c.status == "FAIL"),
                "checks_warning": sum(1 for c in checks if c.status == "WARNING"),
                "checks_unknown": sum(1 for c in checks if c.status == "UNKNOWN"),
                "normalizations_applied": {
                    k: v.transformations for k, v in norm_res.records.items() if v.transformations
                },
                "doc_type_confidence": doc_type_conf,
                "is_doc_type_ambiguous": is_doc_type_ambiguous
            }
        )
