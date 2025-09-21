"""
Elite Dangerous AutoHonk - Standalone Script
Monitors Odyssey journal files and fires.

Requirements:
- pip install pywin32 watchdog pydirectinput
"""

import os
import json
import time
import threading
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
import logging

# Hardware input simulation
import pydirectinput

# File monitoring
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Third party API imports for window handling
import win32api
import win32con
import win32gui
import win32process


# Configuration
CONFIG = {
    # IMPORTANT: For reliability with multiple accounts, change this to the specific
    # commander name for the sandbox this script is running in.
    # For example: "CMDRQuadstronaut"
    "window_title_contains": "Elite - Dangerous (CLIENT)",
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


class AutoHonk:
    def __init__(self):
        self.current_system = None
        self.primary_fire_key = None
        self.running = True

        # Detect primary fire key on startup
        self.detect_primary_fire_key()

        print("=" * 60)
        print("Elite Dangerous AutoHonk - Standalone (Updated)")
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
        """Convert Elite Dangerous key name to a pydirectinput-compatible format."""
        if elite_key.startswith("Key_"):
            elite_key = elite_key[4:]

        # Mapping from Elite's names to pydirectinput's names
        key_mapping = {
            "Numpad_Add": "add",
            "Numpad_Subtract": "subtract",
            "Numpad_Multiply": "multiply",
            "Numpad_Divide": "divide",
            # Add other mappings here if needed
        }
        
        # Return the mapped key, or the lowercase version of the original if not in the map
        return key_mapping.get(elite_key, elite_key.lower())

    def find_elite_window(self) -> Optional[int]:
        """Find Elite Dangerous window handle by process name and window title."""

        def enum_windows_callback(hwnd, windows):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    
                    # Since we are inside the sandbox, we just check the title and process name
                    if CONFIG["window_title_contains"].lower() in title.lower():
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
                        process_name = win32process.GetModuleFileNameEx(process_handle, 0).lower()
                        win32api.CloseHandle(process_handle)
                        
                        if "elitedangerous64" in process_name:
                            windows.append((hwnd, title))
            except Exception:
                pass  # Ignore windows we can't access
            return True

        try:
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            if windows:
                hwnd, title = windows[0]
                logger.info("Found Elite window: '%s'", title)
                return hwnd
            else:
                logger.warning(
                    "Elite Dangerous window not found (title should contain '%s')",
                    CONFIG["window_title_contains"],
                )
                return None
        except Exception as e:
            logger.error("Error finding Elite window: %s", e)
            return None

    def send_keypress(self, key: str, duration: float):
        """
        MODIFIED: Finds, focuses, and sends a keypress to the Elite window.
        """
        try:
            logger.info("Attempting to find and focus Elite window...")
            elite_hwnd = self.find_elite_window()

            if not elite_hwnd:
                logger.error("Elite Dangerous window not found. Cannot send keypress.")
                print("❌ Elite Dangerous window not found - cannot send keypress")
                return

            # --- CRITICAL CHANGE ---
            # Bring the window to the foreground before sending input.
            try:
                win32gui.SetForegroundWindow(elite_hwnd)
                # Add a small delay to allow Windows to process the focus change
                time.sleep(0.2)
                logger.info("Successfully set Elite window to foreground.")
            except Exception as e:
                logger.error(f"Could not set window to foreground: {e}")
                print(f"❌ Could not focus window: {e}")
                return
            # --- END OF CHANGE ---

            logger.info(f"Sending key '{key}' down for {duration} seconds.")
            print(f"⬇️  Key DOWN: {key} for {duration} seconds...")

            pydirectinput.keyDown(key)
            time.sleep(duration)
            pydirectinput.keyUp(key)

            logger.info("Keypress sequence complete.")
            print(f"⬆️  Key UP: {key}")
            print("✅ Keypress complete!")

        except Exception as e:
            logger.error(f"An error occurred during send_keypress: {e}")
            print(f"❌ Error sending keypress: {e}")

    def process_journal_entry(self, entry: dict):
        """Process a journal entry and trigger honk if needed."""
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

                key_to_use = (
                    CONFIG["manual_key_override"]
                    or self.primary_fire_key
                    or "add" # Fallback to numpad '+'
                )
                
                print(f"  Using key: {key_to_use}")
                print(f"  Waiting {CONFIG['delay_after_jump']} seconds before honking...")

                def delayed_honk():
                    time.sleep(CONFIG["delay_after_jump"])
                    self.send_keypress(key_to_use, CONFIG["hold_duration"])
                    print("-" * 60)

                threading.Thread(target=delayed_honk, daemon=True).start()

        elif event_type in ["Location", "LoadGame", "StartUp"]:
            system = entry.get("StarSystem")
            if system and system != self.current_system:
                self.current_system = system
                print(f"📍 Current system: {system}")


class JournalMonitor(FileSystemEventHandler):
    def __init__(self, autohonk: AutoHonk):
        self.autohonk = autohonk
        self.current_file = None
        self.file_position = 0
        self.find_latest_journal()

    def find_latest_journal(self):
        try:
            journal_files = list(CONFIG["journal_folder"].glob("Journal.*.log"))
            if journal_files:
                latest_journal = max(journal_files, key=lambda x: x.stat().st_mtime)
                self.current_file = latest_journal
                self.file_position = latest_journal.stat().st_size
                logger.info("Monitoring journal file: %s", latest_journal)
                print(f"📖 Monitoring: {latest_journal.name}")
            else:
                logger.warning("No journal files found")
                print("⚠️  No journal files found")
        except Exception as e:
            logger.error("Error finding journal files: %s", e)

    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path).name.startswith("Journal."):
            self.read_new_lines(Path(event.src_path))

    def on_created(self, event):
        if not event.is_directory and Path(event.src_path).name.startswith("Journal."):
            file_path = Path(event.src_path)
            print(f"\n📖 New journal file detected: {file_path.name}")
            self.current_file = file_path
            self.file_position = 0

    def read_new_lines(self, file_path: Path):
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
                            self.autohonk.process_journal_entry(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            logger.error("Error reading journal file: %s", e)


def main():
    """Main function to start the AutoHonk monitor."""
    if not CONFIG["journal_folder"].exists():
        print(f"❌ Journal folder not found: {CONFIG['journal_folder']}")
        input("Press Enter to exit...")
        return

    autohonk = AutoHonk()
    event_handler = JournalMonitor(autohonk)
    observer = Observer()
    observer.schedule(event_handler, str(CONFIG["journal_folder"]), recursive=False)
    observer.start()

    try:
        print("\n✅ AutoHonk is running! Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping AutoHonk...")
        observer.stop()
    observer.join()
    print("👋 AutoHonk stopped. Goodbye!")


if __name__ == "__main__":
    main()
