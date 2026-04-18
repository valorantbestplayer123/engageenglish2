# EngageEnglish v4 - Quick Start Guide

## Installation

### Option 1: Run from Source
```bash
# Navigate to the project directory
cd EngageEnglish

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Option 2: Build Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller EngageEnglish.spec

# The executable will be in dist/EngageEnglish
# On Windows: dist\EngageEnglish.exe
# On Linux/Mac: dist/EngageEnglish
```

## Game Modes

### 1. Speed Challenge (Speed & Automaticity)
- **Goal:** Answer definition questions as fast as possible
- **Time:** 15 seconds per question
- **HP:** Start with 3 HP, +1 per level
- **Bonus:** Streak bonus (+10 per streak, max +50)
- **Levels:** 5 (academic1-5), 60 questions each

### 2. Vocabulary Mastery (Breadth & Depth)
- **Goal:** Match words with their synonyms
- **Time:** No timer, work at your own pace
- **HP:** 5 HP per round
- **Scoring:** Earn stars (3★ = 90%+, 2★ = 70%+, 1★ = 50%+)
- **Levels:** 7 (level1-7), 8 pairs per round (60 total each)

### 3. Context Builder (Context & Morphology)
- **Goal:** Complete sentences with the correct word
- **Time:** 15 seconds per sentence
- **HP:** 5 HP per level
- **Scoring:** 100 points per correct answer
- **Levels:** 3 (level1-3), 8 sentences each (with fallback to definitions)

### 4. Practice Lab (Resilience)
- **Goal:** Practice without penalties
- **Time:** No time pressure
- **HP:** None (unlimited retries)
- **Features:** Hint button removes 1 wrong option (-20 pts)
- **Levels:** 5 (academic1-5), 60 questions each

## Controls

### Mouse
- **Click** on buttons, cards, and options
- **Hover** to see animations
- **Click "Exit"** to return to previous screen

### Keyboard
- **ESC** - Return to main menu
- **Arrow keys** - Navigate options (in some modes)

## Progress Saving

Your progress is automatically saved to `progress.json` in the application directory.

### Tracked Progress:
- **Speed Mode:** Unlocked levels, best streak, accuracy, scores
- **Breadth Mode:** Unlocked levels, stars earned, accuracy, scores
- **Context Mode:** Unlocked levels, sentences completed, accuracy, scores
- **Resilience Mode:** Unlocked levels, hints used, retries, practice count

## Troubleshooting

### Application won't start
- Ensure pygame is installed: `pip install pygame>=2.5.0`
- Check Python version: 3.8 or higher recommended

### Fonts not displaying correctly
- The app will fallback to Arial if the custom font is missing
- Ensure `assets/fonts/Selfie_Black.otf` exists

### Sounds not playing
- Sounds are optional; the app works without them
- Check that sound files exist in `assets/sounds/`
- Verify system audio is not muted

### Progress not saving
- Ensure you have write permissions in the application directory
- Check that `progress.json` is not read-only

### PyInstaller build fails
- Ensure all data and assets are included in the spec file
- Verify that you're running from the EngageEnglish directory
- Try `pyinstaller --clean EngageEnglish.spec` to rebuild

## File Structure

```
EngageEnglish/
├── src/                    # Source code
│   ├── core/              # Core infrastructure
│   ├── ui/                # UI components
│   ├── modes/             # Game modes
│   ├── scenes/            # Application screens
│   └── main.py            # Entry point
├── data/                  # Game data
│   ├── synonyms/          # Synonym pairs (7 levels)
│   ├── definitions/       # Definition questions (5 levels)
│   └── context/           # Sentence completion (3 levels)
├── assets/                # Media files
│   ├── fonts/             # Custom fonts
│   └── sounds/            # Sound effects
├── requirements.txt       # Python dependencies
├── EngageEnglish.spec     # PyInstaller build config
└── progress.json          # User progress (auto-created)
```

## Performance Tips

- **For better performance:** Close other applications
- **For smooth animations:** Ensure 60 FPS (default)
- **For faster loading:** The app caches data after first load

## Getting Help

- Check the README.md for detailed documentation
- Review REBUILD_SUMMARY.md for technical details
- Run `python test_app.py` to verify installation
- Run `python test_headless.py` to test without display

## Enjoy Learning English!

The EngageEnglish application is designed to help you master academic vocabulary through four different learning approaches. Each mode targets a different aspect of language proficiency:

1. **Automaticity** (Speed) - Quick word recognition
2. **Depth** (Breadth) - Synonym relationships
3. **Context** (Context) - Word usage in sentences
4. **Resilience** (Practice) - Learning from mistakes

Start with the mode that best fits your learning goals!
