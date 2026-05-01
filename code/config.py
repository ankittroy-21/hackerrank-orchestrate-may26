from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR  = REPO_ROOT / "data"

INPUT_CSV  = REPO_ROOT / "support_tickets" / "support_tickets.csv"
OUTPUT_CSV = REPO_ROOT / "support_tickets" / "output.csv"
SAMPLE_CSV = REPO_ROOT / "support_tickets" / "sample_support_tickets.csv"

CHROMA_DIR        = Path(__file__).parent / "local_storage" / "chroma"
CHROMA_COLLECTION = "support_corpus"

# ── Models ────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"
LLM_PROVIDER    = "groq"

# Set to False if using a paid API tier with high rate limits
RESPECT_RATE_LIMITS = True

CHUNK_SIZE_WORDS    = 300
CHUNK_OVERLAP_WORDS = 60

TOP_K_CHUNKS       = 2
MAJORITY_THRESHOLD = 3

COMPANIES = ["HackerRank", "Claude", "Visa"]

HIGH_RISK_KEYWORDS = [
    "fraud", "stolen", "identity theft", "hack", "compromised",
    "unauthorized", "scam", "chargeback", "dispute", "legal",
    "lawyer", "sue", "police", "emergency", "stolen card",
    "account takeover", "security breach", "vulnerability"
]

ALLOWED_STATUS       = {"replied", "escalated"}
ALLOWED_REQUEST_TYPE = {"product_issue", "feature_request", "bug", "invalid"}

# Semantic Caching Config
CACHE_COLLECTION = "triage_cache"
CACHE_THRESHOLD = 0.25 # Lower is stricter. 0.25 means "very similar meaning"