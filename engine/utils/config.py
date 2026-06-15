import os
import sys
import json

def get_base_dir():
    """
    Returns the appropriate base directory depending on whether the script 
    is running normally or packaged as a PyInstaller executable.
    """
    if getattr(sys, 'frozen', False):
        # If compiled by PyInstaller, look in the directory containing the .exe
        return os.path.dirname(sys.executable)
    else:
        # If running from source, look in the project root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CONFIG_FILE = os.path.join(get_base_dir(), "settings.json")

DEFAULT_CONFIG = {
    "watch_paths": ["Downloads", "Desktop"],
    "auto_start": True,
    "scan_on_start": True,
    "max_workers": 4
}

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception:
            pass
        return DEFAULT_CONFIG
        
    try:
        with open(CONFIG_FILE, 'r') as f:
            user_config = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            merged.update(user_config)
            return merged
    except Exception as e:
        print(f"[WARN] Failed to read settings.json: {e}")
        return DEFAULT_CONFIG

def save_config(config: dict) -> bool:
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save settings.json: {e}")
        return False

def get_watch_paths() -> list:
    config = load_config()
    paths = config.get("watch_paths", [])
    
    resolved_paths = []
    for path in paths:
        if path.lower() == "downloads":
            resolved_paths.append(os.path.join(os.path.expanduser("~"), "Downloads"))
        elif path.lower() == "desktop":
            resolved_paths.append(os.path.join(os.path.expanduser("~"), "Desktop"))
        elif path.lower() == "documents":
            resolved_paths.append(os.path.join(os.path.expanduser("~"), "Documents"))
        else:
            resolved_paths.append(path)
            
    return resolved_paths

def get_worker_count() -> int:
    return load_config().get("max_workers", 4)
    
def should_scan_on_start() -> bool:
    return load_config().get("scan_on_start", True)
