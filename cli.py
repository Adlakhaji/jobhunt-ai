"""Command-line interface for TinyFish Job & Internship Scraper."""
import argparse
import sys
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from app.db import init_db, list_jobs, list_portals, get_stats, get_active_profile
from app.scraper import scraper
from app.tinyfish_client import tinyfish_service
from app.config import settings

console = Console()

def cmd_scrape(args):
    init_db()
    console.print(Panel.fit(
        "[bold cyan]TinyFish Agentic Job & Internship Scraper[/bold cyan]\n"
        "[italic]Pulling live openings, matching roles, location, and seniority[/italic]",
        border_style="cyan"
    ))

    profile = get_active_profile()
    if profile:
        console.print(f"[bold]Active Profile:[/bold] {profile['title']}")
        console.print(f"[dim]Roles: {profile['roles']}[/dim]")
        console.print(f"[dim]Locations: {profile['locations']} | Seniorities: {profile['seniorities']}[/dim]\n")

    portals = list_portals(only_enabled=True)
    if not portals:
        console.print("[yellow]No enabled career portals found. Run `python cli.py portals` to configure.[/yellow]")
        return

    console.print(f"Targeting [bold green]{len(portals)}[/bold green] company career portals...\n")

    def cli_progress(evt):
        stage = evt.get("stage", "")
        msg = evt.get("message", "")
        if stage == "portal_start":
            console.print(f"[bold blue]►[/bold blue] {msg}")
        elif stage == "agent_step":
            console.print(f"  [dim cyan]•[/dim cyan] {msg}")
        elif stage == "portal_complete":
            console.print(f"  [bold green]✓[/bold green] {msg}\n")
        elif stage == "jobhunt_complete":
            console.print(f"[bold green]✔ {msg}[/bold green]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Crawling portals with TinyFish...", total=None)
        res = scraper.run_all(event_callback=cli_progress)

    cmd_list(args)

def cmd_list(args):
    init_db()
    min_score = getattr(args, "min_score", 40)
    role_filter = getattr(args, "role", None)
    loc_filter = getattr(args, "location", None)
    sen_filter = getattr(args, "seniority", None)
    limit = getattr(args, "limit", 25)

    jobs = list_jobs(
        role=role_filter,
        location=loc_filter,
        seniority=sen_filter,
        min_score=min_score,
        limit=limit,
        sort_by="match_score"
    )

    if not jobs:
        console.print("[yellow]No matching jobs found in local database. Run `python cli.py scrape` first![/yellow]")
        return

    table = Table(title=f"Matched Openings (Showing top {len(jobs)})", show_lines=True)
    table.add_column("Score", style="bold magenta", width=8, justify="center")
    table.add_column("Company", style="bold cyan", width=16)
    table.add_column("Job Title", style="white", min_width=24)
    table.add_column("Seniority", style="yellow", width=14)
    table.add_column("Location & Mode", style="green", width=22)
    table.add_column("Apply URL", style="blue", min_width=28)

    for j in jobs:
        score = j.get("match_score", 0)
        score_color = "bold green" if score >= 80 else ("bold yellow" if score >= 60 else "cyan")
        score_badge = f"[{score_color}]{score}%[/{score_color}]"
        
        mode = j.get("work_mode", "Remote")
        loc_display = f"{j.get('location', 'Remote')}\n[dim]({mode})[/dim]"

        table.add_row(
            score_badge,
            j.get("company", ""),
            f"[bold]{j.get('title', '')}[/bold]",
            j.get("seniority", "Entry Level"),
            loc_display,
            j.get("apply_url") or j.get("url") or ""
        )

    console.print(table)
    console.print(f"[dim]Tip: Launch the Web UI with `python cli.py serve` to view match breakdown, filter interactively, or track application status.[/dim]\n")

def cmd_portals(args):
    init_db()
    portals = list_portals()
    table = Table(title="Configured Target Career Portals")
    table.add_column("ID", justify="center", width=4)
    table.add_column("Portal / Company", style="bold cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Status", justify="center")
    table.add_column("Career URL", style="dim blue")

    for p in portals:
        status = "[bold green]Active[/bold green]" if p["enabled"] else "[red]Disabled[/red]"
        table.add_row(
            str(p["id"]),
            p["name"],
            p.get("category", "Tech"),
            p.get("portal_type", "career_page"),
            status,
            p["url"]
        )

    console.print(table)

def cmd_stats(args):
    init_db()
    stats = get_stats()
    tf_status = "[bold green]Configured & Active[/bold green]" if tinyfish_service.is_configured() else "[yellow]Key pending (agent simulation & feeds active)[/yellow]"

    panel = Panel(
        f"[bold]TinyFish Agent Status:[/bold] {tf_status}\n\n"
        f"• [bold green]{stats['total_active_jobs']}[/bold green] Total Active Openings Indexed\n"
        f"• [bold magenta]{stats['high_matches']}[/bold magenta] High Match (Score ≥ 70%)\n"
        f"• [bold yellow]{stats['bookmarked']}[/bold yellow] Bookmarked Roles\n"
        f"• [bold blue]{stats['applied']}[/bold blue] Applications In Progress\n"
        f"• [bold cyan]{stats['active_portals']}[/bold cyan] / {stats['total_portals']} Target Portals Active\n",
        title="JobHunt AI Summary",
        border_style="cyan"
    )
    console.print(panel)

def cmd_serve(args):
    import uvicorn
    init_db()
    port = getattr(args, "port", settings.port)
    host = getattr(args, "host", settings.host)
    url = f"http://{host}:{port}"
    console.print(f"\n[bold green]🚀 Launching TinyFish Job Scraper Web Dashboard on {url}...[/bold green]")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    uvicorn.run("main:app", host=host, port=port, reload=False)

def main():
    parser = argparse.ArgumentParser(description="TinyFish-powered Job & Internship Scraper CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Scrape
    p_scrape = subparsers.add_parser("scrape", help="Trigger a live scrape run across portals")
    p_scrape.add_argument("--min-score", type=int, default=40, help="Minimum match score threshold")
    p_scrape.add_argument("--role", type=str, help="Filter role keyword")
    p_scrape.add_argument("--location", type=str, help="Filter location")
    p_scrape.add_argument("--seniority", type=str, help="Filter seniority")
    p_scrape.add_argument("--limit", type=int, default=25, help="Number of jobs to show")

    # List
    p_list = subparsers.add_parser("list", help="List matched jobs in the database")
    p_list.add_argument("--min-score", type=int, default=40, help="Minimum match score threshold")
    p_list.add_argument("--role", type=str, help="Filter role keyword")
    p_list.add_argument("--location", type=str, help="Filter location")
    p_list.add_argument("--seniority", type=str, help="Filter seniority")
    p_list.add_argument("--limit", type=int, default=25, help="Number of jobs to show")

    # Portals
    subparsers.add_parser("portals", help="List configured target career portals")

    # Stats
    subparsers.add_parser("stats", help="Display system statistics")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Run the FastAPI Web UI Dashboard")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to bind server")
    p_serve.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind server")

    args = parser.parse_args()

    if args.command == "scrape":
        cmd_scrape(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "portals":
        cmd_portals(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        # Default action: show stats & scrape
        cmd_scrape(args)

if __name__ == "__main__":
    main()
