### `Elite Dangerous` Automation Scripts

This repository contains a collection of Python scripts designed to automate various tasks in the game **Elite Dangerous**. Each script is standalone and focuses on a specific function, from monitoring in-game prices to automating common actions.

---

### AutoHonk 📣

The `autohonk.py` script is a standalone tool that automatically activates your ship's discovery scanner ("honk") after every hyperspace jump. This is an essential time-saver for explorers who want to quickly scan new systems for astronomical bodies without manually pressing the key each time.

**How it works:**
* **Journal Monitoring**: The script uses the `watchdog` library to monitor your Elite Dangerous player journal files in real-time.
* **Event Detection**: It listens for the `FSDJump` event in the journal, which signifies a successful jump to a new star system.
* **Keypress Simulation**: After a jump is detected, the script waits for a configurable delay and then uses `pydirectinput` to simulate a keypress for your ship's "Primary Fire" button, which is typically bound to the discovery scanner.
* **Window Management**: The script automatically finds and focuses the Elite Dangerous game window to ensure the keypress is sent to the correct application.
* **Bindings Detection**: It can automatically detect your "Primary Fire" key binding from your game's settings, eliminating the need for manual configuration.

---

### Debug_Inputs 🩺

The `debug_inputs.py` script is a utility for diagnosing and testing various methods of simulating keyboard input on Windows. This script was created to help troubleshoot issues with the `AutoHonk` script and can be useful for anyone developing tools that require sending keypresses to games. It tests four different input methods and provides feedback on whether the keypress was successfully registered.

---

### Wine Price Scraper 🍇

This cron-scheduled Python script, `rackham_wine.py`, monitors the in-game price of **Wine** at the Rackham's Peak starport. It uses **Selenium** to scrape data from `inara.cz`, a third-party Elite Dangerous database, and sends a notification to a **Discord** channel via a webhook if the price exceeds a specific threshold. This is particularly useful for traders looking to capitalize on high-profit trading opportunities.

**How it works:**
* **Web Scraping**: `selenium` is used to fetch the current price of Wine from a specific station's market page on `inara.cz`.
* **Price History**: The script maintains a local JSON file (`wine_price_history.json`) to track price changes over time.
* **Discord Notifications**: A message is sent to a configurable Discord webhook when the price of Wine surpasses a set threshold (e.g., 250,000 Cr.), ensuring you never miss a profitable trade.
* **Cron Job**: The `wrapper_rackham_wine.sh` script is designed to run the Python script as a scheduled task. It uses `xvfb-run` to provide a virtual display environment, which is necessary for Selenium to run correctly in a `crontab` context.
