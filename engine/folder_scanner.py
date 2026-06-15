import os
import concurrent.futures
from engine.utils.hasher import compute_hash
from engine.utils.logger import load_logs, update_log
from engine.scanner import scan_file

def scan_wrapper(file_path):
    """
    Worker function executed in parallel to process a single file.
    """
    try:
        # 1. Compute Hash
        file_hash = compute_hash(file_path)
        
        # 2. Check logs 
        logs = load_logs()
        if file_hash in logs:
            is_malicious = logs[file_hash].get("label") == "malicious"
            return {"file_path": file_path, "status": "skipped", "malicious": is_malicious}
            
        # 3. Call scan_file()
        print(f"Scanning: {file_path}")
        result = scan_file(file_path)
        
        # 4. Store Result
        if "error" not in result:
            update_log(file_path, file_hash, result)
            is_malicious = result.get("label") == "malicious"
            return {"file_path": file_path, "status": "scanned", "malicious": is_malicious}
        else:
            return {"file_path": file_path, "status": "error", "error": result["error"]}
            
    except Exception as e:
        return {"file_path": file_path, "status": "error", "error": str(e)}

def scan_folder(folder_path: str) -> None:
    """
    Recursively scans a folder using multiprocessing for performance scaling.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory '{folder_path}' does not exist.")
        return

    print(f"Starting parallel scan on folder: {folder_path}...\n")
    
    # Collect all executable file paths
    file_paths = []
    for root, _, files in os.walk(folder_path):
        supported_extensions = ['.exe', '.dll', '.sys', '.zip']
        for file in files:
            _, ext = os.path.splitext(file.lower())
            if ext in supported_extensions:
                file_paths.append(os.path.join(root, file))

    total_files = len(file_paths)
    if total_files == 0:
        print("No executables found to scan.")
        return

    scanned_count = 0
    skipped_count = 0
    malicious_files_list = []
    error_count = 0

    # Dynamically limit workers based on system CPU cores to avoid thrashing
    max_workers = min(os.cpu_count() or 4, 8)
    
    # Process files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(scan_wrapper, file_paths)
        
        for res in results:
            if res["status"] == "skipped":
                skipped_count += 1
                if res.get("malicious"):
                    malicious_files_list.append(res['file_path'])
            elif res["status"] == "scanned":
                scanned_count += 1
                if res.get("malicious"):
                    malicious_files_list.append(res['file_path'])
            elif res["status"] == "error":
                error_count += 1
                print(f"Failed to scan {os.path.basename(res['file_path'])}: {res['error']}")

    # Print Summary
    print("\n" + "="*40)
    print("SCAN COMPLETE")
    print("="*40)
    print(f"Total executables/scripts found: {total_files}")
    print(f"Scanned: {scanned_count} files (parallel)")
    print(f"Skipped (cached): {skipped_count} files")
    print(f"Malicious files found: {len(malicious_files_list)}")
    
    if len(malicious_files_list) > 0:
        print("\n[🚨] MALWARE DETECTED IN:")
        for idx, mal_file in enumerate(malicious_files_list, 1):
            print(f"  {idx}. {mal_file}")
            
    if error_count > 0:
        print(f"\nErrors: {error_count} files failed to scan")
    print("="*40)

if __name__ == "__main__":
    # Test script - point it to the parent directory to test
    test_folder = os.path.abspath("..")
    scan_folder(test_folder)
