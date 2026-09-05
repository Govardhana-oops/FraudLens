"""Validation Rule Definitions and Canonical Catalog for Module 2.

Classifies all deterministic validation checks across Schema, Date, MRZ,
Consistency, and Document-Specific categories with explicit Authority Tiers.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RuleCategoryEnum(str, Enum):
    SCHEMA = "SCHEMA"
    DATE = "DATE"
    CHRONOLOGY = "CHRONOLOGY"
    MRZ = "MRZ"
    CONSISTENCY = "CONSISTENCY"
    FORMAT = "FORMAT"
    DOMAIN = "DOMAIN"

class RuleSeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class RuleAuthorityTier(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"               # Based on international standard (ICAO, ISO)
    PROJECT_SYNTHETIC_RULE = "PROJECT_SYNTHETIC" # Defined for prototype / synthetic dataset
    HEURISTIC = "HEURISTIC"                       # Sanity check guideline

class ValidationRule(BaseModel):
    rule_id: str
    category: RuleCategoryEnum
    name: str
    description: str
    severity: RuleSeverityEnum
    authority_tier: RuleAuthorityTier = RuleAuthorityTier.AUTHORITATIVE
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    applies_to: list[str] = Field(default_factory=lambda: ["ALL"])
    is_active: bool = True

# Canonical Catalog of Standard Validation Rules
STANDARD_RULE_CATALOG: Dict[str, ValidationRule] = {
    "REQ_FIELD_PRESENCE": ValidationRule(
        rule_id="REQ_FIELD_PRESENCE",
        category=RuleCategoryEnum.SCHEMA,
        name="Mandatory Field Presence",
        description="Verifies mandatory fields exist and are populated per document type",
        severity=RuleSeverityEnum.HIGH,
        authority_tier=RuleAuthorityTier.PROJECT_SYNTHETIC_RULE,
        weight=1.0
    ),
    "DATE_FORMAT_ISO8601": ValidationRule(
        rule_id="DATE_FORMAT_ISO8601",
        category=RuleCategoryEnum.DATE,
        name="ISO 8601 Date Format",
        description="Verifies date string conforms to standard YYYY-MM-DD syntax",
        severity=RuleSeverityEnum.MEDIUM,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=0.75
    ),
    "DATE_CALENDAR_VALIDITY": ValidationRule(
        rule_id="DATE_CALENDAR_VALIDITY",
        category=RuleCategoryEnum.DATE,
        name="Calendar Date Validity",
        description="Verifies calendar bounds (leap years, month 1-12, days 1-31)",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0
    ),
    "CHRONO_DOB_BEFORE_ISSUE": ValidationRule(
        rule_id="CHRONO_DOB_BEFORE_ISSUE",
        category=RuleCategoryEnum.CHRONOLOGY,
        name="Date of Birth Before Issue",
        description="Verifies Date of Birth strictly precedes Date of Issue and DOB <= Today",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0
    ),
    "CHRONO_ISSUE_BEFORE_EXPIRY": ValidationRule(
        rule_id="CHRONO_ISSUE_BEFORE_EXPIRY",
        category=RuleCategoryEnum.CHRONOLOGY,
        name="Issue Date Before Expiry",
        description="Verifies Date of Issue strictly precedes Date of Expiry",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0
    ),
    "CHRONO_EXPIRATION_STATUS": ValidationRule(
        rule_id="CHRONO_EXPIRATION_STATUS",
        category=RuleCategoryEnum.CHRONOLOGY,
        name="Document Expiration Status",
        description="Determines if document has passed its expiration date",
        severity=RuleSeverityEnum.HIGH,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=0.75
    ),
    "MRZ_LINE_GEOMETRY": ValidationRule(
        rule_id="MRZ_LINE_GEOMETRY",
        category=RuleCategoryEnum.MRZ,
        name="MRZ Geometry & Line Length",
        description="Verifies ICAO line lengths (TD1=30, TD2=36, TD3=44, MRV=44)",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "visa", "national_id"]
    ),
    "MRZ_DOC_NUMBER_CHECKSUM": ValidationRule(
        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
        category=RuleCategoryEnum.MRZ,
        name="MRZ Document Number Check Digit",
        description="Recalculates ICAO Modulo-10 7-3-1 check digit on document number",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "visa", "national_id"]
    ),
    "MRZ_DOB_CHECKSUM": ValidationRule(
        rule_id="MRZ_DOB_CHECKSUM",
        category=RuleCategoryEnum.MRZ,
        name="MRZ Date of Birth Check Digit",
        description="Recalculates ICAO Modulo-10 7-3-1 check digit on birth date",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "visa", "national_id"]
    ),
    "MRZ_EXPIRY_CHECKSUM": ValidationRule(
        rule_id="MRZ_EXPIRY_CHECKSUM",
        category=RuleCategoryEnum.MRZ,
        name="MRZ Expiry Date Check Digit",
        description="Recalculates ICAO Modulo-10 7-3-1 check digit on expiry date",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "visa", "national_id"]
    ),
    "MRZ_COMPOSITE_CHECKSUM": ValidationRule(
        rule_id="MRZ_COMPOSITE_CHECKSUM",
        category=RuleCategoryEnum.MRZ,
        name="MRZ Composite Master Check Digit",
        description="Recalculates ICAO Modulo-10 7-3-1 composite master check digit",
        severity=RuleSeverityEnum.CRITICAL,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "national_id"]
    ),
    "CROSS_VISUAL_MRZ_DOC_NUMBER": ValidationRule(
        rule_id="CROSS_VISUAL_MRZ_DOC_NUMBER",
        category=RuleCategoryEnum.CONSISTENCY,
        name="Visual vs MRZ Document Number Match",
        description="Verifies visual zone document number matches MRZ identifier",
        severity=RuleSeverityEnum.HIGH,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "visa", "national_id"]
    ),
    "CROSS_VISUAL_MRZ_NATIONALITY": ValidationRule(
        rule_id="CROSS_VISUAL_MRZ_NATIONALITY",
        category=RuleCategoryEnum.CONSISTENCY,
        name="Visual vs MRZ Country Code Match",
        description="Verifies visual nationality matches MRZ ISO country code",
        severity=RuleSeverityEnum.HIGH,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=0.75,
        applies_to=["passport", "visa", "national_id"]
    ),
    "CROSS_VISUAL_MRZ_EXPIRY": ValidationRule(
        rule_id="CROSS_VISUAL_MRZ_EXPIRY",
        category=RuleCategoryEnum.CONSISTENCY,
        name="Visual vs MRZ Expiry Match",
        description="Verifies visual expiration date matches MRZ expiry date",
        severity=RuleSeverityEnum.HIGH,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=1.0,
        applies_to=["passport", "visa", "national_id"]
    ),
    "FORMAT_COUNTRY_ISO3": ValidationRule(
        rule_id="FORMAT_COUNTRY_ISO3",
        category=RuleCategoryEnum.FORMAT,
        name="ISO 3166-1 Country Code Validity",
        description="Verifies 3-letter country code exists in ISO 3166-1 dictionary",
        severity=RuleSeverityEnum.MEDIUM,
        authority_tier=RuleAuthorityTier.AUTHORITATIVE,
        weight=0.50
    ),
    "FORMAT_PASSPORT_NUMBER_SYNTAX": ValidationRule(
        rule_id="FORMAT_PASSPORT_NUMBER_SYNTAX",
        category=RuleCategoryEnum.FORMAT,
        name="Passport Number Alphanumeric Syntax",
        description="Verifies passport number conforms to alphanumeric syntax",
        severity=RuleSeverityEnum.MEDIUM,
        authority_tier=RuleAuthorityTier.PROJECT_SYNTHETIC_RULE,
        weight=0.50,
        applies_to=["passport"]
    ),
    "FORMAT_DRIVER_LICENSE_SYNTAX": ValidationRule(
        rule_id="FORMAT_DRIVER_LICENSE_SYNTAX",
        category=RuleCategoryEnum.FORMAT,
        name="Driver License Number Syntax",
        description="Verifies driver license number conforms to alphanumeric format",
        severity=RuleSeverityEnum.MEDIUM,
        authority_tier=RuleAuthorityTier.PROJECT_SYNTHETIC_RULE,
        weight=0.50,
        applies_to=["driver_license"]
    ),
    "DOMAIN_PASSPORT_VALIDITY_SPAN": ValidationRule(
        rule_id="DOMAIN_PASSPORT_VALIDITY_SPAN",
        category=RuleCategoryEnum.DOMAIN,
        name="Passport Validity Duration Bounds",
        description="Checks that passport validity span does not exceed 10.5 years",
        severity=RuleSeverityEnum.MEDIUM,
        authority_tier=RuleAuthorityTier.HEURISTIC,
        weight=0.50,
        applies_to=["passport"]
    ),
    "DOMAIN_DL_MINIMUM_AGE": ValidationRule(
        rule_id="DOMAIN_DL_MINIMUM_AGE",
        category=RuleCategoryEnum.DOMAIN,
        name="Driver License Minimum Operating Age",
        description="Checks bearer age at issuance meets minimum driving threshold",
        severity=RuleSeverityEnum.HIGH,
        authority_tier=RuleAuthorityTier.HEURISTIC,
        weight=0.75,
        applies_to=["driver_license"]
    ),
    "DOMAIN_PERMIT_CATEGORY_VALIDITY": ValidationRule(
        rule_id="DOMAIN_PERMIT_CATEGORY_VALIDITY",
        category=RuleCategoryEnum.DOMAIN,
        name="Permit Category Authorization",
        description="Checks permit category against authorized immigration classifications",
        severity=RuleSeverityEnum.LOW,
        authority_tier=RuleAuthorityTier.PROJECT_SYNTHETIC_RULE,
        weight=0.50,
        applies_to=["permit"]
    )
}
