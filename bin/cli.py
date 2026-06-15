import argparse
import os
import sys

# Add root to sys.path so we can import engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.scanner import scan_file
from engine.folder_scanner import scan_folder
from engine.watcher import start_watcher

def main():
    parser = argparse.ArgumentParser(description="Next-Gen Malware Scanning Engine")
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ==========================================
    # SUBCOMMAND: scan (for files and folders)
    # ==========================================
    scan_parser = subparsers.add_parser("scan", help="Scan a single file or an entire directory")
    
    # Require either a file or a folder for scanning
    group = scan_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", "-f", type=str, help="Path to a single executable file to scan")
    group.add_argument("--folder", "-d", type=str, help="Path to a folder to scan recursively")
    
    # The phase 5 intelligence layer flag
    scan_parser.add_argument("--explain", "-e", action="store_true", help="Provide SHAP explanation for the prediction (Single file scan only)")
    
    # ==========================================
    # SUBCOMMAND: help
    # ==========================================
    subparsers.add_parser("help", help="Show the main help message and exit")
    
    # ==========================================
    # SUBCOMMAND: protect (Background Agent Mode)
    # ==========================================
    run_parser = subparsers.add_parser("protect", help="Start the background agent automatically using settings.json")
    run_parser.add_argument("--config", type=str, help="Path to a custom settings.json file")
    run_parser.add_argument("--no-watch", action="store_true", help="Disable the background real-time watcher")
    
    # ==========================================
    # SUBCOMMAND: config (Modify Settings)
    # ==========================================
    config_parser = subparsers.add_parser("config", help="Modify the settings.json configuration")
    config_parser.add_argument("--add-path", type=str, help="Add a directory path to the real-time watcher")
    config_parser.add_argument("--remove-path", type=str, help="Remove a directory path from the real-time watcher")
    config_parser.add_argument("--view", action="store_true", help="Print the current configuration")
    
    # Check if no arguments were provided
    if len(sys.argv) == 1:
        # If user double-clicks the executable, default to the background agent
        sys.argv.append("protect")
        
    args = parser.parse_args()

    # ==========================
    # ROUTE: Scan
    # ==========================
    if args.command == "scan":
        if args.file:
            if not os.path.isfile(args.file):
                print(f"Error: File '{args.file}' does not exist.")
                sys.exit(1)
                
            # Delegate to the decoupled scanner module
            result = scan_file(args.file, explain=args.explain)
            
            print("-" * 40)
            print(f"File: {os.path.basename(args.file)}")
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                label_display = result["label"].capitalize()
                confidence_pct = result["score"] * 100
                
                print(f"Result: {label_display}")
                print(f"Confidence: {confidence_pct:.2f}%")
                
                # Print explanation if requested
                if "explanation" in result:
                    print("\n[AI Explanation] Driving Features:")
                    for item in result["explanation"]:
                        direction = "Pushed towards Malware" if item['impact'] > 0 else "Pushed towards Safe"
                        print(f"  -> {item['feature']:<25} | Impact: {item['impact']:>6}  ({direction})")
                elif "explanation_error" in result:
                    print(f"\n[Explanation Error] {result['explanation_error']}")
                    
            print("-" * 40)

        elif args.folder:
            if not os.path.isdir(args.folder):
                print(f"Error: Directory '{args.folder}' does not exist.")
                sys.exit(1)
                
            if args.explain:
                print("Warning: The --explain flag is only supported for single file scans. Proceeding with bulk scan without explanations.\n")
                
            # Delegate to the folder scanning module
            scan_folder(args.folder)

    # ==========================
    # ROUTE: Help
    # ==========================
    elif args.command == "help":
        parser.print_help()
        sys.exit(0)
        
    # ==========================
    # ROUTE: Protect (Agent Mode)
    # ==========================
    elif args.command == "protect":
        from engine.utils.config import load_config, get_watch_paths, should_scan_on_start
        import engine.utils.config as config
        
        if args.config:
            config.CONFIG_FILE = args.config
            
        settings = load_config()
        print("\n" + "="*45)
        print("🛡️  MALWARE DEFENDER - BACKGROUND AGENT 🛡️")
        print("="*45)
        
        watch_paths = get_watch_paths()
        
        if should_scan_on_start():
            print("\n[INFO] Executing initial sweep on configured paths...")
            for path in watch_paths:
                if os.path.exists(path):
                    scan_folder(path)
                    
        if not args.no_watch:
            print("\n[INFO] Transitioning to background monitoring mode...")
            print("[INFO] Press Ctrl+C at any time to gracefully exit.")
            start_watcher(watch_paths)
        else:
            print("\n[INFO] Background watcher disabled via flag. Exiting.")
            sys.exit(0)

    # ==========================
    # ROUTE: Config (Modify Settings)
    # ==========================
    elif args.command == "config":
        from engine.utils.config import load_config, save_config
        import json
        
        config = load_config()
        changed = False
        
        if args.add_path:
            if args.add_path not in config.get("watch_paths", []):
                config.setdefault("watch_paths", []).append(args.add_path)
                changed = True
                print(f"[INFO] Added '{args.add_path}' to watch_paths.")
            else:
                print(f"[INFO] '{args.add_path}' is already in watch_paths.")
                
        if args.remove_path:
            if args.remove_path in config.get("watch_paths", []):
                config["watch_paths"].remove(args.remove_path)
                changed = True
                print(f"[INFO] Removed '{args.remove_path}' from watch_paths.")
            else:
                print(f"[WARN] '{args.remove_path}' not found in watch_paths.")
                
        if changed:
            if save_config(config):
                print("[SUCCESS] Settings successfully updated.")
            else:
                print("[ERROR] Failed to update settings.")
                
        if args.view or not (args.add_path or args.remove_path):
            print("\n[CURRENT CONFIGURATION]")
            print(json.dumps(config, indent=4))

if __name__ == "__main__":
    import multiprocessing
    # Required for PyInstaller to handle ProcessPoolExecutor correctly on Windows
    multiprocessing.freeze_support()
    main()
