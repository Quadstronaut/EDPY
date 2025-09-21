import time
import ctypes
from typing import Optional

# Install required packages: pip install pydirectinput pyautogui pywin32
import pydirectinput
import pyautogui
import win32gui
import win32con
import win32api

# --- Configuration ---
WINDOW_TITLE_CONTAINS = "Elite - Dangerous (CLIENT)"  # Use a general title for testing
TARGET_KEY_PYDIRECTINPUT = 'add'          # Key name for pydirectinput/pyautogui ('+' is often mapped to 'add' for numpad)
TARGET_KEY_WIN32 = win32con.VK_ADD        # Virtual-Key code for Numpad +
HOLD_DURATION_S = 6.0
DELAY_BEFORE_PRESS_S = 2.0

def find_and_focus_window(title_part: str) -> Optional[int]:
    """Finds a window with a title containing title_part and brings it to the foreground."""
    def callback(hwnd, hwnds):
        if title_part.lower() in win32gui.GetWindowText(hwnd).lower():
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)

    if not hwnds:
        print(f"❌ ERROR: Could not find a window with title containing '{title_part}'.")
        return None

    hwnd = hwnds[0]
    print(f"✅ Found window: '{win32gui.GetWindowText(hwnd)}' (handle: {hwnd})")

    try:
        # Bring the window to the front
        win32gui.SetForegroundWindow(hwnd)
        # Allow time for the OS to process the focus change
        time.sleep(0.5)
        print("Brought window to foreground.")
        return hwnd
    except Exception as e:
        print(f"❌ ERROR: Could not set foreground window: {e}")
        print("    -> Try running this script as an Administrator.")
        return None

def test_pydirectinput():
    """Method 1: Uses pydirectinput (SendInput wrapper)."""
    print("\n--- Testing Method 1: pydirectinput ---")
    hwnd = find_and_focus_window(WINDOW_TITLE_CONTAINS)
    if not hwnd:
        return

    print(f"Waiting {DELAY_BEFORE_PRESS_S} seconds...")
    time.sleep(DELAY_BEFORE_PRESS_S)

    print(f"Holding '{TARGET_KEY_PYDIRECTINPUT}' key down for {HOLD_DURATION_S}s...")
    pydirectinput.keyDown(TARGET_KEY_PYDIRECTINPUT)
    time.sleep(HOLD_DURATION_S)
    pydirectinput.keyUp(TARGET_KEY_PYDIRECTINPUT)
    print("Key released. Test complete.")

def test_pyautogui():
    """Method 2: Uses pyautogui (another SendInput wrapper)."""
    print("\n--- Testing Method 2: pyautogui ---")
    hwnd = find_and_focus_window(WINDOW_TITLE_CONTAINS)
    if not hwnd:
        return

    print(f"Waiting {DELAY_BEFORE_PRESS_S} seconds...")
    time.sleep(DELAY_BEFORE_PRESS_S)

    print(f"Holding '{TARGET_KEY_PYDIRECTINPUT}' key down for {HOLD_DURATION_S}s...")
    pyautogui.keyDown(TARGET_KEY_PYDIRECTINPUT)
    time.sleep(HOLD_DURATION_S)
    pyautogui.keyUp(TARGET_KEY_PYDIRECTINPUT)
    print("Key released. Test complete.")

def test_win32_keybd_event():
    """Method 3: Uses the low-level win32api.keybd_event."""
    print("\n--- Testing Method 3: win32api.keybd_event ---")
    hwnd = find_and_focus_window(WINDOW_TITLE_CONTAINS)
    if not hwnd:
        return

    print(f"Waiting {DELAY_BEFORE_PRESS_S} seconds...")
    time.sleep(DELAY_BEFORE_PRESS_S)

    print(f"Holding VK_CODE '{TARGET_KEY_WIN32}' down for {HOLD_DURATION_S}s...")
    # Press key down
    win32api.keybd_event(TARGET_KEY_WIN32, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(HOLD_DURATION_S)
    # Release key
    win32api.keybd_event(TARGET_KEY_WIN32, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)
    print("Key released. Test complete.")

def test_win32_postmessage():
    """Method 4: Sends window messages directly to the application."""
    print("\n--- Testing Method 4: win32api.PostMessage (WM_KEYDOWN/UP) ---")
    hwnd = find_and_focus_window(WINDOW_TITLE_CONTAINS)
    if not hwnd:
        return

    print(f"Waiting {DELAY_BEFORE_PRESS_S} seconds...")
    time.sleep(DELAY_BEFORE_PRESS_S)

    print(f"Posting WM_KEYDOWN for VK_CODE '{TARGET_KEY_WIN32}' for {HOLD_DURATION_S}s...")
    # This method is tricky for 'holding'. We send a 'down' message, wait, then 'up'.
    # Many games ignore this method, but it's good for testing.
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, TARGET_KEY_WIN32, 0)
    time.sleep(HOLD_DURATION_S)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, TARGET_KEY_WIN32, 0)
    print("WM_KEYUP posted. Test complete.")


def main():
    """Main loop to display the menu and run tests."""
    while True:
        print("\n" + "="*50)
        print("      Elite Dangerous Input Diagnostic Tool")
        print("="*50)
        print("Select an input method to test holding the Numpad '+' key:")
        print(" 1. pydirectinput (Hardware Simulation via SendInput)")
        print(" 2. pyautogui (Alternative Hardware Simulation)")
        print(" 3. win32api.keybd_event (Low-Level WinAPI Hardware Event)")
        print(" 4. win32api.PostMessage (Direct Window Message)")
        print("\n 0. Exit")
        print("="*50)

        choice = input("Enter your choice: ")

        if choice == '1':
            test_pydirectinput()
        elif choice == '2':
            test_pyautogui()
        elif choice == '3':
            test_win32_keybd_event()
        elif choice == '4':
            test_win32_postmessage()
        elif choice == '0':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print("Please ensure you have the required packages installed:")
    print("pip install pydirectinput pyautogui pywin32")
    main()