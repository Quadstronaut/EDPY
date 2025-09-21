"""
Minimal AutoHonk Test Plugin - For debugging EDMC integration
Save this as load.py in plugins/AutoHonkTest/ folder to test basic EDMC integration
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Dict, Any

# Plugin metadata
plugin_name = "AutoHonk Test"
plugin_version = "1.0.0"

# Setup logging
logger = logging.getLogger(__name__)

# Simple config
test_enabled = True
test_var = None
status_label = None

def plugin_start3(plugin_dir: str) -> str:
    """Start the plugin."""
    global test_var
    logger.info(f"AutoHonk Test Plugin {plugin_version} starting")
    logger.info(f"Plugin directory: {plugin_dir}")
    
    test_var = tk.BooleanVar(value=test_enabled)
    
    return plugin_name

def plugin_stop() -> None:
    """Stop the plugin."""
    logger.info("AutoHonk Test Plugin stopping")

def plugin_app(parent: tk.Frame) -> tk.Frame:
    """Create the main application UI."""
    global status_label
    
    frame = tk.Frame(parent)
    
    status_label = tk.Label(
        frame,
        text="AutoHonk Test - OK",
        fg="white",
        bg="green",
        padx=5,
        pady=2
    )
    status_label.pack()
    
    return frame

def plugin_prefs(parent: tk.Tk, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    """Create preferences panel."""
    frame = tk.Frame(parent)
    
    tk.Label(frame, text="AutoHonk Test Plugin").pack()
    tk.Checkbutton(frame, text="Test Enabled", variable=test_var).pack()
    tk.Label(frame, text="If you see this, the plugin structure is working!").pack()
    
    return frame

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """Handle preference changes."""
    global test_enabled
    test_enabled = test_var.get()
    logger.info(f"Test preferences changed: enabled={test_enabled}")

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]) -> None:
    """Handle journal entries."""
    event_type = entry.get('event')
    if event_type == 'FSDJump':
        logger.info(f"TEST: FSDJump detected to {entry.get('StarSystem')}")
        if status_label:
            status_label.config(text="AutoHonk Test - Jump Detected!", bg="orange")

if __name__ == "__main__":
    print(f"AutoHonk Test Plugin {plugin_version}")