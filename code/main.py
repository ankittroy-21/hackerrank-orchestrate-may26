import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from rich.console import Console
from rich.panel import Panel
from ingestion.embedder import embed_corpus
from pipeline.runner import run

console = Console()

def main():
    console.print(Panel.fit(
        "[bold cyan]HackerRank Orchestrate[/bold cyan]\n"
        "[white]Multi-Domain Support Triage Agent[/white]\n"
        "[dim]Domains: HackerRank · Claude · Visa[/dim]",
        border_style="cyan"
    ))

    console.print("\n[yellow]Step 1: Checking corpus...[/yellow]")
    embed_corpus()

    console.print("\n[yellow]Step 2: Running triage pipeline...[/yellow]")
    run()

if __name__ == "__main__":
    main()