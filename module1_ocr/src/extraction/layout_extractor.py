"""Layout-Aware Spatial Field Extractor for AI-DIDSS Module 1.

Implements:
- Multi-region spatial and multiline label-value association
- Multi-line label pairing (e.g. 'SURNAME / NOM:' on line N -> 'TAYLOR' on line N+1)
- Bidirectional MRZ and VIZ cross-field fusion
- Document-specific extraction for Passport, Visa, Driver License, National ID, Residence Permit
- Controlled character normalization (Zero Hallucination)
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from .schema import ExtractedField, DocumentExtractionResult
from ..ocr.mrz_parser import MRZParser

ISO_COUNTRY_CODES = {
    "UTO": "UTOPIA", "XAN": "XANADU", "ATL": "ATLANTIS",
    "ELD": "ELDORADO", "VAL": "VALHALLA", "ARC": "ARCADIA",
    "USA": "UNITED STATES", "GBR": "UNITED KINGDOM", "CAN": "CANADA",
    "FRA": "FRANCE", "DEU": "GERMANY", "ITA": "ITALY", "ESP": "SPAIN"
}

class LayoutAwareFieldExtractor:
    def __init__(self, confidence_threshold: float = 0.40):
        self.confidence_threshold = confidence_threshold
        self.mrz_parser = MRZParser()

    def normalize_date(self, date_str: Optional[str]) -> Optional[str]:
        """Normalizes varied date formats into standard ISO 8601 (YYYY-MM-DD)."""
        if not date_str:
            return None
        cleaned = date_str.strip().replace("/", "-").replace(".", "-")
        # Fix OCR typos where hyphen was dropped, e.g. 1990-0428 -> 1990-04-28
        m_glitch = re.search(r"(\d{4})-(\d{2})(\d{2})", cleaned)
        if m_glitch:
            cleaned = f"{m_glitch.group(1)}-{m_glitch.group(2)}-{m_glitch.group(3)}"
            
        # YYYY-MM-DD
        m = re.search(r"(\d{4})-(\d{2})-(\d{2})", cleaned)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
            
        # DD-MM-YYYY
        m = re.search(r"(\d{2})-(\d{2})-(\d{4})", cleaned)
        if m:
            v1, v2, yyyy = int(m.group(1)), int(m.group(2)), m.group(3)
            if v1 > 12 and v2 <= 12:
                return f"{yyyy}-{v2:02d}-{v1:02d}"
            else:
                return f"{yyyy}-{v2:02d}-{v1:02d}"
            
        # YYMMDD (MRZ format)
        m = re.search(r"^(\d{2})(\d{2})(\d{2})$", cleaned)
        if m:
            yy, mm, dd = int(m.group(1)), m.group(2), m.group(3)
            century = 1900 if yy >= 40 else 2000
            return f"{century + yy}-{mm}-{dd}"

        return date_str

    def identify_document_type(self, raw_text: str, mrz_res: Any = None) -> str:
        """Robust document type classifier using header keywords and MRZ format."""
        text_upper = raw_text.upper()

        if "DRIVER LICENSE" in text_upper or "DRIVING LICENCE" in text_upper or "DL NO" in text_upper or "DRIVER'S LICENSE" in text_upper or "AAMVA" in text_upper:
            return "driver_license"
        elif "RESIDENCE" in text_upper or "PERMIT NO" in text_upper or "WORK PERMIT" in text_upper:
            return "permit"
        elif "TRAVEL VISA" in text_upper or "VISA NO" in text_upper or text_upper.startswith("VISA"):
            return "visa"
        elif "PASSPORT" in text_upper or "PASSEPORT" in text_upper:
            return "passport"
        elif "NATIONAL IDENTITY" in text_upper or "NATIONAL ID" in text_upper or "CITIZEN ID" in text_upper:
            return "national_id"

        if mrz_res and mrz_res.mrz_format:
            if mrz_res.mrz_format == "TD3":
                return "passport"
            elif mrz_res.mrz_format in ["MRV_A", "MRV_B"]:
                return "visa"
            elif mrz_res.mrz_format == "TD1":
                return "national_id"

        # Check for passport markers
        if "SURNAME" in text_upper and ("GIVEN NAMES" in text_upper or "PRENOMS" in text_upper):
            return "passport"

        return "unknown_document"

    def find_field_value(self, label_patterns: List[str], lines: List[str], is_date: bool = False) -> Optional[Tuple[str, float]]:
        """Extracts value either inline with label or on the immediately following line."""
        date_regex = r"(\d{4}[-\/\.]\d{1,2}[-\/\.]\d{1,2}|\d{1,2}[-\/\.]\d{1,2}[-\/\.]\d{4})"
        
        for idx, line in enumerate(lines):
            line_str = line.strip()
            for pat in label_patterns:
                # 1. Inline match (LABEL: VALUE)
                m_inline = re.search(pat + r"[:\s\-\.]+(.+)$", line_str, re.IGNORECASE)
                if m_inline:
                    val = m_inline.group(1).strip()
                    # If date required, ensure date pattern exists in val
                    if is_date:
                        m_d = re.search(date_regex, val)
                        if m_d:
                            return m_d.group(1), 0.94
                    elif val and not any(re.match(p, val, re.IGNORECASE) for p in label_patterns):
                        # Filter out known header tokens
                        if not any(token in val.upper() for token in ["PASSPORT", "PASSEPORT", "DRIVER", "NATIONAL"]):
                            return val, 0.90
                
                # 2. Exact label line match (Value is on next line or next next line)
                if re.search(r"^" + pat + r"[:\s\-\.\/]*$", line_str, re.IGNORECASE) or line_str.upper() in ["DOB", "EXP", "ISS", "SEX", "SURNAME", "GIVEN NAMES"]:
                    for offset in [1, 2]:
                        if idx + offset < len(lines):
                            cand = lines[idx + offset].strip()
                            if is_date:
                                m_d = re.search(date_regex, cand)
                                if m_d:
                                    return m_d.group(1), 0.93
                            else:
                                common_labels = ["SURNAME", "GIVEN", "NAME", "DATE", "SEX", "NATIONALITY", "PASSPORT", "DOB", "EXPIRY", "EXP", "ISS", "TYPE", "CODE"]
                                if cand and not any(cand.upper().startswith(cl) for cl in common_labels):
                                    return cand, 0.89

        return None

    def extract(self, raw_text: str, preproc_metadata: Optional[Dict[str, Any]] = None) -> DocumentExtractionResult:
        """Executes layout-aware extraction with MRZ/VIZ cross-field fusion."""
        preproc_metadata = preproc_metadata or {}
        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
        mrz_hints = preproc_metadata.get("mrz_lines", [])
        
        # 1. Parse MRZ
        mrz_fields, mrz_validation = self.mrz_parser.parse(raw_text, mrz_hints=mrz_hints)
        
        # 2. Identify Document Type
        doc_type = self.identify_document_type(raw_text, mrz_validation)
        
        fields: Dict[str, ExtractedField] = {}
        
        # 3. Document-Specific Layout Extraction & Fusion
        if doc_type == "passport":
            fields["document_type"] = ExtractedField(value="PASSPORT", raw_value="PASSPORT", confidence=0.99, source="visual_ocr", status="EXTRACTED")
            
            # Passport Number (Look for PASS[P|F]ORT NO: <ALPHANUMERIC>)
            p_num = None
            for l in lines:
                m_p = re.search(r"(?:PASSPORT|PASSFORT|PASSEPORT)\s*(?:NO|NUMBER|N°)?[:\s\.]*([A-Z0-9]{8,10})\b", l, re.IGNORECASE)
                if m_p and not any(w in m_p.group(1).upper() for w in ["PASSPORT", "PASSEPORT", "ARCADIA", "UTOPIA"]):
                    p_num = m_p.group(1)
                    break
                    
            if not p_num and "passport_number" in mrz_fields and mrz_fields["passport_number"].value:
                p_num = mrz_fields["passport_number"].value
            if p_num:
                fields["passport_number"] = ExtractedField(value=p_num, raw_value=p_num, confidence=0.95, source="visual_ocr" if p_num != (mrz_fields.get("passport_number", ExtractedField(value="")).value) else "mrz", status="EXTRACTED")

            # Surname & Given Names
            s_res = self.find_field_value([r"SURNAME\s*[\/\']?\s*NOM", r"SURNAME", r"NOM"], lines)
            g_res = self.find_field_value([r"GIVEN\s*NAMES?\s*[\/\']?\s*PRENOMS?", r"GIVEN\s*NAMES?", r"PRENOMS?"], lines)
            
            s_name = s_res[0] if s_res else None
            g_name = g_res[0] if g_res else None
            
            if not s_name and "surname" in mrz_fields:
                s_name = mrz_fields["surname"].value
            if not g_name and "given_names" in mrz_fields:
                g_name = mrz_fields["given_names"].value
                
            if s_name:
                s_clean = re.sub(r"[^A-Za-z\s\-]", "", s_name).strip().upper()
                s_conf = s_res[1] if s_res else (mrz_fields.get("surname").confidence if "surname" in mrz_fields else 0.88)
                fields["surname"] = ExtractedField(value=s_clean, raw_value=s_name, confidence=s_conf, source="visual_ocr" if s_res else "mrz", status="EXTRACTED")
            if g_name:
                g_clean = re.sub(r"[^A-Za-z\s\-]", "", g_name).strip().upper()
                g_conf = g_res[1] if g_res else (mrz_fields.get("given_names").confidence if "given_names" in mrz_fields else 0.88)
                fields["given_names"] = ExtractedField(value=g_clean, raw_value=g_name, confidence=g_conf, source="visual_ocr" if g_res else "mrz", status="EXTRACTED")
            if s_name and g_name:
                mean_name_conf = round((fields["surname"].confidence + fields["given_names"].confidence) / 2.0, 3)
                fields["full_name"] = ExtractedField(value=f"{fields.get('given_names', ExtractedField(value=g_name)).value} {fields.get('surname', ExtractedField(value=s_name)).value}", confidence=mean_name_conf, source="derived", status="EXTRACTED")

            # Nationality & Issuing Country
            nat_res = self.find_field_value([r"NATIONALITY\s*[\/\']?\s*NATIONALITE", r"NATIONALITY", r"CODE"], lines)
            nat = nat_res[0] if nat_res else None
            if not nat and "nationality" in mrz_fields:
                nat = mrz_fields["nationality"].value
            if nat:
                # Check for 3-letter code in parentheses or isolated word
                m_code = re.search(r"\b([A-Z]{3})\b", nat)
                nat_clean = m_code.group(1) if m_code else nat.strip().upper()
                nat_conf = nat_res[1] if nat_res else (mrz_fields.get("nationality").confidence if "nationality" in mrz_fields else 0.90)
                fields["nationality"] = ExtractedField(value=nat_clean, raw_value=nat, confidence=nat_conf, source="visual_ocr" if nat_res else "mrz", status="EXTRACTED")
                fields["issuing_country"] = ExtractedField(value=nat_clean, raw_value=nat, confidence=nat_conf, source="visual_ocr" if nat_res else "mrz", status="EXTRACTED")

            # Date of Birth
            dob_res = self.find_field_value([r"DATE\s*OF\s*BIRTH", r"DOB", r"DATE\s*NAISSANCE"], lines, is_date=True)
            dob = dob_res[0] if dob_res else None
            if not dob and "date_of_birth" in mrz_fields:
                dob = self.normalize_date(mrz_fields["date_of_birth"].value)
            if dob:
                norm_dob = self.normalize_date(dob)
                dob_conf = dob_res[1] if dob_res else (mrz_fields.get("date_of_birth").confidence if "date_of_birth" in mrz_fields else 0.88)
                fields["date_of_birth"] = ExtractedField(value=norm_dob, raw_value=dob, confidence=dob_conf, source="visual_ocr" if dob_res else "mrz", status="EXTRACTED")

            # Date of Expiry
            exp_res = self.find_field_value([r"DATE\s*OF\s*EXPIRY", r"EXPIRY", r"EXPIRATION"], lines, is_date=True)
            exp = exp_res[0] if exp_res else None
            if not exp and "date_of_expiry" in mrz_fields:
                exp = self.normalize_date(mrz_fields["date_of_expiry"].value)
            if exp:
                norm_exp = self.normalize_date(exp)
                exp_conf = exp_res[1] if exp_res else (mrz_fields.get("date_of_expiry").confidence if "date_of_expiry" in mrz_fields else 0.88)
                fields["date_of_expiry"] = ExtractedField(value=norm_exp, raw_value=exp, confidence=exp_conf, source="visual_ocr" if exp_res else "mrz", status="EXTRACTED")

            # Date of Issue
            iss_res = self.find_field_value([r"DATE\s*OF\s*ISSUE", r"ISSUE\s*DATE", r"EMISSION"], lines, is_date=True)
            if iss_res:
                fields["date_of_issue"] = ExtractedField(value=self.normalize_date(iss_res[0]), raw_value=iss_res[0], confidence=iss_res[1], source="visual_ocr", status="EXTRACTED")

            # Gender / Sex
            sex_res = self.find_field_value([r"SEX", r"GENDER", r"SEXE"], lines)
            gender = sex_res[0] if sex_res else None
            if not gender and "gender" in mrz_fields:
                gender = mrz_fields["gender"].value
            if gender:
                m_g = re.search(r"\b([MFU])\b", gender.upper())
                g_val = m_g.group(1) if m_g else "U"
                sex_conf = sex_res[1] if sex_res else (mrz_fields.get("gender").confidence if "gender" in mrz_fields else 0.90)
                fields["gender"] = ExtractedField(value=g_val, raw_value=gender, confidence=sex_conf, source="visual_ocr" if sex_res else "mrz", status="EXTRACTED")

            # Include MRZ lines
            if "mrz_line1" in mrz_fields:
                fields["mrz_line1"] = mrz_fields["mrz_line1"]
            if "mrz_line2" in mrz_fields:
                fields["mrz_line2"] = mrz_fields["mrz_line2"]

        elif doc_type == "driver_license":
            fields["document_type"] = ExtractedField(value="DRIVER_LICENSE", raw_value="DRIVER_LICENSE", confidence=0.99, source="visual_ocr", status="EXTRACTED")
            
            dl_res = self.find_field_value([r"DL\s*NO", r"LICENSE\s*NO", r"LICENCE\s*NO"], lines)
            if dl_res:
                m_dl = re.search(r"(DL-[A-Z0-9]+|[A-Z0-9]{8,12})", dl_res[0].replace(" ", ""))
                dl_val = m_dl.group(1) if m_dl else dl_res[0]
                fields["license_number"] = ExtractedField(value=dl_val, raw_value=dl_res[0], confidence=dl_res[1], source="visual_ocr", status="EXTRACTED")
                
            name_res = self.find_field_value([r"NAME"], lines)
            if name_res:
                c_name = re.sub(r"\s+", " ", name_res[0].replace(",", " ")).strip().upper()
                fields["full_name"] = ExtractedField(value=c_name, raw_value=name_res[0], confidence=name_res[1], source="visual_ocr", status="EXTRACTED")
                
            addr_res = self.find_field_value([r"ADDR", r"ADDRESS"], lines)
            if addr_res:
                fields["address"] = ExtractedField(value=addr_res[0].strip().upper(), raw_value=addr_res[0], confidence=addr_res[1], source="visual_ocr", status="EXTRACTED")
                
            dob_res = self.find_field_value([r"DOB", r"DATE\s*OF\s*BIRTH"], lines, is_date=True)
            if dob_res:
                fields["date_of_birth"] = ExtractedField(value=self.normalize_date(dob_res[0]), raw_value=dob_res[0], confidence=dob_res[1], source="visual_ocr", status="EXTRACTED")
                
            iss_res = self.find_field_value([r"ISS", r"ISSUE"], lines, is_date=True)
            if iss_res:
                fields["issue_date"] = ExtractedField(value=self.normalize_date(iss_res[0]), raw_value=iss_res[0], confidence=iss_res[1], source="visual_ocr", status="EXTRACTED")
                
            exp_res = self.find_field_value([r"EXP", r"EXPIRY"], lines, is_date=True)
            if exp_res:
                fields["expiry_date"] = ExtractedField(value=self.normalize_date(exp_res[0]), raw_value=exp_res[0], confidence=exp_res[1], source="visual_ocr", status="EXTRACTED")
                
            cls_res = self.find_field_value([r"CLASS"], lines)
            if cls_res:
                fields["vehicle_class"] = ExtractedField(value=cls_res[0].strip().upper(), raw_value=cls_res[0], confidence=cls_res[1], source="visual_ocr", status="EXTRACTED")

        elif doc_type == "visa":
            fields["document_type"] = ExtractedField(value="VISA", raw_value="VISA", confidence=0.99, source="visual_ocr", status="EXTRACTED")
            
            v_res = self.find_field_value([r"VISA\s*NO"], lines)
            v_num = v_res[0] if v_res else None
            if not v_num and "visa_number" in mrz_fields:
                v_num = mrz_fields["visa_number"].value
            if v_num:
                m_v = re.search(r"([A-Z0-9]{8,10})", v_num.replace(" ", ""))
                val = m_v.group(1) if m_v else v_num
                v_conf = v_res[1] if v_res else (mrz_fields.get("visa_number").confidence if "visa_number" in mrz_fields else 0.90)
                fields["visa_number"] = ExtractedField(value=val, raw_value=v_num, confidence=v_conf, source="visual_ocr" if v_res else "mrz", status="EXTRACTED")
                
            b_res = self.find_field_value([r"BEARER", r"NAME"], lines)
            b_name = b_res[0] if b_res else None
            if not b_name and "full_name" in mrz_fields:
                b_name = mrz_fields["full_name"].value
            if b_name:
                cleaned_b = re.sub(r"\s+", " ", b_name.replace(",", " ")).strip().upper()
                b_conf = b_res[1] if b_res else (mrz_fields.get("full_name").confidence if "full_name" in mrz_fields else 0.88)
                fields["full_name"] = ExtractedField(value=cleaned_b, raw_value=b_name, confidence=b_conf, source="visual_ocr" if b_res else "mrz", status="EXTRACTED")
                
            p_res = self.find_field_value([r"PASSPORT\s*NO", r"PASSFORT\s*NO"], lines)
            if p_res:
                m_p = re.search(r"([A-Z0-9]{8,10})", p_res[0].replace(" ", ""))
                val = m_p.group(1) if m_p else p_res[0]
                fields["passport_number"] = ExtractedField(value=val, raw_value=p_res[0], confidence=p_res[1], source="visual_ocr", status="EXTRACTED")
                
            iss_res = self.find_field_value([r"VALID\s*FROM"], lines, is_date=True)
            if iss_res:
                fields["issue_date"] = ExtractedField(value=self.normalize_date(iss_res[0]), raw_value=iss_res[0], confidence=iss_res[1], source="visual_ocr", status="EXTRACTED")
                
            exp_res = self.find_field_value([r"VALID\s*UNTIL"], lines, is_date=True)
            exp = exp_res[0] if exp_res else None
            if not exp and "date_of_expiry" in mrz_fields:
                exp = self.normalize_date(mrz_fields["date_of_expiry"].value)
            if exp:
                exp_conf = exp_res[1] if exp_res else (mrz_fields.get("date_of_expiry").confidence if "date_of_expiry" in mrz_fields else 0.88)
                fields["expiry_date"] = ExtractedField(value=self.normalize_date(exp), raw_value=exp, confidence=exp_conf, source="visual_ocr" if exp_res else "mrz", status="EXTRACTED")
                
            ent_res = self.find_field_value([r"ENTRIES"], lines)
            if ent_res:
                fields["entries"] = ExtractedField(value=ent_res[0].strip().upper(), raw_value=ent_res[0], confidence=ent_res[1], source="visual_ocr", status="EXTRACTED")
                
            if "mrz_line1" in mrz_fields:
                fields["mrz_line1"] = mrz_fields["mrz_line1"]
            if "mrz_line2" in mrz_fields:
                fields["mrz_line2"] = mrz_fields["mrz_line2"]

        elif doc_type == "national_id":
            fields["document_type"] = ExtractedField(value="NATIONAL_ID", raw_value="NATIONAL_ID", confidence=0.99, source="visual_ocr", status="EXTRACTED")
            
            id_res = self.find_field_value([r"ID\s*NO", r"IDENTITY\s*NO"], lines)
            id_num = id_res[0] if id_res else None
            if not id_num and "id_number" in mrz_fields:
                id_num = f"ID-{mrz_fields['id_number'].value}"
            if id_num:
                m_id = re.search(r"(ID-[A-Z0-9]+|[A-Z0-9]{8,12})", id_num.replace(" ", ""))
                val = m_id.group(1) if m_id else id_num
                id_conf = id_res[1] if id_res else (mrz_fields.get("id_number").confidence if "id_number" in mrz_fields else 0.90)
                fields["id_number"] = ExtractedField(value=val, raw_value=id_num, confidence=id_conf, source="visual_ocr" if id_res else "mrz", status="EXTRACTED")
                
            name_res = self.find_field_value([r"NAME"], lines)
            name = name_res[0] if name_res else None
            if not name and "full_name" in mrz_fields:
                name = mrz_fields["full_name"].value
            if name:
                cleaned_name = re.sub(r"\s+", " ", name.replace(",", " ")).strip().upper()
                n_conf = name_res[1] if name_res else (mrz_fields.get("full_name").confidence if "full_name" in mrz_fields else 0.88)
                fields["full_name"] = ExtractedField(value=cleaned_name, raw_value=name, confidence=n_conf, source="visual_ocr" if name_res else "mrz", status="EXTRACTED")
                
            dob_res = self.find_field_value([r"DOB", r"DATE\s*OF\s*BIRTH"], lines, is_date=True)
            dob = dob_res[0] if dob_res else None
            if not dob and "date_of_birth" in mrz_fields:
                dob = self.normalize_date(mrz_fields["date_of_birth"].value)
            if dob:
                d_conf = dob_res[1] if dob_res else (mrz_fields.get("date_of_birth").confidence if "date_of_birth" in mrz_fields else 0.88)
                fields["date_of_birth"] = ExtractedField(value=self.normalize_date(dob), raw_value=dob, confidence=d_conf, source="visual_ocr" if dob_res else "mrz", status="EXTRACTED")
                
            cit_res = self.find_field_value([r"CITIZENSHIP", r"NATIONALITY"], lines)
            cit = cit_res[0] if cit_res else None
            if not cit and "nationality" in mrz_fields:
                cit = mrz_fields["nationality"].value
            if cit:
                m_cit = re.search(r"([A-Z]{3})", cit.upper())
                val = m_cit.group(1) if m_cit else cit.strip().upper()
                c_conf = cit_res[1] if cit_res else (mrz_fields.get("nationality").confidence if "nationality" in mrz_fields else 0.90)
                fields["nationality"] = ExtractedField(value=val, raw_value=cit, confidence=c_conf, source="visual_ocr" if cit_res else "mrz", status="EXTRACTED")
                
            exp_res = self.find_field_value([r"EXPIRY", r"EXP"], lines, is_date=True)
            exp = exp_res[0] if exp_res else None
            if not exp and "date_of_expiry" in mrz_fields:
                exp = self.normalize_date(mrz_fields["date_of_expiry"].value)
            if exp:
                e_conf = exp_res[1] if exp_res else (mrz_fields.get("date_of_expiry").confidence if "date_of_expiry" in mrz_fields else 0.88)
                fields["date_of_expiry"] = ExtractedField(value=self.normalize_date(exp), raw_value=exp, confidence=e_conf, source="visual_ocr" if exp_res else "mrz", status="EXTRACTED")
                
            if "mrz_line1" in mrz_fields:
                fields["mrz_line1"] = mrz_fields["mrz_line1"]
            if "mrz_line2" in mrz_fields:
                fields["mrz_line2"] = mrz_fields["mrz_line2"]
            if "mrz_line3" in mrz_fields:
                fields["mrz_line3"] = mrz_fields["mrz_line3"]

        elif doc_type == "permit":
            fields["document_type"] = ExtractedField(value="RESIDENCE_PERMIT", raw_value="RESIDENCE_PERMIT", confidence=0.99, source="visual_ocr", status="EXTRACTED")
            
            p_res = self.find_field_value([r"PERMIT\s*NO"], lines)
            if p_res:
                m_p = re.search(r"(RP-[A-Z0-9]+|[A-Z0-9]{8,12})", p_res[0].replace(" ", ""))
                val = m_p.group(1) if m_p else p_res[0]
                fields["permit_number"] = ExtractedField(value=val, raw_value=p_res[0], confidence=p_res[1], source="visual_ocr", status="EXTRACTED")
                
            h_res = self.find_field_value([r"HOLDER", r"NAME"], lines)
            if h_res:
                cleaned_h = re.sub(r"\s+", " ", h_res[0].replace(",", " ")).strip().upper()
                fields["full_name"] = ExtractedField(value=cleaned_h, raw_value=h_res[0], confidence=h_res[1], source="visual_ocr", status="EXTRACTED")
                
            cat_res = self.find_field_value([r"CATEGORY"], lines)
            if cat_res:
                fields["permit_category"] = ExtractedField(value=cat_res[0].strip().upper(), raw_value=cat_res[0], confidence=cat_res[1], source="visual_ocr", status="EXTRACTED")
                
            exp_res = self.find_field_value([r"VALID\s*UNTIL", r"EXPIRY"], lines, is_date=True)
            if exp_res:
                fields["valid_until"] = ExtractedField(value=self.normalize_date(exp_res[0]), raw_value=exp_res[0], confidence=exp_res[1], source="visual_ocr", status="EXTRACTED")
                
            sp_res = self.find_field_value([r"EMPLOYER", r"SPONSOR"], lines)
            if sp_res:
                fields["sponsor"] = ExtractedField(value=sp_res[0].strip().upper(), raw_value=sp_res[0], confidence=sp_res[1], source="visual_ocr", status="EXTRACTED")

        # 4. Overall Status Determination
        num_fields = len(fields)
        if num_fields >= 4:
            status = "SUCCESS"
        elif num_fields >= 1:
            status = "PARTIAL"
        elif doc_type != "unknown_document":
            status = "REVIEW_REQUIRED"
        else:
            status = "UNKNOWN"

        return DocumentExtractionResult(
            document_type=doc_type,
            document_type_confidence=0.95 if doc_type != "unknown_document" else 0.0,
            raw_text=raw_text,
            fields=fields,
            mrz_validation=mrz_validation if doc_type in ["passport", "visa", "national_id"] else None,
            processing_metadata=preproc_metadata,
            status=status
        )
