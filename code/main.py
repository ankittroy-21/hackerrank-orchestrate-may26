from pipeline.runner import run
from ingestion.embedder import embed_corpus
import warnings

warnings.filterwarnings("ignore")

def main():
    print("Step 1: Checking corpus...")
    embed_corpus()
    
    print("\nStep 2: Running triage pipeline...")
    run()

if __name__ == "__main__":
    main()