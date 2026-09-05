"""Security Auditor and SAIF Compliance Verification Engine."""

from typing import Dict, Any, List
import re

class SecurityAuditor:
    """Evaluates pipeline responses against SAIF, OWASP, and PII safety constraints."""

    # PII sensitive patterns
    SENSITIVE_PATTERNS = [
        re.compile(r"password", re.IGNORECASE),
        re.compile(r"secret_key", re.IGNORECASE),
        re.compile(r"raw_biometric_vector", re.IGNORECASE),
        re.compile(r"bearer_ssn", re.IGNORECASE)
    ]

    @classmethod
    def audit_dossier_privacy(cls, dossier_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Verifies that no raw secrets or unmasked sensitive PII are exposed in the dossier."""
        dossier_str = str(dossier_dict)
        violations = []

        for pat in cls.SENSITIVE_PATTERNS:
            if pat.search(dossier_str):
                violations.append(f"Sensitive key pattern detected: {pat.pattern}")

        return {
            "privacy_compliant": len(violations) == 0,
            "violations": violations
        }
