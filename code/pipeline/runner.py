import pandas as pd
import time
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import config
from agent.triage import triage

console = Console()

def get_status_color(status: str, is_cache: bool, latency: float) -> str:
    # If it was instant but not a cache hit, it was a local safety catch!
    if is_cache:
        return "[bold cyan]CACHE HIT[/bold cyan]"
    if latency < 0.1: 
        return "[bold yellow]SAFETY OK[/bold yellow]"
    if status.lower() == "escalated":
        return "[bold red]ESCALATED[/bold red]"
    return "[bold green]REPLIED  [/bold green]"

def run():
    console.clear()
    
    header_panel = Panel.fit(
        "[bold blue]HackerRank Orchestrate[/bold blue]\n"
        "[dim]Multi-Domain Support Triage Agent[/dim]\n"
        "[dim]Domains: HackerRank · Claude · Visa[/dim]",
        border_style="blue",
        padding=(1, 5)
    )
    console.print(Align.center(header_panel))
    console.print("\n[bold magenta]Starting Live Triage Stream...[/bold magenta]\n")

    try:
        df = pd.read_csv(config.INPUT_CSV)
        df.columns = df.columns.str.lower()
    except FileNotFoundError:
        console.print(f"[red]Error: Could not find {config.INPUT_CSV}[/red]")
        return
    
    results = []

    for idx, row in df.iterrows():
        start_time = time.time()
        
        issue = str(row.get("issue", ""))
        subject = str(row.get("subject", ""))
        company = str(row.get("company", "None"))
        
        # Clean text for single-line display
        display_issue = issue.replace("\n", " ")
        display_issue = display_issue[:45] + "..." if len(display_issue) > 45 else display_issue.ljust(48)
        
        # Run Triage
        out = triage(issue, subject, company)
        
        # Calculate Latency
        latency = time.time() - start_time
        is_cache_hit = "[CACHE HIT]" in out.thought_process
        
        # SMART SLEEP: Only sleep if it took longer than 0.5s
        if config.RESPECT_RATE_LIMITS and latency > 0.5:
            time.sleep(2.5) 
            
        action_col = get_status_color(out.status, is_cache_hit, latency).ljust(20)
        latency_str = f"{latency:.2f}s".rjust(6)
        
        # Print a beautiful single-line log
        console.print(
            f"[dim]ID {idx + 1:02d}[/dim] │ "
            f"{display_issue} │ "
            f"{action_col} │ "
            f"[yellow]{out.product_area[:20].ljust(20)}[/yellow] │ "
            f"[cyan]{latency_str}[/cyan]"
        )
        
        row_dict = out.model_dump()
        results.append(row_dict)

    # Save to CSV
    output_df = pd.DataFrame(results)
    output_df.to_csv(config.OUTPUT_CSV, index=False)
    
    console.print(f"\n[bold green]✔ Triage Complete![/bold green] Results saved to [cyan]{config.OUTPUT_CSV}[/cyan]")