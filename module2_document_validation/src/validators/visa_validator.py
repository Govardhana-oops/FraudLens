"""Travel Visa Specific Validator for Module 2.

Handles ICAO Doc 9303 Part 7 Travel Visa Specifications:
- Mandatory field presence: visa_number, date_of_expiry / valid_until (Marks UNKNOWN if absent)
- Visa number structure (alphanumeric, 6-12 chars; CRITICAL if malformed)
- Entries validity formatting
"""

import re
from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class VisaValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mandatory_fields = ["visa_number"]

    def validate(self, payload: Module1InputPayload) -> List[ValidationCheckResult]:
        results: List[ValidationCheckResult] = []
        fields = payload.fields

        # 1. Mandatory Field Presence (Marks UNKNOWN if unavailable)
        for req_f in self.mandatory_fields:
            if req_f not in fields or not fields[req_f].value:
                results.append(ValidationCheckResult(
                    rule_id="REQ_FIELD_PRESENCE",
                    category=RuleCategoryEnum.SCHEMA.value,
                    status="UNKNOWN",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Mandatory visa field '{req_f}' unavailable in OCR extraction",
                    field_name=req_f
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="REQ_FIELD_PRESENCE",
                    category=RuleCategoryEnum.SCHEMA.value,
                    status="PASS",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Mandatory visa field '{req_f}' is present",
                    field_name=req_f,
                    actual=fields[req_f].value
                ))

        # Check Expiry presence (either date_of_expiry or valid_until)
        has_expiry = ("date_of_expiry" in fields and fields["date_of_expiry"].value) or \
                     ("valid_until" in fields and fields["valid_until"].value)
        if not has_expiry:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="UNKNOWN",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory visa expiration date (date_of_expiry or valid_until) unavailable in OCR extraction",
                field_name="date_of_expiry"
            ))
        else:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="PASS",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory visa expiration date is present",
                field_name="date_of_expiry",
                actual=fields.get("date_of_expiry", fields.get("valid_until")).value
            ))

        # 2. Visa Number Structure (CRITICAL if present and malformed)
        vnum = fields.get("visa_number")
        if vnum and vnum.value:
            clean_vnum = vnum.value.replace(" ", "").upper()
            if clean_vnum:
                if re.match(r"^[A-Z0-9<]{6,12}$", clean_vnum):
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_VISA_NUMBER_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Visa number syntax '{clean_vnum}' conforms to standard format",
                        field_name="visa_number",
                        actual=clean_vnum
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_VISA_NUMBER_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Visa number syntax '{clean_vnum}' violates expected length constraints",
                        field_name="visa_number",
                        actual=clean_vnum
                    ))

        # 3. Entries Formatting (if extracted)
        entries = fields.get("entries")
        if entries and entries.value:
            clean_ent = entries.value.strip().upper()
            if clean_ent in ["M", "MULTIPLE", "1", "SINGLE", "2", "DOUBLE"]:
                results.append(ValidationCheckResult(
                    rule_id="FORMAT_VISA_ENTRIES",
                    category=RuleCategoryEnum.FORMAT.value,
                    status="PASS",
                    severity=RuleSeverityEnum.LOW.value,
                    message=f"Visa entries representation '{clean_ent}' is valid",
                    field_name="entries",
                    actual=clean_ent
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="FORMAT_VISA_ENTRIES",
                    category=RuleCategoryEnum.FORMAT.value,
                    status="WARNING",
                    severity=RuleSeverityEnum.LOW.value,
                    message=f"Visa entries representation '{clean_ent}' is non-standard",
                    field_name="entries",
                    actual=clean_ent
                ))

        return results
