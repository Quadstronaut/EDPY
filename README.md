# AutoHonk EDMC Plugin

An Elite Dangerous Market Connector (EDMC) plugin that automatically triggers your Primary Fire key (which is also your Discovery Scanner) when you enter a new system.

## Features

- **Auto-detects your Primary Fire key** from Elite Dangerous bindings files
- Automatically detects when you enter a new system via FSD jump
- Uses your actual Primary Fire key binding from the game
- Adjustable delay before triggering the honk
- Configurable key hold duration
- Cross-platform support (Windows, macOS, Linux)
- Manual key override option
- Easy enable/disable toggle

## Installation

### Method 1: Manual Installation

1. **Download the Plugin**: Save the `load.py` file from the artifact above
2. **Find your EDMC plugins folder**:
   - **Windows**: `%LOCALAPPDATA%\EDMarketConnector\plugins\` or `C:\Users\[YourUsername]\AppData\Local\EDMarketConnector\plugins\`
   - **macOS**: `~/Library/Application Support/EDMarketConnector/plugins/`
   - **Linux**: `~/.local/share/EDMarketConnector/plugins/`
3. **Create plugin directory**: Create a new folder called `AutoHonk` in the plugins directory
4. **Install the plugin**: Place the `load.py` file inside the `AutoHonk` folder
5. **Restart EDMC**: Close and restart Elite Dangerous Market Connector

### Method 2: Via EDMC Plugins Folder

1. Open EDMC
2. Go to `File` > `Settings`
3. Click on the `Plugins` tab
4. Click `Open` next to "Plugins folder"
5. Create a new folder called `AutoHonk`
6. Place the `load.py` file inside this folder
7. Restart EDMC

## Configuration

After installation and restarting EDMC:

1. Open EDMC Settings (`File` > `Settings`)
2. Go to the `AutoHonk` tab
3. Configure the following options:
   - **Enable AutoHonk**: Check to enable the plugin
   - **Auto-detect Primary Fire key**: Automatically finds your Primary Fire binding from Elite Dangerous (recommended)
   - **Detected key**: Shows the key that was found in your bindings (with refresh button)
   - **Manual key override**: Specify a different key if auto-detection fails or you want to use a different key
   - **Delay (seconds)**: How long to wait after entering a system before honking (default: 2.0)
   - **Hold duration (seconds)**: How long to hold the key press (default: 0.1)

## How It Works

The plugin reads your Elite Dangerous bindings files to find your Primary Fire key binding. In Elite Dangerous, the Primary Fire key is also used for the Discovery Scanner when no weapons are deployed. The plugin looks in these locations:

- **Windows**: `%LOCALAPPDATA%\Frontier Developments\Elite Dangerous\Options\Bindings\`
- **macOS**: `~/Library/Application Support/Frontier Developments/Elite Dangerous/Options/Bindings/`
- **Linux**: Various Wine prefix locations

## Usage

1. Make sure the plugin is enabled in settings
2. Verify the key binding matches your in-game Discovery Scanner hotkey
3. Start Elite Dangerous and EDMC
4. When you jump to a new system, the plugin will automatically trigger your Discovery Scanner after the configured delay

## Troubleshooting

### Plugin Not Working

- **Check Elite Dangerous is the active window**: The keypress is sent to the currently active window
- **Verify key binding**: Make sure the key in plugin settings matches your in-game Discovery Scanner binding
- **Check EDMC logs**: Look for AutoHonk messages in EDMC's log files
- **Platform-specific issues**:
  - **Windows**: Ensure you have the `pywin32` package (usually included with EDMC)
  - **macOS**: The plugin uses AppleScript, which may require accessibility permissions
  - **Linux**: Requires `xdotool` to be installed (`sudo apt-get install xdotool` on Debian/Ubuntu)

### Key Not Recognized

- Single character keys: Use the actual character (e.g., "1", "a", "x")
- Special keys: Use lowercase names (e.g., "space", "enter", "f1", "f12")
- Function keys: Use "f1" through "f12"

### Timing Issues

- If honking happens too early: Increase the delay
- If honking happens too late: Decrease the delay
- If key press isn't registered: Increase the hold duration

## System Requirements

- Elite Dangerous Market Connector (EDMC) version 3.0 or higher
- Elite Dangerous (PC version only)
- Python dependencies (usually included with EDMC):
  - Windows: `pywin32`
  - macOS: Built-in `subprocess` and `osascript`
  - Linux: `xdotool` (may need separate installation)

## How It Works

The plugin monitors Elite Dangerous journal entries for:
- `FSDJump` events (jumping to a new system)
- `StartUp` and `LoadGame` events (in case jumps are missed)

When a new system is detected, it schedules a keypress using the configured delay and sends the keypress to simulate pressing your Discovery Scanner hotkey.

## Privacy and Security

- The plugin only reads game journal files and sends keypresses
- No data is transmitted over the internet
- No personal information is collected or stored
- All operations are performed locally on your computer

## License

This plugin is provided as-is for educational and convenience purposes. Use at your own risk.

## Support

For issues, questions, or improvements:
1. Check the troubleshooting section above
2. Verify your EDMC and Elite Dangerous setup
3. Check EDMC's log files for error messages

## Version History

- **1.0.0**: Initial release
  - Basic autohonk functionality
  - Cross-platform support
  - Configurable settings
  - System entry detection via journal monitoring