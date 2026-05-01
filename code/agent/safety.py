import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HIGH_RISK_KEYWORDS

INJECTION_PATTERNS = [
    r"ignore (all |previous |above )?instructions",
    r"disregard (all |previous |above )?instructions",
    r"you are now",
    r"act as (a |an )?",
    r"reveal (your |all |internal |system )?prompt",
    r"show (me |all |your )?(internal |system |hidden )?rules",
    r"forget (all |previous |your )?instructions",
    r"pretend (you are|to be)",
    r"jailbreak",
    r"bypass (safety|filter|restriction)",
    r"display (all |internal |hidden |retrieved )?documents",
    r"affiche toutes les",
    r"logique exacte",
]

def is_injection(text: str) -> bool:
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def is_high_risk(text: str) -> bool:
    text_lower = text.lower()
    for kw in HIGH_RISK_KEYWORDS:
        # For multi-word keywords, check as substring
        # For single words, ensure not part of a larger word
        if " " in kw:
            if kw in text_lower:
                return True
        else:
            # Use word boundary check
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                return True
    return False

def check_safety(issue: str, subject: str = "") -> dict:
    combined = f"{issue} {subject}".strip()
    if is_injection(combined):
        return {
            "safe": False,
            "reason": "injection",
            "status": "escalated",
            "request_type": "invalid",
            "product_area": "security",
            "response": "This request cannot be processed as it appears to contain instructions that attempt to manipulate the support system.",
            "justification": "Prompt injection attempt detected. Escalating for security review."
        }
    if is_high_risk(combined):
        return {
            "safe": False,
            "reason": "high_risk",
            "status": "escalated",
            "request_type": "product_issue",
            "product_area": "security",
            "response": "This issue has been flagged as high priority and requires immediate attention from our support team.",
            "justification": "High-risk keywords detected. Escalating to human agent immediately."
        }
    return {"safe": True}