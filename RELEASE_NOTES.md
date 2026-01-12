# Release Notes - v1.0.0

## 🎉 Initial Release

Welcome to the first official release of **BoD/BoG Auto Reroll**! This tool automates the stat rerolling process for Blessing of Dekane (BoD) and Blessing of Goddess (BoG) in Flyff Universe.

## ✨ Key Features

### Modern GUI Interface

- **CustomTkinter-based UI** with dark mode support
- Clean, intuitive design with visual feedback
- Theme switcher (Light/Dark/System)
- Responsive layout that scales with window size

### Smart Configuration System

- **Configuration Persistence**: All settings preserved when reconfiguring
- **Adaptive Value Dropdowns**: Options automatically update based on selected stat
- **Visual Region Selection**: Built-in snipping tool for easy dialog capture
- **Dual Stat Support**: Configure one or two target stats with minimum values
- **Smart Value Preservation**: Keeps valid selections when switching stats

### Powerful Automation

- **OCR-Based Stat Detection**: Uses Tesseract OCR to read stats from dialog
- **Template Matching**: Finds and clicks reroll button automatically
- **Intelligent Summing**: When one stat configured, sums values from both panels
- **GUI-Based Prompts**: All confirmations appear in the app window
- **Real-time Activity Log**: Monitor OCR detection and automation status

### Enhanced User Experience

- **No Terminal Required**: Everything happens through the GUI
- **Immediate Dropdown Updates**: Value options update instantly when changing stats
- **Clean Process Termination**: Proper cleanup when closing windows
- **Always-on-Top Mode**: Window stays visible during automation
- **Start/Stop Control**: Large, intuitive button for automation control

## 🔧 Technical Highlights

- **Enhanced ConfigUI Class**: Full initial value support for reconfiguration
- **Callback Architecture**: `on_stat1_change()` and `on_stat2_change()` for immediate updates
- **State Management**: Proper CTkComboBox state transitions (disabled → readonly)
- **apply_initial_values() Method**: Restores all configuration on reconfiguration
- **Color-Coded Logging**: Timestamped messages with emoji indicators
- **Image Preprocessing**: 3x upscaling, binary thresholding, noise reduction for better OCR

## 📦 Installation

### Pre-built Release (Windows)

1. Download `bod-auto.exe` from the releases page
2. Run `bod-auto.exe` - no installation required!
3. Configure your target stats and start automation

**Note**: Windows may show a SmartScreen warning for unsigned executables. Click "More info" → "Run anyway"

### From Source

```bash
git clone https://github.com/ravenda900/flyff-autobod.git
cd flyff-autobod
pip install -r requirements.txt
python bod-auto.py
```

## 🎯 Quick Start

1. **Select Dialog Region**: Click "SELECT DIALOG REGION" and draw a box around your BoD/BoG dialog
2. **Configure Stats**:
   - Choose Stat 1 (e.g., STR) and minimum value (e.g., 3)
   - Optionally choose Stat 2 and its minimum value
   - Configure at least one stat
3. **Start Automation**: Click "START AUTOMATION" button
4. **Monitor Progress**: Watch the activity log for OCR results and status updates
5. **Reconfigure Anytime**: Click "⚙️ Reconfigure" to change settings without restarting

## 📊 Supported Stats

- **Primary Stats**: STR, DEX, INT, STA (0-5)
- **Critical Stats**: CriticalChance, CriticalDamage (0-2.5)
- **Speed Stats**: Speed, AttackSpeed, CastingSpeed (0-3.0)
- **Combat Stats**: Attack (0-21), Defense (0-14), MagicDefense (0-18)
- **Resource Stats**: HP, MP, FP (0-37)
- **Block Stats**: Parry, MeleeBlock, RangedBlock (0-3.0)
- **PvE Stats**: PvEDamage (0-30), PvEDmgResist (0-25)

## 📋 Requirements

- **Windows 10/11** (64-bit)
- **Game**: Flyff Universe running in browser or desktop app
- **Screen**: Works with any resolution (1080p, 1440p, 4K)

## 🔍 How It Works

1. **Button Detection**: Uses OpenCV template matching (0.9 confidence) to find reroll button
2. **Screenshot Capture**: Grabs the configured dialog region
3. **OCR Processing**: Applies image preprocessing and runs Tesseract OCR
4. **Stat Parsing**: Regex pattern matching to extract stat names and values
5. **Target Checking**: Compares detected values against configured targets
6. **Auto-Click**: Clicks reroll button if targets not met
7. **User Prompt**: Shows GUI dialog when targets achieved

## 📋 Known Issues

None at this time. Please report any issues on the GitHub repository.

## 🙏 Acknowledgments

- **Tesseract OCR** - Google's open-source OCR engine
- **CustomTkinter** - Modern UI library for Python
- **OpenCV** - Computer vision and image processing
- **PyAutoGUI** - Cross-platform GUI automation

Thank you to all testers and users who helped shape this tool!

---

**Full Changelog**: https://github.com/ravenda900/flyff-autobod/commits/v1.0.0
