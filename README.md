# EDPY

A collection of Python scripts and shell wrappers for use alongside **Elite: Dangerous**. These are out-of-game utilities — monitoring, diagnostics, and notification tools. None of them inject input into a running game session during live play without explicit user action.

> **Full documentation:** [GitHub Wiki](https://github.com/Quadstronaut/EDPY/wiki)

---

## Scripts

| Folder | Script(s) | What it does | Platform |
|---|---|---|---|
| `LogTail/` | `logtail.py` | Watches Odyssey journal files in real time; counts every event type and persists counts across sessions. Bonus: alerts loudly if `RAXXLA` ever appears in a journal line. | Windows / Linux / macOS |
| `Rackham_Wine/` | `rackham_wine.py` + `wrapper_rackham_wine.sh` | Headless Selenium scraper for the Wine sell price at Rackham's Peak (via inara.cz). Fires a Discord webhook notification when the price crosses a configurable threshold; maintains a rolling 365-day price history. Designed to run as a cron job on a remote Linux host. | Linux (cron) |
| `InputTesting/` | `debug_inputs.py` | Interactive diagnostic tool — tests four distinct Windows input methods (pydirectinput, pyautogui, win32api.keybd_event, win32api.PostMessage) for sending a held Numpad `+` key to the Elite Dangerous window. Useful for verifying which method the game client accepts. | Windows only |
| `WindowTitles/` | `constrained_windowtitles.py` | Enumerates all top-level windows, finds `EliteDangerous64.exe` by process name (not window title), and polls its window title every 3 seconds using pywin32. | Windows only |
| `WindowTitles/` | `pygetwindow_windowtitles.py` | Alternative window-title poller using psutil + pygetwindow; polls every 0.5 s. | Windows only |
| `WindowTitles/` | `rich_windowtitles.py` | Process monitor that searches all running processes for a user-supplied string and renders results in a Rich table refreshing every 0.5 s. Window title column is a placeholder (`"Available"`) — not yet implemented. | Windows / Linux / macOS |
| `audio_listener/` | `audio_listener.py` | Polls Windows audio sessions (via pycaw) to detect whether specified Elite Dangerous client windows have active audio output. Exits with code `0` and prints `TRUE` when all configured windows are producing audio. | Windows only |

---

## Requirements

Each script lists its own `pip install` requirements at the top of the file. Global summary:

| Dependency | Used by |
|---|---|
| `watchdog` | `logtail.py` |
| `selenium`, `requests`, `python-dotenv` | `rackham_wine.py` |
| `pydirectinput`, `pyautogui`, `pywin32` | `debug_inputs.py` |
| `pywin32` | `constrained_windowtitles.py`, `audio_listener.py` |
| `psutil`, `pygetwindow` | `pygetwindow_windowtitles.py` |
| `psutil`, `rich` | `rich_windowtitles.py` |
| `pywin32`, `pycaw` | `audio_listener.py` |

Python 3.9+ recommended. No single `requirements.txt` is provided — install per-script as needed.

---

## Rackham Wine — configuration

Create a `.env` file in the `Rackham_Wine/` directory:

```
RACKHAM_WEBHOOK=https://discord.com/api/webhooks/...
```

The price threshold (`PRICE_THRESHOLD`), inara.cz URL (`INARA_URL`), and price history file path (`PRICE_FILE`) are constants at the top of `rackham_wine.py` — edit them directly.

The `wrapper_rackham_wine.sh` contains two placeholder paths (`/foo/bar/...`) that **must** be updated to reflect the actual deployment directory before the script is run or added to crontab.

---

## License

MIT — see individual file headers where present. Author: Kyle Green ([Quadstronaut](https://github.com/Quadstronaut)).
