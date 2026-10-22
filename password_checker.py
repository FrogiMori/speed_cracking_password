#!/usr/bin/env python3
"""
Password Strength Meter CLI
An interactive terminal application rating password strength from 0% to 100%.
"""

import sys
import os
import argparse
import getpass
import secrets
import string
import json
from evaluator import evaluate_password

# Try importing rich for enhanced UI, fallback to standard ANSI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress_bar import ProgressBar
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def generate_secure_password(length: int = 16) -> str:
    """Generates a cryptographically strong password rated > 90%."""
    if length < 12:
        length = 12
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    while True:
        pw = "".join(secrets.choice(chars) for _ in range(length))
        res = evaluate_password(pw)
        if res["score"] >= 90:
            return pw


def get_color_for_score(score: int) -> str:
    if score < 25:
        return "red"
    elif score < 50:
        return "yellow"
    elif score < 75:
        return "cyan"
    elif score < 90:
        return "blue"
    else:
        return "green"


def get_ansi_color(score: int) -> str:
    if score < 25:
        return "\033[91m"  # Red
    elif score < 50:
        return "\033[93m"  # Yellow
    elif score < 75:
        return "\033[96m"  # Cyan
    elif score < 90:
        return "\033[94m"  # Blue
    else:
        return "\033[92m"  # Green


def render_bar(score: int, width: int = 30) -> str:
    filled = int((score / 100) * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def display_rich_result(res: dict, show_password: str = None):
    color = get_color_for_score(res["score"])
    score = res["score"]
    rating = res["rating"]

    # Title panel
    title = f"Password Security Rating: [{color}]{score}% - {rating}[/{color}]"
    
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold white", justify="left")
    table.add_column(justify="left")

    # Visual Bar
    bar_str = f"[{color}]{render_bar(score, 32)}[/{color}] [bold {color}]{score}%[/bold {color}]"
    table.add_row("Strength Meter:", bar_str)
    
    if show_password:
        table.add_row("Password:", f"[italic yellow]{show_password}[/italic yellow]")
    table.add_row("Length:", f"{res['length']} characters")
    table.add_row("Entropy:", f"{res['entropy']} bits")
    
    # Character composition
    comp = []
    comp.append("[green]✓ a-z[/green]" if res["has_lower"] else "[red]✗ a-z[/red]")
    comp.append("[green]✓ A-Z[/green]" if res["has_upper"] else "[red]✗ A-Z[/red]")
    comp.append("[green]✓ 0-9[/green]" if res["has_digit"] else "[red]✗ 0-9[/red]")
    comp.append("[green]✓ Special[/green]" if res["has_symbol"] else "[red]✗ Special[/red]")
    table.add_row("Composition:", "  ".join(comp))

    # Crack time
    crack = res["crack_times"]
    table.add_row("Crack Time (GPU 100B/s):", f"[bold {color}]{crack['offline_gpu']}[/bold {color}]")
    table.add_row("Crack Time (Online Throttled):", f"{crack['online_throttled']}")

    # Feedback
    feedback_text = ""
    for tip in res["feedback"]:
        icon = "[green]✓[/green]" if score >= 80 and "Excellent" in tip else "[yellow]•[/yellow]"
        feedback_text += f"\n  {icon} {tip}"

    table.add_row("Feedback / Tips:", feedback_text.lstrip("\n"))

    panel = Panel(
        table,
        title=f"[bold]{title}[/bold]",
        border_style=color,
        expand=False,
        padding=(1, 2)
    )
    console.print(panel)


def display_ansi_result(res: dict, show_password: str = None):
    reset = "\033[0m"
    bold = "\033[1m"
    color = get_ansi_color(res["score"])
    score = res["score"]
    rating = res["rating"]

    print("\n" + "=" * 55)
    print(f" {bold}Password Security Rating:{reset} {color}{bold}{score}% - {rating}{reset}")
    print("=" * 55)

    bar = render_bar(score, 30)
    print(f" Strength Meter: {color}{bar}{reset} {bold}{score}%{reset}")
    
    if show_password:
        print(f" Password:       \033[33m{show_password}{reset}")
    print(f" Length:         {res['length']} characters")
    print(f" Entropy:        {res['entropy']} bits")

    comp = []
    comp.append("\033[92m✓ a-z\033[0m" if res["has_lower"] else "\033[91m✗ a-z\033[0m")
    comp.append("\033[92m✓ A-Z\033[0m" if res["has_upper"] else "\033[91m✗ A-Z\033[0m")
    comp.append("\033[92m✓ 0-9\033[0m" if res["has_digit"] else "\033[91m✗ 0-9\033[0m")
    comp.append("\033[92m✓ Special\033[0m" if res["has_symbol"] else "\033[91m✗ Special\033[0m")
    print(f" Composition:    {'  '.join(comp)}")

    crack = res["crack_times"]
    print(f" GPU Crack Time: {color}{crack['offline_gpu']}{reset}")
    print(f" Online Throttled: {crack['online_throttled']}")
    
    print("\n Feedback & Suggestions:")
    for tip in res["feedback"]:
        print(f"   • {tip}")
    print("=" * 55 + "\n")


def display_result(res: dict, show_password: str = None):
    if RICH_AVAILABLE:
        display_rich_result(res, show_password)
    else:
        display_ansi_result(res, show_password)


def run_interactive_mode(show_plain: bool = False):
    if RICH_AVAILABLE:
        console.print("[bold cyan]══════════════════════════════════════════════════════════[/bold cyan]")
        console.print("[bold white]      🔐 Password Security Strength Meter (0% - 100%)    [/bold white]")
        console.print("[bold cyan]══════════════════════════════════════════════════════════[/bold cyan]")
        console.print("[dim]Type your password to evaluate, 'gen' to generate, or 'q' to exit.[/dim]\n")
    else:
        print("==========================================================")
        print("      🔐 Password Security Strength Meter (0% - 100%)    ")
        print("==========================================================")
        print("Type your password to evaluate, 'gen' to generate, or 'q' to exit.\n")

    while True:
        try:
            prompt = "Enter Password (visible): " if show_plain else "Enter Password (hidden): "
            if show_plain:
                pw = input(prompt)
            else:
                pw = getpass.getpass(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Stay secure!")
            break

        if pw.strip().lower() in ('q', 'quit', 'exit'):
            print("Exiting. Stay secure!")
            break

        if pw.strip().lower() == 'gen':
            generated = generate_secure_password(16)
            res = evaluate_password(generated)
            if RICH_AVAILABLE:
                console.print(f"\n[bold green]🔑 Generated Strong Password:[/bold green] [bold yellow]{generated}[/bold yellow]")
            else:
                print(f"\n🔑 Generated Strong Password: {generated}")
            display_result(res, show_password=generated)
            continue

        res = evaluate_password(pw)
        display_result(res, show_password=pw if show_plain else None)


def main():
    parser = argparse.ArgumentParser(
        description="Password Strength Analyzer CLI (0%% - 100%%)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 password_checker.py
  python3 password_checker.py "MySuperSecret#2026!"
  python3 password_checker.py -s "MyPass123"
  python3 password_checker.py --generate --length 20
  python3 password_checker.py --json "Password123"
  echo "pass123" | python3 password_checker.py
        """
    )
    parser.add_argument("password", nargs="?", help="Password to evaluate (optional)")
    parser.add_argument("-s", "--show", action="store_true", help="Display the password in plain text")
    parser.add_argument("-g", "--generate", action="store_true", help="Generate a secure password (score >= 90%%)")
    parser.add_argument("-l", "--length", type=int, default=16, help="Length for generated password (default: 16)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("-f", "--file", type=str, help="Evaluate a list of passwords from a file")

    args = parser.parse_args()

    # Generator mode
    if args.generate:
        gen_pw = generate_secure_password(args.length)
        res = evaluate_password(gen_pw)
        if args.json:
            print(json.dumps({"password": gen_pw, "analysis": res}, indent=2))
        else:
            if RICH_AVAILABLE:
                console.print(f"\n[bold green]🔑 Generated Strong Password:[/bold green] [bold yellow]{gen_pw}[/bold yellow]")
            else:
                print(f"\n🔑 Generated Strong Password: {gen_pw}")
            display_result(res, show_password=gen_pw)
        return

    # File batch mode
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        batch_results = []
        for line in lines:
            res = evaluate_password(line)
            if args.json:
                batch_results.append({"password": line, "analysis": res})
            else:
                display_result(res, show_password=line if args.show else f"{line[:2]}***{line[-1:]}" if len(line) > 3 else "***")
        if args.json:
            print(json.dumps(batch_results, indent=2))
        return

    # Direct argument mode
    if args.password is not None:
        res = evaluate_password(args.password)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            display_result(res, show_password=args.password if args.show else None)
        return

    # Pipe/Stdin mode
    if not sys.stdin.isatty():
        input_data = sys.stdin.read().strip()
        if input_data:
            res = evaluate_password(input_data)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                display_result(res, show_password=input_data if args.show else None)
            return

    # Interactive mode
    run_interactive_mode(show_plain=args.show)


if __name__ == "__main__":
    main()
