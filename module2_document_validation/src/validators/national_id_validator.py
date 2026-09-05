"""National Identity Card Validator for Module 2.

Handles ICAO Doc 9303 Part 5 (TD1) and National Identity Card Specifications:
- Mandatory field presence: id_number, full_name (or surname), date_of_birth (Marks UNKNOWN if absent)
- ID number alphanumeric format (CRITICAL if present and malformed)
"""

import re
from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class NationalIDValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mandatory_fields = ["id_number", "date_of_birth"]

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
                    message=f"Mandatory national identity field '{req_f}' unavailable in OCR extraction",
                    field_name=req_f
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="REQ_FIELD_PRESENCE",
                    category=RuleCategoryEnum.SCHEMA.value,
                    status="PASS",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Mandatory national identity field '{req_f}' is present",
                    field_name=req_f,
                    actual=fields[req_f].value
                ))

        # Check Name
        has_name = ("full_name" in fields and fields["full_name"].value) or \
                   ("surname" in fields and fields["surname"].value)
        if not has_name:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="UNKNOWN",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory bearer name (full_name or surname) unavailable in OCR extraction",
                field_name="full_name"
            ))
        else:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="PASS",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory bearer name is present",
                field_name="full_name",
                actual=fields.get("full_name", fields.get("surname")).value
            ))

        # 2. National ID Number Syntax (CRITICAL if present and malformed)
        id_num = fields.get("id_number")
        if id_num and id_num.value:
            clean_id = id_num.value.replace(" ", "").upper()
            if clean_id:
                if re.match(r"^[A-Z0-9-]{6,18}$", clean_id):
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_NATIONAL_ID_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"National ID number '{clean_id}' conforms to standard alphanumeric structure",
                        field_name="id_number",
                        actual=clean_id
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_NATIONAL_ID_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"National ID number '{clean_id}' violates length/character constraints",
                        field_name="id_number",
                        actual=clean_id
                    ))

        return results
