"""MRZ and Modulo-10 Checksum Validator for Module 2.

Independently recalculates and verifies ICAO Doc 9303 compliance across all standard formats:
- Geometry: TD1 (3x30), TD2 (2x36), TD3 (2x44), MRV-A (2x44), MRV-B (2x36)
- Check digits: 7-3-1 weighted modulo-10 algorithm across doc number, DOB, expiry, and composite.
"""

from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class MRZValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.weights = [7, 3, 1]

    def _calculate_modulo10_checksum(self, data_str: str) -> int:
        """Calculates ICAO Doc 9303 modulo-10 checksum using 7-3-1 repeating weights."""
        total = 0
        for i, char in enumerate(data_str):
            weight = self.weights[i % 3]
            if char.isdigit():
                val = int(char)
            elif 'A' <= char.upper() <= 'Z':
                val = ord(char.upper()) - ord('A') + 10
            elif char == '<':
                val = 0
            else:
                val = 0
            total += val * weight
        return total % 10

    def validate(self, payload: Module1InputPayload) -> List[ValidationCheckResult]:
        results: List[ValidationCheckResult] = []
        mrz_data = payload.mrz
        
        # If MRZ is not present in payload, no MRZ rules apply
        if not mrz_data or not mrz_data.lines:
            return results

        lines = [line.strip().upper() for line in mrz_data.lines if line.strip()]
        num_lines = len(lines)

        # 1. Geometry Validation
        if num_lines == 2:
            len1, len2 = len(lines[0]), len(lines[1])
            if len1 == 44 and len2 == 44:
                mrz_type = "TD3_OR_MRVA"
            elif len1 == 36 and len2 == 36:
                mrz_type = "TD2_OR_MRVB"
            else:
                mrz_type = "INVALID_2LINE"
        elif num_lines == 3:
            len1, len2, len3 = len(lines[0]), len(lines[1]), len(lines[2])
            if len1 == 30 and len2 == 30 and len3 == 30:
                mrz_type = "TD1"
            else:
                mrz_type = "INVALID_3LINE"
        else:
            mrz_type = "UNKNOWN_GEOMETRY"

        if "INVALID" in mrz_type or mrz_type == "UNKNOWN_GEOMETRY":
            results.append(ValidationCheckResult(
                rule_id="MRZ_LINE_GEOMETRY",
                category=RuleCategoryEnum.MRZ.value,
                status="FAIL",
                severity=RuleSeverityEnum.CRITICAL.value,
                message=f"MRZ line lengths do not conform to ICAO standards (Found {num_lines} lines with lengths {[len(l) for l in lines]})",
                expected="TD3 (2x44), TD2 (2x36), or TD1 (3x30)",
                actual=[len(l) for l in lines]
            ))
            return results
        else:
            results.append(ValidationCheckResult(
                rule_id="MRZ_LINE_GEOMETRY",
                category=RuleCategoryEnum.MRZ.value,
                status="PASS",
                severity=RuleSeverityEnum.HIGH.value,
                message=f"MRZ geometry conforms to ICAO standards ({mrz_type})",
                actual=f"{num_lines} lines"
            ))

        # 2. Checksum recalculation for TD3 (Passport / Visa MRV-A)
        if mrz_type == "TD3_OR_MRVA" and len(lines) == 2:
            l2 = lines[1]
            
            # Document number check digit (chars 0..8, check digit at char 9)
            doc_num_field = l2[0:9]
            doc_num_cd = l2[9:10]
            if doc_num_cd.isdigit():
                calc_cd = self._calculate_modulo10_checksum(doc_num_field)
                if calc_cd == int(doc_num_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Document number checksum valid (Calculated: {calc_cd}, Found: {doc_num_cd})",
                        expected=calc_cd,
                        actual=int(doc_num_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Document number check digit mismatch (Calculated: {calc_cd}, Found: {doc_num_cd})",
                        expected=calc_cd,
                        actual=int(doc_num_cd)
                    ))

            # Date of Birth check digit (chars 13..18, check digit at char 19)
            dob_field = l2[13:19]
            dob_cd = l2[19:20]
            if dob_cd.isdigit():
                calc_dob_cd = self._calculate_modulo10_checksum(dob_field)
                if calc_dob_cd == int(dob_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOB_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Date of birth checksum valid (Calculated: {calc_dob_cd})",
                        expected=calc_dob_cd,
                        actual=int(dob_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOB_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Date of birth check digit mismatch (Calculated: {calc_dob_cd}, Found: {dob_cd})",
                        expected=calc_dob_cd,
                        actual=int(dob_cd)
                    ))

            # Date of Expiry check digit (chars 21..26, check digit at char 27)
            exp_field = l2[21:27]
            exp_cd = l2[27:28]
            if exp_cd.isdigit():
                calc_exp_cd = self._calculate_modulo10_checksum(exp_field)
                if calc_exp_cd == int(exp_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_EXPIRY_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Expiry date checksum valid (Calculated: {calc_exp_cd})",
                        expected=calc_exp_cd,
                        actual=int(exp_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_EXPIRY_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Expiry date check digit mismatch (Calculated: {calc_exp_cd}, Found: {exp_cd})",
                        expected=calc_exp_cd,
                        actual=int(exp_cd)
                    ))

            # Composite Checksum (char 43)
            comp_cd = l2[43:44]
            if comp_cd.isdigit():
                comp_data = l2[0:10] + l2[13:20] + l2[21:43]
                calc_comp_cd = self._calculate_modulo10_checksum(comp_data)
                if calc_comp_cd == int(comp_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_COMPOSITE_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Composite master checksum valid (Calculated: {calc_comp_cd})",
                        expected=calc_comp_cd,
                        actual=int(comp_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_COMPOSITE_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"Composite master check digit mismatch (Calculated: {calc_comp_cd}, Found: {comp_cd})",
                        expected=calc_comp_cd,
                        actual=int(comp_cd)
                    ))

        # 3. Checksum recalculation for TD2 / MRV-B (2 lines of 36 characters)
        elif mrz_type == "TD2_OR_MRVB" and len(lines) == 2:
            l2 = lines[1]

            # Document Number check digit (chars 0..8, check digit at char 9)
            doc_num_field = l2[0:9]
            doc_num_cd = l2[9:10]
            if doc_num_cd.isdigit():
                calc_cd = self._calculate_modulo10_checksum(doc_num_field)
                if calc_cd == int(doc_num_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 document number checksum valid (Calculated: {calc_cd})",
                        expected=calc_cd,
                        actual=int(doc_num_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 document number check digit mismatch (Calculated: {calc_cd}, Found: {doc_num_cd})",
                        expected=calc_cd,
                        actual=int(doc_num_cd)
                    ))

            # DOB check digit (chars 13..18, check digit at char 19)
            dob_field = l2[13:19]
            dob_cd = l2[19:20]
            if dob_cd.isdigit():
                calc_dob_cd = self._calculate_modulo10_checksum(dob_field)
                if calc_dob_cd == int(dob_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOB_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 date of birth checksum valid (Calculated: {calc_dob_cd})",
                        expected=calc_dob_cd,
                        actual=int(dob_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOB_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 date of birth check digit mismatch (Calculated: {calc_dob_cd}, Found: {dob_cd})",
                        expected=calc_dob_cd,
                        actual=int(dob_cd)
                    ))

            # Expiry date check digit (chars 21..26, check digit at char 27)
            exp_field = l2[21:27]
            exp_cd = l2[27:28]
            if exp_cd.isdigit():
                calc_exp_cd = self._calculate_modulo10_checksum(exp_field)
                if calc_exp_cd == int(exp_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_EXPIRY_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 expiry date checksum valid (Calculated: {calc_exp_cd})",
                        expected=calc_exp_cd,
                        actual=int(exp_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_EXPIRY_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 expiry date check digit mismatch (Calculated: {calc_exp_cd}, Found: {exp_cd})",
                        expected=calc_exp_cd,
                        actual=int(exp_cd)
                    ))

            # Composite check digit (char 35)
            comp_cd = l2[35:36]
            if comp_cd.isdigit():
                comp_data = l2[0:10] + l2[13:20] + l2[21:35]
                calc_comp_cd = self._calculate_modulo10_checksum(comp_data)
                if calc_comp_cd == int(comp_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_COMPOSITE_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 composite master checksum valid (Calculated: {calc_comp_cd})",
                        expected=calc_comp_cd,
                        actual=int(comp_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_COMPOSITE_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD2 composite check digit mismatch (Calculated: {calc_comp_cd}, Found: {comp_cd})",
                        expected=calc_comp_cd,
                        actual=int(comp_cd)
                    ))

        # 4. Checksum recalculation for TD1 (3-line National ID / Residence Card)
        elif mrz_type == "TD1" and len(lines) == 3:
            l1, l2 = lines[0], lines[1]

            # Document number check digit (Line 1 chars 5..13, check digit at char 14)
            doc_num_field = l1[5:14]
            doc_num_cd = l1[14:15]
            if doc_num_cd.isdigit():
                calc_cd = self._calculate_modulo10_checksum(doc_num_field)
                if calc_cd == int(doc_num_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 document number checksum valid (Calculated: {calc_cd})",
                        expected=calc_cd,
                        actual=int(doc_num_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOC_NUMBER_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 document number check digit mismatch (Calculated: {calc_cd}, Found: {doc_num_cd})",
                        expected=calc_cd,
                        actual=int(doc_num_cd)
                    ))

            # Date of Birth check digit (Line 2 chars 0..5, check digit at char 6)
            dob_field = l2[0:6]
            dob_cd = l2[6:7]
            if dob_cd.isdigit():
                calc_dob_cd = self._calculate_modulo10_checksum(dob_field)
                if calc_dob_cd == int(dob_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOB_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 date of birth checksum valid (Calculated: {calc_dob_cd})",
                        expected=calc_dob_cd,
                        actual=int(dob_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_DOB_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 date of birth check digit mismatch (Calculated: {calc_dob_cd}, Found: {dob_cd})",
                        expected=calc_dob_cd,
                        actual=int(dob_cd)
                    ))

            # Expiry date check digit (Line 2 chars 8..13, check digit at char 14)
            exp_field = l2[8:14]
            exp_cd = l2[14:15]
            if exp_cd.isdigit():
                calc_exp_cd = self._calculate_modulo10_checksum(exp_field)
                if calc_exp_cd == int(exp_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_EXPIRY_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 expiry date checksum valid (Calculated: {calc_exp_cd})",
                        expected=calc_exp_cd,
                        actual=int(exp_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_EXPIRY_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 expiry date check digit mismatch (Calculated: {calc_exp_cd}, Found: {exp_cd})",
                        expected=calc_exp_cd,
                        actual=int(exp_cd)
                    ))

            # Composite check digit (Line 2 char 29)
            comp_cd = l2[29:30]
            if comp_cd.isdigit():
                comp_data = l1[5:30] + l2[0:7] + l2[8:15] + l2[18:29]
                calc_comp_cd = self._calculate_modulo10_checksum(comp_data)
                if calc_comp_cd == int(comp_cd):
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_COMPOSITE_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="PASS",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 composite checksum valid (Calculated: {calc_comp_cd})",
                        expected=calc_comp_cd,
                        actual=int(comp_cd)
                    ))
                else:
                    results.append(ValidationCheckResult(
                        rule_id="MRZ_COMPOSITE_CHECKSUM",
                        category=RuleCategoryEnum.MRZ.value,
                        status="FAIL",
                        severity=RuleSeverityEnum.CRITICAL.value,
                        message=f"TD1 composite check digit mismatch (Calculated: {calc_comp_cd}, Found: {comp_cd})",
                        expected=calc_comp_cd,
                        actual=int(comp_cd)
                    ))

        return results
