### The 'Grapevine' System: A Rackham Wine Market Monitor Module

This repository contains the **Grapevine System**, a standalone module designed to provide real-time market monitoring for **Rackham's Peak**. The system is a remote-access, autonomous unit built for the discerning trader who wants to capitalize on the highly volatile wine market. It operates by scraping crucial market data from third-party pilot databases and sends an encrypted comms burst directly to your personal datapad via a secure channel when the price of Wine surges past a profitable threshold.

The Grapevine System requires a standalone operating environment, as its unique operational parameters and security protocols prevent it from being integrated into a ship's main computer.

---

### Grapevine Module: `rackham_wine.py` 🍇

The main component of the Grapevine System is the `rackham_wine.py` module. It uses a proprietary, low-power, distributed computing array to scrape crucial market data from external pilot networks. This is the heart of the system, responsible for data retrieval, analysis, and notification.

* **Data Scavenging**: It deploys a `selenium` web agent to scrape price information from a specified station on external pilot network databases like `inara.cz`. This is how it gathers the raw market data.
* **Historical Record**: The module maintains a local log, `wine_price_history.json`, to track and analyze all price fluctuations. This historical data is crucial for predicting future market trends and identifying cyclical price spikes.
* **Comms Burst**: A secure, low-latency comms burst is transmitted to a pre-configured webhook on your personal datapad. The message is triggered when the price of Wine surpasses a set threshold (e.g., 250,000 Cr.), ensuring you receive a timely notification.

---

### Grapevine Deployment Wrapper: `wrapper_rackham_wine.sh` ⚙️

This is the boot-time executable for the Grapevine System. The `wrapper_rackham_wine.sh` script is a critical component for deploying the main module as a scheduled background task. It ensures the module runs securely and efficiently on a remote host.

* **Virtual Operating Environment**: The script uses `xvfb-run` to create a virtual, "headless" display. This is a crucial security measure and a technical necessity for the secure data-scavenging agent to run correctly within a timed-deployment routine.
* **Dependency Management**: It activates the correct Python virtual environment, guaranteeing all required dependencies are met before executing the main module.
* **Error Logging**: The wrapper includes robust error handling and logging, writing all output to a dedicated log file to assist with diagnostics and troubleshooting.

---

### Configuration File: `.env` 📜

The `.env` file is the central hub for configuring the Grapevine System's operational parameters. All sensitive information and configurable thresholds are stored here to keep them separate from the main codebase, ensuring both security and ease of use.

* **Secure API Keys**: This file holds the Discord webhook URL, allowing the system to send encrypted comms bursts to your personal datapad.
* **Custom Thresholds**: You can set the price threshold that triggers a notification, allowing you to tailor the system to your specific trading strategy.
* **Runtime Variables**: The `.env` file can also store other runtime variables, such as the specific `inara.cz` URL to monitor, making the system highly flexible.

---

It is important to note that when you are performing automated actions on the internet that you do so at a sane and reasonable pace so as not to incur high execution costs or infringe on service availability for other users. Please scrape responsibly.