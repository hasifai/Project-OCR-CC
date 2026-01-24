# OCR Translator

Real-time screen OCR and translation tool powered by Claude Code CLI.

## Features

- **Glass Overlay**: Position a transparent capture region over any text
- **Hotkey Capture**: Press F1 to capture and translate instantly
- **Auto Mode**: Automatic capture at configurable intervals (1-30 seconds)
- **Model Selection**: Toggle between Haiku (fast) and Sonnet (quality)
- **Translation History**: Keep track of all translations in a session

## Requirements

1. **Claude Code CLI** - Required for translation
   - Install Node.js from https://nodejs.org/
   - Run: `npm install -g @anthropic-ai/claude-code`
   - Run: `claude` (to login with your account)

2. **Python 3.8+** (if running from source)

## Installation

### Option 1: Run from Source
```bash
pip install -r requirements.txt
python main.py
```

### Option 2: Use Pre-built Launcher
1. Download `OCR Translator.exe` and `main.py`
2. Place both files in the same folder
3. Run `OCR Translator.exe`

## Usage

1. **Position the overlay** - Drag the purple-bordered region over the text you want to translate
2. **Resize as needed** - Drag the edges to resize the capture area
3. **Press F1** - Capture and translate the text
4. **Or enable Auto mode** - Automatically capture at set intervals

### Hotkeys
- `F1` - Capture and translate
- `Escape` - Quit application

### Controls
- **Auto: ON/OFF** - Toggle automatic capture mode
- **Clear History** - Clear translation history
- **Toggle Overlay** - Show/hide the capture region
- **Haiku/Sonnet** - Switch between fast and quality models
- **Interval Slider** - Set auto-capture interval (1-30 seconds)

## Building the Launcher

To build the .exe launcher yourself:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "OCR Translator" launcher.py
```

Or simply run `build.bat` on Windows.

## Distribution

To share this tool, distribute these files together:
- `OCR Translator.exe` (from dist folder after build)
- `main.py`

Each user needs their own Claude Code CLI login - no API keys are shared or exposed.

## License

MIT License
