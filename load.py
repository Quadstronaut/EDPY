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

# Import for keypress simulation - Windows only
if sys.platform == "win32":
    import win32api
    import win32con
    import win32gui
else:
    # Plugin only supports Windows
    raise ImportError("AutoHonk plugin only supports Windows")

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
    'auto_detect_key': True,  # Whether to auto-detect primary fire key
    'window_title': 'Elite - Dangerous (CLIENT)'  # Elite Dangerous window title to target
}
detected_primary_fire_key = None

# Tkinter variables for settings
enabled_var = None
key_var = None
delay_var = None
hold_var = None
auto_detect_var = None
detected_key_label = None
window_title_var = None
status_frame = None
status_label = None

def plugin_start3(plugin_dir: str) -> str:
    """
    Start the plugin.
    
    Args:
        plugin_dir: The plugin directory
        
    Returns:
        Plugin name or error message
    """
    try:
        global enabled_var, key_var, delay_var, hold_var, auto_detect_var, detected_primary_fire_key, window_title_var
        
        logger.info(f"AutoHonk Plugin {plugin_version} starting")
        logger.info(f"Plugin directory: {plugin_dir}")
        logger.info(f"Python platform: {sys.platform}")
        
        # Test win32 import
        try:
            import win32api
            import win32gui
            logger.info("win32 modules imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import win32 modules: {e}")
            return f"{plugin_name} - Error: Missing win32 modules"
        
        # Initialize tkinter variables for settings
        try:
            enabled_var = tk.BooleanVar(value=config['enabled'])
            key_var = tk.StringVar(value=config['key_to_press'])
            delay_var = tk.DoubleVar(value=config['delay_seconds'])
            hold_var = tk.DoubleVar(value=config['hold_duration'])
            auto_detect_var = tk.BooleanVar(value=config['auto_detect_key'])
            window_title_var = tk.StringVar(value=config['window_title'])
            logger.info("Tkinter variables initialized")
        except Exception as e:
            logger.error(f"Failed to initialize tkinter variables: {e}")
            return f"{plugin_name} - Error: Tkinter init failed"
        
        # Try to detect the primary fire key from Elite Dangerous bindings
        try:
            detected_primary_fire_key = detect_primary_fire_key()
            if detected_primary_fire_key:
                logger.info(f"Detected primary fire key: {detected_primary_fire_key}")
            else:
                logger.warning("Could not detect primary fire key from bindings")
        except Exception as e:
            logger.error(f"Error detecting primary fire key: {e}")
            detected_primary_fire_key = None
        
        logger.info(f"AutoHonk Plugin {plugin_version} started successfully")
        return plugin_name
        
    except Exception as e:
        logger.error(f"Critical error in plugin_start3: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"{plugin_name} - Critical Error"

def plugin_stop() -> None:
    """Stop the plugin."""
    logger.info("AutoHonk Plugin stopping")

def initialize_variables():
    """Initialize tkinter variables if they haven't been initialized yet."""
    global enabled_var, key_var, delay_var, hold_var, auto_detect_var, window_title_var
    
    try:
        if enabled_var is None:
            enabled_var = tk.BooleanVar(value=config['enabled'])
        if key_var is None:
            key_var = tk.StringVar(value=config['key_to_press'])
        if delay_var is None:
            delay_var = tk.DoubleVar(value=config['delay_seconds'])
        if hold_var is None:
            hold_var = tk.DoubleVar(value=config['hold_duration'])
        if auto_detect_var is None:
            auto_detect_var = tk.BooleanVar(value=config['auto_detect_key'])
        if window_title_var is None:
            window_title_var = tk.StringVar(value=config['window_title'])
        
        logger.info("Variables initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing variables: {e}")
        # Create default variables
        enabled_var = tk.BooleanVar(value=True)
        key_var = tk.StringVar(value='auto')
        delay_var = tk.DoubleVar(value=2.0)
        hold_var = tk.DoubleVar(value=0.1)
        auto_detect_var = tk.BooleanVar(value=True)
        window_title_var = tk.StringVar(value='Elite - Dangerous (CLIENT)')

def plugin_app(parent: tk.Frame) -> tk.Frame:
    """
    Create the main application UI for the plugin.
    
    Args:
        parent: Parent frame in the main EDMC window
        
    Returns:
        Frame containing plugin UI elements
    """
    global status_frame, status_label
    
    # Create a frame to hold our status indicator
    status_frame = tk.Frame(parent)
    status_frame.columnconfigure(1, weight=1)
    
    # Status indicator (colored box + text)
    status_label = tk.Label(
        status_frame,
        text="AutoHonk Disabled",
        fg="white",
        bg="red",
        padx=5,
        pady=2,
        relief="solid",
        borderwidth=1
    )
    status_label.grid(row=0, column=0, sticky="w")
    
    # Update initial status
    update_status_display()
    
    return status_frame

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
    
    try:
        frame = tk.Frame(parent)
        frame.columnconfigure(1, weight=1)
        
        # Check if variables are initialized, if not, initialize them
        if enabled_var is None:
            logger.warning("Variables not initialized in plugin_prefs, initializing now")
            initialize_variables()
        
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
        
        # Window title
        row += 1
        tk.Label(frame, text="Elite Dangerous window title:").grid(row=row, column=0, sticky="w")
        window_title_entry = tk.Entry(frame, textvariable=window_title_var, width=30)
        window_title_entry.grid(row=row, column=1, sticky="w", padx=(10, 0))
        
        # Window title help
        row += 1
        window_help = tk.Label(
            frame,
            text="Common titles: 'Elite - Dangerous (CLIENT)', 'Elite - Dangerous (ALPHA)', etc.\n"
                 "For multiboxing, use specific window titles or partial matches.",
            wraplength=500,
            justify="left",
            fg="gray"
        )
        window_help.grid(row=row, column=0, columnspan=2, sticky="w", pady=(2, 5))
        
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
        
        logger.info("AutoHonk preferences panel created successfully")
        return frame
        
    except Exception as e:
        logger.error(f"Error creating preferences panel: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Return a simple error frame
        error_frame = tk.Frame(parent)
        tk.Label(error_frame, text=f"AutoHonk Settings Error: {str(e)}", fg="red").pack()
        return error_frame

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
    config['window_title'] = window_title_var.get()
    
    # Update the status display when preferences change
    update_status_display()
    
    logger.info(f"AutoHonk preferences updated: {config}")

def update_status_display():
    """Update the main window status indicator."""
    if status_label is not None:
        if config['enabled']:
            status_label.config(
                text="AutoHonk Enabled",
                bg="green",
                fg="white"
            )
        else:
            status_label.config(
                text="AutoHonk Disabled", 
                bg="red",
                fg="white"
            )

def on_auto_detect_changed():
    """Handle changes to the auto-detect checkbox."""
    try:
        # This function can be used to enable/disable manual key entry
        # For now, just log that it was called
        if auto_detect_var is not None:
            logger.debug(f"Auto-detect changed to: {auto_detect_var.get()}")
    except Exception as e:
        logger.error(f"Error in on_auto_detect_changed: {e}")

def refresh_detected_key():
    """Refresh the detected primary fire key."""
    try:
        global detected_primary_fire_key
        detected_primary_fire_key = detect_primary_fire_key()
        if detected_key_label:
            detected_key_label.config(
                text=detected_primary_fire_key or "Not found",
                fg="green" if detected_primary_fire_key else "red"
            )
        logger.info(f"Refreshed detected key: {detected_primary_fire_key}")
    except Exception as e:
        logger.error(f"Error refreshing detected key: {e}")

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
    
    # Debug logging
    event_type = entry.get('event', 'Unknown')
    logger.debug(f"Journal entry: {event_type}")
    
    if not config['enabled']:
        logger.debug("AutoHonk disabled, ignoring journal entry")
        return
    
    # Check for FSDJump event (entering a new system)
    if entry.get('event') == 'FSDJump':
        new_system = entry.get('StarSystem')
        logger.info(f"FSDJump detected to system: {new_system}")
        
        if new_system and new_system != current_system:
            logger.info(f"Entered new system: {new_system} (previous: {current_system})")
            current_system = new_system
            
            # Determine which key to use
            actual_key = config['key_to_press']
            if config['auto_detect_key'] and detected_primary_fire_key:
                actual_key = detected_primary_fire_key
            elif config['key_to_press'] == 'auto' and detected_primary_fire_key:
                actual_key = detected_primary_fire_key
            elif config['key_to_press'] == 'auto':
                actual_key = '1'  # Fallback default
            
            logger.info(f"Scheduling honk with key: {actual_key}, delay: {config['delay_seconds']}s")
            
            # Schedule the honk with a delay
            threading.Thread(
                target=delayed_honk,
                args=(config['delay_seconds'], actual_key, config['hold_duration']),
                daemon=True
            ).start()
    
    # Also handle StartUp and LoadGame events in case we missed the jump
    elif entry.get('event') in ('StartUp', 'LoadGame'):
        if system and system != current_system:
            current_system = system
            logger.info(f"System on startup/load: {system}")
    
    # Handle Location event (when already in a system)
    elif entry.get('event') == 'Location':
        location_system = entry.get('StarSystem')
        if location_system:
            current_system = location_system
            logger.info(f"Location event - current system: {location_system}")

def delayed_honk(delay: float, key: str, hold_duration: float) -> None:
    """
    Send a keypress after a delay.
    
    Args:
        delay: Delay in seconds before pressing key
        key: Key to press
        hold_duration: How long to hold the key
    """
    # Show "honking" status briefly
    if status_label is not None:
        status_label.config(
            text="AutoHonk - Firing!",
            bg="orange",
            fg="white"
        )
    
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
    
    # Restore normal status after a brief moment
    threading.Thread(target=restore_status_after_delay, daemon=True).start()

def restore_status_after_delay():
    """Restore the normal status display after a short delay."""
    time.sleep(1.5)  # Show "Firing!" for 1.5 seconds
    update_status_display()

def send_keypress(key: str, hold_duration: float) -> None:
    """
    Send a keypress to Elite Dangerous window.
    
    Args:
        key: Key to press
        hold_duration: How long to hold the key
    """
    try:
        send_keypress_windows(key, hold_duration)
    except Exception as e:
        logger.error(f"Failed to send keypress: {e}")

def find_elite_window() -> Optional[int]:
    """
    Find the Elite Dangerous window handle.
    
    Returns:
        Window handle or None if not found
    """
    try:
        window_title = config.get('window_title', 'Elite - Dangerous (CLIENT)')
        logger.info(f"Looking for window with title containing: {window_title}")
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and window_title.lower() in title.lower():
                    logger.info(f"Found potential window: '{title}' (hwnd: {hwnd})")
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # Return the first matching window
            hwnd, title = windows[0]
            logger.info(f"Selected Elite Dangerous window: '{title}' (hwnd: {hwnd})")
            return hwnd
        else:
            logger.warning(f"Elite Dangerous window not found with title containing: '{window_title}'")
            
            # Debug: List all visible windows
            logger.info("Listing all visible windows:")
            def debug_enum_callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:  # Only log windows with titles
                        logger.info(f"  Window: '{title}' (hwnd: {hwnd})")
                return True
            
            win32gui.EnumWindows(debug_enum_callback, None)
            return None
            
    except Exception as e:
        logger.error(f"Error finding Elite Dangerous window: {e}")
        return None

def send_keypress_windows(key: str, hold_duration: float) -> None:
    """Send keypress on Windows to Elite Dangerous window."""
    logger.info(f"Attempting to send keypress: {key} (hold: {hold_duration}s)")
    
    # Find Elite Dangerous window
    elite_hwnd = find_elite_window()
    
    # Get the virtual key code
    vk_code = ord(key.upper()) if len(key) == 1 else get_windows_vk_code(key)
    
    if vk_code is None:
        logger.error(f"Unknown key: {key}")
        return
    
    logger.info(f"Using virtual key code: {vk_code} for key: {key}")
    
    if elite_hwnd:
        logger.info(f"Found Elite window: {elite_hwnd}")
        try:
            # Try to bring Elite Dangerous to foreground
            win32gui.SetForegroundWindow(elite_hwnd)
            time.sleep(0.2)  # Longer delay to ensure window is focused
            logger.info("Set Elite window as foreground")
        except Exception as e:
            logger.warning(f"Could not set Elite Dangerous as foreground window: {e}")
        
        # Send key to specific window using PostMessage
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        
        try:
            # Send key down
            result1 = win32gui.PostMessage(elite_hwnd, WM_KEYDOWN, vk_code, 0)
            logger.info(f"PostMessage keydown result: {result1}")
            time.sleep(hold_duration)
            # Send key up
            result2 = win32gui.PostMessage(elite_hwnd, WM_KEYUP, vk_code, 0)
            logger.info(f"PostMessage keyup result: {result2}")
            logger.info(f"Sent keypress {key} to Elite Dangerous window")
        except Exception as e:
            logger.error(f"Failed to send message to Elite window: {e}")
            # Fallback to global keypress
            logger.info("Falling back to global keypress")
            send_global_keypress_windows(key, hold_duration)
    else:
        # Fallback to global keypress if window not found
        logger.warning("Elite window not found, using global keypress")
        send_global_keypress_windows(key, hold_duration)

def send_global_keypress_windows(key: str, hold_duration: float) -> None:
    """Send global keypress on Windows using win32api."""
    logger.info(f"Sending global keypress: {key}")
    
    vk_code = ord(key.upper()) if len(key) == 1 else get_windows_vk_code(key)
    
    if vk_code is None:
        logger.error(f"Unknown key for global press: {key}")
        return
    
    try:
        # Send key down
        win32api.keybd_event(vk_code, 0, 0, 0)
        logger.info(f"Global keydown sent for: {key}")
        time.sleep(hold_duration)
        # Send key up
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        logger.info(f"Global keyup sent for: {key}")
    except Exception as e:
        logger.error(f"Failed to send global keypress: {e}")

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
        # Numpad keys
        'numpad_add': win32con.VK_ADD,
        'numpad_subtract': win32con.VK_SUBTRACT,
        'numpad_multiply': win32con.VK_MULTIPLY,
        'numpad_divide': win32con.VK_DIVIDE,
        'numpad_decimal': win32con.VK_DECIMAL,
        'numpad0': win32con.VK_NUMPAD0,
        'numpad1': win32con.VK_NUMPAD1,
        'numpad2': win32con.VK_NUMPAD2,
        'numpad3': win32con.VK_NUMPAD3,
        'numpad4': win32con.VK_NUMPAD4,
        'numpad5': win32con.VK_NUMPAD5,
        'numpad6': win32con.VK_NUMPAD6,
        'numpad7': win32con.VK_NUMPAD7,
        'numpad8': win32con.VK_NUMPAD8,
        'numpad9': win32con.VK_NUMPAD9,
    }
    
    return special_keys.get(key.lower())

def get_elite_bindings_paths() -> list:
    """
    Get possible paths to Elite Dangerous bindings files on Windows.
    
    Returns:
        List of potential binding file paths
    """
    paths = []
    
    # Standard Windows path
    local_appdata = os.environ.get('LOCALAPPDATA')
    if local_appdata:
        bindings_dir = Path(local_appdata) / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings"
        logger.info(f"Checking bindings directory: {bindings_dir}")
        if bindings_dir.exists():
            # Look for .binds files
            binds_files = glob.glob(str(bindings_dir / "*.binds"))
            logger.info(f"Found {len(binds_files)} .binds files")
            paths.extend(binds_files)
        else:
            logger.warning(f"Bindings directory does not exist: {bindings_dir}")
    
    # Check for Sandboxie or other virtualized paths
    # Sandboxie typically redirects to a sandbox-specific location
    try:
        import winreg
        # Try to find Elite Dangerous install location from registry
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{696F8871-C91D-4CB1-825D-36BE18065575}_is1") as key:
            install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
            logger.info(f"Found Elite install location: {install_location}")
    except Exception as e:
        logger.debug(f"Could not find Elite install location from registry: {e}")
    
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
        # Numpad keys
        'Numpad_Add': 'numpad_add',
        'Numpad_Subtract': 'numpad_subtract', 
        'Numpad_Multiply': 'numpad_multiply',
        'Numpad_Divide': 'numpad_divide',
        'Numpad_Decimal': 'numpad_decimal',
        'Numpad_0': 'numpad0',
        'Numpad_1': 'numpad1',
        'Numpad_2': 'numpad2',
        'Numpad_3': 'numpad3',
        'Numpad_4': 'numpad4',
        'Numpad_5': 'numpad5',
        'Numpad_6': 'numpad6',
        'Numpad_7': 'numpad7',
        'Numpad_8': 'numpad8',
        'Numpad_9': 'numpad9',
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