# EngageEnglish - Premium Vocabulary Trainer

A modern Pygame-based vocabulary learning application with four proficiency-based modes.

## Features

### Four Game Modes

1. **Speed Challenge** - Test your automaticity under time pressure with multiple-choice questions
   - Fast-paced gameplay
   - Streak counter with bonus points
   - Time limit per question

2. **Vocabulary Mastery** - Build vocabulary depth through progressive synonym matching levels
   - Match words with their synonyms
   - Progressive difficulty
   - Star rating system (1-3 stars)

3. **Context Builder** - Master word usage in real sentences
   - Fill-in-the-blank sentence completion
   - Learn words in context
   - Improves reading comprehension

4. **Practice Lab** - Practice without penalties, learn from mistakes
   - No HP system
   - Hint system available
   - Unlimited retries
   - Focus on learning over scoring

### Key Features

- **Modern Flat UI** - Clean, contemporary design with smooth animations
- **Progress Tracking** - Save progress across all four modes
- **Four Proficiency Indicators** - Speed, Accuracy, Context, Resilience
- **Smooth Transitions** - 60fps animations between scenes
- **Sound Effects** - Audio feedback for correct/incorrect answers
- **Consecutive Day Tracking** - Maintain daily practice streaks

## Installation

### Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

### Building Windows Executable

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the executable:
   ```bash
   pyinstaller EngageEnglish.spec
   ```
3. The executable will be in the `dist/` folder

## Project Structure

```
EngageEnglish/
├── src/
│   ├── main.py              # Application entry point
│   ├── core/                # Core systems
│   │   ├── constants.py     # Design system and configuration
│   │   ├── resource_manager.py  # Asset loading with PyInstaller support
│   │   ├── data_loader.py   # JSON data loading
│   │   ├── progress_manager.py  # Save/load progress
│   │   ├── scene_manager.py     # Scene stack management
│   │   ├── scene_base.py        # Abstract scene class
│   │   └── transition.py        # Screen transitions
│   ├── ui/                  # UI components
│   │   ├── button.py        # Interactive buttons
│   │   ├── card.py          # Card containers
│   │   ├── label.py         # Text labels
│   │   ├── progress_bar.py  # Progress indicators
│   │   ├── timer.py         # Countdown timers
│   │   └── stars.py         # Star ratings
│   ├── scenes/              # Game scenes
│   │   ├── main_menu.py     # Main menu with mode selection
│   │   ├── level_select.py  # Level selection screen
│   │   └── results_screen.py    # Unified results display
│   └── modes/               # Game mode implementations
│       ├── speed_mode.py        # Speed & Automaticity
│       ├── breadth_mode.py       # Breadth & Depth
│       ├── context_mode.py       # Context & Morphology
│       └── resilience_mode.py    # Behavioral/Resilience
├── data/                    # Game data
│   ├── synonyms/            # Synonym matching levels
│   ├── definitions/         # Definition quiz levels
│   └── context/             # Sentence completion levels
├── assets/                  # Game assets
│   ├── fonts/               # Font files
│   └── sounds/              # Sound effects
├── EngageEnglish.spec       # PyInstaller configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Progress System

Progress is automatically saved to `progress.json` with the following tracking:

- Unlocked levels for each mode
- Scores and star ratings
- Accuracy statistics
- Consecutive days played
- Best streaks (Speed mode)
- Hints used and retries (Resilience mode)

## Adding New Content

### Adding Synonym Levels

Create JSON files in `data/synonyms/` following this format:

```json
{
  "level": 1,
  "title": "Level Title",
  "instructions": "Match each word with its synonym.",
  "pairs": {
    "word1": "synonym1",
    "word2": "synonym2"
  }
}
```

### Adding Definition Levels

Create JSON files in `data/definitions/` following this format:

```json
{
  "level": 1,
  "title": "Academic Word List 1",
  "questions": [
    {
      "definition": "Word definition",
      "options": ["Wrong1", "Correct", "Wrong2", "Wrong3"],
      "answer": "Correct"
    }
  ]
}
```

### Adding Context Levels

Create JSON files in `data/context/` following this format:

```json
{
  "level": 1,
  "title": "Context Level 1",
  "instructions": "Complete each sentence with the correct word.",
  "sentences": [
    {
      "text": "The _____ was unexpected.",
      "answer": "outcome",
      "options": ["result", "consequence", "effect", "impact"]
    }
  ]
}
```

## System Requirements

- Python 3.8 or higher
- Pygame 2.5.0 or higher
- Windows, macOS, or Linux
- 1600x900 minimum resolution

## License

This project is developed for educational purposes.

## Credits

Built with Pygame, featuring the Selfie Black font.
