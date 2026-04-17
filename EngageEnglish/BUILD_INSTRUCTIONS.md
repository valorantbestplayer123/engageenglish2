# Build Instructions for EngageEnglish

## Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Navigate to the EngageEnglish directory:
   ```bash
   cd /path/to/EngageEnglish
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

## Building Windows Executable

### Using PyInstaller

1. Ensure PyInstaller is installed:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller EngageEnglish.spec
   ```

3. The executable will be created in the `dist/` directory:
   ```
   dist/
   └── EngageEnglish.exe
   ```

4. Run the executable:
   ```bash
   cd dist
   ./EngageEnglish.exe
   ```

### PyInstaller Spec File Details

The `EngageEnglish.spec` file is configured to:
- Create a single-file executable
- Include all data files (levels, fonts, sounds)
- Hide the console window (GUI application)
- Use UPX compression to reduce file size

### Customization Options

To modify the build:

1. **Change icon**: Add an `.ico` file and update the spec:
   ```python
   icon='path/to/icon.ico'
   ```

2. **Enable console for debugging**:
   ```python
   console=True
   ```

3. **Exclude unnecessary modules** (smaller executable):
   ```python
   excludes=['tkinter', 'matplotlib', ...]
   ```

## Troubleshooting

### PyInstaller Issues

**Problem**: Missing module errors
**Solution**: Add to `hiddenimports` in spec file:
```python
hiddenimports=['pygame', 'json', ...]
```

**Problem**: Large executable size
**Solution**: 
- Use UPX compression (already enabled)
- Add more modules to `excludes` list
- Consider using `--onefile` vs `--onedir`

**Problem**: Assets not found in bundled executable
**Solution**: Ensure `resource_manager.py` is using the correct `sys._MEIPASS` path (already implemented)

### Runtime Issues

**Problem**: Font not loading
**Solution**: Verify font file path in `constants.py` matches actual file location

**Problem**: Sound not playing
**Solution**: Check pygame mixer initialization and sound file formats

**Problem**: Data files not loading
**Solution**: Ensure data directory structure is correct:
```
EngageEnglish/
├── data/
│   ├── synonyms/
│   ├── definitions/
│   └── context/
└── assets/
    ├── fonts/
    └── sounds/
```

## Distribution

### Creating a ZIP Archive

1. Build the executable
2. Create a distribution folder:
   ```
   EngageEnglish-v1.0/
   ├── EngageEnglish.exe
   ├── README.md
   └── LICENSE (if applicable)
   ```

3. Compress into ZIP:
   ```bash
   zip -r EngageEnglish-v1.0.zip EngageEnglish-v1.0/
   ```

### Windows Installer (Optional)

For creating an installer, consider:
- **Inno Setup**: Free, popular for Windows
- **NSIS**: Nullsoft Scriptable Install System
- **WiX Toolset**: Windows Installer XML

## Testing

### Pre-Build Testing

1. Test all game modes
2. Verify progress saving/loading
3. Check sound playback
4. Test on different screen resolutions

### Post-Build Testing

1. Run the executable on a clean Windows machine
2. Verify all features work without Python installed
3. Test performance and memory usage
4. Check for antivirus false positives

## Performance Optimization

### Tips for Smaller/Faster Executable

1. **UPX Compression**: Already enabled in spec
2. **Exclude Unused Modules**: Add to `excludes` list
3. **Optimize Imports**: Only import what's needed
4. **Asset Compression**: Compress audio files if possible

### Tips for Better Performance

1. **Frame Rate**: App targets 60 FPS
2. **Asset Loading**: Uses caching to avoid repeated loads
3. **Dirty Rectangle Updates**: Currently using full redraw (acceptable for this UI complexity)

## Version Information

- Python: 3.8+
- Pygame: 2.5.0+
- PyInstaller: 5.0.0+

## Support

For issues or questions:
1. Check this document
2. Review README.md
3. Examine inline code comments
