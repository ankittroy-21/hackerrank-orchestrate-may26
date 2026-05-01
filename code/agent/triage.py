import json
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import LLM_MODEL, COMPANIES
from agent.schemas import TriageOutput, TriageInput
from agent.safety import check_safety
from agent.retriever import retrieve, infer_company
from agent.prompts import SYSTEM_PROMPT, build_user_prompt
from dotenv import load_dotenv

# Import Groq instead of google.genai
from groq import Groq

load_dotenv()
_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

def triage(issue: str, subject: str = "", company: str = "None") -> TriageOutput:
    # Step 1: Safety check
    safety = check_safety(issue, subject)
    if not safety["safe"]:
        return TriageOutput(
            thought_process="Safety violation detected. Escalating immediately.",
            status=safety["status"],
            product_area=safety["product_area"],
            response=safety["response"],
            justification=safety["justification"],
            request_type=safety["request_type"]
        )

    # Step 2: Company resolution
    resolved_company = None
    if company and company.strip() not in ("None", "", "none"):
        resolved_company = company.strip()
    else:
        resolved_company = infer_company(issue)

    # Step 3: Retrieve chunks
    chunks = retrieve(issue, company=resolved_company)

    if not chunks:
        return TriageOutput(
            thought_process="No relevant corpus chunks were found for this query. Escalating.",
            status="escalated",
            product_area="general",
            response="We were unable to find relevant information to address your issue. A support agent will follow up shortly.",
            justification="No relevant corpus chunks found for this query.",
            request_type="product_issue"
        )

    product_area = chunks[0]["product_area"] if chunks else "general"

    # Step 4: Call Groq
    user_prompt = build_user_prompt(issue, subject, resolved_company or "Unknown", chunks)
    client = get_client()

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL, 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n\nYou MUST output your response as a valid JSON object."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        raw = response.choices[0].message.content.strip()
        
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
                
        data = json.loads(raw.strip())
        
        # SAFETY NET: If Groq forgets the thought process, we inject a default one so Pydantic doesn't crash
        if "thought_process" not in data:
            data["thought_process"] = "LLM generated response but omitted thought process."
            
        return TriageOutput(**data)
        
    except Exception as e:
        return TriageOutput(
            thought_process="An error occurred during LLM generation. Defaulting to safe escalation.",
            status="escalated",
            product_area=product_area,
            response="An error occurred while processing your request. A support agent will assist you.",
            justification=f"LLM error: {str(e)}",
            request_type="product_issue"
        )