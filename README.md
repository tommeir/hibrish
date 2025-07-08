# hibrish

A smart keyboard layout switcher and auto-corrector for Windows, supporting English and Hebrew.

## Features
- **Automatic Keyboard Layout Switching:** Seamlessly switch between English and Hebrew layouts based on your typing.
- **Auto-Correction:** Instantly corrects common typing mistakes and misspelled words.
- **System Tray Integration:** Runs in the background with a convenient tray icon for quick access and quitting.
- **Usage Statistics:** Tracks the number of auto-corrections and estimates time saved.
- **Details Popup:** View your usage stats and a clickable LinkedIn link for the author.

## Installation
1. **Download the latest release** from [GitHub Releases](https://github.com/tommeir/hibrish/releases) (or build from source).
2. **Run the installer** or the standalone executable.
3. The app will appear in your system tray and start working automatically.

## Building from Source
1. Clone this repository:
   ```sh
   git clone https://github.com/tommeir/hibrish.git
   cd hibrish
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the app:
   ```sh
   python main.py
   ```

## Packaging as an Executable
- Use [PyInstaller](https://pyinstaller.org/) to create a standalone Windows executable:
  ```sh
  pyinstaller --onefile --add-data "dictionaries;dictionaries" main.py
  ```
- See the `dist/` folder for the output.

## Usage
- The app runs in the background and auto-corrects as you type.
- Right-click the tray icon for options and to view details.

## Contributing
Pull requests and suggestions are welcome! Please open an issue or contact the author.

## Author
[Tom Meir](https://www.linkedin.com/in/tommeir/)

---
*This project is open source and provided as-is. Enjoy smarter typing!* 