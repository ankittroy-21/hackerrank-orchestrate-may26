import json
import uuid
from config import CHROMA_DIR, CACHE_COLLECTION, CACHE_THRESHOLD
from agent.retriever import get_model
from agent.schemas import TriageOutput
import chromadb

_cache_collection = None

def get_cache_collection():
    global _cache_collection
    if _cache_collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _cache_collection = client.get_or_create_collection(name=CACHE_COLLECTION)
    return _cache_collection

def check_cache(issue: str, company: str) -> TriageOutput | None:
    collection = get_cache_collection()
    if collection.count() == 0:
        return None
        
    model = get_model()
    embedding = model.encode(issue).tolist()
    where_filter = {"company": company} if company and company != "None" else None
    
    results = collection.query(
        query_embeddings=[embedding],
        n_results=1,
        where=where_filter,
        include=["metadatas", "distances"]
    )
    
    if results and results["distances"] and results["distances"][0]:
        distance = results["distances"][0][0]
        if distance < CACHE_THRESHOLD:
            cached_data = json.loads(results["metadatas"][0][0]["triage_json"])
            cached_data["thought_process"] = f"[CACHE HIT] " + cached_data.get("thought_process", "")
            return TriageOutput(**cached_data)
    return None

def save_to_cache(issue: str, company: str, output: TriageOutput):
    collection = get_cache_collection()
    model = get_model()
    embedding = model.encode(issue).tolist()
    
    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[issue],
        embeddings=[embedding],
        metadatas=[{
            "company": company or "None",
            "triage_json": output.model_dump_json()
        }]
    )