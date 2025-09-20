"""
AutoHonk Plugin for Elite Dangerous Market Connector (EDMC)
Automatically sends a keypress when entering a new system to trigger the Discovery Scanner (honk)

Author: Generated for user request
Version: 1.0.0
"""

import sys
import os
import logging
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any

# Import for keypress simulation
if sys.platform == "win32":
    import win32api
    import win32con
    import win32gui
elif sys.platform == "darwin":
    # macOS - using subprocess for osascript
    import subprocess
elif sys.platform.startswith("linux"):
    # Linux - using subprocess for xdotool
    import subprocess

# Plugin metadata
plugin_name = "AutoHonk"
plugin_version = "1.0.0"

# Global variables
logger = logging.getLogger(f'{plugin_name}.{os.path.basename(os.path.dirname(__file__))}')
current_system = None
config = {
    'enabled': True,
    'key_to_press': '1',  # Default key (usually discovery scanner)
    'delay_seconds': 2.0,  # Delay after system entry before honking
    'hold_duration': 0.1   # How long to hold the key
}

# Tkinter variables for settings
enabled_var = None
key_var = None
delay_var = None
hold_var = None

def plugin_start3(plugin_dir: str) -> str:
    """
    Start the plugin.
    
    Args:
        plugin_dir: The plugin directory
        
    Returns:
        Plugin name or error message
    """
    global enabled_var, key_var, delay_var, hold_var
    
    logger.info(f"AutoHonk Plugin {plugin_version} starting")
    
    # Initialize tkinter variables for settings
    enabled_var = tk.BooleanVar(value=config['enabled'])
    key_var = tk.StringVar(value=config['key_to_press'])
    delay_var = tk.DoubleVar(value=config['delay_seconds'])
    hold_var = tk.DoubleVar(value=config['hold_duration'])
    
    return plugin_name

def plugin_stop() -> None:
    """Stop the plugin."""
    logger.info("AutoHonk Plugin stopping")

def plugin_prefs(parent: tk.Tk, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    """
    Create the preferences panel for the plugin.
    
    Args:
        parent: Parent window
        cmdr: Commander name
        is_beta: Whether this is beta
        
    Returns:
        Frame containing preferences
    """
    frame = tk.Frame(parent)
    frame.columnconfigure(1, weight=1)
    
    # Enabled checkbox
    row = 0
    tk.Checkbutton(
        frame,
        text="Enable AutoHonk",
        variable=enabled_var
    ).grid(row=row, column=0, columnspan=2, sticky="w")
    
    # Key to press
    row += 1
    tk.Label(frame, text="Key to press:").grid(row=row, column=0, sticky="w")
    key_entry = tk.Entry(frame, textvariable=key_var, width=5)
    key_entry.grid(row=row, column=1, sticky="w", padx=(10, 0))
    
    # Delay
    row += 1
    tk.Label(frame, text="Delay (seconds):").grid(row=row, column=0, sticky="w")
    delay_spinbox = tk.Spinbox(
        frame, 
        from_=0.1, 
        to=10.0, 
        increment=0.1, 
        textvariable=delay_var, 
        width=10,
        format="%.1f"
    )
    delay_spinbox.grid(row=row, column=1, sticky="w", padx=(10, 0))
    
    # Hold duration
    row += 1
    tk.Label(frame, text="Hold duration (seconds):").grid(row=row, column=0, sticky="w")
    hold_spinbox = tk.Spinbox(
        frame, 
        from_=0.05, 
        to=2.0, 
        increment=0.05, 
        textvariable=hold_var, 
        width=10,
        format="%.2f"
    )
    hold_spinbox.grid(row=row, column=1, sticky="w", padx=(10, 0))
    
    # Help text
    row += 1
    help_text = tk.Label(
        frame,
        text="AutoHonk will automatically press the specified key when entering a new system.\n"
             "Make sure the key matches your Discovery Scanner binding in-game.",
        wraplength=400,
        justify="left"
    )
    help_text.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
    
    return frame

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Handle preferences changes.
    
    Args:
        cmdr: Commander name
        is_beta: Whether this is beta
    """
    global config
    
    config['enabled'] = enabled_var.get()
    config['key_to_press'] = key_var.get()
    config['delay_seconds'] = delay_var.get()
    config['hold_duration'] = hold_var.get()
    
    logger.info(f"AutoHonk preferences updated: {config}")

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]) -> None:
    """
    Handle journal entries.
    
    Args:
        cmdr: Commander name
        is_beta: Whether this is beta
        system: Current system
        station: Current station
        entry: Journal entry
        state: Current state
    """
    global current_system
    
    if not config['enabled']:
        return
    
    # Check for FSDJump event (entering a new system)
    if entry.get('event') == 'FSDJump':
        new_system = entry.get('StarSystem')
        if new_system and new_system != current_system:
            logger.info(f"Entered new system: {new_system}")
            current_system = new_system
            
            # Schedule the honk with a delay
            threading.Thread(
                target=delayed_honk,
                args=(config['delay_seconds'], config['key_to_press'], config['hold_duration']),
                daemon=True
            ).start()
    
    # Also handle StartUp and LoadGame events in case we missed the jump
    elif entry.get('event') in ('StartUp', 'LoadGame'):
        if system and system != current_system:
            current_system = system
            logger.info(f"System on startup/load: {system}")

def delayed_honk(delay: float, key: str, hold_duration: float) -> None:
    """
    Send a keypress after a delay.
    
    Args:
        delay: Delay in seconds before pressing key
        key: Key to press
        hold_duration: How long to hold the key
    """
    time.sleep(delay)
    send_keypress(key, hold_duration)
    logger.info(f"AutoHonk: Pressed {key} for {hold_duration}s")

def send_keypress(key: str, hold_duration: float) -> None:
    """
    Send a keypress to the active window.
    
    Args:
        key: Key to press
        hold_duration: How long to hold the key
    """
    try:
        if sys.platform == "win32":
            send_keypress_windows(key, hold_duration)
        elif sys.platform == "darwin":
            send_keypress_macos(key, hold_duration)
        elif sys.platform.startswith("linux"):
            send_keypress_linux(key, hold_duration)
        else:
            logger.warning(f"Unsupported platform: {sys.platform}")
    except Exception as e:
        logger.error(f"Failed to send keypress: {e}")

def send_keypress_windows(key: str, hold_duration: float) -> None:
    """Send keypress on Windows using win32api."""
    # Get the virtual key code
    vk_code = ord(key.upper()) if len(key) == 1 else get_windows_vk_code(key)
    
    if vk_code is None:
        logger.error(f"Unknown key: {key}")
        return
    
    # Send key down
    win32api.keybd_event(vk_code, 0, 0, 0)
    time.sleep(hold_duration)
    # Send key up
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)

def send_keypress_macos(key: str, hold_duration: float) -> None:
    """Send keypress on macOS using osascript."""
    # Convert key to AppleScript key code if needed
    script = f'tell application "System Events" to keystroke "{key}"'
    subprocess.run(['osascript', '-e', script], capture_output=True)

def send_keypress_linux(key: str, hold_duration: float) -> None:
    """Send keypress on Linux using xdotool."""
    # Send key down
    subprocess.run(['xdotool', 'keydown', key], capture_output=True)
    time.sleep(hold_duration)
    # Send key up  
    subprocess.run(['xdotool', 'keyup', key], capture_output=True)

def get_windows_vk_code(key: str) -> Optional[int]:
    """
    Get Windows virtual key code for special keys.
    
    Args:
        key: Key name
        
    Returns:
        Virtual key code or None if unknown
    """
    special_keys = {
        'space': win32con.VK_SPACE,
        'enter': win32con.VK_RETURN,
        'tab': win32con.VK_TAB,
        'escape': win32con.VK_ESCAPE,
        'shift': win32con.VK_SHIFT,
        'ctrl': win32con.VK_CONTROL,
        'alt': win32con.VK_MENU,
        'f1': win32con.VK_F1,
        'f2': win32con.VK_F2,
        'f3': win32con.VK_F3,
        'f4': win32con.VK_F4,
        'f5': win32con.VK_F5,
        'f6': win32con.VK_F6,
        'f7': win32con.VK_F7,
        'f8': win32con.VK_F8,
        'f9': win32con.VK_F9,
        'f10': win32con.VK_F10,
        'f11': win32con.VK_F11,
        'f12': win32con.VK_F12,
    }
    
    return special_keys.get(key.lower())

# Required plugin entry points
if __name__ == "__main__":
    # This allows testing the plugin independently
    print(f"AutoHonk Plugin {plugin_version}")
    print("This is an EDMC plugin and should be placed in the plugins directory.")
