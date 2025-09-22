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
    # IMPORTANT: For reliability with multiple accounts, change this to the specific
    # commander name for the sandbox this script is running in.
    # For example: "CMDRQuadstronaut"
    "window_title_contains": "Elite - Dangerous (CLIENT)",
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
        print(f"Looking for window containing: '{CONFIG['window_title_contains']}'")
        print("Waiting for Elite Dangerous window to appear...")
        print("-" * 60)

    def find_elite_window(self) -> Optional[int]:
        """Find Elite Dangerous window handle by process name and window title."""

        def enum_windows_callback(hwnd, windows):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    
                    if CONFIG["window_title_contains"].lower() in title.lower():
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process_handle = win32api.OpenProcess(
                            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 
                            False, 
                            pid
                        )
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
                return None
        except Exception as e:
            logger.error("Error finding Elite window: %s", e)
            return None

    def wait_for_window(self) -> int:
        """Wait until Elite Dangerous window appears."""
        print("Waiting for Elite Dangerous to start...")
        
        while True:
            elite_hwnd = self.find_elite_window()
            if elite_hwnd:
                print(f"Elite Dangerous window found!")
                logger.info("Elite Dangerous window detected")
                return elite_hwnd
            
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
        # Wait for Elite window to appear
        elite_hwnd = self.wait_for_window()
        
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