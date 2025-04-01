import subprocess
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


class PythonHandler(FileSystemEventHandler):
    def __init__(self, python_process):
        self.python_process = python_process

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"\nPython file changed: {event.src_path}")
            self.restart_python()

    def restart_python(self):
        print("Restarting Python server...")
        self.python_process.terminate()
        self.python_process.wait()
        self.python_process = subprocess.Popen([sys.executable, "usage.py"])


def main():
    # Start the initial Python process
    python_process = subprocess.Popen([sys.executable, "usage.py"])

    # Set up the file system observer
    event_handler = PythonHandler(python_process)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()

    try:
        # Start nodemon for JavaScript watching
        print("Starting development environment...")
        print("Watching for changes in Python and JavaScript files...")
        print("Press Ctrl+C to stop")

        # Run nodemon in the dash_paperdragon directory
        nodemon_process = subprocess.Popen(
            ["npm", "run", "build:watch"], cwd="dash_paperdragon", shell=True
        )

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping development environment...")
        observer.stop()
        python_process.terminate()
        nodemon_process.terminate()
        observer.join()


if __name__ == "__main__":
    main()
