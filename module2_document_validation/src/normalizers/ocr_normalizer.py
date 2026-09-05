"""OCR-Noise Normalization Engine for Module 2.

Implements controlled, deterministic, traceable, and reversible normalization
of extracted optical character fields prior to rule validation.

Key Principles:
1. Field-Specific Rules: Dates, identifiers, names, and country codes receive tailored transforms.
2. Traceability: Original raw OCR text is strictly preserved in audit records.
3. Safety: Character repairs on ambiguous inputs are tracked and explainable.
4. Unicode Hygiene: Normalizes invisible control characters and NFC/NFKC variants.
"""

import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class FieldNormalizationRecord:
    field_name: str
    original_value: str
    normalized_value: str
    transformations: List[str] = field(default_factory=list)
    ambiguity_detected: bool = False
    ambiguity_details: Optional[str] = None
    confidence_impact: float = 0.0

@dataclass
class NormalizationResult:
    normalized_fields: Dict[str, Any]
    records: Dict[str, FieldNormalizationRecord]
    has_ambiguities: bool = False
    warnings: List[str] = field(default_factory=list)

class OCRNormalizer:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Controlled character confusion maps for numeric-only contexts
        self.numeric_confusion_map = {
            'O': '0', 'o': '0', 'Q': '0', 'D': '0',
            'I': '1', 'l': '1', 'i': '1', '|': '1', '!': '1',
            'Z': '2', 'z': '2',
            'E': '3',
            'A': '4',
            'S': '5', 's': '5', '$': '5',
            'G': '6', 'b': '6',
            'T': '7',
            'B': '8', '&': '8',
            'g': '9', 'q': '9'
        }

        self.date_fields = {
            "date_of_birth", "dob", "date_of_issue", "issue_date",
            "date_of_expiry", "expiry_date", "valid_until"
        }

        self.identifier_fields = {
            "passport_number", "visa_number", "license_number",
            "id_number", "permit_number", "document_number"
        }

        self.country_fields = {
            "nationality", "country", "issuing_country", "country_code"
        }

        self.name_fields = {
            "full_name", "surname", "given_names", "first_name", "last_name"
        }

    def _clean_unicode_and_whitespace(self, text: str) -> Tuple[str, List[str]]:
        """Cleans invisible unicode control chars, tabs, newlines, and compresses spaces."""
        transforms = []
        if not text or str(text).strip().upper() in ["NONE", "NULL", "UNKNOWN"]:
            return "", transforms

        # 1. Unicode NFKC normalization
        norm_text = unicodedata.normalize('NFKC', text)
        if norm_text != text:
            transforms.append("UNICODE_NFKC_NORMALIZATION")

        # 2. Strip invisible control characters (except standard space)
        clean_text = "".join(ch for ch in norm_text if unicodedata.category(ch)[0] != "C" or ch == " ")
        if clean_text != norm_text:
            transforms.append("STRIP_CONTROL_CHARACTERS")

        # 3. Normalize multiple whitespace and newlines to single space
        compact_text = re.sub(r"\s+", " ", clean_text).strip()
        if compact_text != clean_text:
            transforms.append("COMPACT_WHITESPACE")

        return compact_text, transforms

    def normalize_date_field(self, raw_val: str) -> Tuple[str, List[str], bool, Optional[str]]:
        """Normalizes date string formats (e.g. YYYY/MM/DD, YYYY.MM.DD -> YYYY-MM-DD)."""
        transforms = []
        ambiguity = False
        ambiguity_msg = None

        text, ws_transforms = self._clean_unicode_and_whitespace(raw_val)
        transforms.extend(ws_transforms)

        if not text:
            return "", transforms, False, None

        # Standard ISO format: YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
            return text, transforms, False, None

        # Alternative separators: YYYY/MM/DD, YYYY.MM.DD, YYYY MM DD
        alt_match = re.match(r"^(\d{4})[./\s](\d{2})[./\s](\d{2})$", text)
        if alt_match:
            standardized = f"{alt_match.group(1)}-{alt_match.group(2)}-{alt_match.group(3)}"
            transforms.append("STANDARDIZE_DATE_SEPARATORS_ISO8601")
            return standardized, transforms, False, None

        # OCR character confusion repair in numeric date components (e.g. 2O25-O8-12 -> 2025-08-12)
        if re.match(r"^[0-9A-Za-z]{4}[-./\s][0-9A-Za-z]{2}[-./\s][0-9A-Za-z]{2}$", text):
            repaired_chars = []
            char_subs = 0
            for ch in text:
                if ch in "-./ ":
                    repaired_chars.append("-")
                elif ch.isdigit():
                    repaired_chars.append(ch)
                elif ch in self.numeric_confusion_map:
                    repaired_chars.append(self.numeric_confusion_map[ch])
                    char_subs += 1
                else:
                    repaired_chars.append(ch)
            
            repaired_date = "".join(repaired_chars)
            if re.match(r"^\d{4}-\d{2}-\d{2}$", repaired_date) and char_subs > 0:
                transforms.append(f"DISAMBIGUATE_NUMERIC_DATE_CHARS ({char_subs} substitutions)")
                ambiguity = True
                ambiguity_msg = f"Date OCR characters repaired from '{text}' to '{repaired_date}'"
                return repaired_date, transforms, ambiguity, ambiguity_msg

        return text, transforms, False, None

    def normalize_identifier_field(self, raw_val: str) -> Tuple[str, List[str], bool, Optional[str]]:
        """Normalizes document numbers, license numbers, permit numbers."""
        transforms = []
        ambiguity = False
        ambiguity_msg = None

        text, ws_transforms = self._clean_unicode_and_whitespace(raw_val)
        transforms.extend(ws_transforms)

        if not text:
            return "", transforms, False, None

        # Remove internal spaces in document numbers (e.g. "P 1234 5678" -> "P12345678")
        clean_id = text.replace(" ", "").upper()
        if clean_id != text:
            transforms.append("STRIP_INTERNAL_WHITESPACE")
        if clean_id != text.upper():
            transforms.append("UPPERCASE_IDENTIFIER")

        return clean_id, transforms, False, None

    def normalize_country_field(self, raw_val: str) -> Tuple[str, List[str], bool, Optional[str]]:
        """Normalizes 3-letter ISO country codes."""
        transforms = []
        text, ws_transforms = self._clean_unicode_and_whitespace(raw_val)
        transforms.extend(ws_transforms)

        clean_country = text.replace(" ", "").upper()
        if clean_country != text:
            transforms.append("STRIP_WHITESPACE")
        if text != text.upper():
            transforms.append("UPPERCASE_COUNTRY_CODE")

        return clean_country, transforms, False, None

    def normalize_name_field(self, raw_val: str) -> Tuple[str, List[str], bool, Optional[str]]:
        """Normalizes bearer personal names (preserves international accents and hyphens)."""
        transforms = []
        text, ws_transforms = self._clean_unicode_and_whitespace(raw_val)
        transforms.extend(ws_transforms)

        clean_name = text.upper()
        if clean_name != text:
            transforms.append("UPPERCASE_NAME")

        return clean_name, transforms, False, None

    def normalize_field(self, field_name: str, raw_val: str) -> FieldNormalizationRecord:
        """Normalizes a single field according to its semantic category."""
        fname_lower = field_name.lower()

        if fname_lower in self.date_fields:
            norm_val, transforms, ambig, ambig_msg = self.normalize_date_field(raw_val)
        elif fname_lower in self.identifier_fields:
            norm_val, transforms, ambig, ambig_msg = self.normalize_identifier_field(raw_val)
        elif fname_lower in self.country_fields:
            norm_val, transforms, ambig, ambig_msg = self.normalize_country_field(raw_val)
        elif fname_lower in self.name_fields:
            norm_val, transforms, ambig, ambig_msg = self.normalize_name_field(raw_val)
        else:
            norm_val, transforms = self._clean_unicode_and_whitespace(raw_val)
            ambig, ambig_msg = False, None

        return FieldNormalizationRecord(
            field_name=field_name,
            original_value=raw_val,
            normalized_value=norm_val,
            transformations=transforms,
            ambiguity_detected=ambig,
            ambiguity_details=ambig_msg
        )

    def normalize_payload_fields(self, fields: Dict[str, Any]) -> NormalizationResult:
        """Applies field-specific normalization across all extracted fields in payload."""
        normalized_dict = {}
        records: Dict[str, FieldNormalizationRecord] = {}
        warnings: List[str] = []
        has_ambig = False

        for k, v in fields.items():
            if hasattr(v, "value"):
                raw_str = str(v.value or "")
                rec = self.normalize_field(k, raw_str)
                records[k] = rec
                
                # Clone field with normalized value while preserving raw_value
                v.raw_value = raw_str
                v.value = rec.normalized_value
                if rec.transformations:
                    v.corrections.extend(rec.transformations)
                if rec.ambiguity_detected:
                    has_ambig = True
                    warnings.append(f"[{k}] {rec.ambiguity_details}")
                normalized_dict[k] = v
            elif isinstance(v, dict):
                raw_str = str(v.get("value", "") or "")
                rec = self.normalize_field(k, raw_str)
                records[k] = rec
                v_copy = dict(v)
                v_copy["raw_value"] = raw_str
                v_copy["value"] = rec.normalized_value
                if rec.ambiguity_detected:
                    has_ambig = True
                    warnings.append(f"[{k}] {rec.ambiguity_details}")
                normalized_dict[k] = v_copy
            else:
                raw_str = str(v or "")
                rec = self.normalize_field(k, raw_str)
                records[k] = rec
                normalized_dict[k] = rec.normalized_value

        return NormalizationResult(
            normalized_fields=normalized_dict,
            records=records,
            has_ambiguities=has_ambig,
            warnings=warnings
        )
