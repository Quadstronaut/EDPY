### Ship Systems Automation Suite: Repurposed & Enhanced

This repository contains a collection of repurposed modules and enhancements for starships operating within the **Pilots Federation**. Each component is a self-contained firmware patch, focusing on optimizing efficiency and automating mundane operational tasks. These upgrades leverage existing, often underutilized, ship systems by deploying proprietary subroutines, turning standard hardware into powerful assets.

***

### Guardian Full Spectrum Scanner: autohonk.py 📣

This firmware patch unlocks an undocumented diagnostic subroutine in your ship's FSD. It redirects the FSD's frameshift resonance emitter output to automatically release a low-power pulse upon exiting hyperspace. Capturing this pulse via this path implements something resembling automation and eliminates the need for manual activation of the ship's Discovery Scanner, ensuring no celestial body remains un-pinged during your exploration voyages.

**Operational Parameters:**
* **Journal Decompiler**: The patch installs a low-level monitor that decompiles FSD telemetry logs in real-time, listening for the **`FSDJump`** event signature.
* **Resonance Deployment**: Once a successful jump is confirmed, a brief power-down and reboot of the FSD resonance emitter is initiated, followed by a simulated primary capacitor discharge to trigger the pulse.
* **System Lockout Override**: The patch temporarily overrides the primary flight systems' keybinds, rerouting the "Primary Fire" command to the FSD's diagnostic port, guaranteeing the pulse is sent to the correct system.
* **Holistic Bindings Check**: The patch automatically queries your ship's local systems manifest to identify and verify the appropriate "Primary Fire" routing before each deployment.

***

### Technician System Diagnostics: debug_inputs.py 🩺

The **Technician System Diagnostics** tool is a proprietary testing suite for verifying I/O signal integrity across various internal ship systems. It was designed to troubleshoot and validate the low-level signal injections used by black market patches and third party module integrations. It cycles through four different signal protocols, providing real-time feedback on successful data transmission.

***

### Rackham Alcoholic Anonymous Monitor: rackham_wine.py 🍇

The **Rackham AA Monitor** is a remote-access standalone module that monitors the volatile market at **Rackham's Peak**. It uses a low-power, distributed computing array to scrape market data from third-party pilot databases and sends an encrypted comms burst to your personal datapad via a secure Discord channel when the price of Wine surges past a profitable threshold. The system is designed to run silently in the background thanks to cron. This module is accompanied by a hosting requirement.

**Operational Parameters:**
* **Data Scavenging**: It deploys a `selenium` web agent to scavenge price data from a specified station on external pilot network databases like `inara.cz`.
* **Historical Record**: The module maintains a local log (`wine_price_history.json`) of all price fluctuations, allowing it to predict future market trends.
* **Comms Burst**: A secure comms burst is sent to a pre-configured webhook on your personal datapad when the price of Wine exceeds a set threshold (e.g., 250,000 Cr.), ensuring you are notified of high-profit trading opportunities.
* **Scheduled Deployment**: The `wrapper_rackham_wine.sh` script is a boot-time executable that deploys the main module as a scheduled background task. It uses `xvfb-run` to create a virtual, headless operating environment, necessary for the secure data-scavenging agent to run correctly within a timed-deployment routine.