import time
import os
import concurrent.futures
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .scanner import scan_file
from .hasher import compute_hash
from .logger import load_logs, update_log

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        # Track recently processed files to prevent duplicate triggers
        self.processed_files = set()
        # Thread pool allows us to push heavy scanning to the background instantly
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def process_file_background(self, file_path: str, file_hash: str):
        """
        Background worker that performs the ML scan without blocking the event loop.
        """
        print(f"[INFO] Scanned in background: {os.path.basename(file_path)}")
        try:
            # 3. Scan the new file
            result = scan_file(file_path)
            
            # 4. Handle Result
            if "error" in result:
                print(f"[ERROR] Failed to scan {os.path.basename(file_path)}: {result['error']}")
                self.processed_files.discard(file_path)
                return
                
            # Log the result
            update_log(file_path, file_hash, result)
            
            # 5. Alert System
            confidence = result['score'] * 100
            if result['label'] == "malicious":
                print(f"[ALERT] Malware detected: {os.path.basename(file_path)} (Confidence: {confidence:.2f}%)")
            else:
                print(f"[INFO] Safe file: {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"[ERROR] Exception processing {file_path}: {e}")
            self.processed_files.discard(file_path)

    def queue_file(self, file_path: str):
        """
        Handles pre-processing logic (hashing & checking cache) before sending to worker.
        """
        if file_path in self.processed_files:
            return
            
        self.processed_files.add(file_path)
        
        # Add a short delay to ensure the file is fully downloaded/written to disk
        time.sleep(1.5)
        
        try:
            # 1. Compute Hash (Must be done before dispatching to worker)
            file_hash = compute_hash(file_path)
            
            # 2. Check Logs (Skip duplicates)
            logs = load_logs()
            if file_hash in logs:
                is_malicious = logs[file_hash].get("label") == "malicious"
                if is_malicious:
                    confidence = logs[file_hash].get("score", 0.0) * 100
                    print(f"\n[🚨 ALERT] CACHED MALWARE BLOCKED: {file_path} (Confidence: {confidence:.2f}%)")
                else:
                    print(f"[INFO] File already scanned (cached safe): {os.path.basename(file_path)}")
                return
                
            print(f"[INFO] File queued for background AI scan: {os.path.basename(file_path)}")
            
            # Dispatch to background worker pool
            self.executor.submit(self.process_file_background, file_path, file_hash)
            
        except Exception as e:
            print(f"[ERROR] Exception queueing {file_path}: {e}")
            self.processed_files.discard(file_path)

    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        supported_extensions = ('.exe', '.dll', '.sys', '.bat', '.ps1', '.vbs', '.js', '.txt', '.zip')
        if not file_path.lower().endswith(supported_extensions):
            return
            
        self.queue_file(file_path)

    def on_moved(self, event):
        if event.is_directory:
            return
            
        file_path = event.dest_path
        supported_extensions = ('.exe', '.dll', '.sys', '.bat', '.ps1', '.vbs', '.js', '.txt', '.zip')
        if not file_path.lower().endswith(supported_extensions):
            return
            
        self.queue_file(file_path)

def start_watcher(paths: list):
    observer = Observer()
    handler = FileHandler()
    
    valid_paths = []
    for path in paths:
        if os.path.exists(path):
            observer.schedule(handler, path, recursive=False)
            valid_paths.append(path)
            print(f"[INFO] Watching: {path}")
        else:
            print(f"[WARN] Path does not exist, skipping: {path}")
            
    if not valid_paths:
        print("[ERROR] No valid paths to watch. Exiting.")
        return

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping watcher...")
        handler.executor.shutdown(wait=False)
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Test script 
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    start_watcher([desktop_path])
