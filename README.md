# ⚡ BoD/BoG Auto Reroll

An automated Blessing of the Demon (BoD) and Blessing of the Goddess (BoG) reroll tool for Flyff Universe. This application automatically detects stats using OCR (Optical Character Recognition) and rerolls your item until target stats are achieved.

## ✨ Features

- 🎯 **Automatic Stat Detection** - Uses OCR to read stats from the blessing dialog
- 🔄 **Smart Rerolling** - Automatically clicks the reroll button until target stats are met
- 📊 **Dual Stat Support** - Configure one or two target stats with minimum values
- ➕ **Stat Summing** - When only one stat is configured, values from both panels are summed
- ✂️ **Visual Region Selection** - Snipping tool interface for easy dialog region selection
- 🎨 **Modern GUI** - Clean, intuitive interface built with CustomTkinter
- 🔍 **Real-time Logging** - Monitor OCR detection and automation status
- ⚙️ **Reconfigurable** - Change settings without restarting the application

## 📋 Requirements

- Windows OS
- Flyff Universe game client
- Python 3.8+ (for development)
- Tesseract OCR (included in release)

## 🚀 Usage (End Users)

### Quick Start

1. **Download the release**

   - Get the latest `bod-auto.exe` from the releases page
   - Extract to a folder (includes `tesseract` folder and `stats.txt`)

2. **Launch the application**

   - Run `bod-auto.exe`
   - The configuration window will appear

3. **Configure your settings**

   **STEP 1: Select Dialog Region**

   - Open Flyff Universe and display the BoD/BoG blessing dialog
   - Click "✂️ SELECT DIALOG REGION" button
   - The screen will overlay with a gray transparent layer
   - Click and drag to draw a rectangle around the entire blessing dialog
   - Include the title, stat panels, and buttons in your selection
   - Press ESC to cancel if needed

   **Alternative:** Manually enter coordinates in format `left,top,right,bottom` (e.g., `813,153,1339,494`)

   **STEP 2: Configure Target Stats**

   - **Stat 1 (Optional):** Select your primary stat and minimum value
   - **Stat 2 (Optional):** Select your secondary stat and minimum value
   - Configure at least one stat

   **Stat Behavior:**

   - If only ONE stat configured → Values from BOTH panels are SUMMED
   - If BOTH stats configured → Each checked INDIVIDUALLY
   - Stats can appear in either Stat 1 or Stat 2 panel of the dialog

4. **Start automation**

   - Click "🚀 START AUTOMATION"
   - The automation window opens with activity log
   - Click "▶️ START AUTOMATION" button to begin
   - The bot will continuously:
     - Search for the reroll button
     - Click it when found
     - Read stats using OCR
     - Check if targets are met
     - Stop and notify when targets achieved

5. **When targets are met**
   - Automation pauses
   - Console prompts: `Do you want to re-awake? (y/n):`
   - Type `y` to continue rerolling
   - Type `n` to stop automation

### Available Stats

Check `stats.txt` file for the complete list. Common stats include:

- **Attributes:** STR, DEX, INT, STA
- **Combat:** Attack, Defense, CriticalChance, CriticalDamage
- **Speed:** Speed, AttackSpeed, CastingSpeed
- **Resources:** HP, MP, FP
- **Advanced:** PvEDamage, Parry, MeleeBlock, RangedBlock

### Tips for Best Results

1. **Region Selection**

   - Ensure the entire dialog is captured including borders
   - Don't make the region too large (avoid background elements)
   - Keep the game window in the same position during automation

2. **OCR Accuracy**

   - Use clear, high-contrast game settings
   - Ensure the dialog is fully visible and not obscured
   - Avoid transparent or overlapping windows

3. **Stat Configuration**
   - Stat names must exactly match those in `stats.txt`
   - Values are based on game mechanics (see stat value ranges)
   - Single stat mode is useful for maximizing one attribute

## 🛠️ Development

### Prerequisites

1. **Python 3.8 or higher**

   ```bash
   python --version
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Or manually:

   ```bash
   pip install pyautogui pytesseract pillow opencv-python customtkinter numpy
   ```

3. **Install Tesseract OCR**
   - Download: [Tesseract OCR v5.5.0](https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)
   - Install to project folder: `./tesseract/`
   - Ensure structure: `./tesseract/tesseract.exe` exists
   - Required files:
     - `tesseract.exe`
     - `tessdata/eng.traineddata`
     - `tessdata/osd.traineddata`

### Running from Source

```bash
python bod-auto.py
```

### Project Structure

```
autobod/
├── bod-auto.py          # Main application
├── bod-auto.spec        # PyInstaller specification
├── build-app.bat        # Build script for Windows
├── requirements.txt     # Python dependencies
├── stats.txt           # Available stats list
├── button_image.png    # Reference button image
├── README.md           # This file
├── tesseract/          # Tesseract OCR installation
│   ├── tesseract.exe
│   └── tessdata/
│       ├── eng.traineddata
│       └── osd.traineddata
└── dist/               # Built executable (after build)
    └── bod-auto.exe
```

### Building Executable

1. **Install PyInstaller**

   ```bash
   pip install pyinstaller
   ```

2. **Run build script**

   ```bash
   build-app.bat
   ```

3. **Output location**
   - Executable: `./dist/bod-auto.exe`
   - Includes all dependencies

### Build Script Details

The `build-app.bat` / `bod-auto.spec` configuration:

- Bundles Python runtime
- Includes Tesseract OCR engine
- Packages `stats.txt` and `button_image.png`
- Creates single-file executable
- Console enabled for debug output

### Modifying Available Stats

Edit `stats.txt`:

```
STR
DEX
INT
CriticalChance
Attack
...
```

Rules:

- One stat name per line
- No spaces (use CriticalChance, not Critical Chance)
- Case-sensitive (must match in-game text)
- Update `stat_values` dict in `bod-auto.py` for dropdown values

### Understanding the Code

**Main Components:**

1. **ConfigUI Class** - Configuration window

   - Region selection (snipping tool)
   - Stat dropdown selectors
   - Target value configuration
   - Theme switcher

2. **StatusWindow Class** - Automation window

   - Real-time activity logging
   - Start/Stop controls
   - Reconfiguration option
   - Status indicators

3. **capture_and_check()** - OCR detection

   - Screenshots the selected region
   - Preprocesses image (grayscale, threshold, resize)
   - Runs Tesseract OCR
   - Parses stat values using regex
   - Compares against targets
   - Supports stat summing for single-stat mode

4. **click_image()** - Button detection
   - Uses template matching
   - Finds reroll button on screen
   - Triggers OCR check
   - Handles user prompts

**OCR Preprocessing Pipeline:**

```python
# 1. Capture region
screenshot = ImageGrab.grab(bbox=region)

# 2. Convert to grayscale
gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

# 3. Upscale 3x for better OCR
gray = cv2.resize(gray, fx=3, fy=3)

# 4. Binary threshold
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# 5. Noise reduction
thresh = cv2.medianBlur(thresh, 3)

# 6. Character enhancement
thresh = cv2.erode(thresh, kernel)
```

### Customization

**Adjust OCR Settings:**

```python
# In capture_and_check() function
config = r'--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+.%# '
```

**Modify Stat Value Ranges:**

```python
# In ConfigUI.__init__()
self.stat_values = {
    'STR': [0, 1, 2, 3, 4, 5],
    'CriticalChance': [0, 0.5, 1.0, 1.5, 2.0, 2.5],
    # Add your custom ranges
}
```

**Change Button Detection Confidence:**

```python
# In click_image() function
location = pyautogui.locateCenterOnScreen(image_path, confidence=0.9)
```

### Debugging

1. **Enable OCR output visualization**

   - Uncomment debug lines in `capture_and_check()`
   - Saves preprocessed images to disk

2. **Check console output**

   - OCR detected text
   - Regex matches
   - Stat comparisons
   - Error messages

3. **Common Issues**
   - **OCR not detecting stats:** Adjust threshold value (150), try different values
   - **Wrong button clicked:** Update `button_image.png` template
   - **Stats not matching:** Verify stat names in `stats.txt` match game text exactly

## 🔧 Troubleshooting

### Application won't start

- Ensure `tesseract` folder exists with `tesseract.exe`
- Check `stats.txt` is present
- Run from console to see error messages

### OCR not detecting stats

- Verify region includes the entire stats area
- Check game resolution and UI scale
- Ensure dialog is fully visible (no overlays)
- Try adjusting in-game brightness/contrast

### Button not being found

- Update `button_image.png` with current button screenshot
- Ensure game window is active and visible
- Check button confidence threshold

### Stats not summing correctly

- Verify only ONE stat is configured (not both)
- Check OCR is detecting both stat panels
- Review console output for matched values

## 📝 Changelog

### v2.0 (Current)

- ✨ Complete UI overhaul with CustomTkinter
- ✂️ Visual region selection with snipping tool
- 📊 Dual stat support with dropdown selectors
- ➕ Automatic stat summing for single-stat mode
- 🔄 Reconfiguration without restart
- 🎨 Modern dark theme interface
- 📈 Improved OCR accuracy (simpler preprocessing)
- 🛑 Proper process termination on window close

### v1.0 (Legacy)

- 🎯 Basic OCR stat detection
- ⌨️ Text input for stats and coordinates
- 🔄 Automatic rerolling
- 📝 Console-based logging

## 📄 License

This project is provided as-is for personal use with Flyff Universe.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Guidelines

- Follow PEP 8 style guide
- Add comments for complex logic
- Test OCR with various game resolutions
- Update README for new features

## 🙏 Credits

- **Tesseract OCR** - Google's open-source OCR engine
- **CustomTkinter** - Modern UI library for Python
- **OpenCV** - Image processing library
- **PyAutoGUI** - Automation library

## ⚠️ Disclaimer

This tool is for educational purposes. Use at your own risk. Automated tools may violate game terms of service. The authors are not responsible for any consequences of using this software.
