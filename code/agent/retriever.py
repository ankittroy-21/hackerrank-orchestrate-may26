import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TOP_K_CHUNKS, MAJORITY_THRESHOLD, COMPANIES, EMBEDDING_MODEL
from ingestion.embedder import get_collection
from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def retrieve(query: str, company: str = None, top_k: int = TOP_K_CHUNKS) -> list[dict]:
    collection = get_collection()
    model = get_model()
    embedding = model.encode(query).tolist()

    where = {"company": company} if company and company != "None" else None

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            chunks.append({
                "text":         results["documents"][0][i],
                "metadata":     results["metadatas"][0][i],
                "distance":     results["distances"][0][i],
                "company":      results["metadatas"][0][i].get("company", ""),
                "product_area": results["metadatas"][0][i].get("product_area", "general"),
                "source_url":   results["metadatas"][0][i].get("source_url", "")
            })
    return chunks

def infer_company(query: str) -> str | None:
    chunks = retrieve(query, company=None, top_k=TOP_K_CHUNKS)
    if not chunks:
        return None
    votes = {}
    for chunk in chunks:
        c = chunk["company"]
        votes[c] = votes.get(c, 0) + 1
    top_company = max(votes, key=votes.get)
    if votes[top_company] >= MAJORITY_THRESHOLD:
        return top_company
    return None