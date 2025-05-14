# This script installs the required Python dependencies, starts the Flask website and writescript, and opens the website in a browser.
import os
import subprocess
import sys
import webbrowser
import time

def get_base_path():
    # If running as a PyInstaller executable, use the temporary _MEIPASS directory
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Otherwise, use the script's directory
    return os.path.dirname(os.path.abspath(__file__))

def install_dependencies():
    # Use the correct path for requirements.txt
    base_path = get_base_path()
    requirements_path = os.path.join(get_base_path(), "requirements.txt")
    print(f"Installing Python dependencies from: {requirements_path}")
    subprocess.run(["pip", "install", "-r", requirements_path], check=True)

def start_website():
    print("Starting the Flask website...")
    return subprocess.Popen(["python", os.path.join(get_base_path(), "website", "app.py")])

def start_writescript():
    print("Starting the writescript...")
    return subprocess.Popen(["python", os.path.join(get_base_path(), "website", "writescript.py")])

def open_browser():
    # Wait a few seconds to ensure the Flask server is running
    time.sleep(3)
    print("Opening the website in the default web browser...")
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    install_dependencies()
    website_process = start_website()
    writescript_process = start_writescript()
    open_browser()

    print("Press Ctrl+C to stop the application.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        website_process.terminate()
        writescript_process.terminate()
        print("Processes terminated. Goodbye!")

