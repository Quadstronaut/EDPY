import time
import logging
from typing import Optional

# Third party API imports for window handling
import win32api
import win32con
import win32gui
import win32process

def find_elite_dangerous_window_and_get_title() -> Optional[str]:
    """
    Enumerates all windows to find the EliteDangerous64.exe process
    and returns its main window title.
    """
    def callback(hwnd, extra):
        # Retrieve the process ID for the current window handle
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            try:
                # Get PID from window handle
                thread_id, process_id = win32process.GetWindowThreadProcessId(hwnd)
                
                # Open the process with limited rights to get its executable name
                process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, process_id)
                
                # Get the process executable name
                process_name = win32process.GetModuleFileNameEx(process_handle, 0)
                win32api.CloseHandle(process_handle)
                
                # Check if the process name matches Elite Dangerous
                if "EliteDangerous64.exe" in process_name:
                    extra.append(win32gui.GetWindowText(hwnd))
            except Exception:
                # This can fail for system processes, so we ignore errors
                pass
        return True
    
    found_titles = []
    # Enumerate all top-level windows and call the callback function
    win32gui.EnumWindows(callback, found_titles)
    
    # Return the first title found, or None if not found
    return found_titles[0] if found_titles else None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Polling for Elite Dangerous window title. Press Ctrl+C to stop.")
    
    while True:
        title = find_elite_dangerous_window_and_get_title()
        if title:
            logging.info(f"Current Window Title: {title}")
        else:
            logging.info("EliteDangerous64.exe process is not currently running.")
        
        time.sleep(3) # Poll every 3 seconds