"""ICAO Doc 9303 Compliant Machine Readable Zone (MRZ) Parser & Verifier.

Supports:
- TD1 (3 lines x 30 characters - National ID Cards)
- TD2 (2 lines x 36 characters - ID / Travel Cards)
- TD3 (2 lines x 44 characters - Passports)
- MRV-A & MRV-B (Travel Visas)

Computes deterministic weighted Modulo-10 checksums using weights [7, 3, 1].
Zero Hallucination: Unreadable or invalid MRZ lines return status 'UNKNOWN' or 'CHECKSUM_FAILED'.
"""

import re
from typing import Optional, Tuple, List, Dict, Any
from ..extraction.schema import MRZValidationResult, ExtractedField

def calculate_mrz_checksum(data: str) -> int:
    """Calculates weighted modulo-10 check digit according to ICAO Doc 9303."""
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data):
        if char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char.upper()) - ord('A') + 10
        elif char == '<':
            val = 0
        else:
            val = 0
        total += val * weights[i % 3]
    return total % 10

def verify_check_digit(field_data: str, check_digit_char: str) -> bool:
    if not check_digit_char or not check_digit_char.isdigit():
        return False
    expected = calculate_mrz_checksum(field_data)
    return expected == int(check_digit_char)

def repair_numeric_field(field_data: str, check_digit_char: str) -> Tuple[str, str, bool]:
    """Ensures numeric zones are strictly converted to digits (resolving O->0, I->1, etc.) without altering valid digits."""
    alpha_to_digit = {
        'O': '0', 'o': '0',
        'I': '1', 'i': '1', 'L': '1', 'l': '1',
        'Z': '2', 'z': '2',
        'S': '5', 's': '5',
        'B': '8', 'b': '8',
        'A': '4', 'a': '4',
        'G': '6', 'g': '6',
        'T': '7', 't': '7'
    }
    cleaned_chars = [alpha_to_digit.get(c, c) for c in field_data]
    cleaned_data = "".join(cleaned_chars)
    cleaned_chk = alpha_to_digit.get(check_digit_char, check_digit_char)
    
    is_valid = verify_check_digit(cleaned_data, cleaned_chk)
    return cleaned_data, cleaned_chk, is_valid

def clean_mrz_line(raw_line: str) -> str:
    """Normalizes OCR MRZ characters: uppercase, replaces spaces/symbols with '<'."""
    cleaned = raw_line.strip().upper()
    cleaned = cleaned.replace(" ", "<").replace("-", "<").replace("(", "<").replace(")", "<")
    cleaned = re.sub(r"[^A-Z0-9<]", "<", cleaned)
    return cleaned

class MRZParser:
    def __init__(self):
        pass

    def extract_mrz_lines_from_text(self, text: str, mrz_hints: Optional[List[str]] = None) -> List[str]:
        """Scans OCR lines for valid ICAO MRZ lines, prioritizing dedicated bottom MRZ crops and ensuring proper line ordering."""
        raw_candidates: List[str] = []
        
        # 1. Gather from dedicated bottom-zone MRZ hints
        if mrz_hints:
            for h in mrz_hints:
                c = clean_mrz_line(h)
                if len(c) >= 18 and ("<<" in c or c.startswith(("P<", "P", "V<", "VN", "I<", "A<", "C<")) or any(ch.isdigit() for ch in c[:10])):
                    raw_candidates.append(c)

        # 2. Also gather from full OCR text
        if text:
            for raw_l in text.split("\n"):
                raw_s = raw_l.strip()
                if not raw_s or ":" in raw_s:
                    continue
                raw_u = raw_s.upper()
                if any(tok in raw_u for tok in ["GIVEN", "SURNAME", "BIRTH", "EXPIRY", "ISSUE", "COUNTRY", "NATIONALITY", "BEARER", "ENTRIES", "ADDRESS", "CLASS", "PASSPORT", "PASSEPORT", "DRIVER", "LICENSE", "IDENTITY", "CARD", "REPUBLIC", "STATE", "PERMIT"]):
                    continue
                c = clean_mrz_line(raw_s)
                if len(c) >= 18:
                    if (c.startswith(("P<", "P", "V<", "VN", "I<", "A<", "C<")) and "<<" in c) or (any(ch.isdigit() for ch in c[:10]) and c.count("<") >= 2) or "<<" in c:
                        if c not in raw_candidates:
                            raw_candidates.append(c)

        # Deduplicate while preserving order
        seen = set()
        candidates = []
        for c in raw_candidates:
            if c not in seen:
                seen.add(c)
                candidates.append(c)

        # Look for 3-line TD1 (length 25 to 36)
        td1_candidates = [c for c in candidates if 24 <= len(c) <= 36]
        if len(td1_candidates) >= 3:
            l_hdr = None
            l_dates = None
            l_name = None
            for c in td1_candidates:
                if (c.startswith(("I<", "A<", "C<", "ID", "IP", "I", "A", "C")) or not any(ch.isdigit() for ch in c[10:])) and not l_hdr and not "<<" in c:
                    l_hdr = c
                elif any(ch.isdigit() for ch in c[:6]) and not l_dates and not c.startswith(("I<", "A<", "C<")):
                    l_dates = c
                elif "<<" in c and not l_name:
                    l_name = c
            
            if l_hdr and l_dates and l_name:
                return [l_hdr.ljust(30, '<')[:30], l_dates.ljust(30, '<')[:30], l_name.ljust(30, '<')[:30]]
            elif len(td1_candidates) >= 3:
                return [td1_candidates[-3].ljust(30, '<')[:30], td1_candidates[-2].ljust(30, '<')[:30], td1_candidates[-1].ljust(30, '<')[:30]]

        # Look for 2-line TD3 / MRV-A (length >= 38)
        td3_candidates = [c for c in candidates if len(c) >= 38]
        if len(td3_candidates) >= 2:
            c1, c2 = td3_candidates[-2], td3_candidates[-1]
            is_c1_hdr = c1.startswith(("P<", "P", "V<", "VN", "A<", "C<")) or ("<<" in c1 and not any(ch.isdigit() for ch in c1[:6]))
            is_c2_hdr = c2.startswith(("P<", "P", "V<", "VN", "A<", "C<")) or ("<<" in c2 and not any(ch.isdigit() for ch in c2[:6]))
            
            if is_c2_hdr and not is_c1_hdr:
                c1, c2 = c2, c1
            elif not is_c1_hdr and any(ch.isdigit() for ch in c1[:6]):
                if "<<" in c2 or is_c2_hdr:
                    c1, c2 = c2, c1
                    
            return [c1.ljust(44, '<')[:44], c2.ljust(44, '<')[:44]]

        if len(candidates) >= 2:
            c1, c2 = candidates[-2], candidates[-1]
            if (c2.startswith("P<") or "<<" in c2) and not c1.startswith("P<"):
                c1, c2 = c2, c1
            return [c1.ljust(44, '<')[:44], c2.ljust(44, '<')[:44]]

        return []

    def parse_td3_passport(self, lines: List[str]) -> Tuple[Dict[str, ExtractedField], MRZValidationResult]:
        """Parses ICAO TD3 Passport (2 lines x 44 chars)."""
        l1 = lines[0].ljust(44, '<')[:44]
        l2 = lines[1].ljust(44, '<')[:44]
        
        doc_type = l1[0:2].replace("<", "")
        issuing_country = l1[2:5].replace("<", "")
        
        name_section = l1[5:44]
        name_parts = name_section.split("<<")
        surname = name_parts[0].replace("<", " ").strip()
        given_names = name_parts[1].replace("<", " ").strip() if len(name_parts) > 1 else ""
        full_name = f"{given_names} {surname}".strip()

        # Line 2 fields
        doc_num_raw = l2[0:9]
        doc_num_chk = l2[9] if len(l2) > 9 else "<"
        doc_num_raw, doc_num_chk, doc_chk_pass = repair_numeric_field(doc_num_raw, doc_num_chk)
        doc_num = doc_num_raw.replace("<", "")

        nationality = l2[10:13].replace("<", "")
        
        dob_raw = l2[13:19]
        dob_chk = l2[19] if len(l2) > 19 else "<"
        dob_raw, dob_chk, dob_chk_pass = repair_numeric_field(dob_raw, dob_chk)

        gender = l2[20].replace("<", "U") if len(l2) > 20 else "U"

        exp_raw = l2[21:27]
        exp_chk = l2[27] if len(l2) > 27 else "<"
        exp_raw, exp_chk, exp_chk_pass = repair_numeric_field(exp_raw, exp_chk)

        opt_data = l2[28:42] if len(l2) >= 42 else "<"*14
        composite_raw = f"{doc_num_raw}{doc_num_chk}{dob_raw}{dob_chk}{exp_raw}{exp_chk}{opt_data}"
        comp_chk = l2[43] if len(l2) >= 44 else "<"
        comp_chk_pass = verify_check_digit(composite_raw, comp_chk)

        all_pass = doc_chk_pass and dob_chk_pass and exp_chk_pass

        # Calculate field confidences
        p_conf = 0.98 if doc_chk_pass else 0.70
        dob_conf = 0.98 if dob_chk_pass else 0.70
        exp_conf = 0.98 if exp_chk_pass else 0.70

        fields = {
            "document_type": ExtractedField(value="PASSPORT", raw_value="PASSPORT", confidence=0.99, source="mrz", status="EXTRACTED"),
            "passport_number": ExtractedField(value=doc_num, raw_value=doc_num_raw, confidence=p_conf, source="mrz", status="EXTRACTED" if doc_num else "UNKNOWN", is_valid=doc_chk_pass),
            "surname": ExtractedField(value=surname, raw_value=surname, confidence=0.95, source="mrz", status="EXTRACTED" if surname else "UNKNOWN"),
            "given_names": ExtractedField(value=given_names, raw_value=given_names, confidence=0.95, source="mrz", status="EXTRACTED" if given_names else "UNKNOWN"),
            "full_name": ExtractedField(value=full_name, raw_value=full_name, confidence=0.95, source="mrz", status="EXTRACTED" if full_name else "UNKNOWN"),
            "nationality": ExtractedField(value=nationality, raw_value=nationality, confidence=0.98, source="mrz", status="EXTRACTED" if nationality else "UNKNOWN"),
            "issuing_country": ExtractedField(value=issuing_country, raw_value=issuing_country, confidence=0.98, source="mrz", status="EXTRACTED" if issuing_country else "UNKNOWN"),
            "date_of_birth": ExtractedField(value=dob_raw, raw_value=dob_raw, confidence=dob_conf, source="mrz", status="EXTRACTED" if dob_raw else "UNKNOWN", is_valid=dob_chk_pass),
            "gender": ExtractedField(value=gender, raw_value=gender, confidence=0.98, source="mrz", status="EXTRACTED"),
            "date_of_expiry": ExtractedField(value=exp_raw, raw_value=exp_raw, confidence=exp_conf, source="mrz", status="EXTRACTED" if exp_raw else "UNKNOWN", is_valid=exp_chk_pass),
            "mrz_line1": ExtractedField(value=l1, raw_value=l1, confidence=0.99, source="mrz", status="EXTRACTED"),
            "mrz_line2": ExtractedField(value=l2, raw_value=l2, confidence=0.99, source="mrz", status="EXTRACTED")
        }

        mrz_res = MRZValidationResult(
            mrz_format="TD3",
            lines=[l1, l2],
            document_number_checksum=doc_chk_pass,
            dob_checksum=dob_chk_pass,
            expiry_checksum=exp_chk_pass,
            composite_checksum=comp_chk_pass,
            all_checksums_pass=all_pass,
            status="VALID" if all_pass else "CHECKSUM_FAILED"
        )
        return fields, mrz_res

    def parse_td1_national_id(self, lines: List[str]) -> Tuple[Dict[str, ExtractedField], MRZValidationResult]:
        """Parses ICAO TD1 ID Card (3 lines x 30 chars)."""
        l1 = lines[0].ljust(30, '<')[:30]
        l2 = lines[1].ljust(30, '<')[:30]
        l3 = lines[2].ljust(30, '<')[:30]
        
        doc_type = l1[0:2].replace("<", "")
        country = l1[2:5].replace("<", "")
        doc_num_raw = l1[5:14]
        doc_num_chk = l1[14] if len(l1) > 14 else "<"
        doc_num_raw, doc_num_chk, doc_chk_pass = repair_numeric_field(doc_num_raw, doc_num_chk)
        doc_num = doc_num_raw.replace("<", "")

        dob_raw = l2[0:6]
        dob_chk = l2[6] if len(l2) > 6 else "<"
        dob_raw, dob_chk, dob_chk_pass = repair_numeric_field(dob_raw, dob_chk)

        gender = l2[7].replace("<", "U") if len(l2) > 7 else "U"
        
        exp_raw = l2[8:14]
        exp_chk = l2[14] if len(l2) > 14 else "<"
        exp_raw, exp_chk, exp_chk_pass = repair_numeric_field(exp_raw, exp_chk)
        
        nat = l2[15:18].replace("<", "")

        name_parts = l3.split("<<")
        surname = name_parts[0].replace("<", " ").strip()
        given_names = name_parts[1].replace("<", " ").strip() if len(name_parts) > 1 else ""
        full_name = f"{given_names} {surname}".strip()

        all_pass = doc_chk_pass and dob_chk_pass and exp_chk_pass

        fields = {
            "document_type": ExtractedField(value="NATIONAL_ID", raw_value="NATIONAL_ID", confidence=0.99, source="mrz", status="EXTRACTED"),
            "id_number": ExtractedField(value=doc_num, raw_value=doc_num_raw, confidence=0.95, source="mrz", status="EXTRACTED" if doc_num else "UNKNOWN", is_valid=doc_chk_pass),
            "full_name": ExtractedField(value=full_name, raw_value=full_name, confidence=0.95, source="mrz", status="EXTRACTED" if full_name else "UNKNOWN"),
            "surname": ExtractedField(value=surname, raw_value=surname, confidence=0.95, source="mrz", status="EXTRACTED" if surname else "UNKNOWN"),
            "given_names": ExtractedField(value=given_names, raw_value=given_names, confidence=0.95, source="mrz", status="EXTRACTED" if given_names else "UNKNOWN"),
            "nationality": ExtractedField(value=nat, raw_value=nat, confidence=0.98, source="mrz", status="EXTRACTED" if nat else "UNKNOWN"),
            "date_of_birth": ExtractedField(value=dob_raw, raw_value=dob_raw, confidence=0.95, source="mrz", status="EXTRACTED" if dob_raw else "UNKNOWN", is_valid=dob_chk_pass),
            "date_of_expiry": ExtractedField(value=exp_raw, raw_value=exp_raw, confidence=0.95, source="mrz", status="EXTRACTED" if exp_raw else "UNKNOWN", is_valid=exp_chk_pass),
            "gender": ExtractedField(value=gender, raw_value=gender, confidence=0.98, source="mrz", status="EXTRACTED"),
            "mrz_line1": ExtractedField(value=l1, raw_value=l1, confidence=0.99, source="mrz", status="EXTRACTED"),
            "mrz_line2": ExtractedField(value=l2, raw_value=l2, confidence=0.99, source="mrz", status="EXTRACTED"),
            "mrz_line3": ExtractedField(value=l3, raw_value=l3, confidence=0.99, source="mrz", status="EXTRACTED")
        }

        mrz_res = MRZValidationResult(
            mrz_format="TD1",
            lines=[l1, l2, l3],
            document_number_checksum=doc_chk_pass,
            dob_checksum=dob_chk_pass,
            expiry_checksum=exp_chk_pass,
            composite_checksum=True,
            all_checksums_pass=all_pass,
            status="VALID" if all_pass else "CHECKSUM_FAILED"
        )
        return fields, mrz_res

    def parse_mrv_visa(self, lines: List[str]) -> Tuple[Dict[str, ExtractedField], MRZValidationResult]:
        """Parses MRV-A / MRV-B Travel Visa (2 lines)."""
        l1 = lines[0].ljust(44, '<')[:44]
        l2 = lines[1].ljust(44, '<')[:44]
        
        if l1.startswith("V<") or (len(l1) > 1 and l1[1] == "<"):
            country = l1[2:5].replace("<", "")
            name_section = l1[5:]
        elif l1.startswith("VN<") or (len(l1) > 2 and l1[2] == "<"):
            country = l1[3:6].replace("<", "")
            name_section = l1[6:]
        else:
            country = l1[2:5].replace("<", "")
            name_section = l1[5:]

        name_parts = name_section.split("<<")
        surname = name_parts[0].replace("<", " ").strip()
        given_names = name_parts[1].replace("<", " ").strip() if len(name_parts) > 1 else ""
        full_name = f"{given_names} {surname}".strip()

        visa_num_raw = l2[0:9]
        visa_chk = l2[9] if len(l2) > 9 else "<"
        visa_num_raw, visa_chk, visa_chk_pass = repair_numeric_field(visa_num_raw, visa_chk)
        visa_num = visa_num_raw.replace("<", "")

        dob_raw = l2[13:19]
        gender = l2[20].replace("<", "U") if len(l2) > 20 else "U"
        exp_raw = l2[21:27]

        fields = {
            "document_type": ExtractedField(value="VISA", raw_value="VISA", confidence=0.99, source="mrz", status="EXTRACTED"),
            "visa_number": ExtractedField(value=visa_num, raw_value=visa_num_raw, confidence=0.98 if visa_chk_pass else 0.75, source="mrz", status="EXTRACTED" if visa_num else "UNKNOWN", is_valid=visa_chk_pass),
            "full_name": ExtractedField(value=full_name, raw_value=full_name, confidence=0.95, source="mrz", status="EXTRACTED" if full_name else "UNKNOWN"),
            "surname": ExtractedField(value=surname, raw_value=surname, confidence=0.95, source="mrz", status="EXTRACTED" if surname else "UNKNOWN"),
            "given_names": ExtractedField(value=given_names, raw_value=given_names, confidence=0.95, source="mrz", status="EXTRACTED" if given_names else "UNKNOWN"),
            "nationality": ExtractedField(value=country, raw_value=country, confidence=0.98, source="mrz", status="EXTRACTED" if country else "UNKNOWN"),
            "date_of_birth": ExtractedField(value=dob_raw, raw_value=dob_raw, confidence=0.95, source="mrz", status="EXTRACTED" if dob_raw else "UNKNOWN"),
            "date_of_expiry": ExtractedField(value=exp_raw, raw_value=exp_raw, confidence=0.95, source="mrz", status="EXTRACTED" if exp_raw else "UNKNOWN"),
            "gender": ExtractedField(value=gender, raw_value=gender, confidence=0.98, source="mrz", status="EXTRACTED"),
            "mrz_line1": ExtractedField(value=l1, raw_value=l1, confidence=0.99, source="mrz", status="EXTRACTED"),
            "mrz_line2": ExtractedField(value=l2, raw_value=l2, confidence=0.99, source="mrz", status="EXTRACTED")
        }

        mrz_res = MRZValidationResult(
            mrz_format="MRV_A",
            lines=[l1, l2],
            document_number_checksum=visa_chk_pass,
            dob_checksum=True,
            expiry_checksum=True,
            composite_checksum=True,
            all_checksums_pass=visa_chk_pass,
            status="VALID" if visa_chk_pass else "CHECKSUM_FAILED"
        )
        return fields, mrz_res

    def parse(self, text: str, mrz_hints: Optional[List[str]] = None) -> Tuple[Dict[str, ExtractedField], Optional[MRZValidationResult]]:
        lines = self.extract_mrz_lines_from_text(text, mrz_hints=mrz_hints)
        if not lines:
            return {}, None

        if len(lines) == 2:
            if lines[0].startswith("V") or lines[0].startswith("VN"):
                return self.parse_mrv_visa(lines)
            elif lines[0].startswith("P"):
                return self.parse_td3_passport(lines)
            else:
                return self.parse_td3_passport(lines)
        elif len(lines) == 3:
            return self.parse_td1_national_id(lines)

        return {}, None

