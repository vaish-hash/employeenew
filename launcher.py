import subprocess
import threading
import time
import os
import sys
import platform # To detect OS for subprocess flags

# --- Configuration ---
FLASK_PORT = 5000
APP_URL = f"http://127.0.0.1:{FLASK_PORT}/"
FLASK_APP_FILE = "app.py"

# --- Use sys.executable to refer to the current Python interpreter (the bundled .exe) ---
PYTHON_EXECUTABLE = sys.executable

# Determine the base directory of the executable (this will be the 'dist' folder when bundled)
BASE_DIR = os.path.dirname(sys.executable)

# Define a log file for Flask's output, ensuring it's in the same directory as the .exe
FLASK_LOG_FILE_NAME = "flask_output.log"
FLASK_LOG_FILE_PATH = os.path.join(BASE_DIR, FLASK_LOG_FILE_NAME)

# --- Function to start the Flask server ---
def start_flask_server():
    print(f"DEBUG: Entering start_flask_server function.", file=sys.stderr, flush=True)
    print(f"DEBUG: Current working directory: {os.getcwd()}", file=sys.stderr, flush=True)
    print(f"DEBUG: Base directory (sys.executable dirname): {BASE_DIR}", file=sys.stderr, flush=True)

    env = os.environ.copy()
    
    # When bundled, sys._MEIPASS points to the temporary extraction directory
    if hasattr(sys, '_MEIPASS'):
        app_path_in_bundle = os.path.join(sys._MEIPASS, FLASK_APP_FILE)
        env['FLASK_APP'] = app_path_in_bundle
        print(f"DEBUG: Running from PyInstaller bundle. FLASK_APP set to: {env['FLASK_APP']}", file=sys.stderr, flush=True)
    else:
        # For direct execution (e.g., `python launcher.py`), use relative path
        env['FLASK_APP'] = FLASK_APP_FILE
        print(f"DEBUG: Running directly. FLASK_APP set to: {env['FLASK_APP']}", file=sys.stderr, flush=True)
    
    env['FLASK_DEBUG'] = '0' # Ensure debug mode is off for the bundled app

    cmd = [
        PYTHON_EXECUTABLE, # This should point to the bundled Python interpreter
        '-m', 'flask', 'run',
        '--no-debugger',
        '--no-reload',
        f'--port={FLASK_PORT}'
    ]

    print(f"DEBUG: Attempting to start Flask server with command: {' '.join(cmd)}", file=sys.stderr, flush=True)
    print(f"DEBUG: Flask output will be redirected to: {FLASK_LOG_FILE_PATH}", file=sys.stderr, flush=True)

    process = None
    log_file = None
    try:
        # Ensure the directory for the log file exists
        os.makedirs(os.path.dirname(FLASK_LOG_FILE_PATH), exist_ok=True)
        print(f"DEBUG: Ensured log directory exists: {os.path.dirname(FLASK_LOG_FILE_PATH)}", file=sys.stderr, flush=True)

        # Open the log file in write mode, with line buffering for immediate writes
        log_file = open(FLASK_LOG_FILE_PATH, 'w', buffering=1, encoding='utf-8')
        print(f"DEBUG: Successfully opened log file for Flask output.", file=sys.stderr, flush=True)

        # Start the Flask subprocess
        creationflags = 0
        if platform.system() == "Windows":
            # Use DETACHED_PROCESS to ensure the Flask server runs independently
            # and doesn't terminate if the main launcher.exe console is closed.
            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

        process = subprocess.Popen(
            cmd, 
            env=env, 
            stdout=log_file, 
            stderr=log_file, 
            text=True, 
            encoding='utf-8',
            creationflags=creationflags,
            close_fds=True # Close file descriptors in child process
        )
        print(f"DEBUG: Flask subprocess started with PID: {process.pid}", file=sys.stderr, flush=True)

        # Give Flask a moment to start up
        time.sleep(10) 

        # Check if Flask process is still running
        poll_result = process.poll()
        if poll_result is not None:
            print(f"ERROR: Flask server exited prematurely with return code {poll_result}.", file=sys.stderr, flush=True)
            print(f"ERROR: Check '{FLASK_LOG_FILE_PATH}' for Flask's detailed error output.", file=sys.stderr, flush=True)
            show_error_message("Application Startup Error",
                               f"The application server failed to start.\n\nCheck '{FLASK_LOG_FILE_PATH}' for details.")
            sys.exit(1)
        else:
            print(f"INFO: Flask server is running on {APP_URL}", file=sys.stderr, flush=True)
            print(f"INFO: Please open your web browser and navigate to: {APP_URL}", file=sys.stderr, flush=True)
            # Keep the Flask server running indefinitely as a daemon thread
            # The main thread will join this thread, keeping the console open.
            process.wait() # This will block until the Flask process terminates
            print("DEBUG: Flask server process terminated.", file=sys.stderr, flush=True)

    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: File not found when trying to launch Flask or open log: {e}", file=sys.stderr, flush=True)
        show_error_message("Critical Error", f"Required file not found: {e}\n\nCannot start application.")
        sys.exit(1)
    except PermissionError as e:
        print(f"CRITICAL ERROR: Permission denied when trying to open log file or launch Flask: {e}", file=sys.stderr, flush=True)
        show_error_message("Permission Error", f"Cannot create log file or launch server due to permissions: {e}\n\nTry running as administrator or move to a different folder.")
        sys.exit(1)
    except Exception as e:
        print(f"CRITICAL ERROR: An unexpected error occurred in start_flask_server: {e}", file=sys.stderr, flush=True)
        show_error_message("Unexpected Error", f"An unexpected error occurred during server startup: {e}\n\nCheck console for more details.")
        sys.exit(1)
    finally:
        if log_file:
            log_file.close()
            print(f"DEBUG: Closed Flask log file.", file=sys.stderr, flush=True)


# --- Function to show a simple message box (for errors) ---
def show_error_message(title, message):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw() # Hide the main window
        messagebox.showerror(title, message)
        root.destroy()
    except ImportError:
        print(f"ERROR: {title} - {message}", file=sys.stderr, flush=True)
        print("tkinter not available, showing error in console.", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"ERROR: Could not show message box: {e}", file=sys.stderr, flush=True)
        print(f"Original Error: {title} - {message}", file=sys.stderr, flush=True)


# --- Main execution logic ---
if __name__ == "__main__":
    print("DEBUG: Main execution started.", file=sys.stderr, flush=True)
    
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.daemon = True # Daemon threads exit when the main program exits
    flask_thread.start()

    # The main thread will now simply wait for the Flask thread to finish.
    # The Flask thread will only finish if the Flask server itself stops.
    print("DEBUG: Main thread waiting for Flask server thread to finish.", file=sys.stderr, flush=True)
    flask_thread.join()
    print("DEBUG: Main execution finished.", file=sys.stderr, flush=True)
