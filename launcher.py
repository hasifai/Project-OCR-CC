"""
OCR Translator Launcher
Compiled to .exe - runs the external main.py script
"""

import subprocess
import sys
import os

def get_script_dir():
    """Get the directory where the exe/script is located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def show_error(title, message):
    """Show error message - uses messagebox for exe, print for console"""
    if getattr(sys, 'frozen', False):
        # Running as exe - use tkinter messagebox
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    else:
        # Running as script - print to console
        print(f"\n{title}")
        print("=" * 50)
        print(message)

def check_claude_cli():
    """Check if Claude CLI is installed and accessible"""
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=10,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return result.returncode == 0
    except Exception:
        return False

def main():
    script_dir = get_script_dir()
    main_script = os.path.join(script_dir, 'main.py')

    # Check if main.py exists
    if not os.path.exists(main_script):
        show_error(
            "File Not Found",
            f"main.py not found!\n\n"
            f"Expected location:\n{main_script}\n\n"
            f"Make sure main.py is in the same folder as this launcher."
        )
        sys.exit(1)

    # Check Claude CLI
    if not check_claude_cli():
        show_error(
            "Claude CLI Not Found",
            "This application requires Claude Code CLI to work.\n\n"
            "Installation steps:\n"
            "1. Install Node.js from https://nodejs.org/\n"
            "2. Run: npm install -g @anthropic-ai/claude-code\n"
            "3. Run: claude (to login)\n\n"
            "After installation, run this launcher again."
        )
        sys.exit(1)

    # Run main.py with the current Python interpreter
    try:
        subprocess.run([sys.executable, main_script], check=True)
    except subprocess.CalledProcessError as e:
        show_error("Application Error", f"Application exited with error:\n{e}")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
