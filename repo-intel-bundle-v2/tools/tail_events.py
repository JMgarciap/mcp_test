import argparse
import time
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def tail_file(path):
    with open(path, "r") as f:
        # Go to the end of the file
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield line

def main():
    parser = argparse.ArgumentParser(description="Tail event logs for a project.")
    parser.add_argument("--project", required=True, help="Project name to tail (folder in outputs/)")
    parser.add_argument("--log-dir", default="outputs", help="Directory where outputs are stored")
    args = parser.parse_args()

    events_path = os.path.join(args.log_dir, args.project, "events.jsonl")
    
    if not os.path.exists(events_path):
        logger.error(f"Event log not found at {events_path}")
        return

    print(f"Tailing events for {args.project}...")
    
    # First, read existing lines
    with open(events_path, "r") as f:
        for line in f:
            print_event(line)
            
    # Then tail
    for line in tail_file(events_path):
        print_event(line)

def print_event(line):
    try:
        data = json.loads(line)
        ts = data.get("ts", "").split("T")[1][:8] if "T" in data.get("ts", "") else data.get("ts")
        stage = data.get("stage", "UNKNOWN")
        status = data.get("status", "UNKNOWN")
        msg = data.get("message", "")
        repo = f" [{data['repo']}]" if data.get("repo") else ""
        
        icon = "⚪"
        if status == "STARTED": icon = "🔵"
        elif status == "COMPLETED": icon = "🟢"
        elif status == "FAILED": icon = "🔴"
        
        print(f"{ts} {icon} {stage:<15} {status:<10}{repo} : {msg}")
    except:
        pass

if __name__ == "__main__":
    main()
