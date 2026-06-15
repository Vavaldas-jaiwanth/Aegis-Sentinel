import json
import os
import sys
from datetime import datetime

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Place the log file in the cache directory at the project root
LOG_FILE = os.path.join(get_base_dir(), "data", "cache", "scan_logs.json")

def load_logs() -> dict:
    """
    Loads existing logs from the JSON file.
    Returns an empty dict if the file does not exist.
    """
    if not os.path.exists(LOG_FILE):
        return {}
        
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If the file is corrupted or empty
        return {}

def save_logs(logs: dict) -> None:
    """
    Saves the log dictionary to the JSON file.
    """
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def update_log(file_path: str, file_hash: str, result: dict) -> None:
    """
    Updates the log dictionary with a new scan result and saves it.
    Uses the file hash as the unique key to prevent duplicates.
    """
    logs = load_logs()
    
    # Do not log errors so we can retry scanning them later if needed
    if "error" in result:
        return
        
    logs[file_hash] = {
        "file_path": file_path,
        "label": result.get("label"),
        "score": result.get("score"),
        "timestamp": datetime.now().isoformat()
    }
    
    save_logs(logs)
