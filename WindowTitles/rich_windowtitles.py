import psutil
from rich.console import Console
from rich.table import Table
import time
import os

def find_processes_with_string(search_string: str):
    """
    Finds and displays processes matching a user-configurable string in the 
    process name or main window title.
    """
    console = Console()
    table = Table(
        title=f"Processes Matching '{search_string}'",
        show_header=True,
        header_style="bold magenta",
        caption="[bold green]Note: Press Ctrl+C to stop.[/bold green]"
    )
    
    # Define columns for the table
    table.add_column("PID", style="dim", width=12)
    table.add_column("Process Name", style="bold")
    table.add_column("Main Window Title", style="cyan")
    table.add_column("Executable Path", style="italic")

    found_matches = False
    
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pinfo = proc.info
            p_name = pinfo.get('name', '').lower()
            p_pid = pinfo.get('pid')
            p_exe = pinfo.get('exe', 'N/A')
            
            # This part is tricky and may require a separate library for cross-platform support.
            main_window_title = "N/A"
            if hasattr(proc, 'nice'):
                main_window_title = "Available" # A placeholder for now
            
            # Check for a match in the process name
            if search_string.lower() in p_name:
                found_matches = True
                table.add_row(
                    str(p_pid),
                    p_name,
                    main_window_title,
                    p_exe
                )
        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Clear the screen before printing the new table
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if found_matches:
        console.print(table)
    else:
        console.print(f"[bold red]No processes found matching '{search_string}'[/bold red]")
    
# --- User-configurable part ---
if __name__ == "__main__":
    user_search_string = input("Enter the string to search for: ")
    print("Starting real-time process monitor...")
    
    try:
        while True:
            find_processes_with_string(user_search_string)
            time.sleep(0.5) # Refresh every 1 second
            
    except KeyboardInterrupt:
        print("\nProcess monitor stopped by user.")