"""
Design system constants for EngageEnglish.
Colors, fonts, screen dimensions, and configuration.
"""

import os

# Screen dimensions
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
FPS = 60

# Color palette - Modern flat design
class Colors:
    # Background colors
    BG = (15, 15, 26)           # #0F0F1A
    SURFACE = (26, 26, 46)      # #1A1A2E
    PANEL = (22, 33, 62)        # #16213E
    CARD = (31, 43, 71)         # #1F2B47
    CARD_HOVER = (38, 51, 84)   # #263354
    BORDER = (45, 53, 97)       # #2D3561
    
    # Accent colors
    ACCENT = (124, 58, 237)     # #7C3AED (Purple)
    ACCENT2 = (168, 85, 247)    # #A855F7 (Lighter purple)
    ACCENT_GLOW = (192, 132, 252) # #C084FC
    
    # Semantic colors
    TEAL = (6, 182, 212)        # #06B6D4
    TEAL_DIM = (14, 116, 144)   # #0E7490
    GOLD = (245, 158, 11)       # #F59E0B
    GOLD_DIM = (180, 83, 9)     # #B45309
    GREEN = (16, 185, 129)      # #10B981
    GREEN_DIM = (6, 95, 70)     # #065F46
    RED = (239, 68, 68)         # #EF4444
    RED_DIM = (127, 29, 29)     # #7F1D1D
    
    # Text colors
    TEXT = (241, 245, 249)      # #F1F5F9
    TEXT_DIM = (148, 163, 184)  # #94A3B8
    TEXT_MUTED = (71, 85, 105)  # #475569
    WHITE = (255, 255, 255)
    
    # Game-specific colors
    DRAG_WORD = (49, 46, 129)   # #312E81
    DRAG_BORDER = (99, 102, 241) # #6366F1
    TARGET_BOX = (30, 58, 95)   # #1E3A5F
    TARGET_BORDER = (59, 130, 246) # #3B82F6
    MATCH_OK = (6, 78, 59)      # #064E3B
    MATCH_BORDER = (16, 185, 129) # #10B981
    WRONG_FLASH = (127, 29, 29) # #7F1D1D
    SUCCESS_BG = (13, 27, 42)   # #0D1B2A
    FAIL_BG = (18, 10, 10)      # #120A0A

# Font sizes
FONT_SIZE_TITLE = 72
FONT_SIZE_HEADER = 48
FONT_SIZE_SUBHEADER = 32
FONT_SIZE_BODY = 24
FONT_SIZE_SMALL = 18
FONT_SIZE_TINY = 14

# Game configuration
DEFAULT_HP = 5
QUESTION_TIME_SECONDS = 15
STAR_THRESHOLDS = {
    3: 90,   # 90%+ for 3 stars
    2: 70,   # 70%+ for 2 stars
    1: 50    # 50%+ for 1 star
}

# Animation durations (in seconds)
TRANSITION_FADE_DURATION = 0.3
TRANSITION_SLIDE_DURATION = 0.4
BUTTON_HOVER_DURATION = 0.2
CARD_LIFT_DURATION = 0.15

# Mode identifiers
MODE_SPEED = "speed"
MODE_BREADTH = "breadth"
MODE_CONTEXT = "context"
MODE_RESILIENCE = "resilience"

# Mode display names
MODE_NAMES = {
    MODE_SPEED: "Speed Challenge",
    MODE_BREADTH: "Vocabulary Mastery",
    MODE_CONTEXT: "Context Builder",
    MODE_RESILIENCE: "Practice Lab"
}

# Mode descriptions
MODE_DESCRIPTIONS = {
    MODE_SPEED: "Test your automaticity under time pressure",
    MODE_BREADTH: "Build vocabulary depth through progressive levels",
    MODE_CONTEXT: "Master word usage in real sentences",
    MODE_RESILIENCE: "Practice without penalties, learn from mistakes"
}

# Asset paths
FONT_SELFIE = "assets/fonts/Selfie_Black.otf"
FONT_FALLBACK = "arial"  # System font fallback

# Data directories
DATA_DIR = "data"
SYNONYMS_DIR = os.path.join(DATA_DIR, "synonyms")
DEFINITIONS_DIR = os.path.join(DATA_DIR, "definitions")
CONTEXT_DIR = os.path.join(DATA_DIR, "context")

# Progress file
PROGRESS_FILE = "progress.json"

# Sound effects
SOUND_CORRECT = "assets/sounds/correct.wav"
SOUND_WRONG = "assets/sounds/wrong.wav"

# Layout constants
PADDING = 20
CARD_RADIUS = 12
BUTTON_RADIUS = 8
SHADOW_OFFSET = 4
SHADOW_BLUR = 8
