"""Field Normalizer & Controlled OCR Error Correction Engine.

Provides:
- Date Normalization into ISO 8601 (YYYY-MM-DD)
- Text and Name Normalization (whitespace collapsing, uppercase normalization)
- Traceable, Pattern-Aware Character Disambiguation (O <-> 0, I <-> 1, S <-> 5)
"""

import re
from typing import Tuple, List, Dict, Any, Optional

MONTH_NAME_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
    "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
    "JUNE": "06", "JULY": "07", "AUGUST": "08", "SEPTEMBER": "09",
    "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12"
}

class FieldNormalizer:
    def __init__(self):
        pass

    def normalize_whitespace(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def normalize_name(self, name_str: Optional[str]) -> Tuple[str, List[Dict[str, Any]]]:
        """Cleans and normalizes personal name strings."""
        if not name_str:
            return "", []
        raw = name_str
        cleaned = re.sub(r"[,\t\n\r]+", " ", raw)
        cleaned = re.sub(r"[^A-Za-z\s\-\']", "", cleaned)
        normalized = self.normalize_whitespace(cleaned).upper()
        
        corrections = []
        if raw != normalized:
            corrections.append({
                "original": raw,
                "normalized": normalized,
                "reason": "name_whitespace_and_punctuation_cleanup"
            })
        return normalized, corrections

    def normalize_date(self, date_str: Optional[str]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Converts varied date strings into standardized ISO 8601 (YYYY-MM-DD)."""
        if not date_str:
            return None, []
            
        raw = str(date_str).strip()
        corrections = []

        # Replace separators
        cleaned = raw.replace("/", "-").replace(".", "-")

        # 1. Standard ISO YYYY-MM-DD
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", cleaned)
        if m:
            iso_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            return iso_date, corrections

        # 2. DD-MM-YYYY or MM-DD-YYYY
        m = re.search(r"(\d{2})-(\d{2})-(\d{4})", cleaned)
        if m:
            v1, v2, yyyy = int(m.group(1)), int(m.group(2)), m.group(3)
            # If v1 > 12, it must be DD-MM-YYYY
            if v1 > 12 and v2 <= 12:
                iso_date = f"{yyyy}-{v2:02d}-{v1:02d}"
            else:
                iso_date = f"{yyyy}-{v2:02d}-{v1:02d}"  # Default DD-MM-YYYY in travel docs
            corrections.append({"original": raw, "normalized": iso_date, "reason": "dmy_to_iso_conversion"})
            return iso_date, corrections

        # 3. DD MON YYYY (e.g. 20 MAY 1999)
        m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", cleaned)
        if m:
            dd, mon_str, yyyy = int(m.group(1)), m.group(2).upper(), m.group(3)
            if mon_str in MONTH_NAME_MAP:
                mm = MONTH_NAME_MAP[mon_str]
                iso_date = f"{yyyy}-{mm}-{dd:02d}"
                corrections.append({"original": raw, "normalized": iso_date, "reason": "text_month_to_iso"})
                return iso_date, corrections

        # 4. MRZ YYMMDD format
        m = re.search(r"^(\d{2})(\d{2})(\d{2})$", cleaned)
        if m:
            yy, mm, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1 <= mm <= 12 and 1 <= dd <= 31:
                century = 1900 if yy >= 40 else 2000
                iso_date = f"{century + yy}-{mm:02d}-{dd:02d}"
                corrections.append({"original": raw, "normalized": iso_date, "reason": "mrz_yymmdd_to_iso"})
                return iso_date, corrections

        return raw, corrections

    def disambiguate_document_number(self, doc_num: Optional[str], doc_type: str = "passport") -> Tuple[str, List[Dict[str, Any]]]:
        """Applies pattern-aware character disambiguation on document numbers."""
        if not doc_num:
            return "", []
        raw = doc_num.strip().upper()
        normalized = raw
        corrections = []

        # For standard passport numbers: 1 letter prefix + 7-8 digits (e.g. P12345678)
        if doc_type == "passport" and len(raw) >= 8:
            prefix = raw[0]
            digits_part = raw[1:]
            new_digits = list(digits_part)
            
            for idx, c in enumerate(digits_part):
                if c == 'O':
                    new_digits[idx] = '0'
                    corrections.append({"position": idx + 1, "from": "O", "to": "0", "reason": "passport_numeric_zone"})
                elif c == 'I':
                    new_digits[idx] = '1'
                    corrections.append({"position": idx + 1, "from": "I", "to": "1", "reason": "passport_numeric_zone"})
                elif c == 'S' and idx > 2:
                    new_digits[idx] = '5'
                    corrections.append({"position": idx + 1, "from": "S", "to": "5", "reason": "passport_numeric_zone"})
                    
            normalized = prefix + "".join(new_digits)

        return normalized, corrections
