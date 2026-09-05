"""Cross-Field and Visual-to-MRZ Consistency Validator for Module 2.
"""

from typing import List, Dict, Any, Optional
from .base_validator import BaseValidator
from ..schemas.input_schema import Module1InputPayload
from ..schemas.output_schema import ValidationCheckResult, RuleCategoryEnum, RuleSeverityEnum

class ConsistencyValidator(BaseValidator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    def validate(self, payload: Module1InputPayload) -> List[ValidationCheckResult]:
        results: List[ValidationCheckResult] = []
        fields = payload.fields
        mrz_data = payload.mrz

        # 1. Evaluate Module 1 injected/detected conflicts directly
        if payload.consistency and "conflicts" in payload.consistency:
            for conflict in payload.consistency["conflicts"]:
                fld_name = conflict.get("field", "unknown_field")
                v_val = conflict.get("visual_value", "")
                m_val = conflict.get("mrz_value", "")
                results.append(ValidationCheckResult(
                    rule_id=f"CROSS_VISUAL_MRZ_{fld_name.upper()}",
                    category=RuleCategoryEnum.CONSISTENCY.value,
                    status="FAIL",
                    severity=RuleSeverityEnum.HIGH.value,
                    message=f"Visual and MRZ values conflict for field '{fld_name}' (Visual: '{v_val}', MRZ: '{m_val}')",
                    field_name=fld_name,
                    expected=m_val,
                    actual=v_val,
                    details=conflict
                ))

        # 2. If MRZ lines are present, perform independent cross-field consistency checks
        if mrz_data and len(mrz_data.lines) >= 2:
            lines = [l.strip().upper() for l in mrz_data.lines if l.strip()]
            num_lines = len(lines)
            
            # A. Document Number Consistency
            doc_num_field = fields.get("passport_number") or fields.get("visa_number") or fields.get("id_number")
            if doc_num_field and doc_num_field.value:
                vis_num = doc_num_field.value.replace(" ", "").replace("-", "").upper()
                
                if num_lines == 2: # TD3 / MRV
                    mrz_num = lines[1][0:9].replace("<", "")
                elif num_lines == 3: # TD1
                    mrz_num = lines[0][5:14].replace("<", "")
                else:
                    mrz_num = ""
                
                if vis_num and mrz_num:
                    if vis_num.endswith(mrz_num) or mrz_num in vis_num or vis_num == mrz_num:
                        results.append(ValidationCheckResult(
                            rule_id="CROSS_VISUAL_MRZ_DOC_NUMBER",
                            category=RuleCategoryEnum.CONSISTENCY.value,
                            status="PASS",
                            severity=RuleSeverityEnum.HIGH.value,
                            message=f"Visual document number '{vis_num}' matches MRZ identifier '{mrz_num}'",
                            field_name="document_number",
                            expected=mrz_num,
                            actual=vis_num
                        ))
                    else:
                        if not any(r.rule_id == "CROSS_VISUAL_MRZ_DOCUMENT_NUMBER" for r in results):
                            results.append(ValidationCheckResult(
                                rule_id="CROSS_VISUAL_MRZ_DOC_NUMBER",
                                category=RuleCategoryEnum.CONSISTENCY.value,
                                status="FAIL",
                                severity=RuleSeverityEnum.HIGH.value,
                                message=f"Visual document number '{vis_num}' conflicts with MRZ identifier '{mrz_num}'",
                                field_name="document_number",
                                expected=mrz_num,
                                actual=vis_num
                            ))

            # B. Nationality Code Consistency
            nat_field = fields.get("nationality")
            if nat_field and nat_field.value:
                vis_nat = nat_field.value.strip().upper()
                if num_lines == 2: # TD3 (Line 2 chars 10:13)
                    mrz_nat = lines[1][10:13].replace("<", "")
                elif num_lines == 3: # TD1 (Line 2 chars 15:18)
                    mrz_nat = lines[1][15:18].replace("<", "")
                else:
                    mrz_nat = ""

                if vis_nat and mrz_nat and len(mrz_nat) == 3:
                    if vis_nat == mrz_nat:
                        results.append(ValidationCheckResult(
                            rule_id="CROSS_VISUAL_MRZ_NATIONALITY",
                            category=RuleCategoryEnum.CONSISTENCY.value,
                            status="PASS",
                            severity=RuleSeverityEnum.HIGH.value,
                            message=f"Visual nationality '{vis_nat}' matches MRZ country code '{mrz_nat}'",
                            field_name="nationality",
                            expected=mrz_nat,
                            actual=vis_nat
                        ))
                    else:
                        results.append(ValidationCheckResult(
                            rule_id="CROSS_VISUAL_MRZ_NATIONALITY",
                            category=RuleCategoryEnum.CONSISTENCY.value,
                            status="FAIL",
                            severity=RuleSeverityEnum.HIGH.value,
                            message=f"Visual nationality '{vis_nat}' conflicts with MRZ country code '{mrz_nat}'",
                            field_name="nationality",
                            expected=mrz_nat,
                            actual=vis_nat
                        ))

            # C. Expiry Date Consistency
            exp_field = fields.get("date_of_expiry") or fields.get("expiry_date")
            if exp_field and exp_field.value and num_lines == 2:
                vis_exp = exp_field.value.strip() # e.g. "2028-12-18"
                mrz_exp = lines[1][21:27] # YYMMDD e.g. "281218"
                
                if len(vis_exp) == 10 and mrz_exp.isdigit() and len(mrz_exp) == 6:
                    vis_yymmdd = vis_exp[2:4] + vis_exp[5:7] + vis_exp[8:10]
                    if vis_yymmdd == mrz_exp:
                        results.append(ValidationCheckResult(
                            rule_id="CROSS_VISUAL_MRZ_EXPIRY",
                            category=RuleCategoryEnum.CONSISTENCY.value,
                            status="PASS",
                            severity=RuleSeverityEnum.HIGH.value,
                            message=f"Visual expiry date '{vis_exp}' matches MRZ date '{mrz_exp}'",
                            field_name="date_of_expiry",
                            expected=mrz_exp,
                            actual=vis_yymmdd
                        ))
                    else:
                        results.append(ValidationCheckResult(
                            rule_id="CROSS_VISUAL_MRZ_EXPIRY",
                            category=RuleCategoryEnum.CONSISTENCY.value,
                            status="FAIL",
                            severity=RuleSeverityEnum.HIGH.value,
                            message=f"Visual expiry date '{vis_exp}' conflicts with MRZ date '{mrz_exp}'",
                            field_name="date_of_expiry",
                            expected=mrz_exp,
                            actual=vis_yymmdd
                        ))

        return results
