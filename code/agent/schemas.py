from pydantic import BaseModel
from typing import Literal
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ALLOWED_STATUS, ALLOWED_REQUEST_TYPE

class TriageOutput(BaseModel):
    thought_process: str
    status: Literal["replied", "escalated"]
    product_area: str
    response: str
    justification: str
    request_type: Literal["product_issue", "feature_request", "bug", "invalid"]

class TriageInput(BaseModel):
    issue: str
    subject: str = ""
    company: str = "None"