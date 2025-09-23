"""
Elite Dangerous AutoLoad - Multi-Commander Script
Sends a couple ESC keys to skip the opening cutscene for multiple commanders.

Requirements:
- pip install pywin32 pydirectinput pycaw
"""

import time
import logging
from typing import Optional, Set, List, Tuple
import ctypes
from ctypes import wintypes

# Hardware input simulation
import pydirectinput

# Third party API imports for window handling
import win32api
import win32con
import win32gui
import win32process

# Audio detection imports
from pycaw.pycaw import AudioUtilities

# Configuration
CONFIG = {
    "window_title_contains": "Elite - Dangerous (CLIENT)",
    "process_name": "elitedangerous64",
    "commanders": ["Duvrazh", "Bistronaut", "Tristronaut", "Quadstronaut"],
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("elite_autoload.log")],
)
logger = logging.getLogger(__name__)


class MultiCommanderAutoLoad:
    def __init__(self):
        self.processed_commanders: Set[str] = set()
        self.total_commanders = len(CONFIG["commanders"])
        
        print("=" * 60)
        print("Elite Dangerous Multi-Commander AutoLoad - Skip Cutscene")
        print("=" * 60)
        print(f"Looking for process: '{CONFIG['process_name']}.exe'")
        print(f"Window title must contain: '{CONFIG['window_title_contains']}'")
        print(f"Commanders to process: {', '.join(CONFIG['commanders'])}")
        print("Will wait for window title AND audio output before sending keys...")
        print("-" * 60)

    def find_unprocessed_elite_windows(self) -> List[Tuple[int, str, str]]:
        """Find Elite Dangerous windows for commanders that haven't been processed yet."""
        
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
                            # Check if title contains our base window title
                            if title.strip() and CONFIG["window_title_contains"].lower() in title.lower():
                                # Check if title contains any unprocessed commander name
                                for commander in CONFIG["commanders"]:
                                    if commander not in self.processed_commanders and commander.lower() in title.lower():
                                        windows.append((hwnd, title, commander))
                                        logger.info(f"Found Elite window for {commander}: '{title}' from process: {process_name}")
                                        break
                            elif title.strip():
                                logger.debug(f"Elite process found but title doesn't match pattern: '{title}' from process: {process_name}")
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
            return windows
        except Exception as e:
            logger.error("Error finding Elite windows: %s", e)
            return []

    def is_elite_producing_audio(self) -> bool:
        """Check if any Elite Dangerous process is currently producing audio."""
        try:
            # Get all audio sessions
            sessions = AudioUtilities.GetAllSessions()
            
            for session in sessions:
                if session.Process:
                    process_name = session.Process.name().lower()
                    if CONFIG["process_name"].lower() in process_name:
                        # Check if the session is active and has volume > 0
                        volume = session.SimpleAudioVolume
                        if volume and not volume.GetMute():
                            # Session exists and is not muted - Elite is producing audio
                            logger.debug(f"Elite audio session found: {process_name}, muted: {volume.GetMute()}")
                            return True
                        elif volume:
                            logger.debug(f"Elite audio session found but muted: {process_name}")
                        else:
                            logger.debug(f"Elite process found but no audio volume interface: {process_name}")
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking audio sessions: {e}")
            return False

    def wait_for_next_commander_window(self) -> Optional[Tuple[int, str, str]]:
        """Wait for the next unprocessed commander's window to appear."""
        remaining_commanders = [cmd for cmd in CONFIG["commanders"] if cmd not in self.processed_commanders]
        
        if not remaining_commanders:
            return None
            
        print(f"\nWaiting for windows from remaining commanders: {', '.join(remaining_commanders)}")
        
        check_count = 0
        while remaining_commanders:
            windows = self.find_unprocessed_elite_windows()
            if windows:
                # Return the first found window
                hwnd, title, commander = windows[0]
                print(f"Found window for commander {commander}: '{title}'")
                logger.info(f"Elite Dangerous window detected for {commander}")
                return hwnd, title, commander
            
            check_count += 1
            if check_count % 10 == 0:  # Every 5 seconds
                print(f"Still waiting for commander windows... (checked {check_count} times)")
                
            time.sleep(0.5)  # Check every 500ms
            
            # Update remaining commanders list in case some were processed
            remaining_commanders = [cmd for cmd in CONFIG["commanders"] if cmd not in self.processed_commanders]
            
        return None

    def wait_for_audio(self, commander: str) -> None:
        """Wait until Elite Dangerous starts producing audio."""
        print(f"Window found for {commander}! Now waiting for Elite Dangerous to start producing audio...")
        
        audio_check_count = 0
        while True:
            if self.is_elite_producing_audio():
                print(f"Elite Dangerous is now producing audio for {commander}!")
                logger.info(f"Elite Dangerous audio detected for {commander}")
                return
            
            audio_check_count += 1
            if audio_check_count % 10 == 0:  # Every 5 seconds
                print(f"Still waiting for audio for {commander}... (checked {audio_check_count} times)")
                
            time.sleep(0.5)  # Check every 500ms

    def send_esc_keys(self, elite_hwnd: int, commander: str):
        """Send ESC key twice with focus management."""
        try:
            print(f"Sending first ESC key to {commander}'s window...")
            
            # Focus window and send first esc
            win32gui.SetForegroundWindow(elite_hwnd)
            time.sleep(0.1)  # Brief delay to ensure focus
            pydirectinput.press('esc')
            logger.info(f"First ESC key sent to {commander}")
            
            # Wait 250ms
            time.sleep(0.25)
            
            print(f"Sending second ESC key to {commander}'s window...")
            
            # Focus window again and send second esc
            win32gui.SetForegroundWindow(elite_hwnd)
            time.sleep(0.1)  # Brief delay to ensure focus
            pydirectinput.press('esc')
            logger.info(f"Second ESC key sent to {commander}")
            
            print(f"Cutscene skip complete for {commander}!")
            
        except Exception as e:
            logger.error(f"Error sending ESC keys to {commander}: {e}")
            print(f"Error sending keys to {commander}: {e}")

    def process_commander(self, hwnd: int, title: str, commander: str):
        """Process a single commander's window."""
        print(f"\n{'='*60}")
        print(f"Processing Commander: {commander}")
        print(f"Window Title: {title}")
        print(f"{'='*60}")
        
        # Wait for Elite to start producing audio
        self.wait_for_audio(commander)

        # Brief pause to ensure everything is ready
        print(f"Audio detected for {commander}! Waiting 1 second before sending keys...")
        time.sleep(1)
        
        # Send the ESC keys to skip cutscene
        self.send_esc_keys(hwnd, commander)
        
        # Mark this commander as processed
        self.processed_commanders.add(commander)
        remaining = self.total_commanders - len(self.processed_commanders)
        
        print(f"✅ Commander {commander} processed successfully!")
        print(f"Remaining commanders: {remaining}")
        logger.info(f"Commander {commander} processed. {remaining} remaining.")

    def run(self):
        """Main execution logic."""
        print("Starting Multi-Commander AutoLoad process...")
        
        while len(self.processed_commanders) < self.total_commanders:
            # Wait for next commander's window
            result = self.wait_for_next_commander_window()
            
            if result is None:
                print("No more commanders to process.")
                break
                
            hwnd, title, commander = result
            
            # Process this commander
            self.process_commander(hwnd, title, commander)
            
            if len(self.processed_commanders) < self.total_commanders:
                print(f"\n🔄 Looking for next commander...")
                time.sleep(1)  # Brief pause before looking for next commander
        
        print(f"\n{'='*60}")
        print("🎉 All commanders processed!")
        print(f"Processed: {', '.join(sorted(self.processed_commanders))}")
        print(f"{'='*60}")


def main():
    """Main function to start the Multi-Commander AutoLoad process."""
    print("Starting Elite Dangerous Multi-Commander AutoLoad...")
    
    autoload = MultiCommanderAutoLoad()
    autoload.run()
    
    print("Multi-Commander AutoLoad complete. Exiting.")
    logger.info("Multi-Commander AutoLoad process finished")


if __name__ == "__main__":
    main()