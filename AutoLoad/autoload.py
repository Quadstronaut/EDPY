"""
Elite Dangerous AutoLoad - Multi-Commander Script
Sends a couple ESC keys to skip the opening cutscene for one or more commanders.

Requirements:
- pip install pywin32 pycaw
"""

import time
import logging
from typing import Optional, Set, List, Tuple
import ctypes
from ctypes import wintypes

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
    # For multibox setups define your alts here
    "commanders": ["Bistronaut", "Tristronaut", "Quadstronaut"],
    "primary_commander": "Duvrazh",  # Primary commander default without name in window title
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
        self.all_commanders = CONFIG["commanders"] + [CONFIG["primary_commander"]]
        self.total_commanders = len(self.all_commanders)
        
        print("=" * 60)
        print("Elite Dangerous Multi-Commander AutoLoad - Skip Cutscene")
        print("=" * 60)
        print(f"Looking for process: '{CONFIG['process_name']}.exe'")
        print(f"Window title must contain: '{CONFIG['window_title_contains']}'")
        print(f"Named commanders: {', '.join(CONFIG['commanders'])}")
        print(f"Primary commander (no name in title): {CONFIG['primary_commander']}")
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
                                
                                # First, check for named commanders
                                for commander in CONFIG["commanders"]:
                                    if commander not in self.processed_commanders and commander.lower() in title.lower():
                                        windows.append((hwnd, title, commander))
                                        logger.info(f"Found Elite window for {commander}: '{title}' from process: {process_name}")
                                        return True  # Found a named commander, continue
                                
                                # If no named commanders found and primary commander not processed,
                                # check if this could be the primary commander's window
                                primary_commander = CONFIG["primary_commander"]
                                if primary_commander not in self.processed_commanders:
                                    # Check if title contains any OTHER commander names - if not, it's likely the primary
                                    has_other_commander = any(cmd.lower() in title.lower() for cmd in CONFIG["commanders"])
                                    if not has_other_commander:
                                        # This window doesn't contain any named commander, assume it's primary
                                        windows.append((hwnd, title, primary_commander))
                                        logger.info(f"Found Elite window for {primary_commander} (no name in title): '{title}' from process: {process_name}")
                                        
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
        remaining_commanders = [cmd for cmd in self.all_commanders if cmd not in self.processed_commanders]
        
        if not remaining_commanders:
            return None
            
        print(f"\nWaiting for windows from remaining commanders: {', '.join(remaining_commanders)}")
        
        check_count = 0
        while remaining_commanders:
            windows = self.find_unprocessed_elite_windows()
            if windows:
                # Prioritize named commanders over primary commander
                named_windows = [(hwnd, title, cmd) for hwnd, title, cmd in windows if cmd in CONFIG["commanders"]]
                primary_windows = [(hwnd, title, cmd) for hwnd, title, cmd in windows if cmd == CONFIG["primary_commander"]]
                
                # Process named commanders first, then primary
                if named_windows:
                    hwnd, title, commander = named_windows[0]
                elif primary_windows and len(self.processed_commanders) == len(CONFIG["commanders"]):
                    # Only process primary commander after all named commanders are done
                    hwnd, title, commander = primary_windows[0]
                else:
                    # Wait for named commanders first
                    check_count += 1
                    if check_count % 10 == 0:  # Every 5 seconds
                        print(f"Still waiting for named commander windows... (checked {check_count} times)")
                    time.sleep(0.5)
                    continue
                
                print(f"Found window for commander {commander}: '{title}'")
                logger.info(f"Elite Dangerous window detected for {commander}")
                return hwnd, title, commander
            
            check_count += 1
            if check_count % 10 == 0:  # Every 5 seconds
                print(f"Still waiting for commander windows... (checked {check_count} times)")
                
            time.sleep(0.5)  # Check every 500ms
            
            # Update remaining commanders list in case some were processed
            remaining_commanders = [cmd for cmd in self.all_commanders if cmd not in self.processed_commanders]
            
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
        """Send ESC key twice using multiple methods for maximum compatibility."""
        try:
            print(f"Focusing window and sending ESC keys to {commander}...")
            
            # Ensure window is properly focused
            win32gui.SetForegroundWindow(elite_hwnd)
            win32gui.SetActiveWindow(elite_hwnd)
            time.sleep(0.3)  # Give time for focus to establish
            
            # Verify focus
            focused_hwnd = win32gui.GetForegroundWindow()
            if focused_hwnd != elite_hwnd:
                logger.warning(f"Window focus verification failed for {commander}")
                win32gui.ShowWindow(elite_hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(elite_hwnd)
                time.sleep(0.3)
            
            # Method 1: SendMessage with proper key codes (most reliable for games)
            def send_esc_via_sendmessage():
                VK_ESCAPE = 0x1B
                scan_code = 0x01  # ESC scan code
                
                # Create proper lParam values
                lparam_down = 0x00010001  # repeat count=1, scan code=1, extended=0, context=0, previous=0, transition=0
                lparam_up = 0xC0010001    # repeat count=1, scan code=1, extended=0, context=1, previous=1, transition=1
                
                # Send key down
                result1 = win32gui.SendMessage(elite_hwnd, win32con.WM_KEYDOWN, VK_ESCAPE, lparam_down)
                time.sleep(0.01)  # Small delay
                
                # Send key up  
                result2 = win32gui.SendMessage(elite_hwnd, win32con.WM_KEYUP, VK_ESCAPE, lparam_up)
                
                logger.debug(f"SendMessage results for {commander}: down={result1}, up={result2}")
                return result1 == 0 and result2 == 0  # 0 indicates success for SendMessage
            
            # Method 2: PostMessage (asynchronous)
            def send_esc_via_postmessage():
                VK_ESCAPE = 0x1B
                lparam_down = 0x00010001
                lparam_up = 0xC0010001
                
                result1 = win32gui.PostMessage(elite_hwnd, win32con.WM_KEYDOWN, VK_ESCAPE, lparam_down)
                time.sleep(0.01)
                result2 = win32gui.PostMessage(elite_hwnd, win32con.WM_KEYUP, VK_ESCAPE, lparam_up)
                
                logger.debug(f"PostMessage results for {commander}: down={result1}, up={result2}")
                return result1 != 0 and result2 != 0  # Non-zero indicates success for PostMessage
            
            # Method 3: Global keybd_event (your original method)
            def send_esc_via_keybd_event():
                win32api.keybd_event(win32con.VK_ESCAPE, 0x01, 0, 0)  # Key down with scan code
                time.sleep(0.01)
                win32api.keybd_event(win32con.VK_ESCAPE, 0x01, win32con.KEYEVENTF_KEYUP, 0)  # Key up
                return True
            
            # Method 4: SendInput (most modern approach)
            def send_esc_via_sendinput():
                try:
                    # Import additional required constants
                    from ctypes import Structure, c_ulong, c_short, c_long, Union
                    
                    # Define INPUT structures
                    class KEYBDINPUT(Structure):
                        _fields_ = [("wVk", c_short),
                                    ("wScan", c_short),
                                    ("dwFlags", c_ulong),
                                    ("time", c_ulong),
                                    ("dwExtraInfo", ctypes.POINTER(c_ulong))]
                    
                    class HARDWAREINPUT(Structure):
                        _fields_ = [("uMsg", c_ulong),
                                    ("wParamL", c_short),
                                    ("wParamH", c_short)]
                    
                    class MOUSEINPUT(Structure):
                        _fields_ = [("dx", c_long),
                                    ("dy", c_long),
                                    ("mouseData", c_ulong),
                                    ("dwFlags", c_ulong),
                                    ("time", c_ulong),
                                    ("dwExtraInfo", ctypes.POINTER(c_ulong))]
                    
                    class INPUT_UNION(Union):
                        _fields_ = [("ki", KEYBDINPUT),
                                    ("mi", MOUSEINPUT),
                                    ("hi", HARDWAREINPUT)]
                    
                    class INPUT(Structure):
                        _fields_ = [("type", c_ulong),
                                    ("ui", INPUT_UNION)]
                    
                    # Constants
                    INPUT_KEYBOARD = 1
                    KEYEVENTF_KEYUP = 0x0002
                    
                    # Create key down input
                    key_down = INPUT()
                    key_down.type = INPUT_KEYBOARD
                    key_down.ui.ki.wVk = win32con.VK_ESCAPE
                    key_down.ui.ki.wScan = 0x01
                    key_down.ui.ki.dwFlags = 0
                    key_down.ui.ki.time = 0
                    key_down.ui.ki.dwExtraInfo = None
                    
                    # Create key up input
                    key_up = INPUT()
                    key_up.type = INPUT_KEYBOARD
                    key_up.ui.ki.wVk = win32con.VK_ESCAPE
                    key_up.ui.ki.wScan = 0x01
                    key_up.ui.ki.dwFlags = KEYEVENTF_KEYUP
                    key_up.ui.ki.time = 0
                    key_up.ui.ki.dwExtraInfo = None
                    
                    # Send the input
                    inputs = (INPUT * 2)(key_down, key_up)
                    result = ctypes.windll.user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
                    
                    logger.debug(f"SendInput result for {commander}: {result}")
                    return result == 2  # Should return number of inputs sent
                    
                except Exception as e:
                    logger.debug(f"SendInput failed for {commander}: {e}")
                    return False
            
            # Try each method in order of preference
            methods = [
                ("SendMessage", send_esc_via_sendmessage),
                ("SendInput", send_esc_via_sendinput), 
                ("PostMessage", send_esc_via_postmessage),
                ("keybd_event", send_esc_via_keybd_event)
            ]
            
            success_count = 0
            
            for attempt in range(2):  # Send ESC twice
                print(f"Sending ESC key #{attempt + 1} to {commander}...")
                
                method_success = False
                for method_name, method_func in methods:
                    try:
                        if method_func():
                            logger.info(f"ESC key #{attempt + 1} sent successfully to {commander} via {method_name}")
                            method_success = True
                            success_count += 1
                            break
                        else:
                            logger.debug(f"{method_name} failed for {commander} ESC #{attempt + 1}")
                    except Exception as e:
                        logger.debug(f"{method_name} exception for {commander} ESC #{attempt + 1}: {e}")
                
                if not method_success:
                    logger.warning(f"All methods failed for ESC key #{attempt + 1} to {commander}")
                
                # Wait between key presses
                if attempt == 0:
                    time.sleep(0.1)  # 100ms between first and second ESC
            
            if success_count > 0:
                print(f"Cutscene skip complete for {commander}! ({success_count}/2 keys sent successfully)")
                logger.info(f"ESC keys sent to {commander}: {success_count}/2 successful")
            else:
                print(f"Failed to send ESC keys to {commander} - all methods failed")
                logger.error(f"All ESC key methods failed for {commander}")
                
        except Exception as e:
            logger.error(f"Error in send_esc_keys for {commander}: {e}")
            print(f"Critical error sending keys to {commander}: {e}")

    def test_key_methods(self, elite_hwnd: int, commander: str):
        """Test function to verify which key sending method works best."""
        print(f"\n--- Testing key sending methods for {commander} ---")
        
        # Focus window first
        win32gui.SetForegroundWindow(elite_hwnd)
        time.sleep(0.5)
        
        # Test each method individually
        methods_to_test = [
            ("SendMessage", lambda: win32gui.SendMessage(elite_hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0x00010001)),
            ("PostMessage", lambda: win32gui.PostMessage(elite_hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0x00010001)),
            ("keybd_event", lambda: win32api.keybd_event(win32con.VK_ESCAPE, 0x01, 0, 0))
        ]
        
        for method_name, method_func in methods_to_test:
            try:
                result = method_func()
                print(f"{method_name}: {'SUCCESS' if result else 'FAILED'} (result: {result})")
                time.sleep(1)  # Wait between tests
            except Exception as e:
                print(f"{method_name}: ERROR - {e}")
                time.sleep(1)

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