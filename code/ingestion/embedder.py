import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CHROMA_DIR, CHROMA_COLLECTION, EMBEDDING_MODEL, COMPANIES
from ingestion.loader import load_documents
from ingestion.chunker import chunk_documents
import chromadb
from sentence_transformers import SentenceTransformer
from rich.console import Console
from rich.progress import track

console = Console()

def get_collection():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

def embed_corpus(force: bool = False):
    collection = get_collection()
    if not force and collection.count() > 0:
        console.print(f"[green]Corpus already embedded ({collection.count()} chunks). Skipping.[/green]")
        return collection

    console.print("[cyan]Loading documents...[/cyan]")
    docs = load_documents()
    console.print(f"[cyan]Loaded {len(docs)} documents. Chunking...[/cyan]")
    chunks = chunk_documents(docs)
    console.print(f"[cyan]Created {len(chunks)} chunks. Embedding...[/cyan]")

    model = SentenceTransformer(EMBEDDING_MODEL)

    BATCH = 64
    for start in track(range(0, len(chunks), BATCH), description="Embedding"):
        batch = chunks[start:start + BATCH]
        texts = [c["text"] for c in batch]
        ids   = [c["id"]   for c in batch]
        metas = [{
            "company":      c["company"],
            "product_area": c["product_area"],
            "title":        c["title"],
            "source_url":   c["source_url"]
        } for c in batch]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metas)

    console.print("\n[bold green]Embedding complete![/bold green]")
    for company in COMPANIES:
        results = collection.get(where={"company": company})
        console.print(f"  {company}: {len(results['ids'])} chunks")

    return collection

if __name__ == "__main__":
    embed_corpus()