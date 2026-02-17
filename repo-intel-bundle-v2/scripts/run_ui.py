import os
import sys
import subprocess

def main():
    """
    Launches the Streamlit UI (replacing 'make ui').
    """
    # Ensure current directory is in PYTHONPATH
    cwd = os.getcwd()
    env = os.environ.copy()
    env["PYTHONPATH"] = cwd

    print("🚀 Starting AI DevOps Governance Console...")
    print(f"📂 Working Directory: {cwd}")
    
    app_path = os.path.join("ui", "streamlit_app.py")
    
    if not os.path.exists(app_path):
        print(f"❌ Error: Could not find {app_path}. Run this script from the project root.")
        sys.exit(1)

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], env=env, check=True)
    except KeyboardInterrupt:
        print("\n👋 UI Stopped.")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
