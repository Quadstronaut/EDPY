"""
AutoHonk Debug Script
Run this script to test various components of the AutoHonk plugin
"""

import os
import sys
import logging
from pathlib import Path
import glob
import xml.etree.ElementTree as ET

# Add the plugin directory to sys.path if needed
# sys.path.append(r"C:\path\to\your\plugin\directory")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_bindings_detection():
    """Test Elite Dangerous bindings detection."""
    print("=== Testing Bindings Detection ===")
    
    # Check for bindings directory
    local_appdata = os.environ.get('LOCALAPPDATA')
    if local_appdata:
        bindings_dir = Path(local_appdata) / "Frontier Developments" / "Elite Dangerous" / "Options" / "Bindings"
        print(f"Bindings directory: {bindings_dir}")
        print(f"Directory exists: {bindings_dir.exists()}")
        
        if bindings_dir.exists():
            binds_files = glob.glob(str(bindings_dir / "*.binds"))
            print(f"Found {len(binds_files)} .binds files:")
            for f in binds_files:
                print(f"  - {f}")
                
            if binds_files:
                # Try to parse the most recent one
                binds_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                latest_file = binds_files[0]
                print(f"\nTesting latest file: {latest_file}")
                
                try:
                    tree = ET.parse(latest_file)
                    root = tree.getroot()
                    
                    # Look for PrimaryFire binding
                    primary_fire = root.find(".//PrimaryFire")
                    if primary_fire is not None:
                        print("Found PrimaryFire binding!")
                        primary = primary_fire.find("Primary")
                        if primary is not None:
                            device = primary.get("Device")
                            key_attr = primary.get("Key")
                            print(f"  Device: {device}")
                            print(f"  Key: {key_attr}")
                        else:
                            print("  No Primary binding found")
                    else:
                        print("PrimaryFire binding not found in XML")
                        
                except Exception as e:
                    print(f"Error parsing bindings file: {e}")
        else:
            print("Bindings directory does not exist!")

def test_window_detection():
    """Test window detection."""
    print("\n=== Testing Window Detection ===")
    
    try:
        import win32gui
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ("elite" in title.lower() or "dangerous" in title.lower()):
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        print(f"Found {len(windows)} Elite-related windows:")
        for hwnd, title in windows:
            print(f"  - '{title}' (hwnd: {hwnd})")
            
        if not windows:
            print("No Elite Dangerous windows found!")
            print("Make sure Elite Dangerous is running.")
            
    except ImportError:
        print("win32gui not available - cannot test window detection")

def test_keypress():
    """Test keypress functionality."""
    print("\n=== Testing Keypress ===")
    
    try:
        import win32api
        import win32con
        import time
        
        print("Testing keypress in 3 seconds... switch to a text editor!")
        time.sleep(3)
        
        # Test pressing '1' key
        vk_code = ord('1')
        print(f"Sending keypress for '1' (VK code: {vk_code})")
        
        win32api.keybd_event(vk_code, 0, 0, 0)  # Key down
        time.sleep(0.1)  # Hold for 100ms
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up
        
        print("Keypress sent!")
        
    except ImportError:
        print("win32api not available - cannot test keypress")
    except Exception as e:
        print(f"Error testing keypress: {e}")

def test_journal_location():
    """Test journal file location."""
    print("\n=== Testing Journal Location ===")
    
    saved_games = os.path.expanduser("~/Saved Games")
    journal_dir = Path(saved_games) / "Frontier Developments" / "Elite Dangerous"
    
    print(f"Journal directory: {journal_dir}")
    print(f"Directory exists: {journal_dir.exists()}")
    
    if journal_dir.exists():
        journal_files = list(journal_dir.glob("Journal.*.log"))
        print(f"Found {len(journal_files)} journal files")
        
        if journal_files:
            # Find the most recent one
            latest_journal = max(journal_files, key=lambda x: x.stat().st_mtime)
            print(f"Latest journal: {latest_journal}")
            print(f"Size: {latest_journal.stat().st_size} bytes")
            
            # Try to read the last few lines
            try:
                with open(latest_journal, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    print("\nLast 3 lines of journal:")
                    for line in lines[-3:]:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"Error reading journal: {e}")

if __name__ == "__main__":
    print("AutoHonk Plugin Debug Script")
    print("=" * 40)
    
    test_bindings_detection()
    test_window_detection()
    test_keypress()
    test_journal_location()
    
    print("\n=== Debug Complete ===")
    input("Press Enter to exit...")