"""
Elite Dangerous AutoLoad - Standalone Script
Sends a couple Enter keys to skip the opening cutscene.

Requirements:
- pip install pywin32 pydirectinput
"""

import time
import logging
from typing import Optional

# Hardware input simulation
import pydirectinput

# Third party API imports for window handling
import win32api
import win32con
import win32gui
import win32process

# Configuration
CONFIG = {
    "window_title_contains": "Elite - Dangerous (CLIENT)",
    "process_name": "elitedangerous64",
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("elite_autoload.log")],
)
logger = logging.getLogger(__name__)


class AutoLoad:
    def __init__(self):
        print("=" * 60)
        print("Elite Dangerous AutoLoad - Skip Cutscene")
        print("=" * 60)
        print(f"Looking for process: '{CONFIG['process_name']}.exe'")
        print(f"Waiting for window title: '{CONFIG['window_title_contains']}'")
        print("Waiting for Elite Dangerous window to appear with proper title...")
        print("-" * 60)

    def find_elite_window_with_title(self) -> Optional[int]:
        """Find Elite Dangerous window handle by process name and ensure it has the proper title."""

        def enum_windows_callback(hwnd, windows):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    
                    # Get the process info for this window
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process_handle = win32api.OpenProcess(
                            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 
                            False, 
                            pid
                        )
                        process_name = win32process.GetModuleFileNameEx(process_handle, 0).lower()
                        win32api.CloseHandle(process_handle)
                        
                        # Check if this is the Elite Dangerous process
                        if CONFIG["process_name"].lower() in process_name:
                            # Only add if the title is not blank AND contains our target string
                            if title.strip() and CONFIG["window_title_contains"].lower() in title.lower():
                                windows.append((hwnd, title, process_name))
                                logger.info(f"Found Elite window with title: '{title}' from process: {process_name}")
                            elif title.strip():
                                logger.debug(f"Elite process found but title doesn't match: '{title}' from process: {process_name}")
                            else:
                                logger.debug(f"Elite process found but title is blank from process: {process_name}")
                                
                    except Exception as e:
                        logger.debug(f"Could not get process info for PID {pid}: {e}")
                        
            except Exception as e:
                logger.debug(f"Error processing window {hwnd}: {e}")
                pass  # Ignore windows we can't access
            return True

        try:
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            if windows:
                hwnd, title, process_name = windows[0]
                logger.info("Selected Elite window: '%s' from %s", title, process_name)
                return hwnd
            else:
                return None
        except Exception as e:
            logger.error("Error finding Elite window: %s", e)
            return None

    def wait_for_window_with_title(self) -> int:
        """Wait until Elite Dangerous window appears with proper non-blank title."""
        print("Waiting for Elite Dangerous to start and show proper window title...")
        
        check_count = 0
        while True:
            elite_hwnd = self.find_elite_window_with_title()
            if elite_hwnd:
                print(f"Elite Dangerous window found with proper title!")
                logger.info("Elite Dangerous window with title detected")
                return elite_hwnd
            
            check_count += 1
            if check_count % 10 == 0:  # Every 5 seconds, show we're still checking
                print(f"Still waiting... (checked {check_count} times)")
                
            time.sleep(0.5)  # Check every 500ms

    def send_enter_keys(self, elite_hwnd: int):
        """Send Enter key twice with focus management."""
        try:
            print("Sending first Enter key...")
            
            # Focus window and send first Enter
            win32gui.SetForegroundWindow(elite_hwnd)
            time.sleep(0.1)  # Brief delay to ensure focus
            pydirectinput.press('enter')
            logger.info("First Enter key sent")
            
            # Wait 250ms
            time.sleep(0.25)
            
            print("Sending second Enter key...")
            
            # Focus window again and send second Enter
            win32gui.SetForegroundWindow(elite_hwnd)
            time.sleep(0.1)  # Brief delay to ensure focus
            pydirectinput.press('enter')
            logger.info("Second Enter key sent")
            
            print("Cutscene skip complete!")
            
        except Exception as e:
            logger.error(f"Error sending Enter keys: {e}")
            print(f"Error sending keys: {e}")

    def run(self):
        """Main execution logic."""
        # Wait for Elite window to appear with proper title
        elite_hwnd = self.wait_for_window_with_title()

        # Brief pause to ensure the window is fully ready
        print("Window found, waiting 1 second before sending keys...")
        time.sleep(1)
        
        # Send the Enter keys to skip cutscene
        self.send_enter_keys(elite_hwnd)


def main():
    """Main function to start the AutoLoad process."""
    print("Starting Elite Dangerous AutoLoad...")
    
    autoload = AutoLoad()
    autoload.run()
    
    print("AutoLoad complete. Exiting.")
    logger.info("AutoLoad process finished")


if __name__ == "__main__":
    main()