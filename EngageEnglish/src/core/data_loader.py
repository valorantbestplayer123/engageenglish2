"""
Data loader for JSON level files with caching.
Supports synonyms, definitions, and context levels.
"""

import os
import json
import glob
from typing import Dict, List, Optional, Any
from collections import OrderedDict

from core.constants import SYNONYMS_DIR, DEFINITIONS_DIR, CONTEXT_DIR


class DataLoader:
    """Loads and caches JSON data for all game modes."""
    
    def __init__(self):
        self._synonym_cache: Dict[int, Dict] = {}
        self._definition_cache: Dict[int, Dict] = {}
        self._context_cache: Dict[int, Dict] = {}
        self._synonym_list: List[int] = []
        self._definition_list: List[int] = []
        self._context_list: List[int] = []
    
    def _load_json(self, path: str) -> Optional[Dict]:
        """Load a JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_synonym_level(self, level_num: int) -> Optional[Dict]:
        """Get a synonym level data."""
        if level_num not in self._synonym_cache:
            path = os.path.join(SYNONYMS_DIR, f"level{level_num}.json")
            data = self._load_json(path)
            if data:
                self._synonym_cache[level_num] = data
            return data
        return self._synonym_cache[level_num]
    
    def get_definition_level(self, level_num: int) -> Optional[Dict]:
        """Get a definition level data."""
        if level_num not in self._definition_cache:
            path = os.path.join(DEFINITIONS_DIR, f"academic{level_num}.json")
            data = self._load_json(path)
            if data:
                self._definition_cache[level_num] = data
            return data
        return self._definition_cache[level_num]
    
    def get_context_level(self, level_num: int) -> Optional[Dict]:
        """Get a context level data."""
        if level_num not in self._context_cache:
            path = os.path.join(CONTEXT_DIR, f"level{level_num}.json")
            data = self._load_json(path)
            if data:
                self._context_cache[level_num] = data
            return data
        return self._context_cache[level_num]
    
    def get_synonym_levels(self) -> List[Dict]:
        """Get all synonym levels sorted by level number."""
        if not self._synonym_list:
            pattern = os.path.join(SYNONYMS_DIR, "level*.json")
            for path in glob.glob(pattern):
                # Extract level number from filename
                basename = os.path.basename(path)
                try:
                    num = int(basename.replace("level", "").replace(".json", ""))
                    self._synonym_list.append(num)
                except ValueError:
                    continue
            self._synonym_list.sort()
        
        levels = []
        for num in self._synonym_list:
            data = self.get_synonym_level(num)
            if data:
                levels.append(data)
        return levels
    
    def get_definition_levels(self) -> List[Dict]:
        """Get all definition levels sorted by level number."""
        if not self._definition_list:
            pattern = os.path.join(DEFINITIONS_DIR, "academic*.json")
            for path in glob.glob(pattern):
                basename = os.path.basename(path)
                try:
                    num = int(basename.replace("academic", "").replace(".json", ""))
                    self._definition_list.append(num)
                except ValueError:
                    continue
            self._definition_list.sort()
        
        levels = []
        for num in self._definition_list:
            data = self.get_definition_level(num)
            if data:
                levels.append(data)
        return levels
    
    def get_context_levels(self) -> List[Dict]:
        """Get all context levels sorted by level number."""
        if not self._context_list:
            pattern = os.path.join(CONTEXT_DIR, "level*.json")
            for path in glob.glob(pattern):
                basename = os.path.basename(path)
                try:
                    num = int(basename.replace("level", "").replace(".json", ""))
                    self._context_list.append(num)
                except ValueError:
                    continue
            self._context_list.sort()
        
        levels = []
        for num in self._context_list:
            data = self.get_context_level(num)
            if data:
                levels.append(data)
        return levels
    
    def get_synonym_count(self) -> int:
        """Get total number of synonym levels."""
        if not self._synonym_list:
            self.get_synonym_levels()
        return len(self._synonym_list)
    
    def get_definition_count(self) -> int:
        """Get total number of definition levels."""
        if not self._definition_list:
            self.get_definition_levels()
        return len(self._definition_list)
    
    def get_context_count(self) -> int:
        """Get total number of context levels."""
        if not self._context_list:
            self.get_context_levels()
        return len(self._context_list)
    
    def clear_cache(self):
        """Clear all cached data."""
        self._synonym_cache.clear()
        self._definition_cache.clear()
        self._context_cache.clear()
