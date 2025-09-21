# Elite Dangerous PY
My personal python scripts for Elite: Dangerous

**Elite Dangerous AutoHonk** is a standalone Python script that automatically uses your ship's discovery scanner (honk) after every FSD jump in Elite Dangerous. It works by monitoring your game's journal files and simulating a keypress at the appropriate time.

-----

## Features

  - **Automatic FSD Jump Detection**: Monitors your Elite Dangerous journal files to detect FSD jumps in real-time.
  - **Configurable Delay**: Waits a specified amount of time after a jump before honking, giving you time to regain control.
  - **Automatic Key Detection**: By default, it automatically detects your **Primary Fire** key from your game's bindings file.
  - **Manual Key Override**: Option to manually set a specific key to use for the honk.
  - **Simulated Keypress**: Safely sends a keypress command to the Elite Dangerous window, holding the key for a configurable duration.
  - **Foreground Window Focus**: Ensures the Elite Dangerous window is in the foreground before sending the keypress to guarantee the action is registered.

-----

## Requirements

You need to have Python installed on your system. This script has a few dependencies you'll need to install:

  - `pywin32`: For interacting with Windows API (finding and focusing the game window).
  - `watchdog`: For monitoring the journal folder for new file changes.
  - `pydirectinput`: For simulating keyboard input.

To install these, run the following command in your terminal or command prompt:
```sh
pip install pywin32 watchdog pydirectinput
```

If you installed python3 via Chocolatey or Scoop on Windows you may need to call it by pip3:
```sh
pip install pywin32 watchdog pydirectinput
```

-----

## How to Use

### 1\. **Download the Script**

Download the `autohonk.py` file from the repository to a location on your computer.

### 2\. **Configuration**

You can customize the script by editing the `CONFIG` dictionary at the top of the `autohonk.py` file.
```python
CONFIG = {
    # IMPORTANT: Change this if you have multiple accounts to ensure the
    # script targets the correct game instance.
    "window_title_contains": "Elite - Dangerous (CLIENT)", 
    
    # Hold key for x seconds
    "hold_duration": 6.0,  
    
    # Wait x seconds after jump before honking
    "delay_after_jump": 2.0,  
    
    # Auto-detect from bindings (highly recommended)
    "auto_detect_primary_fire": True,  
    
    # Set to a specific key (e.g., 'numpad_add') to override auto-detection
    "manual_key_override": None,  
    
    # Path to your Elite Dangerous journal folder
    "journal_folder": Path.home() / "Saved Games" / "Frontier Developments" / "Elite Dangerous",
}
```

Most users won't need to change anything unless they use a non-standard key for Primary Fire or want to adjust the timing. The script will automatically try to find your Primary Fire key by looking for a keyboard binding, inspired by Razzafrag/EDCoPilot.

### 3\. **Run the Script**

Simply run the script from your terminal:

```sh
python autohonk.py
```

The script will start monitoring your journal files and print its status to the console. Leave this window open while you play Elite Dangerous.

### 4\. **Stop the Script**

To stop the script, go back to the terminal window and press `Ctrl + C`.

-----

## Important Notes

  - **Primary Fire Key**: The script defaults to using your Primary Fire key because the Discovery Scanner is typically bound to this. If you have a custom key binding for the scanner, it's recommended to set `auto_detect_primary_fire` to `False` and provide a `manual_key_override`.
  - **Game Window**: The script needs to bring the Elite Dangerous window to the foreground to send the keypress. This might cause the window to briefly flash or move.
  - **Troubleshooting**: If the script isn't working, check the console output. It will provide logs for key detection, window finding, and any errors. Ensure the `journal_folder` path is correct and that you've installed all the required libraries.