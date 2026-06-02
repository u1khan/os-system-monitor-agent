"""
OS System Monitor Agent
Student: Aibek Ulkhanov | ID: 24013558
Milestone 2 - Full Implementation

Architecture: Observe → Think → Act loop
"""

import psutil
import time
import logging
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich import box

# ─── Configuration ────────────────────────────────────────────────────────────
THRESHOLDS = {
    "cpu":  80,   # % CPU usage
    "ram":  85.0,   # % RAM usage
    "disk": 90.0,   # % Disk usage
}
POLL_INTERVAL   = 5          # seconds between checks
TOP_N_PROCESSES = 5          # how many top processes to show
LOG_FILE        = "monitor.log"

# ─── Setup ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console = Console()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — OBSERVE
# ══════════════════════════════════════════════════════════════════════════════
def observe():
    """Collect real-time system metrics via psutil."""
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            if info["cpu_percent"] is not None:
                processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    processes.sort(key=lambda p: p["cpu_percent"] or 0, reverse=True)

    return {
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu":        cpu,
        "ram":        ram.percent,
        "ram_used":   ram.used // (1024 ** 2),
        "ram_total":  ram.total // (1024 ** 2),
        "disk":       disk.percent,
        "disk_used":  disk.used // (1024 ** 3),
        "disk_total": disk.total // (1024 ** 3),
        "processes":  processes[:TOP_N_PROCESSES],
    }


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — THINK
# ══════════════════════════════════════════════════════════════════════════════
def think(metrics):
    """Compare metrics against thresholds; return list of alerts."""
    alerts = []
    if metrics["cpu"]  > THRESHOLDS["cpu"]:
        alerts.append(("CPU",  metrics["cpu"],  THRESHOLDS["cpu"]))
    if metrics["ram"]  > THRESHOLDS["ram"]:
        alerts.append(("RAM",  metrics["ram"],  THRESHOLDS["ram"]))
    if metrics["disk"] > THRESHOLDS["disk"]:
        alerts.append(("Disk", metrics["disk"], THRESHOLDS["disk"]))
    return alerts


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — ACT
# ══════════════════════════════════════════════════════════════════════════════
def act(metrics, alerts):
    """Print dashboard, log alerts, optionally kill top process."""
    _render_dashboard(metrics, alerts)

    for resource, value, threshold in alerts:
        msg = f"ALERT: {resource} usage {value:.1f}% exceeds threshold {threshold}%"
        logging.warning(msg)
        console.print(f"  [bold red]⚠  {msg}[/bold red]")

        # Optional: suggest killing top CPU process
        if resource == "CPU" and metrics["processes"]:
            top = metrics["processes"][0]
            console.print(
                f"  [yellow]→ Top offender: PID {top['pid']} "
                f"({top['name']}) — {top['cpu_percent']:.1f}% CPU[/yellow]"
            )
            logging.info(f"Top CPU offender: PID {top['pid']} {top['name']} {top['cpu_percent']:.1f}%")

    if not alerts:
        logging.info(
            f"OK | CPU={metrics['cpu']}% RAM={metrics['ram']}% Disk={metrics['disk']}%"
        )


# ─── Rich Dashboard ───────────────────────────────────────────────────────────
def _bar(pct, width=20):
    """Return a colored ASCII progress bar."""
    filled = int(width * pct / 100)
    bar    = "█" * filled + "░" * (width - filled)
    color  = "green" if pct < 70 else ("yellow" if pct < 85 else "red")
    return f"[{color}]{bar}[/{color}] {pct:.1f}%"


def _render_dashboard(metrics, alerts):
    """Print a compact Rich dashboard for one polling cycle."""
    status = "[bold red]⚠  ALERT[/bold red]" if alerts else "[bold green]✔  OK[/bold green]"

    console.rule(f"[bold cyan]OS Monitor Agent[/bold cyan]  {status}  [dim]{metrics['timestamp']}[/dim]")

    # Resource table
    res = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold cyan")
    res.add_column("Resource", style="bold", width=10)
    res.add_column("Usage Bar", width=35)
    res.add_column("Details", width=25)

    res.add_row("CPU",  _bar(metrics["cpu"]),  f"{metrics['cpu']:.1f}%  (threshold {THRESHOLDS['cpu']}%)")
    res.add_row("RAM",  _bar(metrics["ram"]),
                f"{metrics['ram_used']} / {metrics['ram_total']} MB")
    res.add_row("Disk", _bar(metrics["disk"]),
                f"{metrics['disk_used']} / {metrics['disk_total']} GB")
    console.print(res)

    # Top processes table
    proc = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta")
    proc.add_column("PID",    width=8)
    proc.add_column("Name",   width=22)
    proc.add_column("CPU %",  width=10)
    proc.add_column("MEM %",  width=10)

    for p in metrics["processes"]:
        cpu_color = "red" if (p["cpu_percent"] or 0) > 50 else "white"
        proc.add_row(
            str(p["pid"]),
            p["name"][:22],
            f"[{cpu_color}]{p['cpu_percent']:.1f}[/{cpu_color}]",
            f"{p['memory_percent']:.1f}",
        )
    console.print(Panel(proc, title="[bold]Top Processes[/bold]", border_style="magenta"))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════
def main():
    console.print(Panel.fit(
        "[bold cyan]OS System Monitor Agent[/bold cyan]\n"
        "[dim]Aibek Ulkhanov | 24013558[/dim]\n"
        f"Thresholds → CPU: {THRESHOLDS['cpu']}%  RAM: {THRESHOLDS['ram']}%  Disk: {THRESHOLDS['disk']}%\n"
        f"Poll interval: {POLL_INTERVAL}s  |  Log: {LOG_FILE}",
        border_style="cyan",
    ))

    cycle = 0
    try:
        while True:
            cycle += 1
            console.print(f"\n[dim]── Cycle {cycle} ──[/dim]")
            metrics = observe()          # Step 1
            alerts  = think(metrics)     # Step 2
            act(metrics, alerts)         # Step 3
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Agent stopped by user.[/bold yellow]")
        logging.info("Agent stopped by user.")


if __name__ == "__main__":
    main()
