import threading
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich import box

from core.engine import AssistantEngine
from config import WAKE_WORD


console = Console()

BANNER = """
[bold cyan]    ██╗  ██╗ ██████╗ ██████╗ ██████╗ ██╗   ██╗
    ██║ ██╔╝██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
    █████╔╝ ██║   ██║██████╔╝██████╔╝ ╚████╔╝
    ██╔═██╗ ██║   ██║██╔══██╗██╔══██╗  ╚██╔╝
    ██║  ██╗╚██████╔╝██████╔╝██████╔╝   ██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝    ╚═╝[/bold cyan]
"""

STATUS_ICONS = {
    "idle": "[dim]●[/dim] Idle",
    "waiting": "[yellow]◉ Listening for wake word...[/yellow]",
    "listening": "[green]◉ Recording...[/green]",
    "thinking": "[blue]◉ Thinking...[/blue]",
    "executing": "[magenta]◉ Executing...[/magenta]",
    "speaking": "[cyan]◉ Speaking...[/cyan]",
    "error": "[red]● Error[/red]",
}


class JarvisTUI:
    def __init__(self):
        self.engine = AssistantEngine(callback=self.on_event)
        self.running = False
        self.current_status = "idle"
        self.history = []

    def on_event(self, event_type: str, data: str):
        if event_type == "status":
            self.current_status = data

    def clear_screen(self):
        console.clear()

    def show_banner(self):
        self.clear_screen()
        console.print(BANNER)
        console.print(Panel(
            f"[bold]Desktop AI Assistant[/bold]\n"
            f"[dim]Say '[/dim][bold cyan]{WAKE_WORD}[/bold cyan][dim]' to activate[/dim]\n"
            f"[dim]Or type a command below[/dim]",
            title="[bold green]● ONLINE[/bold green]",
            border_style="green",
        ))
        console.print()

    def show_status(self):
        status_text = STATUS_ICONS.get(self.current_status, f"[dim]● {self.current_status}[/dim]")
        console.print(f"  {status_text}", end="\r")

    def show_response(self, user_input: str, response: str):
        console.print()
        console.print(Panel(
            f"[bold white]{user_input}[/bold white]",
            title="[bold yellow]You[/bold yellow]",
            border_style="yellow",
            width=80,
        ))
        console.print(Panel(
            response,
            title="[bold cyan]Jarvis[/bold cyan]",
            border_style="cyan",
            width=80,
        ))
        self.history.append({
            "input": user_input,
            "response": response,
            "time": datetime.now().strftime("%H:%M:%S"),
        })

    def show_history(self):
        if not self.history:
            console.print("[dim]No conversation history yet.[/dim]")
            return
        table = Table(title="Conversation History", box=box.ROUNDED)
        table.add_column("Time", style="dim")
        table.add_column("You", style="yellow")
        table.add_column("Jarvis", style="cyan")
        for entry in self.history[-10:]:
            table.add_row(
                entry["time"],
                entry["input"][:50],
                entry["response"][:80],
            )
        console.print(table)

    def process_text_input(self, text: str):
        if text.lower() in ["exit", "quit", "q"]:
            self.running = False
            console.print("\n[bold red]Shutting down...[/bold red]")
            self.engine.stop()
            return

        if text.lower() in ["history", "h"]:
            self.show_history()
            return

        if text.lower() in ["status", "s"]:
            self.show_status()
            console.print()
            return

        if text.lower() in ["clear", "cls"]:
            self.show_banner()
            return

        self.current_status = "thinking"
        self.show_status()

        response = self.engine.run_interactive(text)
        self.current_status = "idle"
        self.show_response(text, response)

    def run(self):
        self.show_banner()
        self.running = True

        wake_thread = threading.Thread(target=self._wake_word_loop, daemon=True)
        wake_thread.start()

        console.print("[bold green]Jarvis is ready![/bold green]")
        console.print("[dim]Type a command or wait for wake word...[/dim]\n")

        try:
            while self.running:
                try:
                    user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
                    if user_input.strip():
                        self.process_text_input(user_input.strip())
                except EOFError:
                    break
        except KeyboardInterrupt:
            console.print("\n[bold red]Shutting down...[/bold red]")
        finally:
            self.running = False
            self.engine.stop()

    def _wake_word_loop(self):
        try:
            def on_wake():
                import time
                self.current_status = "listening"
                console.print("\n[bold cyan]Wake word detected![/bold cyan]")
                try:
                    text = self.engine.stt.record_and_transcribe()
                    if text:
                        console.print(f"[yellow]You said:[/yellow] {text}")
                        response = self.engine.process_input(text)
                        self.engine.speak(response)
                        self.show_response(text, response)
                    else:
                        console.print("[dim]Could not understand audio.[/dim]")
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                self.current_status = "idle"
                time.sleep(1)

            while self.running:
                self.engine.wakeword.listen(on_wake)
        except Exception:
            pass


def main():
    tui = JarvisTUI()
    tui.run()


if __name__ == "__main__":
    main()
