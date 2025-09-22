"""
Elite Dangerous LogTail - Standalone Script
Monitors Odyssey journal files and logs events and their counts.
Also includes a special search for the term "RAXXLA".

Requirements:
- pip install watchdog
"""

import os
import json
import time
import threading
from collections import defaultdict
from pathlib import Path
import logging
import subprocess

# File monitoring
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
CONFIG = {
    "journal_folder": Path.home()
    / "Saved Games"
    / "Frontier Developments"
    / "Elite Dangerous",
    # Path to the file for persistent event counts
    "save_file": Path(os.getenv('APPDATA')) / "EDLogTail" / "event_counts.json"
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("elite_log_tail.log")],
)
logger = logging.getLogger(__name__)

class LogTail:
    """
    Class to monitor Elite Dangerous journal files for events and log counts.
    """
    def __init__(self):
        self.event_counts = defaultdict(int)
        self.load_counts()
        self.raxxla_found = threading.Event()

        print("=" * 60)
        print("Elite Dangerous LogTail - Standalone")
        print("=" * 60)
        print(f"Monitoring journal folder: {CONFIG['journal_folder']}")
        print(f"Persistent counts saved to: {CONFIG['save_file']}")
        print("Waiting for new events...")
        print("-" * 60)

    def load_counts(self):
        """Loads event counts from the save file if it exists."""
        try:
            if CONFIG["save_file"].exists():
                with open(CONFIG["save_file"], "r", encoding="utf-8") as f:
                    saved_counts = json.load(f)
                    for event, count in saved_counts.items():
                        self.event_counts[event] = count
                logger.info("Loaded previous event counts from %s", CONFIG["save_file"])
            else:
                logger.info("No previous event counts found, starting from zero.")
        except Exception as e:
            logger.error("Error loading event counts: %s", e)

    def save_counts(self):
        """Saves the current event counts to the save file."""
        try:
            # Ensure the directory exists
            CONFIG["save_file"].parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG["save_file"], "w", encoding="utf-8") as f:
                # Convert defaultdict to dict for JSON serialization
                json.dump(dict(self.event_counts), f, indent=4)
            logger.info("Saved current event counts to %s", CONFIG["save_file"])
        except Exception as e:
            logger.error("Error saving event counts: %s", e)

    def process_journal_entry(self, entry: dict):
        """Process a journal entry and count its event type."""
        event_type = entry.get("event")
        if event_type:
            self.event_counts[event_type] += 1
            
        # Check for the term "RAXXLA" in the entire line
        line_str = json.dumps(entry)
        if "RAXXLA" in line_str.upper():
            logger.critical("RAXXLA DETECTED! Full event line: %s", line_str)
            print("\n\n" + "!"*60)
            print("!!! RAXXLA FOUND !!!")
            print("!!!" + line_str + "!!!")
            print("!"*60 + "\n")
            self.raxxla_found.set() # Set the event to stop the main loop
            

class JournalMonitor(FileSystemEventHandler):
    """
    A custom event handler for watchdog that processes new journal file entries.
    """
    def __init__(self, log_tail: LogTail):
        self.log_tail = log_tail
        self.current_file = None
        self.file_position = 0
        self.find_latest_journal()

    def find_latest_journal(self):
        """Find the most recent journal file and start monitoring it."""
        try:
            journal_files = list(CONFIG["journal_folder"].glob("Journal.*.log"))
            if journal_files:
                latest_journal = max(journal_files, key=lambda x: x.stat().st_mtime)
                self.current_file = latest_journal
                self.file_position = latest_journal.stat().st_size
                logger.info("Monitoring journal file: %s", latest_journal)
                print(f"📖 Monitoring: {latest_journal.name}")
            else:
                logger.warning("No journal files found")
                print("⚠️  No journal files found")
        except Exception as e:
            logger.error("Error finding journal files: %s", e)

    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory and Path(event.src_path).name.startswith("Journal."):
            self.read_new_lines(Path(event.src_path))

    def on_created(self, event):
        """Called when a new file is created."""
        if not event.is_directory and Path(event.src_path).name.startswith("Journal."):
            file_path = Path(event.src_path)
            print(f"\n📖 New journal file detected: {file_path.name}")
            self.current_file = file_path
            self.file_position = 0
            self.read_new_lines(file_path)

    def read_new_lines(self, file_path: Path):
        """Read and process new lines from the journal file."""
        try:
            if file_path != self.current_file:
                return

            with open(file_path, "r", encoding="utf-8") as f:
                f.seek(self.file_position)
                new_lines = f.readlines()
                self.file_position = f.tell()

            for line in new_lines:
                line = line.strip()
                if line:
                    try:
                        self.log_tail.process_journal_entry(json.loads(line))
                    except json.JSONDecodeError:
                        # This can happen with incomplete lines being written
                        pass
        except Exception as e:
            logger.error("Error reading journal file: %s", e)

def clear_screen_subprocess():
    if os.name == 'nt':
        subprocess.run('cls', shell=True)
    else:
        subprocess.run('clear', shell=True)

def main():
    """Main function of LogTail."""
    if not CONFIG["journal_folder"].exists():
        print(f"❌ Journal folder not found: {CONFIG['journal_folder']}")
        input("Press Enter to exit...")
        return

    log_tail = LogTail()
    event_handler = JournalMonitor(log_tail)
    observer = Observer()
    observer.schedule(event_handler, str(CONFIG["journal_folder"]), recursive=False)
    observer.start()

    try:
        print("\n✅ LogTail is running! Press Ctrl+C to stop.")
        while not log_tail.raxxla_found.is_set():
            time.sleep(2)
            clear_screen_subprocess()
            print("\r" + " "*80, end="") # Clear the line
            print("\rLive Event Counts:")
            for event, count in log_tail.event_counts.items():
                print(f" {event}: {count}")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping LogTail...")
    finally:
        observer.stop()
        observer.join()
        log_tail.save_counts()
        print("\n\nFinal Event Counts:")
        print("="*25)
        for event, count in sorted(log_tail.event_counts.items()):
            print(f"  {event}: {count}")
        print("="*25)
        print("👋 LogTail stopped. Goodbye!")


if __name__ == "__main__":
    main()
