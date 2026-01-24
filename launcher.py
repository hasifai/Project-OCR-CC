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

def check_claude_cli():
    """Check if Claude CLI is installed and accessible"""
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=10,
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
        print("ERROR: main.py not found!")
        print(f"Expected location: {main_script}")
        print("\nMake sure main.py is in the same folder as this launcher.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Check Claude CLI
    print("Checking Claude CLI installation...")
    if not check_claude_cli():
        print("\n" + "=" * 50)
        print("  Claude CLI not found!")
        print("=" * 50)
        print("\nThis application requires Claude Code CLI to work.")
        print("\nInstallation steps:")
        print("1. Install Node.js from https://nodejs.org/")
        print("2. Run: npm install -g @anthropic-ai/claude-code")
        print("3. Run: claude (to login)")
        print("\nAfter installation, run this launcher again.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print("Claude CLI found! Starting OCR Translator...")
    print()

    # Run main.py with the current Python interpreter
    try:
        subprocess.run([sys.executable, main_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nApplication exited with error: {e}")
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\nApplication closed.")

if __name__ == "__main__":
    main()
