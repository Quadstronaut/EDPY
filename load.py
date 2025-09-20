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
import xml.etree.ElementTree as ET
from pathlib import Path
import glob

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
    'key_to_press': 'auto',  # 'auto' means detect from bindings, or specific key
    'delay_seconds': 2.0,  # Delay after system entry before honking
    'hold_duration': 0.1,   # How long to hold the key
    'auto_detect_key': True  # Whether to auto-detect primary fire key
}
detected_primary_fire_key = None

# Tkinter variables for settings
enabled_var = None
key_var = None
delay_var = None
hold_var = None
auto_detect_var = None
detected_key_label = None

def plugin_start3(plugin_dir: str) -> str:
    """
    Start the plugin.
    
    Args:
        plugin_dir: The plugin directory
        
    Returns:
        Plugin name or error message
    """
    global enabled_var, key_var, delay_var, hold_var, auto_detect_var, detected_primary_fire_key
    
    logger.info(f"AutoHonk Plugin {plugin_version} starting")
    
    # Initialize tkinter variables for settings
    enabled_var = tk.BooleanVar(value=config['enabled'])
    key_var = tk.StringVar(value=config['key_to_press'])
    delay_var = tk.DoubleVar(value=config['delay_seconds'])
    hold_var = tk.DoubleVar(value=config['hold_duration'])
    auto_detect_var = tk.BooleanVar(value=config['auto_detect_key'])
    
    # Try to detect the primary fire key from Elite Dangerous bindings
    detected_primary_fire_key = detect_primary_fire_key()
    if detected_primary_fire_key:
        logger.info(f"Detected primary fire key: {detected_primary_fire_key}")
    else:
        logger.warning("Could not detect primary fire key from bindings")
    
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
    global detected_key_label
    
    frame = tk.Frame(parent)
    frame.columnconfigure(1, weight=1)
    
    # Enabled checkbox
    row = 0
    tk.Checkbutton(
        frame,
        text="Enable AutoHonk",
        variable=enabled_var
    ).grid(row=row, column=0, columnspan=2, sticky="w")
    
    # Auto-detect key checkbox
    row += 1
    auto_detect_cb = tk.Checkbutton(
        frame,
        text="Auto-detect Primary Fire key from Elite Dangerous bindings",
        variable=auto_detect_var,
        command=on_auto_detect_changed
    )
    auto_detect_cb.grid(row=row, column=0, columnspan=2, sticky="w")
    
    # Detected key display
    row += 1
    detected_key_frame = tk.Frame(frame)
    detected_key_frame.grid(row=row, column=0, columnspan=2, sticky="w", pady=(5, 0))
    
    tk.Label(detected_key_frame, text="Detected key:").pack(side="left")
    detected_key_label = tk.Label(
        detected_key_frame, 
        text=detected_primary_fire_key or "Not found",
        fg="green" if detected_primary_fire_key else "red"
    )
    detected_key_label.pack(side="left", padx=(5, 0))
    
    refresh_btn = tk.Button(
        detected_key_frame,
        text="Refresh",
        command=refresh_detected_key
    )
    refresh_btn.pack(side="left", padx=(10, 0))
    
    # Manual key entry
    row += 1
    key_frame = tk.Frame(frame)
    key_frame.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
    
    tk.Label(key_frame, text="Manual key override:").pack(side="left")
    key_entry = tk.Entry(key_frame, textvariable=key_var, width=10)
    key_entry.pack(side="left", padx=(10, 0))
    
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
        text="AutoHonk will use your Primary Fire key when auto-detect is enabled.\n"
             "Otherwise, specify a manual key override. Common keys: space, 1, 2, f1, etc.\n"
             "The key will be pressed when entering a new system to trigger Discovery Scanner.",
        wraplength=500,
        justify="left"
    )
    help_text.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
    
    # Update initial state
    on_auto_detect_changed()
    
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
    config['auto_detect_key'] = auto_detect_var.get()
    
    logger.info(f"AutoHonk preferences updated: {config}")

def on_auto_detect_changed():
    """Handle changes to the auto-detect checkbox."""
    # This function can be used to enable/disable manual key entry
    pass

def refresh_detected_key():
    """Refresh the detected primary fire key."""
    global detected_primary_fire_key
    detected_primary_fire_key = detect_primary_fire_key()
    if detected_key_label:
        detected_key_label.config(
            text=detected_primary_fire_key or "Not found",
            fg="green" if detected_primary_fire_key else "red"
        )
    logger.info(f"Refreshed detected key: {detected_primary_fire_key}")

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
    
    # Determine which key to use
    actual_key = key
    if config['auto_detect_key'] and detected_primary_fire_key:
        actual_key = detected_primary_fire_key
    elif key == 'auto' and detected_primary_fire_key:
        actual_key = detected_primary_fire_key
    elif key == 'auto':
        actual_key = '1'  # Fallback default
    
    send_keypress(actual_key, hold_duration)
    logger.info(f"AutoHonk: Pressed {actual_key} for {hold_duration}s")

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

def get_elite_bindings_paths() -> list:
    """
    Get possible paths to Elite Dangerous bindings files.
    
    Returns:
        List of potential binding file paths
    """
    paths = []
    
    if sys.platform == "win32":
        # Windows paths
        local_appdata = os.environ.get('LOCALAPPDATA')
        if local_appdata:
            bindings_dir = Path(local_appdata) / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings"
            if bindings_dir.exists():
                # Look for .binds files
                paths.extend(glob.glob(str(bindings_dir / "*.binds")))
    elif sys.platform == "darwin":
        # macOS paths
        home = Path.home()
        bindings_dir = home / "Library" / "Application Support" / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings"
        if bindings_dir.exists():
            paths.extend(glob.glob(str(bindings_dir / "*.binds")))
    elif sys.platform.startswith("linux"):
        # Linux paths (if running under Wine or similar)
        home = Path.home()
        # Common Wine prefix locations
        wine_paths = [
            home / ".wine" / "drive_c" / "users" / os.environ.get('USER', 'user') / "AppData" / "Local" / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings",
            home / ".local" / "share" / "Steam" / "steamapps" / "compatdata" / "359320" / "pfx" / "drive_c" / "users" / "steamuser" / "AppData" / "Local" / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings"
        ]
        for wine_path in wine_paths:
            if wine_path.exists():
                paths.extend(glob.glob(str(wine_path / "*.binds")))
    
    return paths

def detect_primary_fire_key() -> Optional[str]:
    """
    Detect the Primary Fire key from Elite Dangerous bindings files.
    
    Returns:
        The primary fire key or None if not found
    """
    try:
        binding_paths = get_elite_bindings_paths()
        
        if not binding_paths:
            logger.warning("No Elite Dangerous bindings files found")
            return None
        
        # Try to find the most recently used bindings file
        binding_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        for bindings_path in binding_paths:
            logger.info(f"Checking bindings file: {bindings_path}")
            
            try:
                tree = ET.parse(bindings_path)
                root = tree.getroot()
                
                # Look for PrimaryFire binding
                primary_fire = root.find(".//PrimaryFire")
                if primary_fire is not None:
                    key = parse_binding_key(primary_fire)
                    if key:
                        logger.info(f"Found PrimaryFire key: {key}")
                        return key
                
            except ET.ParseError as e:
                logger.warning(f"Failed to parse bindings file {bindings_path}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error reading bindings file {bindings_path}: {e}")
                continue
        
        logger.warning("PrimaryFire binding not found in any bindings file")
        return None
        
    except Exception as e:
        logger.error(f"Error detecting primary fire key: {e}")
        return None

def parse_binding_key(binding_element) -> Optional[str]:
    """
    Parse a key binding from an XML element.
    
    Args:
        binding_element: XML element containing binding info
        
    Returns:
        Key name or None if not found/parseable
    """
    try:
        # Look for Primary binding first
        primary = binding_element.find("Primary")
        if primary is not None:
            device = primary.get("Device")
            key_attr = primary.get("Key")
            
            if device == "Keyboard" and key_attr:
                # Convert Elite's key format to our format
                key = convert_elite_key_name(key_attr)
                return key
        
        # If no primary, look for Secondary
        secondary = binding_element.find("Secondary")
        if secondary is not None:
            device = secondary.get("Device")
            key_attr = secondary.get("Key")
            
            if device == "Keyboard" and key_attr:
                key = convert_elite_key_name(key_attr)
                return key
        
        return None
        
    except Exception as e:
        logger.warning(f"Error parsing binding key: {e}")
        return None

def convert_elite_key_name(elite_key: str) -> str:
    """
    Convert Elite Dangerous key name to our key format.
    
    Args:
        elite_key: Key name from Elite Dangerous bindings
        
    Returns:
        Converted key name
    """
    # Elite uses format like "Key_1", "Key_Space", "Key_LeftShift", etc.
    
    # Remove "Key_" prefix if present
    if elite_key.startswith("Key_"):
        elite_key = elite_key[4:]
    
    # Convert common key names
    key_mapping = {
        'Space': 'space',
        'Enter': 'enter',
        'Return': 'enter',
        'Tab': 'tab',
        'Escape': 'escape',
        'LeftShift': 'shift',
        'RightShift': 'shift',
        'LeftControl': 'ctrl',
        'RightControl': 'ctrl',
        'LeftAlt': 'alt',
        'RightAlt': 'alt',
        'F1': 'f1',
        'F2': 'f2',
        'F3': 'f3',
        'F4': 'f4',
        'F5': 'f5',
        'F6': 'f6',
        'F7': 'f7',
        'F8': 'f8',
        'F9': 'f9',
        'F10': 'f10',
        'F11': 'f11',
        'F12': 'f12',
        'LeftMouseButton': 'leftclick',
        'RightMouseButton': 'rightclick',
        'MiddleMouseButton': 'middleclick',
    }
    
    # Check if it's a mapped key
    if elite_key in key_mapping:
        return key_mapping[elite_key]
    
    # For number and letter keys, return as lowercase
    if len(elite_key) == 1:
        return elite_key.lower()
    
    # For numeric keys (might be formatted as numbers)
    if elite_key.isdigit():
        return elite_key
    
    # If we can't convert it, return the original (lowercase)
    return elite_key.lower()

# Required plugin entry points
if __name__ == "__main__":
    # This allows testing the plugin independently
    print(f"AutoHonk Plugin {plugin_version}")
    print("This is an EDMC plugin and should be placed in the plugins directory.")