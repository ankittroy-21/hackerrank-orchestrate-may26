import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import INPUT_CSV, OUTPUT_CSV
from agent.triage import triage
from rich.console import Console
from rich.progress import track
from rich.table import Table
import time
import config

console = Console()

def run():
    df = pd.read_csv(INPUT_CSV)
    results = []

    console.print(f"\n[bold cyan]Processing {len(df)} tickets...[/bold cyan]\n")

    for _, row in track(df.iterrows(), total=len(df), description="Triaging"):
        issue   = str(row.get("Issue", "")).strip()
        subject = str(row.get("Subject", "")).strip()
        company = str(row.get("Company", "None")).strip()

        if not issue or issue.lower() == "nan":
            results.append({
                "status": "escalated",
                "product_area": "general",
                "response": "Empty or invalid ticket.",
                "justification": "No issue content provided.",
                "request_type": "invalid"
            })
            continue

        out = triage(issue, subject, company)

        if config.RESPECT_RATE_LIMITS:
            time.sleep(2.5)
        results.append(out.model_dump())

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_CSV, index=False)
    console.print(f"\n[bold green]Done! Output written to {OUTPUT_CSV}[/bold green]")

    # Summary table
    table = Table(title="Triage Summary")
    table.add_column("Status", style="cyan")
    table.add_column("Count", style="magenta")
    for status, count in out_df["status"].value_counts().items():
        table.add_row(status, str(count))
    console.print(table)

    table2 = Table(title="Request Types")
    table2.add_column("Type", style="cyan")
    table2.add_column("Count", style="magenta")
    for rt, count in out_df["request_type"].value_counts().items():
        table2.add_row(rt, str(count))
    console.print(table2)