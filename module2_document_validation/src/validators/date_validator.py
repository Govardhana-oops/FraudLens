"""Date and Chronological Validator for Module 2.

Handles:
- ISO 8601 YYYY-MM-DD syntax validation
- Strict calendar validity (leap years, month bounds, impossible days)
- Expiration status evaluation relative to reference verification date
- Temporal chronology constraints (DOB < Issue <= Expiry)
"""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class DateValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None, reference_date: Optional[date] = None):
        super().__init__(config)
        # Default reference date for verification
        self.reference_date = reference_date or date(2026, 9, 2)
        self.date_fields = [
            "date_of_birth", "dob",
            "date_of_issue", "issue_date",
            "date_of_expiry", "expiry_date", "valid_until"
        ]

    def _parse_and_validate_date(self, date_str: str) -> Tuple[bool, Optional[date], str]:
        """Parses date string and validates calendar accuracy."""
        if not date_str or not isinstance(date_str, str):
            return False, None, "Empty or invalid date type"

        clean_str = date_str.strip()
        
        # Regex for YYYY-MM-DD
        iso_match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", clean_str)
        if not iso_match:
            return False, None, f"Date '{clean_str}' does not conform to ISO 8601 (YYYY-MM-DD)"

        year, month, day = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))

        if month < 1 or month > 12:
            return False, None, f"Month '{month}' is outside valid calendar range [1, 12]"

        try:
            parsed_d = date(year, month, day)
            return True, parsed_d, "Valid calendar date"
        except ValueError as ve:
            return False, None, f"Invalid calendar day for month {month}: {str(ve)}"

    def validate(self, payload: Module1InputPayload) -> List[ValidationCheckResult]:
        results: List[ValidationCheckResult] = []
        fields = payload.fields
        extracted_dates: Dict[str, date] = {}

        # 1. Format & Calendar Validity for each extracted date field
        for field_name in self.date_fields:
            if field_name in fields:
                f_obj = fields[field_name]
                raw_val = f_obj.value

                if not raw_val or raw_val.upper() in ["UNKNOWN", "NONE", "NULL"]:
                    results.append(ValidationCheckResult(
                        rule_id="DATE_FORMAT_ISO8601",
                        category=RuleCategoryEnum.DATE.value,
                        status="UNKNOWN",
                        severity=RuleSeverityEnum.MEDIUM.value,
                        message=f"Field '{field_name}' is unextracted or unknown in Module 1 OCR",
                        field_name=field_name,
                        actual=raw_val
                    ))
                    continue

                is_valid, parsed_dt, reason = self._parse_and_validate_date(raw_val)

                if is_valid and parsed_dt:
                    extracted_dates[field_name] = parsed_dt
                    results.append(ValidationCheckResult(
                        rule_id="DATE_CALENDAR_VALIDITY",
                        category=RuleCategoryEnum.DATE.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Date '{field_name}' is a valid calendar date ({parsed_dt.isoformat()})",
                        field_name=field_name,
                        actual=raw_val
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="DATE_CALENDAR_VALIDITY",
                        category=RuleCategoryEnum.DATE.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Date '{field_name}' failed calendar validation: {reason}",
                        field_name=field_name,
                        actual=raw_val
                    ))

        # 2. Expiration Status Check (for expiry_date / date_of_expiry / valid_until)
        expiry_dt = extracted_dates.get("date_of_expiry") or extracted_dates.get("expiry_date") or extracted_dates.get("valid_until")
        if expiry_dt:
            if expiry_dt < self.reference_date:
                days_expired = (self.reference_date - expiry_dt).days
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_EXPIRATION_STATUS",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="FAIL",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Document has expired (Expired {days_expired} days ago on {expiry_dt.isoformat()})",
                    field_name="date_of_expiry",
                    expected=f">= {self.reference_date.isoformat()}",
                    actual=expiry_dt.isoformat(),
                    details={"is_expired": True, "days_expired": days_expired}
                ))
            else:
                days_remaining = (expiry_dt - self.reference_date).days
                msg = f"Document is currently valid ({days_remaining} days remaining until {expiry_dt.isoformat()})"
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_EXPIRATION_STATUS",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="PASS",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=msg,
                    field_name="date_of_expiry",
                    expected=f">= {self.reference_date.isoformat()}",
                    actual=expiry_dt.isoformat(),
                    details={"is_expired": False, "days_remaining": days_remaining}
                ))

        # 3. Chronology: Date of Birth in the Past
        dob_dt = extracted_dates.get("date_of_birth") or extracted_dates.get("dob")
        if dob_dt:
            if dob_dt > self.reference_date:
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_DOB_BEFORE_ISSUE",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="FAIL",
                    severity=RuleSeverityEnum.CRITICAL.value,
                    message=f"Date of birth ({dob_dt.isoformat()}) is in the future relative to verification date",
                    field_name="date_of_birth",
                    expected=f"<= {self.reference_date.isoformat()}",
                    actual=dob_dt.isoformat()
                ))
            elif dob_dt.year < 1900:
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_DOB_BEFORE_ISSUE",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="WARNING",
                    severity=RuleSeverityEnum.MEDIUM.value,
                    message=f"Date of birth ({dob_dt.isoformat()}) indicates age > 125 years",
                    field_name="date_of_birth",
                    actual=dob_dt.isoformat()
                ))

        # 4. Chronology: DOB < Issue Date
        issue_dt = extracted_dates.get("date_of_issue") or extracted_dates.get("issue_date")
        if dob_dt and issue_dt:
            if issue_dt <= dob_dt:
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_DOB_BEFORE_ISSUE",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="FAIL",
                    severity=RuleSeverityEnum.CRITICAL.value,
                    message=f"Document issue date ({issue_dt.isoformat()}) occurs on or before date of birth ({dob_dt.isoformat()})",
                    expected=f"> {dob_dt.isoformat()}",
                    actual=issue_dt.isoformat()
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_DOB_BEFORE_ISSUE",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="PASS",
                    severity=RuleSeverityEnum.CRITICAL.value,
                    message=f"Chronology valid: Date of birth ({dob_dt.isoformat()}) precedes issue date ({issue_dt.isoformat()})",
                    expected=f"> {dob_dt.isoformat()}",
                    actual=issue_dt.isoformat()
                ))

        # 5. Chronology: Issue Date <= Expiry Date
        if issue_dt and expiry_dt:
            if issue_dt > expiry_dt:
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_ISSUE_BEFORE_EXPIRY",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="FAIL",
                    severity=RuleSeverityEnum.CRITICAL.value,
                    message=f"Issue date ({issue_dt.isoformat()}) occurs after expiry date ({expiry_dt.isoformat()})",
                    expected=f"<= {expiry_dt.isoformat()}",
                    actual=issue_dt.isoformat()
                ))
            else:
                results.append(ValidationCheckResult(
                    rule_id="CHRONO_ISSUE_BEFORE_EXPIRY",
                    category=RuleCategoryEnum.CHRONOLOGY.value,
                    status="PASS",
                    severity=RuleSeverityEnum.CRITICAL.value,
                    message=f"Chronology valid: Issue date ({issue_dt.isoformat()}) precedes expiry date ({expiry_dt.isoformat()})",
                    expected=f"<= {expiry_dt.isoformat()}",
                    actual=issue_dt.isoformat()
                ))

        return results
