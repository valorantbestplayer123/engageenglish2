"""
Progress manager for saving and loading player progress.
Tracks unlocked levels, scores, and statistics for all four modes.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.constants import PROGRESS_FILE, MODE_SPEED, MODE_BREADTH, MODE_CONTEXT, MODE_RESILIENCE


class ProgressManager:
    """Manages player progress across all game modes."""
    
    def __init__(self):
        self.data = self._create_default_progress()
        self.load()
    
    def _create_default_progress(self) -> Dict[str, Any]:
        """Create default progress structure."""
        return {
            "version": 4,
            "last_updated": None,
            "highest_level": 1,
            "total_play_time": 0,
            "consecutive_days": 0,
            "last_played_date": None,
            "modes": {
                MODE_SPEED: {
                    "unlocked_levels": [1],
                    "level_scores": {},
                    "best_streak": 0,
                    "total_correct": 0,
                    "total_attempts": 0
                },
                MODE_BREADTH: {
                    "unlocked_levels": [1],
                    "level_scores": {},
                    "stars_earned": {},
                    "total_correct": 0,
                    "total_attempts": 0
                },
                MODE_CONTEXT: {
                    "unlocked_levels": [1],
                    "level_scores": {},
                    "sentences_completed": 0,
                    "total_correct": 0,
                    "total_attempts": 0
                },
                MODE_RESILIENCE: {
                    "unlocked_levels": [1],
                    "practice_count": 0,
                    "hints_used": 0,
                    "total_retries": 0,
                    "level_scores": {}
                }
            },
            "achievements": [],
            "settings": {
                "sound_enabled": True,
                "music_enabled": False,
                "volume": 0.7
            }
        }
    
    def load(self) -> bool:
        """Load progress from file."""
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    # Merge with default structure
                    self._merge_progress(saved_data)
                self._update_consecutive_days()
                return True
        except Exception:
            pass
        return False
    
    def _merge_progress(self, saved_data: Dict[str, Any]):
        """Merge saved data with default structure for backward compatibility."""
        # Update simple fields
        for key in ["version", "highest_level", "total_play_time"]:
            if key in saved_data:
                self.data[key] = saved_data[key]
        
        # Update dates
        if "last_played_date" in saved_data:
            self.data["last_played_date"] = saved_data["last_played_date"]
        if "last_updated" in saved_data:
            self.data["last_updated"] = saved_data["last_updated"]
        
        # Merge mode data
        if "modes" in saved_data:
            for mode_name, mode_data in saved_data["modes"].items():
                if mode_name in self.data["modes"]:
                    for key, value in mode_data.items():
                        self.data["modes"][mode_name][key] = value
        
        # Merge achievements
        if "achievements" in saved_data:
            self.data["achievements"] = saved_data["achievements"]
        
        # Merge settings
        if "settings" in saved_data:
            for key, value in saved_data["settings"].items():
                self.data["settings"][key] = value
    
    def save(self) -> bool:
        """Save progress to file."""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            self.data["last_played_date"] = datetime.now().strftime("%Y-%m-%d")
            
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
            return True
        except Exception:
            return False
    
    def _update_consecutive_days(self):
        """Update consecutive days played counter."""
        today = datetime.now().strftime("%Y-%m-%d")
        last = self.data.get("last_played_date")
        
        if last is None:
            self.data["consecutive_days"] = 1
        elif last == today:
            # Already played today, no change
            pass
        else:
            # Check if yesterday
            last_date = datetime.strptime(last, "%Y-%m-%d").date()
            today_date = datetime.now().date()
            delta = (today_date - last_date).days
            
            if delta == 1:
                self.data["consecutive_days"] += 1
            elif delta > 1:
                # Streak broken
                self.data["consecutive_days"] = 1
    
    def get_unlocked_levels(self, mode: str) -> List[int]:
        """Get list of unlocked level numbers for a mode."""
        return self.data["modes"].get(mode, {}).get("unlocked_levels", [1])
    
    def unlock_level(self, mode: str, level: int):
        """Unlock a level for a mode."""
        unlocked = self.get_unlocked_levels(mode)
        if level not in unlocked:
            unlocked.append(level)
            unlocked.sort()
            self.data["modes"][mode]["unlocked_levels"] = unlocked
    
    def get_level_score(self, mode: str, level: int) -> int:
        """Get score for a specific level in a mode."""
        scores = self.data["modes"].get(mode, {}).get("level_scores", {})
        return scores.get(str(level), 0)
    
    def set_level_score(self, mode: str, level: int, score: int):
        """Set score for a specific level in a mode."""
        if "level_scores" not in self.data["modes"][mode]:
            self.data["modes"][mode]["level_scores"] = {}
        self.data["modes"][mode]["level_scores"][str(level)] = score
        
        # Update highest level
        if level > self.data["highest_level"]:
            self.data["highest_level"] = level
    
    def get_stars(self, mode: str, level: int) -> int:
        """Get star rating for a level (Breadth mode only)."""
        if mode == MODE_BREADTH:
            stars = self.data["modes"][mode].get("stars_earned", {})
            return stars.get(str(level), 0)
        return 0
    
    def set_stars(self, mode: str, level: int, stars: int):
        """Set star rating for a level."""
        if mode == MODE_BREADTH:
            if "stars_earned" not in self.data["modes"][mode]:
                self.data["modes"][mode]["stars_earned"] = {}
            current = self.get_stars(mode, level)
            if stars > current:
                self.data["modes"][mode]["stars_earned"][str(level)] = stars
    
    def get_accuracy(self, mode: str) -> float:
        """Calculate accuracy percentage for a mode."""
        mode_data = self.data["modes"].get(mode, {})
        correct = mode_data.get("total_correct", 0)
        attempts = mode_data.get("total_attempts", 0)
        if attempts == 0:
            return 0.0
        return (correct / attempts) * 100
    
    def record_attempt(self, mode: str, correct: bool):
        """Record an answer attempt for a mode."""
        if "total_attempts" not in self.data["modes"][mode]:
            self.data["modes"][mode]["total_attempts"] = 0
        if "total_correct" not in self.data["modes"][mode]:
            self.data["modes"][mode]["total_correct"] = 0
        
        self.data["modes"][mode]["total_attempts"] += 1
        if correct:
            self.data["modes"][mode]["total_correct"] += 1
    
    def get_best_streak(self, mode: str) -> int:
        """Get best streak for Speed mode."""
        if mode == MODE_SPEED:
            return self.data["modes"][mode].get("best_streak", 0)
        return 0
    
    def set_best_streak(self, mode: str, streak: int):
        """Set best streak for Speed mode."""
        if mode == MODE_SPEED:
            current = self.get_best_streak(mode)
            if streak > current:
                self.data["modes"][mode]["best_streak"] = streak
    
    def get_consecutive_days(self) -> int:
        """Get consecutive days played."""
        return self.data.get("consecutive_days", 0)
    
    def reset_progress(self):
        """Reset all progress to default."""
        self.data = self._create_default_progress()
        self.save()
