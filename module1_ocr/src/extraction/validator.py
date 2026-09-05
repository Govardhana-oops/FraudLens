"""Field Validation & Cross-Field Consistency Engine for AI-DIDSS Module 1.

Implements:
- Format & Pattern Validation (Passport, Visa, DL, ID, Dates, Country codes)
- Chronological Logic (DOB < Issue < Expiry)
- Cross-Field Consistency Checks (Visual text vs MRZ fields)
- Explicit Conflict & Review Flag Generation
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .schema import ExtractedField, CrossFieldConflict, ValidationSummary
from .normalizer import FieldNormalizer

ISO_3166_ALPHA3 = {
    "UTO", "XAN", "ATL", "ELD", "VAL", "ARC", "USA", "GBR", "CAN", "FRA", "DEU", "ITA", "ESP",
    "IND", "AUS", "JPN", "CHN", "BRA", "ZAF", "MEX", "ARG", "NZL", "SGP", "KOR", "NLD", "SWE"
}

class FieldValidator:
    def __init__(self):
        self.normalizer = FieldNormalizer()

    def parse_iso_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    def validate_field(self, field_name: str, field_obj: ExtractedField, doc_type: str) -> ExtractedField:
        """Validates a single field against format and value constraints."""
        val = field_obj.value
        if not val or val == "UNKNOWN":
            field_obj.validation_status = "UNKNOWN"
            return field_obj

        # 1. Date Fields
        if "date" in field_name or field_name in ["date_of_birth", "date_of_expiry", "date_of_issue", "valid_until", "valid_from"]:
            dt = self.parse_iso_date(val)
            if dt:
                field_obj.validation_status = "VALID"
            else:
                field_obj.validation_status = "INVALID"
                field_obj.warnings.append("Date does not adhere to ISO 8601 YYYY-MM-DD")
            return field_obj

        # 2. Nationality & Issuing Country
        if field_name in ["nationality", "issuing_country", "citizenship"]:
            clean_code = re.sub(r"[^A-Z]", "", val.upper())
            if len(clean_code) == 3 and clean_code in ISO_3166_ALPHA3:
                field_obj.validation_status = "VALID"
            elif len(clean_code) == 3:
                field_obj.validation_status = "VALID"  # valid 3-letter format
            else:
                field_obj.validation_status = "VALID" if len(val) >= 3 else "INVALID"
            return field_obj

        # 3. Gender
        if field_name in ["gender", "sex"]:
            if val.upper() in ["M", "F", "U", "MALE", "FEMALE"]:
                field_obj.validation_status = "VALID"
            else:
                field_obj.validation_status = "INVALID"
                field_obj.warnings.append(f"Unexpected gender token: {val}")
            return field_obj

        # 4. Document Numbers
        if "number" in field_name or field_name in ["passport_number", "license_number", "id_number", "permit_number", "visa_number"]:
            if re.match(r"^[A-Z0-9\-\s]{6,20}$", val.upper()):
                field_obj.validation_status = "VALID"
            else:
                field_obj.validation_status = "INVALID"
                field_obj.warnings.append("Document number contains non-standard characters")
            return field_obj

        field_obj.validation_status = "VALID"
        return field_obj

    def validate_chronology(self, fields: Dict[str, ExtractedField]) -> List[str]:
        """Validates chronological relationship: DOB < Issue < Expiry."""
        warnings = []
        dob = self.parse_iso_date(fields.get("date_of_birth", ExtractedField(value="", raw_value="", confidence=0)).value)
        issue = self.parse_iso_date(fields.get("date_of_issue", ExtractedField(value="", raw_value="", confidence=0)).value)
        if not issue:
            issue = self.parse_iso_date(fields.get("issue_date", ExtractedField(value="", raw_value="", confidence=0)).value)
        expiry = self.parse_iso_date(fields.get("date_of_expiry", ExtractedField(value="", raw_value="", confidence=0)).value)
        if not expiry:
            expiry = self.parse_iso_date(fields.get("expiry_date", ExtractedField(value="", raw_value="", confidence=0)).value)

        if dob and issue and dob >= issue:
            warnings.append(f"Chronological anomaly: DOB ({dob.date()}) >= Issue Date ({issue.date()})")
        if issue and expiry and issue >= expiry:
            warnings.append(f"Chronological anomaly: Issue Date ({issue.date()}) >= Expiry Date ({expiry.date()})")
        if dob and expiry and dob >= expiry:
            warnings.append(f"Chronological anomaly: DOB ({dob.date()}) >= Expiry Date ({expiry.date()})")

        return warnings

    def check_cross_field_consistency(self, fields: Dict[str, ExtractedField], mrz_fields: Dict[str, ExtractedField]) -> List[CrossFieldConflict]:
        """Performs strict cross-comparison between visual VIZ fields and MRZ fields."""
        conflicts: List[CrossFieldConflict] = []
        
        # 1. Document Number
        v_doc = fields.get("passport_number") or fields.get("visa_number") or fields.get("id_number")
        m_doc = mrz_fields.get("passport_number") or mrz_fields.get("visa_number") or mrz_fields.get("id_number")
        if v_doc and m_doc and v_doc.value and m_doc.value:
            v_val = re.sub(r"[^A-Z0-9]", "", v_doc.value.upper())
            m_val = re.sub(r"[^A-Z0-9]", "", m_doc.value.upper())
            if v_val != m_val:
                conflicts.append(CrossFieldConflict(
                    field="document_number",
                    status="CONFLICT",
                    visual_value=v_doc.value,
                    mrz_value=m_doc.value,
                    confidence_visual=v_doc.confidence,
                    confidence_mrz=m_doc.confidence,
                    resolution_recommendation="REVIEW_REQUIRED"
                ))

        # 2. Date of Birth
        v_dob = fields.get("date_of_birth")
        m_dob = mrz_fields.get("date_of_birth")
        if v_dob and m_dob and v_dob.value and m_dob.value:
            v_norm, _ = self.normalizer.normalize_date(v_dob.value)
            m_norm, _ = self.normalizer.normalize_date(m_dob.value)
            if v_norm != m_norm:
                conflicts.append(CrossFieldConflict(
                    field="date_of_birth",
                    status="CONFLICT",
                    visual_value=v_norm or v_dob.value,
                    mrz_value=m_norm or m_dob.value,
                    confidence_visual=v_dob.confidence,
                    confidence_mrz=m_dob.confidence,
                    resolution_recommendation="REVIEW_REQUIRED"
                ))

        # 3. Date of Expiry
        v_exp = fields.get("date_of_expiry") or fields.get("expiry_date")
        m_exp = mrz_fields.get("date_of_expiry") or mrz_fields.get("expiry_date")
        if v_exp and m_exp and v_exp.value and m_exp.value:
            v_norm, _ = self.normalizer.normalize_date(v_exp.value)
            m_norm, _ = self.normalizer.normalize_date(m_exp.value)
            if v_norm != m_norm:
                conflicts.append(CrossFieldConflict(
                    field="date_of_expiry",
                    status="CONFLICT",
                    visual_value=v_norm or v_exp.value,
                    mrz_value=m_norm or m_exp.value,
                    confidence_visual=v_exp.confidence,
                    confidence_mrz=m_exp.confidence,
                    resolution_recommendation="REVIEW_REQUIRED"
                ))

        # 4. Nationality
        v_nat = fields.get("nationality")
        m_nat = mrz_fields.get("nationality")
        if v_nat and m_nat and v_nat.value and m_nat.value:
            if v_nat.value[:3].upper() != m_nat.value[:3].upper():
                conflicts.append(CrossFieldConflict(
                    field="nationality",
                    status="CONFLICT",
                    visual_value=v_nat.value,
                    mrz_value=m_nat.value,
                    confidence_visual=v_nat.confidence,
                    confidence_mrz=m_nat.confidence,
                    resolution_recommendation="REVIEW_REQUIRED"
                ))

        return conflicts

    def summarize_validation(self, fields: Dict[str, ExtractedField], conflicts: List[CrossFieldConflict], chrono_warnings: List[str]) -> ValidationSummary:
        valid_cnt = sum(1 for f in fields.values() if f.validation_status == "VALID")
        invalid_cnt = sum(1 for f in fields.values() if f.validation_status == "INVALID")
        unknown_cnt = sum(1 for f in fields.values() if f.validation_status == "UNKNOWN")
        conflict_cnt = len(conflicts)

        all_valid = (invalid_cnt == 0 and conflict_cnt == 0 and len(chrono_warnings) == 0)
        return ValidationSummary(
            all_valid=all_valid,
            valid_fields_count=valid_cnt,
            invalid_fields_count=invalid_cnt,
            unknown_fields_count=unknown_cnt,
            conflict_fields_count=conflict_cnt
        )
