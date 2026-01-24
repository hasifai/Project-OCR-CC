# OCR Translator

Real-time screen OCR and translation tool powered by Claude Code CLI.

## Features

- **Glass Overlay**: Position a transparent capture region over any text
- **Hotkey Capture**: Press F1 to capture and translate instantly
- **Auto Mode**: Automatic capture at configurable intervals (1-30 seconds)
- **Model Selection**: Toggle between Haiku (fast) and Sonnet (quality)
- **Translation History**: Keep track of all translations in a session

## Requirements

**Claude Code CLI** - Required for translation
1. Install Node.js from https://nodejs.org/
2. Run: `npm install -g @anthropic-ai/claude-code`
3. Run: `claude` (to login with your account)

## Installation

### Option 1: Download Pre-built
1. Download `OCR Translator.exe`
2. Run it!

### Option 2: Run from Source
```bash
pip install -r requirements.txt
python main.py
```

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

## Building from Source

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "OCR Translator" main.py
```

Or run `build.bat` on Windows.

Output: `dist/OCR Translator.exe`

## Note

Each user needs their own Claude Code CLI login - no API keys are shared or exposed.

## License

MIT License
