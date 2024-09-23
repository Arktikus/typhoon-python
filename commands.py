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

import os
import sys
import requests
from rich.console import Console
from rich.progress import Progress
from config import VERSION

console = Console()

# Define all commands with arguments
commands = {
    "version": lambda: console.print(f"[bold magenta]typhoon[/bold magenta] [bold cyan]Version: {VERSION}[/bold cyan]"),
    "commands": lambda: list_commands(),
    "info": lambda cmd=None: command_info(cmd),
    "greet": {
        'func': lambda name, times=1: greet_user(name, times),  # Function with multiple arguments
        'args': ["name", "times"]  # Possible arguments for autocompletion
    },
    "locate": {
        'func': lambda filename: locate_file(filename),  # Function for locate command
        'args': ["filename"]  # Possible arguments for autocompletion
    },
    "download": {
        'func': lambda url: download_command(url), # Function to download a file or directory
        'args': ["url"], # Possible arguments for autocompletion
        'aliases': ['dl']  # Alias for download command
    },
    "calc": {
        'func': lambda *args: calc_command(" ".join(args)),
        'args': ["expression"],
        'aliases': ['c']  # Alias for calc command
    },
    "clear": lambda: clear_command(), # Clears the screen
    "exit": lambda: exit_command() # Function to exit
}

def execute_command(user_input):
    # Split input into command and arguments
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]

    # Iterate over the commands to find a match
    for cmd, details in commands.items():
        # Check if the command matches or if aliases are defined and match
        if cmd == command or (isinstance(details, dict) and 'aliases' in details and command in details['aliases']):
            if isinstance(details, dict) and 'func' in details:
                # Handle commands with arguments
                details['func'](*args)
            else:
                # Handle simple commands (like 'version', 'clear', etc.)
                details(*args)
            return

    # If no matching command is found, display an error message
    console.print(f"[bold red]Unknown command:[/bold red] {command}. \nUse 'commands' to get a list of all available commands.")

def exit_command():
    # Exits the application
    sys.exit(0)

def clear_command():
    # Clears the screen
    os.system('cls' if os.name == 'nt' else 'clear')

def list_commands():
    # List all commands and their aliases
    console.print("[bold yellow]Available commands:[/bold yellow]")
    for cmd, details in commands.items():
        aliases = ""
        if isinstance(details, dict) and 'aliases' in details:
            aliases = f" (aliases: {', '.join(details['aliases'])})"
        console.print(f"- [cyan]{cmd}[/cyan]{aliases}")

def command_info(command_name=None):
    # Information about a specific command
    if command_name and command_name in commands:
        console.print(f"[bold green]Information about command:[/bold green] {command_name}")
        # Detailed information for each command
        if command_name == "version":
            console.print("Shows the current version of typhoon.")
        elif command_name == "commands":
            console.print("Lists all available commands.")
        elif command_name == "info":
            console.print("Shows information about a specific command. Usage: info [command_name].")
        elif command_name == "greet":
            console.print("Greets a person X times. Usage: greet [name] [times].")
        elif command_name == "locate":
            console.print("Finds files in the filesystem. Usage: locate [filename].")
        elif command_name == "download":
            console.print("Downloads a file. Usage: download [url]")
        elif command_name == "calc":
            console.print("Calculates an expression. Usage: calc [expression] (spaces don't matter and you can use +,-,*,/,** and %)")
        elif command_name == "exit":
            console.print("Exits typhoon.")
        elif command_name == 'clear':
            console.print("Clears the screen.")
    else:
        console.print("[bold red]This command wasn't found.[/bold red]")

def calc_command(expression):
    """Safely evaluate a mathematical expression."""
    try:
        # Define a safe set of allowed operators and functions
        allowed_names = {
            "__builtins__": None,  # Disable all built-ins
        }
        
        # Evaluate the expression with allowed names only
        result = eval(expression, {"__builtins__": None}, allowed_names)
        console.print(f"[bold green]Result:[/bold green] {result}")
    except Exception as e:
        console.print(f"[bold red]Error evaluating expression:[/bold red] {str(e)}")

def download_command(url):
    try:
        console.print(f"[bold cyan]Downloading from: {url}...[/bold cyan]")

        # Initialize the download request
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 # 1 Kilobyte

        if response.status_code != 200:
            console.print(f"[bold red]Failed to connect: {response.status_code} {response.reason}[/bold red]")
            return

        filename = url.split("/")[-1]
        progress_text = f"[cyan]Downloading {filename}...[/cyan]"
        
        # Using Progress to display a download bar
        with Progress() as progress:
            task = progress.add_task(progress_text, total=total_size)
            with open(filename, "wb") as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    progress.update(task, advance=len(data))

        console.print("[bold green]Download completed successfully![/bold green]")

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {str(e)}[/bold red]")

def greet_user(name, times=1):
    # Example command with multiple arguments and progress bar
    try:
        times = int(times)  # Ensure the number is an integer
    except ValueError:
        console.print("[bold red]Error: Must be a number.[/bold red]")
        return

    with Progress() as progress:
        task = progress.add_task(f"[cyan]Sending greetings to {name}...[/cyan]", total=times)
        for _ in range(times):
            progress.update(task, advance=1)
            console.print(f"[bold green]Hello, {name}![/bold green]")

def locate_file(filename):
    # Function to search for a file in the filesystem
    found_files = []
    search_directory = "/"

    console.print(f"[bold cyan]Searching for '{filename}' in Directory {search_directory}...[/bold cyan]")
    
    # Count the total number of directories for the progress bar
    total_dirs = sum([len(dirs) for _, dirs, _ in os.walk(search_directory)])
    progress_update_value = 100 / total_dirs if total_dirs > 0 else 1

    with Progress() as progress:
        task = progress.add_task("[cyan]Searching...[/cyan]", total=100)
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                if filename.lower() in file.lower():
                    found_files.append(os.path.join(root, file))
            
            # Update the progress bar based on the number of directories searched
            progress.update(task, advance=progress_update_value)
        
        progress.update(task, completed=100)  # Set the progress bar to 100% when finished

    if found_files:
        console.print(f"[bold green]Found file(s):[/bold green]")
        for file_path in found_files:
            console.print(file_path)
    else:
        console.print(f"[bold red]No file found named: '{filename}'[/bold red]")

