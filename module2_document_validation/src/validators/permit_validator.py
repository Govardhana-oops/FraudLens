"""Residence and Work Permit Validator for Module 2.

Handles International Residence and Work Permit Standards:
- Mandatory field presence: permit_number, permit_category (Marks UNKNOWN if absent)
- Expiration date presence (date_of_expiry or valid_until; Marks UNKNOWN if absent)
- Permit category authorization (Emits WARNING if non-standard)
- Sponsor identity presence check
"""

import re
from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class PermitValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mandatory_fields = ["permit_number", "permit_category"]
        self.authorized_categories = {
            "WORK AUTHORIZATION", "PERMANENT RESIDENCE", "STUDENT", "STUDENT VISA",
            "BUSINESS", "TEMPORARY RESIDENCE", "EMPLOYMENT", "FAMILY REUNIFICATION"
        }

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
                    message=f"Mandatory permit field '{req_f}' unavailable in OCR extraction",
                    field_name=req_f
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="REQ_FIELD_PRESENCE",
                    category=RuleCategoryEnum.SCHEMA.value,
                    status="PASS",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Mandatory permit field '{req_f}' is present",
                    field_name=req_f,
                    actual=fields[req_f].value
                ))

        # Check Expiry
        has_expiry = ("valid_until" in fields and fields["valid_until"].value) or \
                     ("date_of_expiry" in fields and fields["date_of_expiry"].value) or \
                     ("expiry_date" in fields and fields["expiry_date"].value)
        if not has_expiry:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="UNKNOWN",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory permit expiration date (valid_until / date_of_expiry) unavailable in OCR extraction",
                field_name="valid_until"
            ))
        else:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="PASS",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory permit expiration date is present",
                field_name="valid_until",
                actual=fields.get("valid_until", fields.get("date_of_expiry", fields.get("expiry_date"))).value
            ))

        # 2. Permit Number Syntax (CRITICAL if present and malformed)
        pnum = fields.get("permit_number")
        if pnum and pnum.value:
            clean_pnum = pnum.value.strip().upper()
            if clean_pnum:
                if re.match(r"^(PRM-|RES-|PERMIT-)?[A-Z0-9]{6,16}$", clean_pnum):
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_PERMIT_NUMBER_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Permit registration number '{clean_pnum}' conforms to alphanumeric structure",
                        field_name="permit_number",
                        actual=clean_pnum
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_PERMIT_NUMBER_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Permit registration number '{clean_pnum}' violates alphanumeric constraints",
                        field_name="permit_number",
                        actual=clean_pnum
                    ))

        # 3. Domain: Permit Category Authorization
        pcat = fields.get("permit_category")
        if pcat and pcat.value:
            clean_pcat = pcat.value.strip().upper()
            if any(auth in clean_pcat for auth in self.authorized_categories) or clean_pcat in self.authorized_categories:
                results.append(ValidationCheckResult(
                    rule_id="DOMAIN_PERMIT_CATEGORY_VALIDITY",
                    category=RuleCategoryEnum.DOMAIN.value,
                    status="PASS",
                    severity=RuleSeverityEnum.MEDIUM.value,
                    message=f"Permit category '{clean_pcat}' is an authorized immigration classification",
                    field_name="permit_category",
                    actual=clean_pcat
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="DOMAIN_PERMIT_CATEGORY_VALIDITY",
                    category=RuleCategoryEnum.DOMAIN.value,
                    status="WARNING",
                    severity=RuleSeverityEnum.LOW.value,
                    message=f"Permit category '{clean_pcat}' is non-standard or unrecognized",
                    field_name="permit_category",
                    actual=clean_pcat
                ))

        # 4. Sponsor Field Verification (Informational check)
        spons = fields.get("sponsor")
        if spons and spons.value:
            results.append(ValidationCheckResult(
                rule_id="INFO_SPONSOR_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="PASS",
                severity=RuleSeverityEnum.INFO.value,
                message=f"Permit sponsor entity '{spons.value.strip()}' is documented",
                field_name="sponsor",
                actual=spons.value.strip()
            ))

        return results
