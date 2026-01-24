"""
OCR Translator
Real-time OCR + Translation using Claude Code CLI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import mss
from PIL import Image
import keyboard
import threading
import os
import tempfile
from datetime import datetime

class OCRTranslator:
    """Main application controller"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.capture_count = 0
        self.is_translating = False
        self.overlay_visible = True
        self.translations = []
        self.auto_mode = False
        self.auto_interval = 5000  # 5 seconds in milliseconds
        self.current_model = 'haiku'  # Default to haiku for speed

        # Create main root window (Translation Window)
        self.root = tk.Tk()
        self.root.title("OCR Translator")
        self.root.geometry("600x750+950+100")
        self.root.configure(bg='#1a1a2e')
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # Create glass overlay as Toplevel
        self.create_glass_overlay()

        # Create translation UI
        self.create_translation_ui()

        # Setup hotkey
        keyboard.add_hotkey('F1', self.capture_and_translate)
        keyboard.add_hotkey('Escape', self.quit_app)

        print("OCR Translator initialized!")
        print("F1 - Capture and translate")
        print("Escape - Quit")

    def create_glass_overlay(self):
        """Create the transparent overlay window"""
        self.overlay = tk.Toplevel(self.root)
        self.overlay.title("Capture Region")
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.overrideredirect(True)
        self.overlay.geometry("800x200+100+500")

        # Create frame with visible border
        self.overlay_frame = tk.Frame(
            self.overlay,
            bg='purple',
            highlightbackground='purple',
            highlightthickness=3
        )
        self.overlay_frame.pack(fill=tk.BOTH, expand=True)

        # Inner transparent area
        self.overlay_inner = tk.Frame(self.overlay_frame, bg='white')
        self.overlay_inner.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

        # Label
        self.overlay_label = tk.Label(
            self.overlay_inner,
            text="Position over text area\nDrag edges to resize | Drag center to move",
            bg='white',
            fg='purple',
            font=('Segoe UI', 10)
        )
        self.overlay_label.pack(expand=True)

        # Bind mouse events for dragging
        self.overlay_inner.bind('<Button-1>', self.start_move)
        self.overlay_inner.bind('<B1-Motion>', self.do_move)
        self.overlay_label.bind('<Button-1>', self.start_move)
        self.overlay_label.bind('<B1-Motion>', self.do_move)

        # Resize handles
        self.overlay_frame.bind('<Button-1>', self.start_resize)
        self.overlay_frame.bind('<B1-Motion>', self.do_resize)

        # Track position
        self._drag_data = {"x": 0, "y": 0}
        self._resize_data = {"x": 0, "y": 0, "width": 0, "height": 0}

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_move(self, event):
        x = self.overlay.winfo_x() + (event.x - self._drag_data["x"])
        y = self.overlay.winfo_y() + (event.y - self._drag_data["y"])
        self.overlay.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._resize_data["x"] = event.x_root
        self._resize_data["y"] = event.y_root
        self._resize_data["width"] = self.overlay.winfo_width()
        self._resize_data["height"] = self.overlay.winfo_height()

    def do_resize(self, event):
        delta_x = event.x_root - self._resize_data["x"]
        delta_y = event.y_root - self._resize_data["y"]
        new_width = max(200, self._resize_data["width"] + delta_x)
        new_height = max(100, self._resize_data["height"] + delta_y)
        self.overlay.geometry(f"{new_width}x{new_height}")

    def get_region(self):
        """Get the current capture region coordinates"""
        return {
            'left': self.overlay.winfo_x(),
            'top': self.overlay.winfo_y(),
            'width': self.overlay.winfo_width(),
            'height': self.overlay.winfo_height()
        }

    def create_translation_ui(self):
        """Create the translation display UI"""
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 10))

        # Header
        header = tk.Frame(self.root, bg='#16213e')
        header.pack(fill=tk.X, padx=10, pady=(10, 5))

        title_label = tk.Label(
            header,
            text="OCR Translator",
            font=('Segoe UI', 16, 'bold'),
            fg='#e94560',
            bg='#16213e'
        )
        title_label.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(
            header,
            text="Press F1 to capture",
            font=('Segoe UI', 10),
            fg='#a0a0a0',
            bg='#16213e'
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Control buttons bar
        control_bar = tk.Frame(self.root, bg='#1a1a2e')
        control_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.auto_btn = tk.Button(
            control_bar,
            text="Auto: OFF",
            command=self.toggle_auto,
            bg='#0f3460',
            fg='white',
            relief=tk.FLAT,
            font=('Segoe UI', 10)
        )
        self.auto_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            control_bar,
            text="Clear History",
            command=self.clear_history,
            bg='#e94560',
            fg='white',
            relief=tk.FLAT,
            font=('Segoe UI', 10)
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        toggle_btn = tk.Button(
            control_bar,
            text="Toggle Overlay",
            command=self.toggle_overlay,
            bg='#533483',
            fg='white',
            relief=tk.FLAT,
            font=('Segoe UI', 10)
        )
        toggle_btn.pack(side=tk.LEFT, padx=5)

        # Model toggle button
        self.model_btn = tk.Button(
            control_bar,
            text="Haiku",
            command=self.toggle_model,
            bg='#00ff88',
            fg='black',
            relief=tk.FLAT,
            font=('Segoe UI', 10)
        )
        self.model_btn.pack(side=tk.LEFT, padx=5)

        # Interval control frame
        interval_frame = tk.Frame(control_bar, bg='#1a1a2e')
        interval_frame.pack(side=tk.RIGHT, padx=5)

        interval_label = tk.Label(
            interval_frame,
            text="Interval:",
            font=('Segoe UI', 9),
            fg='#a0a0a0',
            bg='#1a1a2e'
        )
        interval_label.pack(side=tk.LEFT)

        self.interval_var = tk.IntVar(value=5)
        self.interval_slider = tk.Scale(
            interval_frame,
            from_=1,
            to=30,
            orient=tk.HORIZONTAL,
            variable=self.interval_var,
            command=self.update_interval,
            bg='#1a1a2e',
            fg='white',
            highlightthickness=0,
            troughcolor='#0f3460',
            length=100
        )
        self.interval_slider.pack(side=tk.LEFT)

        self.interval_display = tk.Label(
            interval_frame,
            text="5s",
            font=('Segoe UI', 9),
            fg='#00ff88',
            bg='#1a1a2e'
        )
        self.interval_display.pack(side=tk.LEFT, padx=(5, 0))

        # Current translation display
        current_frame = tk.LabelFrame(
            self.root,
            text="Current Translation",
            font=('Segoe UI', 10, 'bold'),
            fg='#e94560',
            bg='#1a1a2e'
        )
        current_frame.pack(fill=tk.X, padx=10, pady=5)

        # Original text
        orig_label = tk.Label(
            current_frame,
            text="Original:",
            font=('Segoe UI', 9, 'bold'),
            fg='#a0a0a0',
            bg='#1a1a2e'
        )
        orig_label.pack(anchor=tk.W, padx=10, pady=(5, 0))

        self.jp_text = tk.Text(
            current_frame,
            height=6,
            font=('MS Gothic', 11),
            bg='#0f3460',
            fg='white',
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.jp_text.pack(fill=tk.X, padx=10, pady=5)

        # Translation
        trans_label = tk.Label(
            current_frame,
            text="Translation:",
            font=('Segoe UI', 9, 'bold'),
            fg='#a0a0a0',
            bg='#1a1a2e'
        )
        trans_label.pack(anchor=tk.W, padx=10, pady=(5, 0))

        self.en_text = tk.Text(
            current_frame,
            height=6,
            font=('Segoe UI', 11),
            bg='#0f3460',
            fg='#00ff88',
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.en_text.pack(fill=tk.X, padx=10, pady=5)

        # History
        history_frame = tk.LabelFrame(
            self.root,
            text="Translation History",
            font=('Segoe UI', 10, 'bold'),
            fg='#e94560',
            bg='#1a1a2e'
        )
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            font=('Segoe UI', 9),
            bg='#16213e',
            fg='white',
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def update_translation(self, japanese, english):
        """Update the current translation display"""
        # Clear previous
        self.jp_text.delete('1.0', tk.END)
        self.en_text.delete('1.0', tk.END)

        # Insert new
        self.jp_text.insert('1.0', japanese)
        self.en_text.insert('1.0', english)

        # Add to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        history_entry = f"[{timestamp}]\nOriginal: {japanese}\nTranslation: {english}\n{'─' * 50}\n\n"
        self.history_text.insert('1.0', history_entry)

        # Store in list
        self.translations.append({
            'time': timestamp,
            'japanese': japanese,
            'english': english
        })

    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)

    def clear_history(self):
        """Clear translation history"""
        self.history_text.delete('1.0', tk.END)
        self.translations = []

    def toggle_overlay(self):
        """Show/hide the glass overlay"""
        if self.overlay_visible:
            self.overlay.withdraw()
            self.overlay_visible = False
        else:
            self.overlay.deiconify()
            self.overlay_visible = True

    def toggle_auto(self):
        """Toggle auto-translate mode"""
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.auto_btn.config(text="Auto: ON", bg='#00ff88', fg='black')
            interval_sec = self.auto_interval // 1000
            self.update_status(f"Auto mode ON - capturing every {interval_sec}s")
            self.auto_translate_loop()
        else:
            self.auto_btn.config(text="Auto: OFF", bg='#0f3460', fg='white')
            self.update_status("Auto mode OFF - Press F1 to capture")

    def toggle_model(self):
        """Toggle between Haiku and Sonnet models"""
        if self.current_model == 'haiku':
            self.current_model = 'sonnet'
            self.model_btn.config(text="Sonnet", bg='#e94560', fg='white')
            self.update_status("Model: Sonnet (higher quality)")
        else:
            self.current_model = 'haiku'
            self.model_btn.config(text="Haiku", bg='#00ff88', fg='black')
            self.update_status("Model: Haiku (faster)")

    def update_interval(self, value):
        """Update auto-capture interval"""
        seconds = int(value)
        self.auto_interval = seconds * 1000
        self.interval_display.config(text=f"{seconds}s")
        if self.auto_mode:
            self.update_status(f"Auto mode ON - capturing every {seconds}s")

    def auto_translate_loop(self):
        """Auto-translate loop that runs every 5 seconds"""
        if self.auto_mode and not self.is_translating:
            self.capture_and_translate()

        if self.auto_mode:
            self.root.after(self.auto_interval, self.auto_translate_loop)

    def quit_app(self):
        """Quit the application"""
        keyboard.unhook_all()
        self.root.destroy()
        os._exit(0)

    def capture_screen(self):
        """Capture the region under the glass overlay"""
        region = self.get_region()

        print(f"Capturing region: {region}")

        with mss.mss() as sct:
            # Capture the region
            monitor = {
                "left": region['left'],
                "top": region['top'],
                "width": region['width'],
                "height": region['height']
            }
            screenshot = sct.grab(monitor)

            # Save to temp file
            self.capture_count += 1
            image_path = os.path.join(self.temp_dir, f"capture_{self.capture_count}.jpg")

            # Convert to PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')

            # Optimize: resize if too large (max 1200px width for faster processing)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Save as JPEG with quality optimization (smaller file = faster upload)
            img.save(image_path, 'JPEG', quality=85, optimize=True)

            print(f"Image saved to: {image_path}")
            print(f"Image size: {img.size}")

            return image_path

    def translate_with_claude(self, image_path):
        """Send image to Claude Code CLI for translation"""
        # Use absolute path and ask Claude to read the image file
        abs_path = os.path.abspath(image_path)

        prompt = f"""Read {abs_path}

OCR the Japanese/Chinese text and translate to English. Keep the emotion.

JAPANESE:
[text]

ENGLISH:
[translation]"""

        try:
            cmd = [
                'claude',
                '-p', prompt,
                '--model', self.current_model,
                '--allowedTools', 'Read'
            ]

            print(f"Running command with image: {abs_path}")

            # Hide console window on Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            output = result.stdout or result.stderr or "No response from Claude"
            print(f"Response: {output[:300]}...")

            return output

        except subprocess.TimeoutExpired:
            return "Translation timeout - please try again"
        except Exception as e:
            return f"Error: {str(e)}"

    def parse_translation(self, response):
        """Parse Claude's response into Japanese and English parts"""
        japanese = ""
        english = ""

        lines = response.split('\n')
        current_section = None

        for line in lines:
            line_stripped = line.strip()

            if 'JAPANESE:' in line_stripped.upper():
                current_section = 'jp'
                continue
            elif 'ENGLISH:' in line_stripped.upper():
                current_section = 'en'
                continue

            if current_section == 'jp' and line_stripped:
                japanese += line_stripped + '\n'
            elif current_section == 'en' and line_stripped:
                english += line_stripped + '\n'

        return japanese.strip(), english.strip()

    def capture_and_translate(self):
        """Main capture and translate workflow"""
        if self.is_translating:
            return

        self.is_translating = True
        self.update_status("Capturing...")

        def do_translation():
            try:
                # Capture screen
                image_path = self.capture_screen()
                self.root.after(0, lambda: self.update_status("Translating..."))

                # Get translation from Claude
                response = self.translate_with_claude(image_path)

                # Parse response
                japanese, english = self.parse_translation(response)

                if japanese or english:
                    self.root.after(
                        0,
                        lambda: self.update_translation(
                            japanese or "Could not read text",
                            english or response
                        )
                    )
                else:
                    # If parsing failed, show raw response
                    self.root.after(
                        0,
                        lambda: self.update_translation(
                            "See translation below",
                            response
                        )
                    )

                self.root.after(
                    0,
                    lambda: self.update_status("Press F1 to capture")
                )

            except Exception as e:
                self.root.after(
                    0,
                    lambda: self.update_status(f"Error: {str(e)}")
                )
            finally:
                self.is_translating = False

        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=do_translation)
        thread.daemon = True
        thread.start()

    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 50)
    print("  OCR Translator")
    print("  Powered by Claude Code CLI")
    print("=" * 50)
    print()

    app = OCRTranslator()
    app.run()
