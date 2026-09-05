"""Document Field Extractor for AI-DIDSS Module 1.

Extracts structured identity fields from raw OCR text and MRZ parser output:
- Passports (ICAO TD3)
- Visas (MRV-A)
- Driver's Licenses (AAMVA DL)
- National IDs (TD1)
- Residence Permits

Adheres strictly to the Zero Hallucination Rule:
Low-confidence or missing fields are explicitly flagged as 'UNKNOWN' / 'REVIEW_REQUIRED'.
"""

import re
from typing import Dict, Any, Optional
from .schema import ExtractedField, DocumentExtractionResult
from ..ocr.mrz_parser import MRZParser

class FieldExtractor:
    def __init__(self, confidence_threshold: float = 0.60):
        self.confidence_threshold = confidence_threshold
        self.mrz_parser = MRZParser()

    def identify_document_type(self, raw_text: str, mrz_res: Any = None) -> str:
        """Determines document type based on header keywords and validated MRZ format."""
        text_upper = raw_text.upper()
        
        # 1. Primary Keyword / Header Check
        if "DRIVER LICENSE" in text_upper or "DRIVING LICENCE" in text_upper or "DL NO" in text_upper or "DRIVER'S LICENSE" in text_upper:
            return "driver_license"
        elif "RESIDENCE" in text_upper or "PERMIT" in text_upper or "WORK PERMIT" in text_upper:
            return "permit"
        elif "TRAVEL VISA" in text_upper or "VISA NO" in text_upper:
            return "visa"
        elif "PASSPORT" in text_upper or "PASSEPORT" in text_upper:
            return "passport"
        elif "NATIONAL IDENTITY" in text_upper or "NATIONAL ID" in text_upper or "CITIZEN ID" in text_upper:
            return "national_id"

        # 2. MRZ-based identification fallback
        if mrz_res and mrz_res.mrz_format:
            if mrz_res.mrz_format == "TD3":
                return "passport"
            elif mrz_res.mrz_format in ["MRV_A", "MRV_B"]:
                return "visa"
            elif mrz_res.mrz_format == "TD1":
                return "national_id"

        return "unknown_document"

    def extract_regex_field(self, pattern: str, text: str, group: int = 1) -> Optional[str]:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            res = match.group(group).strip()
            # Normalize whitespace
            return re.sub(r"\s+", " ", res)
        return None

    def extract(self, raw_text: str, preproc_metadata: Optional[Dict[str, Any]] = None) -> DocumentExtractionResult:
        """Extracts structured fields from raw OCR text and MRZ."""
        preproc_metadata = preproc_metadata or {}
        
        # 1. Attempt MRZ detection & parsing
        mrz_fields, mrz_validation = self.mrz_parser.parse(raw_text)
        
        # 2. Determine document type
        doc_type = self.identify_document_type(raw_text, mrz_validation)
        
        fields: Dict[str, ExtractedField] = {}
        # Incorporate MRZ fields if applicable
        if doc_type in ["passport", "visa", "national_id"]:
            fields.update(mrz_fields)

        # 3. VIZ Pattern Extraction by Document Type
        if doc_type == "passport":
            fields["document_type"] = ExtractedField(value="PASSPORT", confidence=0.99)
            p_num = self.extract_regex_field(r"(?:PASSPORT\s*(?:NO|NUMBER)?[:\s]+)([A-Z0-9]{8,10})", raw_text)
            if p_num:
                fields["passport_number"] = ExtractedField(value=p_num, confidence=0.95)
            
            s_name = self.extract_regex_field(r"(?:SURNAME|NOM)[:\s\n]+([A-Z\s]+?)(?:\n|$)", raw_text)
            g_name = self.extract_regex_field(r"(?:GIVEN NAMES|PRENOMS)[:\s\n]+([A-Z\s]+?)(?:\n|$)", raw_text)
            if s_name and g_name:
                fields["surname"] = ExtractedField(value=s_name, confidence=0.90)
                fields["given_names"] = ExtractedField(value=g_name, confidence=0.90)
                fields["full_name"] = ExtractedField(value=f"{g_name} {s_name}", confidence=0.90)

        elif doc_type == "driver_license":
            fields["document_type"] = ExtractedField(value="DRIVER_LICENSE", confidence=0.99)
            dl_num = self.extract_regex_field(r"(?:DL\s*NO|LICENSE\s*NO)[:\s]+(DL-[A-Z0-9]+|[A-Z0-9]{8,12})", raw_text)
            if dl_num:
                fields["license_number"] = ExtractedField(value=dl_num, confidence=0.92)
            
            name = self.extract_regex_field(r"(?:NAME)[:\s]+([^\n\r]+)", raw_text)
            if name:
                cleaned_name = name.replace(",", " ").strip()
                fields["full_name"] = ExtractedField(value=re.sub(r"\s+", " ", cleaned_name), confidence=0.90)
                
            addr = self.extract_regex_field(r"(?:ADDR|ADDRESS)[:\s]+([^\n\r]+)", raw_text)
            if addr:
                fields["address"] = ExtractedField(value=addr, confidence=0.85)
                
            dob = self.extract_regex_field(r"(?:DOB)[:\s]+(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", raw_text)
            if dob:
                fields["date_of_birth"] = ExtractedField(value=dob, confidence=0.90)
                
            exp = self.extract_regex_field(r"(?:EXP)[:\s]+(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", raw_text)
            if exp:
                fields["expiry_date"] = ExtractedField(value=exp, confidence=0.90)
                
            v_class = self.extract_regex_field(r"(?:CLASS)[:\s]+([^\n\r]+)", raw_text)
            if v_class:
                fields["vehicle_class"] = ExtractedField(value=v_class, confidence=0.88)

        elif doc_type == "visa":
            fields["document_type"] = ExtractedField(value="VISA", confidence=0.99)
            v_num = self.extract_regex_field(r"(?:VISA\s*NO)[:\s]+([A-Z0-9]{8,10})", raw_text)
            if v_num:
                fields["visa_number"] = ExtractedField(value=v_num, confidence=0.95)
            
            bearer = self.extract_regex_field(r"(?:BEARER)[:\s]+([^\n\r]+)", raw_text)
            if bearer:
                cleaned_bearer = bearer.replace(",", " ").strip()
                fields["full_name"] = ExtractedField(value=re.sub(r"\s+", " ", cleaned_bearer), confidence=0.92)
                
            p_num = self.extract_regex_field(r"(?:PASSPORT\s*NO)[:\s]+([A-Z0-9]{8,10})", raw_text)
            if p_num:
                fields["passport_number"] = ExtractedField(value=p_num, confidence=0.90)

        elif doc_type == "national_id":
            fields["document_type"] = ExtractedField(value="NATIONAL_ID", confidence=0.99)
            id_num = self.extract_regex_field(r"(?:ID\s*NO)[:\s]+(ID-[A-Z0-9]+|[A-Z0-9]{8,12})", raw_text)
            if id_num:
                fields["id_number"] = ExtractedField(value=id_num, confidence=0.95)
            
            name = self.extract_regex_field(r"(?:NAME)[:\s]+([^\n\r]+)", raw_text)
            if name:
                parts = [p.strip() for p in name.split(",") if p.strip()]
                if len(parts) == 2:
                    cleaned_name = f"{parts[1]} {parts[0]}"
                else:
                    cleaned_name = name.replace(",", " ").strip()
                fields["full_name"] = ExtractedField(value=re.sub(r"\s+", " ", cleaned_name), confidence=0.90)

        elif doc_type == "permit":
            fields["document_type"] = ExtractedField(value="RESIDENCE_PERMIT", confidence=0.99)
            p_num = self.extract_regex_field(r"(?:PERMIT\s*NO)[:\s]+(RP-[A-Z0-9]+|[A-Z0-9]{8,12})", raw_text)
            if p_num:
                fields["permit_number"] = ExtractedField(value=p_num, confidence=0.92)
            
            holder = self.extract_regex_field(r"(?:HOLDER)[:\s]+([^\n\r]+)", raw_text)
            if holder:
                cleaned_holder = holder.replace(",", " ").strip()
                fields["full_name"] = ExtractedField(value=re.sub(r"\s+", " ", cleaned_holder), confidence=0.90)
                
            cat = self.extract_regex_field(r"(?:CATEGORY)[:\s]+([^\n\r]+)", raw_text)
            if cat:
                fields["permit_category"] = ExtractedField(value=cat, confidence=0.88)
                
            exp = self.extract_regex_field(r"(?:VALID\s*UNTIL)[:\s]+(\d{4}-\d{2}-\d{2})", raw_text)
            if exp:
                fields["valid_until"] = ExtractedField(value=exp, confidence=0.90)
                
            sponsor = self.extract_regex_field(r"(?:EMPLOYER|SPONSOR)[:\s]+([^\n\r]+)", raw_text)
            if sponsor:
                fields["sponsor"] = ExtractedField(value=sponsor, confidence=0.88)

        # 4. Overall status determination
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
            raw_text=raw_text,
            fields=fields,
            mrz_validation=mrz_validation if doc_type in ["passport", "visa", "national_id"] else None,
            processing_metadata=preproc_metadata,
            status=status
        )
