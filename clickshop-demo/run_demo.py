#!/usr/bin/env python3
"""
ClickShop Demo Runner
Main entry point for running ClickShop demos
"""
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def show_menu():
    """Display demo selection menu"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🛍️  ClickShop Demo Suite[/bold cyan]\n"
        "[yellow]Agent Architecture Evolution[/yellow]",
        border_style="cyan"
    ))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Demo", style="yellow", width=30)
    table.add_column("Description", style="white")
    
    table.add_row(
        "1",
        "Phase 1: Single Agent",
        "Basic agent with Aurora DB (50 orders/day)"
    )
    table.add_row(
        "2",
        "Phase 2: MCP Tools",
        "Agent + specialized MCP tools (5K orders/day)"
    )
    table.add_row(
        "3",
        "Phase 3: Multi-Agent",
        "Supervisor pattern (50K orders/day)"
    )
    table.add_row(
        "q",
        "Quit",
        "Exit demo suite"
    )
    
    console.print(table)
    console.print()

def run_phase_1():
    """Run Phase 1 demo"""
    from demos.phase_1_single_agent import run_interactive_demo
    run_interactive_demo()

def run_phase_2():
    """Run Phase 2 demo"""
    from demos.phase_2_agent_mcp import run_interactive_demo
    run_interactive_demo()

def run_phase_3():
    """Run Phase 3 demo"""
    from demos.phase_3_multi_agent import run_interactive_demo
    run_interactive_demo()

def main():
    """Main demo runner"""
    while True:
        show_menu()
        choice = input("Select demo (1-3, q to quit): ").strip().lower()
        
        if choice == "1":
            try:
                run_phase_1()
            except KeyboardInterrupt:
                console.print("\n[yellow]Demo interrupted[/yellow]\n")
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]\n")
        elif choice == "2":
            run_phase_2()
        elif choice == "3":
            run_phase_3()
        elif choice == "q":
            console.print("\n[cyan]Thanks for trying ClickShop! 🚀[/cyan]\n")
            break
        else:
            console.print("\n[red]Invalid choice. Please try again.[/red]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Goodbye![/yellow]\n")
        sys.exit(0)
