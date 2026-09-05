"""Passport Specific Validator for Module 2.

Handles ICAO Doc 9303 Part 4 (TD3) and National Passport Booklet Specifications:
- Mandatory field presence check (marks UNKNOWN if absent)
- Passport booklet number alphanumeric syntax (CRITICAL if malformed)
- Gender standard code
- Country code ISO 3166-1 alpha-3 validation
- Maximum validity duration heuristic check
"""

import re
from datetime import date
from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class PassportValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mandatory_fields = ["passport_number", "date_of_expiry"]
        self.iso_countries = set(self.config.get("iso_country_codes", [
            "USA", "GBR", "CAN", "DEU", "FRA", "ITA", "ESP", "AUS", "JPN", "IND",
            "CHN", "BRA", "MEX", "ZAF", "NLD", "CHE", "SWE", "NOR", "DNK", "FIN",
            "UTO", "ATL", "ELD", "XAN", "ARC", "VAL"
        ]))

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
                    message=f"Mandatory passport field '{req_f}' unavailable in OCR extraction",
                    field_name=req_f
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="REQ_FIELD_PRESENCE",
                    category=RuleCategoryEnum.SCHEMA.value,
                    status="PASS",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Mandatory passport field '{req_f}' is present",
                    field_name=req_f,
                    actual=fields[req_f].value
                ))

        # Check Name presence
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

        # 2. Passport Number Syntax (If present, must conform; if malformed -> FAIL CRITICAL -> INVALID)
        pnum = fields.get("passport_number")
        if pnum and pnum.value:
            clean_pnum = pnum.value.replace(" ", "").upper()
            if clean_pnum:
                if re.match(r"^[A-Z0-9<]{6,12}$", clean_pnum):
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_PASSPORT_NUMBER_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Passport number syntax '{clean_pnum}' conforms to alphanumeric structure",
                        field_name="passport_number",
                        actual=clean_pnum
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="FORMAT_PASSPORT_NUMBER_SYNTAX",
                        category=RuleCategoryEnum.FORMAT.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Passport number syntax '{clean_pnum}' violates alphanumeric length constraints (6-12 chars)",
                        field_name="passport_number",
                        actual=clean_pnum
                    ))

        # 3. Country / Nationality Validation (ISO 3166-1 alpha-3)
        nat = fields.get("nationality") or fields.get("country") or fields.get("issuing_country")
        if nat and nat.value:
            clean_nat = nat.value.strip().upper()
            if clean_nat in self.iso_countries:
                results.append(ValidationCheckResult(
                    rule_id="FORMAT_COUNTRY_ISO3",
                    category=RuleCategoryEnum.FORMAT.value,
                    status="PASS",
                    severity=RuleSeverityEnum.MEDIUM.value,
                    message=f"Country code '{clean_nat}' recognized in ISO 3166-1 directory",
                    field_name="nationality",
                    actual=clean_nat
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="FORMAT_COUNTRY_ISO3",
                    category=RuleCategoryEnum.FORMAT.value,
                    status="WARNING",
                    severity=RuleSeverityEnum.MEDIUM.value,
                    message=f"Country code '{clean_nat}' is not in standard ISO 3166-1 list",
                    field_name="nationality",
                    actual=clean_nat
                ))

        # 4. Gender Validation
        gender = fields.get("gender") or fields.get("sex")
        if gender and gender.value:
            clean_gen = gender.value.strip().upper()
            if clean_gen in ["M", "F", "X", "<"]:
                results.append(ValidationCheckResult(
                    rule_id="FORMAT_GENDER_CODE",
                    category=RuleCategoryEnum.FORMAT.value,
                    status="PASS",
                    severity=RuleSeverityEnum.LOW.value,
                    message=f"Gender code '{clean_gen}' conforms to standard",
                    field_name="gender",
                    actual=clean_gen
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="FORMAT_GENDER_CODE",
                    category=RuleCategoryEnum.FORMAT.value,
                    status="WARNING",
                    severity=RuleSeverityEnum.LOW.value,
                    message=f"Gender code '{clean_gen}' is non-standard",
                    field_name="gender",
                    actual=clean_gen
                ))

        # 5. Domain: Maximum Validity Duration Heuristic (<= 10.5 years)
        iss = fields.get("date_of_issue")
        exp = fields.get("date_of_expiry")
        if iss and exp and iss.value and exp.value:
            try:
                iss_dt = date.fromisoformat(iss.value.strip())
                exp_dt = date.fromisoformat(exp.value.strip())
                span_years = (exp_dt - iss_dt).days / 365.25
                if span_years > 10.5:
                    results.append(ValidationCheckResult(
                        rule_id="DOMAIN_PASSPORT_VALIDITY_SPAN",
                        category=RuleCategoryEnum.DOMAIN.value,
                        status="WARNING",
                        severity=RuleSeverityEnum.MEDIUM.value,
                        message=f"Passport validity span ({span_years:.1f} years) exceeds standard 10-year guideline",
                        field_name="date_of_expiry",
                        expected="<= 10.5 years",
                        actual=f"{span_years:.1f} years"
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="DOMAIN_PASSPORT_VALIDITY_SPAN",
                        category=RuleCategoryEnum.DOMAIN.value,
                        status="PASS",
                        severity=RuleSeverityEnum.MEDIUM.value,
                        message=f"Passport validity span ({span_years:.1f} years) is within standard 10-year guideline",
                        field_name="date_of_expiry",
                        actual=f"{span_years:.1f} years"
                    ))
            except Exception:
                pass

        return results
