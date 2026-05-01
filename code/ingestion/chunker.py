import hashlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS

def _chunk_words(words: list[str], size: int, overlap: int) -> list[list[str]]:
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(words[start:end])
        if end == len(words):
            break
        start += size - overlap
    return chunks

def chunk_documents(docs: list[dict]) -> list[dict]:
    chunks = []
    for doc in docs:
        words = doc["body"].split()
        if not words:
            continue
        word_chunks = _chunk_words(words, CHUNK_SIZE_WORDS, CHUNK_OVERLAP_WORDS)
        path_hash = hashlib.md5(doc["filepath"].encode()).hexdigest()[:8]
        product_area = doc["breadcrumbs"][0] if doc["breadcrumbs"] else "general"
        for i, wc in enumerate(word_chunks):
            text = doc["title"] + "\n\n" + " ".join(wc)
            chunks.append({
                "id":           f"{doc['company']}_{path_hash}_{i}",
                "text":         text,
                "company":      doc["company"],
                "product_area": product_area,
                "title":        doc["title"],
                "source_url":   doc["source_url"]
            })
    return chunks