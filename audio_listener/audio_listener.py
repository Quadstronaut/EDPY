"""
Elite Dangerous Audio Listener
Listens for sound from all specified game client windows.

Requirements:
- pip install pywin32 pycaw
"""

import time
import logging
from typing import Set, List, Tuple
import ctypes
from ctypes import wintypes
import win32gui
import win32process
from pycaw.pycaw import AudioUtilities

# Configuration
CONFIG = {
    "window_title_contains": "Elite - Dangerous (CLIENT)",
    "commanders": ["Bistronaut", "Tristronaut", "Quadstronaut"], # Replace with your commander names
}

def find_target_windows() -> List[Tuple[int, str, str]]:
    """Finds all windows matching the commander names."""
    
    found_windows = []
    
    def enum_handler(hwnd, ctx):
        title = win32gui.GetWindowText(hwnd)
        
        # Get the process ID for the window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = win32process.GetModuleFileNameEx(win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid), 0).split('\\')[-1].split('.')[0]
        
        # Match against commander names
        for commander in CONFIG["commanders"]:
            if commander.lower() in title.lower() or ("primary" in commander.lower() and CONFIG["window_title_contains"] in title and not any(alt.lower() in title.lower() for alt in CONFIG["commanders"])):
                found_windows.append((hwnd, title, commander))
                return True
        return True

    win32gui.EnumWindows(enum_handler, None)
    return found_windows

def has_audio_activity(process_id: int) -> bool:
    """Checks if a given process ID has an active audio session."""
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.pid == process_id:
            return session.State == 1  # 1 is the state for audio playing
    return False

def main():
    """Main function to start the audio listening process."""
    
    while True:
        try:
            target_windows = find_target_windows()
            
            if not target_windows:
                # If no windows are found, wait and try again
                time.sleep(1)
                continue
            
            all_have_audio = True
            
            for hwnd, title, commander in target_windows:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                
                if not has_audio_activity(pid):
                    all_have_audio = False
                    break # Break the inner loop if any window has no audio
            
            if all_have_audio:
                # If all windows have audio, exit successfully
                print("TRUE")
                return 0 # Exit with code 0
            
            time.sleep(1) # Wait and check again
            
        except Exception as e:
            # Handle potential errors, such as a window closing unexpectedly
            continue

if __name__ == "__main__":
    main()