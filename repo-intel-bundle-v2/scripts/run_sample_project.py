import os
import sys
import json
import subprocess

def main():
    """
    Runs the pipeline with sample data (replacing 'make sample').
    """
    sample_file = os.path.join("examples", "repos_list.sample.json")
    
    # Create valid sample if missing
    if not os.path.exists(sample_file):
        mock_data = {
           "project_name": "sample_demo",
           "repos": ["https://github.com/octocat/Hello-World"]
        }
        os.makedirs("examples", exist_ok=True)
        with open(sample_file, "w") as f:
            json.dump(mock_data, f, indent=2)
            
    with open(sample_file, "r") as f:
        data = json.load(f)
        
    # Handle list vs dict
    if isinstance(data, list):
        # Fallback for list format
        project_name = "sample_project_from_list"
        repos = data
    else:
        project_name = data.get("project_name", "sample_project")
        repos = data.get("repos", [])
    
    if not repos:
        print("❌ No repos found in sample file.")
        sys.exit(1)
        
    print(f"🧪 Running Sample Project: {project_name}")
    
    cmd = [
        sys.executable, 
        "scripts/run_orchestrator.py",
        "--project", project_name,
        "--repos"
    ] + repos
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Sample run failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
