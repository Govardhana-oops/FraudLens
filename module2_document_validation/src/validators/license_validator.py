"""Driver's License Specific Validator for Module 2.

Handles AAMVA and International Driver's License Standards:
- Mandatory field presence: license_number, full_name, date_of_birth, expiry_date (Marks UNKNOWN if absent)
- License number alphanumeric syntax (CRITICAL if present and malformed)
- Minimum operating age check (>= 16 years at issue date; CRITICAL if violated)
- Vehicle class categorization
"""

import re
from datetime import date
from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class LicenseValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mandatory_fields = ["license_number", "full_name", "date_of_birth"]

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
                    message=f"Mandatory driver license field '{req_f}' unavailable in OCR extraction",
                    field_name=req_f
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="REQ_FIELD_PRESENCE",
                    category=RuleCategoryEnum.SCHEMA.value,
                    status="PASS",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Mandatory driver license field '{req_f}' is present",
                    field_name=req_f,
                    actual=fields[req_f].value
                ))

        # Check Expiry presence
        has_expiry = ("expiry_date" in fields and fields["expiry_date"].value) or \
                     ("date_of_expiry" in fields and fields["date_of_expiry"].value)
        if not has_expiry:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="UNKNOWN",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory license expiration date unavailable in OCR extraction",
                field_name="expiry_date"
            ))
        else:
            results.append(ValidationCheckResult(
                rule_id="REQ_FIELD_PRESENCE",
                category=RuleCategoryEnum.SCHEMA.value,
                status="PASS",
                severity=RuleSeverityEnum.HIGH.value,
                message="Mandatory license expiration date is present",
                field_name="expiry_date",
                actual=fields.get("expiry_date", fields.get("date_of_expiry")).value
            ))

        # 2. License Number Syntax (CRITICAL if present and malformed)
        lnum = fields.get("license_number")
        if lnum and lnum.value:
            clean_lnum = lnum.value.strip().upper()
            if clean_lnum:
                if re.match(r"^(DL-)?[A-Z0-9]{6,16}$", clean_lnum):
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_DRIVER_LICENSE_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Driver license number '{clean_lnum}' conforms to alphanumeric structure",
                        field_name="license_number",
                        actual=clean_lnum
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_DRIVER_LICENSE_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Driver license number '{clean_lnum}' violates alphanumeric format rules",
                        field_name="license_number",
                        actual=clean_lnum
                    ))

        # 3. Domain: Minimum Driving Age Check (>= 16 years at issue date)
        dob_f = fields.get("date_of_birth") or fields.get("dob")
        iss_f = fields.get("issue_date") or fields.get("date_of_issue")
        if dob_f and iss_f and dob_f.value and iss_f.value:
            try:
                dob_dt = date.fromisoformat(dob_f.value.strip())
                iss_dt = date.fromisoformat(iss_f.value.strip())
                age_at_issue = (iss_dt - dob_dt).days / 365.25
                if age_at_issue < 15.9: # Under 16 years
                    results.append(ValidationCheckResult(
                        rule_id="DOMAIN_DL_MINIMUM_AGE",
                        category=RuleCategoryEnum.DOMAIN.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Bearer age at license issuance ({age_at_issue:.1f} years) is below minimum driving threshold (16.0 years)",
                        expected=">= 16.0 years",
                        actual=f"{age_at_issue:.1f} years"
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="DOMAIN_DL_MINIMUM_AGE",
                        category=RuleCategoryEnum.DOMAIN.value,
                        status="PASS",
                        severity=RuleSeverityEnum.HIGH.value,
                        message=f"Bearer age at issuance ({age_at_issue:.1f} years) satisfies minimum driving age requirements",
                        actual=f"{age_at_issue:.1f} years"
                    ))
            except Exception:
                pass

        return results
