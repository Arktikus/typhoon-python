# Copyright (C) 2024 Arktikus
# 
# This file is part of typhoon.
#
# typhoon is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# typhoon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with typhoon. If not, see <http://www.gnu.org/licenses/>.
#
# GitHub Repository: https://github.com/Arktikus/typhoon
#
# Author: Arktikus

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress
from commands import execute_command, list_commands, commands
from config import VERSION

console = Console()
session = PromptSession()

prompt_style = Style.from_dict({
    'prompt': 'bold magenta'
})

# Custom Completer für Autocompletion
class CommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        words = text.split()

        # If input is empty show everything 
        if len(words) == 0:
            for cmd in commands.keys():
                yield Completion(cmd, start_position=0)

        # If command is entered show possible arguments 
        elif len(words) == 1:
            for cmd in commands.keys():
                if cmd.startswith(words[0]):
                    yield Completion(cmd, start_position=-len(words[0]))

        # If entered command is 'input' 
        elif len(words) > 1 and words[0] == "info":
            # Show all possible commands as argument for 'info' 
            for cmd in commands.keys():
                if cmd.startswith(words[1]):
                    yield Completion(cmd, start_position=-len(words[1]))

        # Wenn ein Befehl und Teile eines Arguments eingegeben wurden
        elif len(words) > 1:
            command = words[0]
            args = words[1:]
            if command in commands and hasattr(commands[command], 'args'):
                possible_args = commands[command].args
                for arg in possible_args:
                    if arg.startswith(args[-1]):
                        yield Completion(arg, start_position=-len(args[-1]))

def display_welcome_message():
    # Begrüßungsnachricht mit Rich Panel
    welcome_text = Text()
    welcome_text.append("Welcome to ", style="bold yellow")
    welcome_text.append("typhoon", style="bold magenta")
    welcome_text.append(f" v{VERSION}", style="bold cyan")
    console.print(Panel(welcome_text, expand=False, border_style="bold magenta"))

def display_commands_table():
    # Table of avaiable commands 
    table = Table(title="Available commands", border_style="yellow")
    table.add_column("Commands", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")

    table.add_row("version", "Shows the current version of typhoon")
    table.add_row("commands", "Lists all avaiable commands")
    table.add_row("info", "Shows information about a specific command")
    console.print(table)

def show_progress():
    # Example: Loading bar 
    with Progress() as progress:
        task = progress.add_task("[cyan]Loading...", total=100)
        for _ in range(100):
            progress.update(task, advance=1)

def main():
    completer = CommandCompleter()

    display_welcome_message()
    display_commands_table()

    while True:
        try:
            # User input with Autocompletion 
            user_input = session.prompt(HTML('<prompt>typhoon ></prompt> '), completer=completer, style=prompt_style).strip()
            if not user_input:
                continue

            if user_input == "load":
                show_progress()
            else:
                execute_command(user_input)

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Good Bye![/bold red]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main()
