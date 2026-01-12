# Release Notes - v1.0.0

## 🎉 What's New

### Configuration Persistence

- All settings are now preserved when reconfiguring
- Region coordinates, stats, and target values are automatically restored
- No need to reconfigure everything when making small adjustments

### Adaptive Value Dropdowns

- Value options automatically update based on the selected stat
- Each stat has predefined valid value ranges based on game mechanics
- Smart value preservation - keeps your selection when switching between compatible stats

### Enhanced User Experience

- **GUI-Based Interactions**: All prompts and confirmations now appear in the application window
- **No Terminal Dependency**: Everything happens through the intuitive GUI
- **Immediate Updates**: Dropdown values update instantly when changing stats during reconfiguration
- **Clean Termination**: Proper process cleanup when closing the window

### Improved Reconfiguration Logic

- Complete rewrite of the reconfiguration system
- Better state management for dropdowns and values
- Explicit widget updates ensure smooth transitions
- Proper callback architecture for reliable stat/value updates

## 🔧 Technical Improvements

- Enhanced `ConfigUI` class with initial value support
- Callback methods (`on_stat1_change`, `on_stat2_change`) for immediate dropdown updates
- `apply_initial_values()` method for restoring configuration during reconfiguration
- Better handling of CTkComboBox state transitions
- Improved logging with color-coded, timestamped messages

## 📦 Installation

### Pre-built Release (Windows)

1. Download `bod-auto.exe` or `bod-auto.zip` from the releases page
2. Extract if using the zip file
3. Run `bod-auto.exe`
4. Configure your target stats and start automation

### From Source

```bash
git clone https://github.com/ravenda900/flyff-autobod.git
cd flyff-autobod
pip install -r requirements.txt
python bod-auto.py
```

## 🎯 Usage

1. **Select Dialog Region**: Use the snipping tool to select the BoD/BoG dialog
2. **Configure Stats**: Choose your target stats and minimum values
3. **Start Automation**: Click the START button and let the bot do the work
4. **Reconfigure Anytime**: Click "⚙️ Reconfigure" to adjust settings without losing your previous configuration

## 🐛 Bug Fixes

- Fixed dropdown state issues during reconfiguration
- Fixed value dropdowns not updating when stat changes
- Fixed configuration values being lost during reconfiguration
- Improved window close handler for clean process termination

## 📋 Known Issues

None at this time. Please report any issues on the GitHub repository.

## 🙏 Acknowledgments

Thank you to all users who provided feedback and helped improve this tool!

---

**Full Changelog**: https://github.com/ravenda900/flyff-autobod/commits/v1.0.0
