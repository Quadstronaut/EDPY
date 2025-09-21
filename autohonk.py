"""
Elite Dangerous AutoHonk - Standalone Script
Monitors Odyssey journal files and fires.

Requirements:
- pip install pywin32 watchdog
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
import logging

# Standard Windows API imports
import ctypes
import ctypes.wintypes

# File monitoring
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Third party API imports
import win32api
import win32con
import win32gui
import win32process


# Configuration
CONFIG = {
    "window_title_contains": "(CLIENT)",  # Part of Elite window title to look for
    "hold_duration": 6.0,  # Hold key for x seconds as requested
    "delay_after_jump": 2.0,  # Wait 2 seconds after jump before honking
    "auto_detect_primary_fire": True,  # Auto-detect from bindings
    "manual_key_override": None,  # Set to specific key if needed (e.g., 'numpad_add')
    "journal_folder": Path.home()
    / "Saved Games"
    / "Frontier Developments"
    / "Elite Dangerous",
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("elite_autohonk.log")],
)
logger = logging.getLogger(__name__)

# Constants for SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ulong),
        ("wParamH", ctypes.c_ulong),
    ]


class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL),
    ]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]


class AutoHonk:
    def __init__(self):
        self.current_system = None
        self.primary_fire_key = None
        self.elite_hwnd = None
        self.running = True

        # Detect primary fire key on startup
        self.detect_primary_fire_key()

        print("=" * 60)
        print("Elite Dangerous AutoHonk - Standalone")
        print("=" * 60)
        print(f"Monitoring journal folder: {CONFIG['journal_folder']}")
        print(f"Looking for window containing: '{CONFIG['window_title_contains']}'")
        print(f"Detected primary fire key: {self.primary_fire_key or 'Not detected'}")
        print(f"Key hold duration: {CONFIG['hold_duration']} seconds")
        print("Waiting for FSD jumps...")
        print("-" * 60)

    def detect_primary_fire_key(self):
        """Detect Primary Fire key from Elite Dangerous bindings."""
        try:
            bindings_dir = (
                Path(os.environ.get("LOCALAPPDATA"))
                / "Frontier Developments"
                / "Elite Dangerous"
                / "Options"
                / "Bindings"
            )

            if not bindings_dir.exists():
                logger.warning("Bindings directory not found: %s", bindings_dir)
                return

            binds_files = list(bindings_dir.glob("*.binds"))
            if not binds_files:
                logger.warning("No .binds files found")
                return

            # Use the most recent bindings file
            latest_bindings = max(binds_files, key=lambda x: x.stat().st_mtime)
            logger.info("Reading bindings from: %s", latest_bindings)

            tree = ET.parse(latest_bindings)
            root = tree.getroot()

            primary_fire = root.find(".//PrimaryFire")
            if primary_fire is not None:
                primary = primary_fire.find("Primary")
                if primary is not None:
                    device = primary.get("Device")
                    key_attr = primary.get("Key")

                    if device == "Keyboard" and key_attr:
                        self.primary_fire_key = self.convert_elite_key_name(key_attr)
                        logger.info(
                            "Detected Primary Fire key: %s -> %s",
                            key_attr,
                            self.primary_fire_key,
                        )
                        return

            logger.warning("PrimaryFire binding not found in bindings file")

        except Exception as e:
            logger.error("Error detecting primary fire key: %s", e)

    def convert_elite_key_name(self, elite_key: str) -> str:
        """Convert Elite Dangerous key name to Windows virtual key format."""
        if elite_key.startswith("Key_"):
            elite_key = elite_key[4:]

        key_mapping = {
            "Numpad_Add": "numpad_add",
            "Numpad_Subtract": "numpad_subtract",
            "Numpad_Multiply": "numpad_multiply",
            "Numpad_Divide": "numpad_divide",
            "Space": "space",
            "Enter": "enter",
            "Tab": "tab",
            "F1": "f1",
            "F2": "f2",
            "F3": "f3",
            "F4": "f4",
            "F5": "f5",
            "F6": "f6",
            "F7": "f7",
            "F8": "f8",
            "F9": "f9",
            "F10": "f10",
            "F11": "f11",
            "F12": "f12",
        }

        return key_mapping.get(elite_key, elite_key.lower())

    def find_elite_window(self) -> Optional[int]:
        """Find Elite Dangerous window handle by process name and window title."""

        def enum_windows_callback(hwnd, windows):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    # Get window title
                    title = win32gui.GetWindowText(hwnd)

                    # Get process ID and name
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process_handle = win32api.OpenProcess(
                        win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                        False,
                        pid,
                    )
                    process_name = win32process.GetModuleFileNameEx(
                        process_handle, 0
                    ).lower()
                    win32api.CloseHandle(process_handle)

                    # Check if it's Elite Dangerous process with matching window title
                    if (
                        "elitedangerous64" in process_name
                        and CONFIG["window_title_contains"].lower() in title.lower()
                    ):
                        windows.append((hwnd, title, process_name))

            except Exception:
                # Skip windows we can't access
                pass
            return True

        try:
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            if windows:
                hwnd, title, process = windows[0]
                logger.info("Found Elite window: '%s' (PID: %s)", title, process)
                return hwnd
            else:
                logger.warning(
                    "Elite Dangerous window not found (looking for process EliteDangerous64 with title containing '%s')",
                    CONFIG["window_title_contains"],
                )
                return None

        except Exception as e:
            logger.error("Error finding Elite window: %s", e)
            return None

    def get_virtual_key_code(self, key: str) -> Optional[int]:
        """Get Windows virtual key code for the key."""
        special_keys = {
            "numpad_add": win32con.VK_ADD,
            "numpad_subtract": win32con.VK_SUBTRACT,
            "numpad_multiply": win32con.VK_MULTIPLY,
            "numpad_divide": win32con.VK_DIVIDE,
            "space": win32con.VK_SPACE,
            "enter": win32con.VK_RETURN,
            "tab": win32con.VK_TAB,
            "f1": win32con.VK_F1,
            "f2": win32con.VK_F2,
            "f3": win32con.VK_F3,
            "f4": win32con.VK_F4,
            "f5": win32con.VK_F5,
            "f6": win32con.VK_F6,
            "f7": win32con.VK_F7,
            "f8": win32con.VK_F8,
            "f9": win32con.VK_F9,
            "f10": win32con.VK_F10,
            "f11": win32con.VK_F11,
            "f12": win32con.VK_F12,
        }

        if key.lower() in special_keys:
            return special_keys[key.lower()]
        elif len(key) == 1:
            return ord(key.upper())
        else:
            return None


def send_keypress(self, key: str, duration: float):
    """Send keypress to Elite Dangerous window using SendInput."""
    try:
        elite_hwnd = self.find_elite_window()
        if not elite_hwnd:
            print("❌ Elite Dangerous window not found - cannot send keypress")
            return

        vk_code = self.get_virtual_key_code(key)
        if vk_code is None:
            print(f"❌ Unknown key: {key}")
            return

        print(
            f"🎯 Sending keypress '{key}' to Elite Dangerous for {duration} seconds..."
        )

        # Bring window to foreground
        win32gui.SetForegroundWindow(elite_hwnd)
        time.sleep(0.2)  # Brief delay to ensure focus

        # Create input structures for key down and key up
        # Key Down
        down_input = Input(
            type=win32con.INPUT_KEYBOARD,
            ii=Input_I(ki=KeyBdInput(wVk=vk_code, dwFlags=0)),
        )

        # Key Up
        up_input = Input(
            type=win32con.INPUT_KEYBOARD,
            ii=Input_I(ki=KeyBdInput(wVk=vk_code, dwFlags=win32con.KEYEVENTF_KEYUP)),
        )

        # Send key down
        ctypes.windll.user32.SendInput(
            1, ctypes.byref(down_input), ctypes.sizeof(down_input)
        )
        print(f"⬇️  Key DOWN: {key}")

        # Hold for specified duration
        time.sleep(duration)

        # Send key up
        ctypes.windll.user32.SendInput(
            1, ctypes.byref(up_input), ctypes.sizeof(up_input)
        )
        print(f"⬆️  Key UP: {key}")
        print(f"✅ Keypress complete!")

    except Exception as e:
        print(f"❌ Error sending keypress: {e}")
        logger.error("Keypress error: %s", e)

    def process_journal_entry(self, entry: dict):
        """Process a journal entry and trigger honk if needed."""
        try:
            event_type = entry.get("event")
            timestamp = entry.get("timestamp", "Unknown")

            if event_type == "FSDJump":
                new_system = entry.get("StarSystem")
                if new_system and new_system != self.current_system:
                    print("\n🚀 FSD JUMP DETECTED!")
                    print(f"  Time: {timestamp}")
                    print(f"  From: {self.current_system or 'Unknown'}")
                    print(f"  To: {new_system}")

                    self.current_system = new_system

                    # Determine which key to use
                    key_to_use = None
                    if CONFIG["manual_key_override"]:
                        key_to_use = CONFIG["manual_key_override"]
                        print(f"  Using manual key override: {key_to_use}")
                    elif CONFIG["auto_detect_primary_fire"] and self.primary_fire_key:
                        key_to_use = self.primary_fire_key
                        print(f"  Using detected Primary Fire key: {key_to_use}")
                    else:
                        key_to_use = "1"  # Default fallback
                        print(f"  Using fallback key: {key_to_use}")

                    # Schedule the honk
                    print(
                        f"  Waiting {CONFIG['delay_after_jump']} seconds before honking..."
                    )

                    def delayed_honk():
                        time.sleep(CONFIG["delay_after_jump"])
                        self.send_keypress(key_to_use, CONFIG["hold_duration"])
                        print("-" * 60)

                    # Run in separate thread so it doesn't block file monitoring
                    threading.Thread(target=delayed_honk, daemon=True).start()

            elif event_type in ["Location", "LoadGame", "StartUp"]:
                # Track current system from these events too
                system = entry.get("StarSystem")
                if system and system != self.current_system:
                    self.current_system = system
                    print(f"📍 Current system: {system}")

        except Exception as e:
            logger.error("Error processing journal entry: %s", e)


class JournalMonitor(FileSystemEventHandler):
    def __init__(self, autohonk: AutoHonk):
        self.autohonk = autohonk
        self.current_file = None
        self.file_position = 0

        # Find the latest journal file
        self.find_latest_journal()

    def find_latest_journal(self):
        """Find and start monitoring the latest journal file."""
        try:
            journal_files = list(CONFIG["journal_folder"].glob("Journal.*.log"))
            if journal_files:
                latest_journal = max(journal_files, key=lambda x: x.stat().st_mtime)
                self.current_file = latest_journal
                self.file_position = (
                    latest_journal.stat().st_size
                )  # Start at end of file
                logger.info("Monitoring journal file: %s", latest_journal)
                print(f"📖 Monitoring: {latest_journal.name}")
            else:
                logger.warning("No journal files found")
                print("⚠️  No journal files found")
        except Exception as journal_exception:
            logger.error("Error finding journal files: %s", journal_exception)

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's a journal file
        if file_path.name.startswith("Journal.") and file_path.name.endswith(".log"):
            self.read_new_lines(file_path)

    def on_created(self, event):
        """Handle new file creation (new journal files)."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.name.startswith("Journal.") and file_path.name.endswith(".log"):
            print(f"\n📖 New journal file detected: {file_path.name}")
            self.current_file = file_path
            self.file_position = 0

    def read_new_lines(self, file_path: Path):
        """Read new lines from the journal file."""
        try:
            if file_path != self.current_file:
                return

            with open(file_path, "r", encoding="utf-8") as f:
                f.seek(self.file_position)
                new_lines = f.readlines()
                self.file_position = f.tell()

                for line in new_lines:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            self.autohonk.process_journal_entry(entry)
                        except json.JSONDecodeError:
                            pass  # Skip invalid JSON lines

        except Exception as e:
            logger.error("Error reading journal file: %s", e)


def main():
    """Main function to start the AutoHonk monitor."""
    print("Starting Elite Dangerous AutoHonk...")

    # Check if journal folder exists
    if not CONFIG["journal_folder"].exists():
        print(f"❌ Journal folder not found: {CONFIG['journal_folder']}")
        print("Make sure Elite Dangerous has been run at least once.")
        input("Press Enter to exit...")
        return

    # Initialize AutoHonk
    autohonk = AutoHonk()

    # Set up file monitoring
    event_handler = JournalMonitor(autohonk)
    observer = Observer()
    observer.schedule(event_handler, str(CONFIG["journal_folder"]), recursive=False)

    # Start monitoring
    observer.start()

    try:
        print("\n✅ AutoHonk is running! Press Ctrl+C to stop.")
        while autohonk.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping AutoHonk...")
        autohonk.running = False
        observer.stop()

    observer.join()
    print("👋 AutoHonk stopped. Goodbye!")


if __name__ == "__main__":
    main()