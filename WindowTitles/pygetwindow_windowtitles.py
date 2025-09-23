import psutil
import pygetwindow as gw
import time

def get_ed_window_title():
    """
    Finds the Elite Dangerous process and prints its main window title.
    """
    process_found = False
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'EliteDangerous64.exe':
            process_found = True
            try:
                # Find the window associated with the process
                windows = gw.getWindowsWithTitle(None)
                ed_window = None
                for window in windows:
                    if 'Elite Dangerous' in window.title:
                        ed_window = window
                        break

                if ed_window:
                    print(f"Current Window Title: {ed_window.title}")
                else:
                    print("Elite Dangerous window found, but no title available.")
            except Exception as e:
                print(f"An error occurred: {e}")
            break

    if not process_found:
        print("EliteDangerous64.exe process is not currently running.")

if __name__ == "__main__":
    print("Polling for Elite Dangerous window title. Press Ctrl+C to stop.")
    while True:
        get_ed_window_title()
        time.sleep(0.5)