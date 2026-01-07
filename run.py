"""Entry point for MiC Dynamic Scheduler"""

import subprocess
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))

app_path = os.path.join(current_dir, "web", "app.py")

def run_app():
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        app_path, "--server.port", "8501"
    ])

if __name__ == "__main__":
    print("Starting MiC Dynamic Scheduler...")
    print("Access the app at http://localhost:8501")
    run_app()