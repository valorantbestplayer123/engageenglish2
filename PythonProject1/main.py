# main.py
# EngageEnglish v3 — Comprehensive UI Overhaul
# Requirements: pip install customtkinter

import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller .exe"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


APP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
PROGRESS_FILE = os.path.join(APP_DIR, "progress.json")

import time
import json
import random
import tkinter as tk

import customtkinter as ctk

try:
    import winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Design System ──────────────────────────────────────────────────────────────

C = {
    "bg":          "#0F0F1A",
    "surface":     "#1A1A2E",
    "panel":       "#16213E",
    "card":        "#1F2B47",
    "card_hover":  "#263354",
    "border":      "#2D3561",
    "accent":      "#7C3AED",
    "accent2":     "#A855F7",
    "accent_glow": "#C084FC",
    "teal":        "#06B6D4",
    "teal_dim":    "#0E7490",
    "gold":        "#F59E0B",
    "gold_dim":    "#B45309",
    "green":       "#10B981",
    "green_dim":   "#065F46",
    "red":         "#EF4444",
    "red_dim":     "#7F1D1D",
    "text":        "#F1F5F9",
    "text_dim":    "#94A3B8",
    "text_muted":  "#475569",
    "white":       "#FFFFFF",
    "drag_word":   "#312E81",
    "drag_border": "#6366F1",
    "target_box":  "#1E3A5F",
    "target_border":"#3B82F6",
    "match_ok":    "#064E3B",
    "match_border":"#10B981",
    "wrong_flash": "#7F1D1D",
    "success_bg":  "#0D1B2A",
    "fail_bg":     "#120A0A",
}

FONT_SELFIE = resource_path("assets/fonts/Selfie_Black.otf")
LEVELS_DIR = "levels"
LEVELS_DEFINITIONS_DIR = "levels_definitions"
APP_WIDTH = 1600
APP_HEIGHT = 900


def play_sound(file):
    if not _HAS_WINSOUND:
        return
    try:
        import winsound
        winsound.PlaySound(file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


def hex_lerp(a, b, t):
    """Interpolate between two hex colours (e.g. '#RRGGBB')."""
    ar, ag, ab = int(a[1:3], 16), int(a[3:5], 16), int(a[5:7], 16)
    br, bg, bb = int(b[1:3], 16), int(b[3:5], 16), int(b[5:7], 16)
    r = int(ar + (br - ar) * t)
    g = int(ag + (bg - ag) * t)
    b_ = int(ab + (bb - ab) * t)
    return f"#{r:02x}{g:02x}{b_:02x}"


# ── Progress IO ────────────────────────────────────────────────────────────────

def load_progress():
    default = {
        "synonym_progress": {"unlocked": [1], "scores": {}},
        "definition_progress": {"unlocked": [1], "scores": {}},
        "highest_level": 1,
        "last_played": 1,
        "hp": 3,
    }
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f)
        return default
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, val in default.items():
            if key not in data:
                data[key] = val
    except Exception:
        data = default
    return data


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f)


# ── Shared Components ──────────────────────────────────────────────────────────

class ModernButton(ctk.CTkButton):
    """Animated button with gradient-style hover glow."""

    def __init__(self, master, variant="primary", **kwargs):
        palettes = {
            "primary":  ("#7C3AED", "#A855F7"),
            "secondary":("#1F2B47", "#263354"),
            "danger":   ("#7F1D1D", "#EF4444"),
            "success":  ("#065F46", "#10B981"),
            "ghost":    ("#0F0F1A", "#1F2B47"),
        }
        self._base, self._hover_target = palettes.get(variant, palettes["primary"])
        defaults = dict(
            corner_radius=12,
            fg_color=self._base,
            hover_color=self._hover_target,
            text_color=C["text"],
            border_width=0,
        )
        defaults.update(kwargs)
        super().__init__(master, **defaults)
        self._step = 0
        self._steps = 16
        self._hovering = False
        self._animating = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _=None):
        self._hovering = True
        if not self._animating:
            self._animating = True
            self._tick()

    def _on_leave(self, _=None):
        self._hovering = False
        if not self._animating:
            self._animating = True
            self._tick()

    def _tick(self):
        if self._hovering and self._step < self._steps:
            self._step += 1
        elif not self._hovering and self._step > 0:
            self._step -= 1
        t = self._step / self._steps
        color = hex_lerp(self._base, self._hover_target, t)
        self.configure(fg_color=color)
        keep_going = (self._hovering and self._step < self._steps) or \
                     (not self._hovering and self._step > 0)
        if keep_going:
            self.after(20, self._tick)
        else:
            self._animating = False


class GlowCard(ctk.CTkFrame):
    """A card frame with an optional hover highlight border."""

    def __init__(self, master, hoverable=False, **kwargs):
        kwargs.setdefault("fg_color", C["card"])
        kwargs.setdefault("corner_radius", 16)
        super().__init__(master, **kwargs)
        if hoverable:
            self.bind("<Enter>", lambda _: self.configure(fg_color=C["card_hover"]))
            self.bind("<Leave>", lambda _: self.configure(fg_color=C["card"]))


class PulsingDot(tk.Canvas):
    """A small animated pulsing circle (used as an accent decoration)."""

    def __init__(self, master, color="#7C3AED", size=10, **kwargs):
        super().__init__(master, width=size * 2, height=size * 2,
                         bg=C["surface"], highlightthickness=0, **kwargs)
        self._color = color
        self._size = size
        self._phase = 0
        self._oval = self.create_oval(2, 2, size * 2 - 2, size * 2 - 2,
                                      fill=color, outline="")
        self._pulse()

    def _pulse(self):
        self._phase = (self._phase + 0.06) % (2 * 3.14159)
        import math
        alpha = 0.55 + 0.45 * math.sin(self._phase)
        r, g, b = int(0x7C + (0xC0 - 0x7C) * alpha), \
                  int(0x3A + (0x84 - 0x3A) * alpha), \
                  int(0xED + (0xFC - 0xED) * alpha)
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.itemconfig(self._oval, fill=color)
        self.after(40, self._pulse)


class TimerArc(tk.Canvas):
    """Circular countdown timer with colour transition green→yellow→red."""

    def __init__(self, master, size=88, bg_color=C["surface"], **kwargs):
        super().__init__(master, width=size, height=size,
                         bg=bg_color, highlightthickness=0, **kwargs)
        pad = 6
        self._size = size
        self._track = self.create_arc(
            pad, pad, size - pad, size - pad,
            start=90, extent=359.9,
            style="arc", outline=C["border"], width=5
        )
        self._arc = self.create_arc(
            pad, pad, size - pad, size - pad,
            start=90, extent=359.9,
            style="arc", outline=C["green"], width=5
        )
        self._text = self.create_text(
            size // 2, size // 2,
            text="", font=("Helvetica", 14, "bold"), fill=C["green"]
        )

    def update_arc(self, remaining, total):
        ratio = max(remaining / total, 0)
        extent = ratio * 359.9
        if ratio > 0.5:
            color = hex_lerp(C["gold"], C["green"], (ratio - 0.5) * 2)
        else:
            color = hex_lerp(C["red"], C["gold"], ratio * 2)
        self.itemconfig(self._arc, extent=extent, outline=color)
        self.itemconfig(self._text, text=str(remaining), fill=color)


class HpDisplay(ctk.CTkFrame):
    """HP hearts/bar display."""

    def __init__(self, master, max_hp, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._max_hp = max_hp
        self._bar = ctk.CTkProgressBar(self, width=220, height=14,
                                        progress_color=C["green"],
                                        fg_color=C["border"])
        self._bar.pack(side="left", padx=(0, 8))
        self._label = ctk.CTkLabel(self, text="", font=("Helvetica", 13, "bold"),
                                   text_color=C["green"])
        self._label.pack(side="left")
        self.set_hp(max_hp)

    def set_hp(self, hp):
        ratio = max(hp / self._max_hp, 0)
        self._bar.set(ratio)
        if ratio > 0.6:
            color = C["green"]
        elif ratio > 0.3:
            color = C["gold"]
        else:
            color = C["red"]
        self._bar.configure(progress_color=color)
        self._label.configure(text=f"HP {hp}/{self._max_hp}", text_color=color)


class Confetti(tk.Canvas):
    """Falling confetti animation for celebration screens."""

    def __init__(self, master, width, height, **kwargs):
        super().__init__(master, width=width, height=height,
                         bg=C["success_bg"], highlightthickness=0, **kwargs)
        self._w = width
        self._h = height
        self._pieces = []
        colors = [C["accent_glow"], C["teal"], C["gold"], C["green"], C["text"]]
        for _ in range(60):
            x = random.randint(0, width)
            y = random.randint(-height, 0)
            sz = random.randint(5, 11)
            color = random.choice(colors)
            oid = self.create_oval(x, y, x + sz, y + sz, fill=color, outline="")
            self._pieces.append((oid, random.uniform(1.5, 3.5),
                                  random.uniform(-0.5, 0.5)))
        self._animate()

    def _animate(self):
        for oid, vy, vx in self._pieces:
            self.move(oid, vx, vy)
            coords = self.coords(oid)
            if not coords:
                continue
            if coords[1] > self._h:
                x = random.randint(0, self._w)
                sz = coords[2] - coords[0]
                self.coords(oid, x, -sz, x + sz, 0)
        self.after(28, self._animate)


class AnimatedBackground(ctk.CTkFrame):
    """Slowly cycles through a palette of dark background colours."""

    PALETTE = ["#0F0F1A", "#0D1B2A", "#12082A", "#0A1628", "#0F0F1A"]

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._ci = 0
        self._ni = 1
        self._step = 0
        self._steps = 120
        self._tick()

    def _tick(self):
        t = self._step / self._steps
        color = hex_lerp(self.PALETTE[self._ci], self.PALETTE[self._ni], t)
        self.configure(fg_color=color)
        self._step += 1
        if self._step > self._steps:
            self._step = 0
            self._ci = self._ni
            self._ni = (self._ni + 1) % len(self.PALETTE)
        self.after(60, self._tick)


# ── Main Menu ──────────────────────────────────────────────────────────────────

class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])

        bg = AnimatedBackground(self, corner_radius=0)
        bg.place(relx=0, rely=0, relwidth=1, relheight=1)

        center = ctk.CTkFrame(bg, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        accent_bar = ctk.CTkFrame(center, fg_color=C["accent"], width=80, height=4, corner_radius=2)
        accent_bar.pack(pady=(0, 18))

        title_lbl = ctk.CTkLabel(
            center,
            text="EngageEnglish",
            font=("Selfie", 96),
            text_color=C["text"],
        )
        title_lbl.pack()

        tagline = ctk.CTkLabel(
            center,
            text="Master Academic English — One Level at a Time",
            font=("Helvetica", 18),
            text_color=C["text_dim"],
        )
        tagline.pack(pady=(6, 48))

        btn_frame = ctk.CTkFrame(center, fg_color="transparent")
        btn_frame.pack()

        ModernButton(
            btn_frame,
            text="▶  Play",
            variant="primary",
            width=300, height=64,
            font=("Helvetica", 22, "bold"),
            command=master.show_game_modes,
        ).pack(pady=10)

        ModernButton(
            btn_frame,
            text="✕  Quit",
            variant="ghost",
            width=300, height=52,
            font=("Helvetica", 18),
            command=master.destroy,
        ).pack(pady=6)

        footer = ctk.CTkLabel(
            bg,
            text="EngageEnglish 2025-2026  ·  @wawa.jett_wonyoung",
            font=("Helvetica", 12),
            text_color=C["text_muted"],
        )
        footer.place(relx=0.5, rely=0.97, anchor="center")

        tip = ctk.CTkLabel(
            bg,
            text="Press  F11  to toggle fullscreen",
            font=("Helvetica", 11),
            text_color=C["text_muted"],
        )
        tip.place(relx=0.98, rely=0.97, anchor="se")


# ── Game Mode Selection ────────────────────────────────────────────────────────

class GameModesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])

        header = ctk.CTkFrame(self, fg_color=C["surface"], height=90, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Choose Game Mode",
                     font=("Selfie", 52), text_color=C["text"]).pack(pady=22)

        subtitle = ctk.CTkLabel(self, text="Select a challenge and start learning",
                                font=("Helvetica", 16), text_color=C["text_dim"])
        subtitle.pack(pady=(28, 40))

        modes_row = ctk.CTkFrame(self, fg_color="transparent")
        modes_row.pack(pady=10)

        self._make_mode_card(
            modes_row,
            icon="🔗",
            title="Word Synonyms",
            desc="Drag & drop words to match\nthem with their synonyms.",
            color=C["accent"],
            command=master.show_level_select,
        ).pack(side="left", padx=30)

        self._make_mode_card(
            modes_row,
            icon="📖",
            title="Word Definitions",
            desc="Read a definition and choose\nthe correct word from 4 options.",
            color=C["teal"],
            command=master.show_definition_level_select,
        ).pack(side="left", padx=30)

        ModernButton(
            self,
            text="⬅  Back to Menu",
            variant="ghost",
            width=220, height=46,
            font=("Helvetica", 16),
            command=master.show_main_menu,
        ).pack(pady=40)

    @staticmethod
    def _make_mode_card(parent, icon, title, desc, color, command):
        card = GlowCard(parent, hoverable=True, width=340, height=260, corner_radius=20)

        icon_lbl = ctk.CTkLabel(card, text=icon, font=("Helvetica", 52),
                                 text_color=color)
        icon_lbl.pack(pady=(30, 6))

        ctk.CTkLabel(card, text=title, font=("Helvetica", 22, "bold"),
                     text_color=C["text"]).pack()

        ctk.CTkLabel(card, text=desc, font=("Helvetica", 13),
                     text_color=C["text_dim"], justify="center").pack(pady=(6, 18))

        ModernButton(card, text="Select", variant="primary",
                     width=180, height=42,
                     font=("Helvetica", 15, "bold"),
                     command=command).pack(pady=(0, 20))

        return card


# ── Level Selection (Synonyms) ─────────────────────────────────────────────────

class LevelSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])

        header = ctk.CTkFrame(self, fg_color=C["surface"], height=90, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="🔗  Word Synonym Levels",
                     font=("Selfie", 46), text_color=C["text"]).pack(pady=22)

        ctk.CTkLabel(self, text="Complete a level to unlock the next one",
                     font=("Helvetica", 15), text_color=C["text_dim"]).pack(pady=(18, 8))

        panel = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        panel.pack(padx=40, pady=8, fill="both", expand=True)

        levels = _scan_levels(LEVELS_DIR)

        if not levels:
            ctk.CTkLabel(panel, text="No synonym levels found.",
                         text_color=C["text_dim"]).pack(pady=30)
        else:
            cols = 3
            for i, (level_num, title, path) in enumerate(levels):
                unlocked = level_num in master.progress["synonym_progress"]["unlocked"]
                score = master.progress["synonym_progress"]["scores"].get(str(level_num)) or \
                        master.progress["synonym_progress"]["scores"].get(level_num)
                r, c = divmod(i, cols)
                card = self._make_level_card(panel, level_num, title, unlocked, score,
                                             command=lambda p=path: master.show_game(p))
                card.grid(row=r, column=c, padx=18, pady=18, sticky="nsew")

        ModernButton(
            self,
            text="⬅  Back",
            variant="ghost",
            width=200, height=44,
            font=("Helvetica", 15),
            command=master.show_main_menu,
        ).pack(pady=16)

    @staticmethod
    def _make_level_card(parent, level_num, title, unlocked, score, command):
        card = GlowCard(parent, width=360, height=170, corner_radius=16,
                        fg_color=C["card"] if unlocked else C["surface"])

        badge_color = C["accent"] if unlocked else C["text_muted"]
        badge_text = f"Level {level_num}"
        ctk.CTkLabel(card, text=badge_text, font=("Helvetica", 12, "bold"),
                     text_color=badge_color).pack(anchor="w", padx=18, pady=(14, 2))

        ctk.CTkLabel(card, text=title, font=("Helvetica", 15, "bold"),
                     text_color=C["text"] if unlocked else C["text_muted"],
                     wraplength=320, justify="left").pack(anchor="w", padx=18)

        if score is not None:
            stars = "★" * _score_stars(score) + "☆" * (3 - _score_stars(score))
            ctk.CTkLabel(card, text=f"{stars}  {score}%",
                         font=("Helvetica", 13), text_color=C["gold"]).pack(anchor="w", padx=18)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=14, pady=(6, 12))

        if unlocked:
            ModernButton(btn_row, text="▶  Play", variant="primary",
                         width=130, height=38,
                         font=("Helvetica", 14, "bold"),
                         command=command).pack(side="left")
        else:
            ctk.CTkLabel(btn_row, text="🔒  Locked",
                         font=("Helvetica", 14),
                         text_color=C["text_muted"]).pack(side="left", padx=6)

        return card


# ── Level Selection (Definitions) ──────────────────────────────────────────────

class DefinitionLevelSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=C["bg"])

        header = ctk.CTkFrame(self, fg_color=C["surface"], height=90, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="📖  Word Definition Levels",
                     font=("Selfie", 46), text_color=C["text"]).pack(pady=22)

        ctk.CTkLabel(self, text="Unlock levels step by step",
                     font=("Helvetica", 15), text_color=C["text_dim"]).pack(pady=(18, 8))

        panel = ctk.CTkScrollableFrame(self, fg_color=C["bg"], corner_radius=0)
        panel.pack(padx=40, pady=8, fill="both", expand=True)

        levels = _scan_levels(LEVELS_DEFINITIONS_DIR)

        if not levels:
            ctk.CTkLabel(panel, text="No definition levels found.",
                         text_color=C["text_dim"]).pack(pady=30)
        else:
            cols = 4
            for i, (level_num, title, path) in enumerate(levels):
                unlocked = level_num in master.progress["definition_progress"]["unlocked"]
                score = master.progress["definition_progress"]["scores"].get(str(level_num)) or \
                        master.progress["definition_progress"]["scores"].get(level_num)
                r, c = divmod(i, cols)
                card = self._make_def_level_card(
                    panel, level_num, title, unlocked, score,
                    command=lambda p=path: master.show_definition_mode(p)
                )
                card.grid(row=r, column=c, padx=14, pady=14, sticky="nsew")

        ModernButton(
            self,
            text="⬅  Back",
            variant="ghost",
            width=200, height=44,
            font=("Helvetica", 15),
            command=master.show_main_menu,
        ).pack(pady=16)

    @staticmethod
    def _make_def_level_card(parent, level_num, title, unlocked, score, command):
        card = GlowCard(parent, width=270, height=160, corner_radius=14,
                        fg_color=C["card"] if unlocked else C["surface"])

        badge_color = C["teal"] if unlocked else C["text_muted"]
        ctk.CTkLabel(card, text=f"Level {level_num}",
                     font=("Helvetica", 11, "bold"),
                     text_color=badge_color).pack(anchor="w", padx=14, pady=(12, 2))

        ctk.CTkLabel(card, text=title, font=("Helvetica", 13, "bold"),
                     text_color=C["text"] if unlocked else C["text_muted"],
                     wraplength=240, justify="left").pack(anchor="w", padx=14)

        if score is not None:
            ctk.CTkLabel(card, text=f"Best: {score}%",
                         font=("Helvetica", 11), text_color=C["gold"]).pack(anchor="w", padx=14)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(anchor="w", padx=10, pady=(6, 10))

        if unlocked:
            ModernButton(btn_row, text="▶  Play", variant="primary",
                         width=110, height=34,
                         font=("Helvetica", 13, "bold"),
                         command=command).pack(side="left")
        else:
            ctk.CTkLabel(btn_row, text="🔒  Locked",
                         font=("Helvetica", 13),
                         text_color=C["text_muted"]).pack(side="left", padx=4)

        return card


# ── Draggable Label ────────────────────────────────────────────────────────────

class DraggableLabel(ctk.CTkLabel):
    def __init__(self, master, text, drop_handler, **kwargs):
        defaults = dict(
            fg_color=C["drag_word"],
            text_color=C["text"],
            corner_radius=10,
            font=("Helvetica", 15, "bold"),
        )
        defaults.update(kwargs)
        super().__init__(master, text=text, **defaults)
        self.drop_handler = drop_handler
        self.original_pos = (0, 0)
        self.locked = False
        self.match_answer = None
        self._dx = 0
        self._dy = 0
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_unhover)

    def _on_hover(self, _=None):
        if not self.locked:
            self.configure(fg_color=C["drag_border"])

    def _on_unhover(self, _=None):
        if not self.locked:
            self.configure(fg_color=C["drag_word"])

    def _on_press(self, event):
        if self.locked:
            return
        self._dx = event.x
        self._dy = event.y
        self.lift()
        self.configure(fg_color=C["accent"])

    def _on_drag(self, event):
        if self.locked:
            return
        x = self.winfo_x() + event.x - self._dx
        y = self.winfo_y() + event.y - self._dy
        self.place(x=x, y=y)

    def _on_release(self, _=None):
        if self.locked:
            return
        self.drop_handler(self)


# ── Synonym Game ───────────────────────────────────────────────────────────────

class GameFrame(ctk.CTkFrame):
    def __init__(self, master, level_path, hp=None):
        super().__init__(master, fg_color=C["bg"])
        self.master = master
        self.level_path = level_path
        self.targets = []
        self.draggables = []
        self.wrong_words = []
        self.level_start_time = time.time()

        self._load_level()

        level_num = int(self.level_data.get("level", 1))
        base_hp = 3 + (level_num - 1)
        self.max_hp = hp if hp is not None else base_hp
        self.hp = self.max_hp

        base_time = 120
        self.max_time = max(25, base_time - (level_num - 1) * 8)
        self.time_left = self.max_time

        self._build_ui()
        self._start_timer()

    def _load_level(self):
        with open(resource_path(self.level_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.level_data = data
        level_num = int(data.get("level", 1))
        raw_pairs = data.get("pairs", {})
        all_pairs = list(raw_pairs.items())
        subset_size = min(5 + (level_num - 1) * 2, len(all_pairs))
        chosen = random.sample(all_pairs, subset_size)
        self.word_to_match = dict(chosen)
        self.words = list(self.word_to_match.keys())
        self.matches = list(self.word_to_match.values())

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=C["surface"], height=72, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(side="left", fill="both", expand=True, padx=24)

        lv = self.level_data.get("level", "")
        title_txt = self.level_data.get("title", "")
        ctk.CTkLabel(header_inner,
                     text=f"Level {lv}  ·  {title_txt}",
                     font=("Helvetica", 18, "bold"),
                     text_color=C["text"]).pack(side="left", pady=18)

        ctk.CTkLabel(header_inner,
                     text=self.level_data.get("instructions", "Drag each word onto its matching synonym."),
                     font=("Helvetica", 12),
                     text_color=C["text_dim"]).pack(side="left", padx=20, pady=18)

        quit_btn = ModernButton(
            header, text="✕  Quit", variant="ghost",
            width=110, height=38, font=("Helvetica", 13),
            command=self.master.show_level_select,
        )
        quit_btn.pack(side="right", padx=20, pady=16)

        status_bar = ctk.CTkFrame(self, fg_color=C["panel"], height=52, corner_radius=0)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        sb_inner = ctk.CTkFrame(status_bar, fg_color="transparent")
        sb_inner.pack(expand=True, fill="both")
        sb_inner.columnconfigure(0, weight=1)
        sb_inner.columnconfigure(1, weight=0)
        sb_inner.columnconfigure(2, weight=1)

        self._hp_display = HpDisplay(sb_inner, max_hp=self.max_hp)
        self._hp_display.grid(row=0, column=0, padx=30, pady=8, sticky="w")

        self._progress_label = ctk.CTkLabel(
            sb_inner,
            text=f"0 / {len(self.words)} matched",
            font=("Helvetica", 13, "bold"),
            text_color=C["text_dim"],
        )
        self._progress_label.grid(row=0, column=1, pady=8)

        self._timer_arc = TimerArc(sb_inner, size=38,
                                    bg_color=C["panel"])
        self._timer_arc.grid(row=0, column=2, padx=30, pady=7, sticky="e")

        area = ctk.CTkFrame(self, fg_color=C["bg"])
        area.pack(fill="both", expand=True)
        self._area = area

        self._layout_cards()

    def _layout_cards(self):
        area = self._area
        n = len(self.words)
        max_rows = 9
        v_spacing = 56
        start_y = 30

        shuffled_words = self.words[:]
        random.shuffle(shuffled_words)
        for i, word in enumerate(shuffled_words):
            col = 0 if i < max_rows else 1
            row_idx = i % max_rows
            x = 50 + col * 340
            y = start_y + row_idx * v_spacing
            d = DraggableLabel(area, text=word, drop_handler=self._check_drop,
                               width=290, height=44)
            d.place(x=x, y=y)
            d.original_pos = (x, y)
            d.match_answer = self.word_to_match[word]
            d.lift()
            self.draggables.append(d)

        shuffled_matches = self.matches[:]
        random.shuffle(shuffled_matches)
        for i, match_text in enumerate(shuffled_matches):
            col = 0 if i < max_rows else 1
            row_idx = i % max_rows
            x = 820 + col * 340
            y = start_y + row_idx * v_spacing

            box = ctk.CTkFrame(area, width=270, height=44,
                               fg_color=C["target_box"], corner_radius=10)
            box.place(x=x, y=y)

            inner_lbl = ctk.CTkLabel(box, text=match_text,
                                     font=("Helvetica", 14, "bold"),
                                     text_color=C["text"])
            inner_lbl.place(relx=0.5, rely=0.5, anchor="center")

            box.match_text = match_text
            box.occupied = False
            self.targets.append(box)

    def _start_timer(self):
        self._timer_arc.update_arc(self.time_left, self.max_time)
        if self.time_left > 0:
            self.time_left -= 1
            self.after(1000, self._start_timer)
        else:
            self.hp = 0
            self._show_game_over()

    def _check_drop(self, widget):
        wx = widget.winfo_rootx() + widget.winfo_width() // 2
        wy = widget.winfo_rooty() + widget.winfo_height() // 2

        for box in self.targets:
            bx1 = box.winfo_rootx()
            by1 = box.winfo_rooty()
            bx2 = bx1 + box.winfo_width()
            by2 = by1 + box.winfo_height()
            if bx1 < wx < bx2 and by1 < wy < by2:
                if box.occupied:
                    widget.place(x=widget.original_pos[0], y=widget.original_pos[1])
                    return
                if widget.match_answer == box.match_text:
                    parent = widget.master
                    relx = box.winfo_rootx() - parent.winfo_rootx() + 10
                    rely = box.winfo_rooty() - parent.winfo_rooty() + 4
                    widget.place(x=relx, y=rely)
                    widget.locked = True
                    box.occupied = True
                    widget.configure(fg_color=C["match_ok"])
                    box.configure(fg_color=C["match_ok"])
                    play_sound(resource_path("levels/correct.wav"))
                    matched = sum(1 for d in self.draggables if d.locked)
                    self._progress_label.configure(
                        text=f"{matched} / {len(self.draggables)} matched"
                    )
                    if all(d.locked for d in self.draggables):
                        self._show_score_panel()
                else:
                    widget.configure(fg_color=C["wrong_flash"])
                    self.after(350, lambda w=widget: w.configure(fg_color=C["drag_word"]))
                    widget.place(x=widget.original_pos[0], y=widget.original_pos[1])
                    self.wrong_words.append(widget.cget("text"))
                    self.hp -= 1
                    self._hp_display.set_hp(self.hp)
                    play_sound(resource_path("levels/wrong.wav"))
                    if self.hp <= 0:
                        self._show_game_over()
                return

        widget.place(x=widget.original_pos[0], y=widget.original_pos[1])
        widget.configure(fg_color=C["drag_word"])

    def _show_game_over(self):
        correct = sum(1 for d in self.draggables if d.locked)
        total = len(self.draggables)
        pct = int(round(correct / total * 100)) if total else 0
        ww = [d.cget("text") for d in self.draggables if not d.locked]
        self._show_fail_panel(correct, total, pct, ww)

    def _show_score_panel(self):
        elapsed = int(time.time() - self.level_start_time)
        minutes, seconds = divmod(elapsed, 60)

        correct = sum(1 for d in self.draggables if d.locked)
        total = len(self.draggables)
        pct = int(round(correct / total * 100)) if total else 0

        current_level = int(self.level_data.get("level", 1))
        next_level_num = current_level + 1

        self.master.progress["synonym_progress"]["scores"][current_level] = pct
        if next_level_num not in self.master.progress["synonym_progress"]["unlocked"]:
            self.master.progress["synonym_progress"]["unlocked"].append(next_level_num)
            self.master.progress["highest_level"] = max(
                self.master.progress.get("highest_level", 1), next_level_num
            )
        save_progress(self.master.progress)

        for w in self.winfo_children():
            w.destroy()

        self._build_success_screen(correct, total, pct, f"{minutes}m {seconds}s", [])

    def _build_success_screen(self, correct, total, pct, time_str, wrong_words):
        self.configure(fg_color=C["success_bg"])

        confetti = Confetti(self, width=APP_WIDTH, height=APP_HEIGHT)
        confetti.place(x=0, y=0)

        panel = GlowCard(self, width=680, height=520, corner_radius=24,
                         fg_color=C["card"])
        panel.place(relx=0.5, rely=0.5, anchor="center")

        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")

        ctk.CTkLabel(panel, text=f"Level {level_num}  ·  {level_title}",
                     font=("Helvetica", 14), text_color=C["text_muted"]).pack(pady=(28, 2))
        ctk.CTkLabel(panel, text="🎉  You Passed!",
                     font=("Helvetica", 40, "bold"), text_color=C["accent_glow"]).pack(pady=(4, 4))

        stars_text = "★" * _score_stars(pct) + "☆" * (3 - _score_stars(pct))
        ctk.CTkLabel(panel, text=stars_text,
                     font=("Helvetica", 32), text_color=C["gold"]).pack(pady=(4, 18))

        stats = GlowCard(panel, fg_color=C["surface"], corner_radius=12)
        stats.pack(padx=30, fill="x")

        row = ctk.CTkFrame(stats, fg_color="transparent")
        row.pack(pady=14, padx=20)
        for label, value, color in [
            ("Score", f"{pct}%", C["accent_glow"]),
            ("Correct", f"{correct}/{total}", C["green"]),
            ("HP Left", f"{self.hp}/{self.max_hp}", C["gold"]),
            ("Time", time_str, C["teal"]),
        ]:
            col_frame = ctk.CTkFrame(row, fg_color="transparent", width=130)
            col_frame.pack(side="left", padx=10)
            ctk.CTkLabel(col_frame, text=value, font=("Helvetica", 22, "bold"),
                         text_color=color).pack()
            ctk.CTkLabel(col_frame, text=label, font=("Helvetica", 11),
                         text_color=C["text_muted"]).pack()

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(pady=24)

        current_level = int(self.level_data.get("level", 1))
        next_level_num = current_level + 1
        next_path = resource_path(os.path.join(LEVELS_DIR, f"level{next_level_num}.json"))
        can_next = os.path.exists(next_path)

        def do_retry():
            lnum = int(self.level_data.get("level", 1))
            self.master.show_game(self.level_path, hp=3 + (lnum - 1))

        def do_next():
            if can_next:
                lnum = next_level_num
                self.master.show_game(next_path, hp=3 + (lnum - 1))
            else:
                self.master.show_level_select()

        ModernButton(btn_row, text="Retry", variant="secondary",
                     width=160, height=46, font=("Helvetica", 15),
                     command=do_retry).pack(side="left", padx=8)

        next_btn = ModernButton(btn_row, text="Next Level ▶", variant="primary",
                                width=180, height=46, font=("Helvetica", 15, "bold"),
                                command=do_next)
        next_btn.pack(side="left", padx=8)
        if not can_next:
            next_btn.configure(state="disabled", fg_color=C["text_muted"])

        ModernButton(btn_row, text="Level Select", variant="ghost",
                     width=160, height=46, font=("Helvetica", 15),
                     command=self.master.show_level_select).pack(side="left", padx=8)

    def _show_fail_panel(self, correct, total, pct, wrong_words):
        for w in self.winfo_children():
            w.destroy()

        self.configure(fg_color=C["fail_bg"])

        panel = GlowCard(self, width=700, height=520, corner_radius=24,
                         fg_color=C["surface"])
        panel.place(relx=0.5, rely=0.5, anchor="center")

        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")

        ctk.CTkLabel(panel, text=f"Level {level_num}  ·  {level_title}",
                     font=("Helvetica", 14), text_color=C["text_muted"]).pack(pady=(28, 2))
        ctk.CTkLabel(panel, text="⚠  Try Again",
                     font=("Helvetica", 38, "bold"), text_color=C["red"]).pack(pady=(4, 2))
        ctk.CTkLabel(panel, text="You're close — keep practising!",
                     font=("Helvetica", 14), text_color=C["text_dim"]).pack(pady=(2, 14))

        stats = GlowCard(panel, fg_color=C["card"], corner_radius=12)
        stats.pack(padx=30, fill="x")
        ctk.CTkLabel(stats, text=f"Correct: {correct} / {total}",
                     font=("Helvetica", 18, "bold"),
                     text_color=C["text"]).pack(pady=10)

        if wrong_words:
            wrong_outer = GlowCard(panel, fg_color=C["card"], corner_radius=10)
            wrong_outer.pack(fill="x", padx=28, pady=(14, 4))
            ctk.CTkLabel(wrong_outer, text="Words to review:",
                         font=("Helvetica", 13, "bold"),
                         text_color=C["red"]).pack(anchor="w", padx=12, pady=(8, 4))
            grid_f = ctk.CTkFrame(wrong_outer, fg_color="transparent")
            grid_f.pack(padx=12, pady=(0, 10))
            for idx, w in enumerate(wrong_words[:10]):
                r, c_ = divmod(idx, 3)
                chip = ctk.CTkFrame(grid_f, fg_color=C["red_dim"], corner_radius=8,
                                    width=170, height=34)
                chip.grid(row=r, column=c_, padx=5, pady=5)
                ctk.CTkLabel(chip, text=w, font=("Helvetica", 13, "bold"),
                             text_color=C["text"]).place(relx=0.5, rely=0.5, anchor="center")

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(pady=20)

        def do_retry():
            lnum = int(self.level_data.get("level", 1))
            self.master.show_game(self.level_path, hp=3 + (lnum - 1))

        ModernButton(btn_row, text="Retry Level", variant="primary",
                     width=180, height=46, font=("Helvetica", 15, "bold"),
                     command=do_retry).pack(side="left", padx=10)
        ModernButton(btn_row, text="Level Select", variant="ghost",
                     width=180, height=46, font=("Helvetica", 15),
                     command=self.master.show_level_select).pack(side="left", padx=10)


# ── Definition Match Game ──────────────────────────────────────────────────────

class DefinitionMatchFrame(ctk.CTkFrame):
    def __init__(self, master, level_path):
        super().__init__(master, fg_color=C["bg"])
        self.master = master
        self.level_path = level_path
        self.wrong_words = []
        self.level_start_time = time.time()

        with open(resource_path(level_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.level_data = data

        all_questions = data.get("questions", [])
        random.shuffle(all_questions)
        level_num = int(data.get("level", 1))
        num_questions = 10 + (level_num - 1) * 5
        self.questions = all_questions[:num_questions]
        self.current_index = 0
        self.correct_count = 0

        base_time = 150
        self.max_time = max(25, base_time - (level_num - 1) * 5)
        self.time_left = self.max_time

        self.max_hp = 3 + (level_num - 1)
        self.hp = self.max_hp

        self._build_ui()
        self.show_question()
        self._start_timer()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color=C["surface"], height=72, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(side="left", fill="both", expand=True, padx=24)

        lv = self.level_data.get("level", "")
        title_txt = self.level_data.get("title", "")
        ctk.CTkLabel(header_inner,
                     text=f"Level {lv}  ·  {title_txt}",
                     font=("Helvetica", 18, "bold"),
                     text_color=C["text"]).pack(side="left", pady=18)

        ModernButton(
            header, text="✕  Quit", variant="ghost",
            width=110, height=38, font=("Helvetica", 13),
            command=self.master.show_main_menu,
        ).pack(side="right", padx=20, pady=16)

        status_bar = ctk.CTkFrame(self, fg_color=C["panel"], height=52, corner_radius=0)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        sb_inner = ctk.CTkFrame(status_bar, fg_color="transparent")
        sb_inner.pack(expand=True, fill="both")
        sb_inner.columnconfigure(0, weight=1)
        sb_inner.columnconfigure(1, weight=0)
        sb_inner.columnconfigure(2, weight=1)

        self._hp_display = HpDisplay(sb_inner, max_hp=self.max_hp)
        self._hp_display.grid(row=0, column=0, padx=30, pady=8, sticky="w")

        self._counter_label = ctk.CTkLabel(
            sb_inner,
            text="",
            font=("Helvetica", 13, "bold"),
            text_color=C["text_dim"],
        )
        self._counter_label.grid(row=0, column=1, pady=8)

        self._timer_arc = TimerArc(sb_inner, size=38, bg_color=C["panel"])
        self._timer_arc.grid(row=0, column=2, padx=30, pady=7, sticky="e")

        body = ctk.CTkFrame(self, fg_color=C["bg"])
        body.pack(fill="both", expand=True)

        question_card = GlowCard(body, fg_color=C["card"], corner_radius=18)
        question_card.pack(padx=120, pady=(34, 20), fill="x")

        prompt_lbl = ctk.CTkLabel(question_card, text="What word is being described?",
                                   font=("Helvetica", 13), text_color=C["text_muted"])
        prompt_lbl.pack(pady=(18, 4))

        self.question_label = ctk.CTkLabel(
            question_card,
            text="",
            font=("Helvetica", 22, "bold"),
            text_color=C["text"],
            wraplength=860,
            justify="center",
        )
        self.question_label.pack(pady=(0, 22))

        options_grid = ctk.CTkFrame(body, fg_color="transparent")
        options_grid.pack(pady=10)

        self.option_buttons = []
        for i in range(4):
            btn = ModernButton(
                options_grid,
                text="",
                variant="secondary",
                width=430, height=80,
                font=("Helvetica", 18, "bold"),
            )
            r, c = divmod(i, 2)
            btn.grid(row=r, column=c, padx=16, pady=12)
            self.option_buttons.append(btn)

    def show_question(self):
        if self.current_index >= len(self.questions):
            self.show_score()
            return

        q = self.questions[self.current_index]
        self.question_label.configure(text=q["definition"])

        remaining = len(self.questions) - self.current_index
        self._counter_label.configure(
            text=f"{remaining} / {len(self.questions)} remaining"
        )

        options = q["options"][:]
        random.shuffle(options)
        for i, opt in enumerate(options):
            self.option_buttons[i].configure(
                text=opt,
                fg_color=C["card"],
                command=lambda ch=opt: self.check_answer(ch),
            )
            self.option_buttons[i]._base = C["card"]
            self.option_buttons[i]._hover_target = C["card_hover"]

    def check_answer(self, selected):
        q = self.questions[self.current_index]
        correct = q["answer"]

        for btn in self.option_buttons:
            btn.configure(state="disabled")

        if selected == correct:
            self.correct_count += 1
            for btn in self.option_buttons:
                if btn.cget("text") == correct:
                    btn.configure(fg_color=C["green"])
            play_sound(resource_path("levels/correct.wav"))
            self.after(600, self._next_question)
        else:
            self.hp -= 1
            self._hp_display.set_hp(self.hp)
            self.wrong_words.append(correct)
            for btn in self.option_buttons:
                if btn.cget("text") == selected:
                    btn.configure(fg_color=C["red"])
                elif btn.cget("text") == correct:
                    btn.configure(fg_color=C["green"])
            play_sound(resource_path("levels/wrong.wav"))
            if self.hp <= 0:
                self.after(700, self.show_score)
                return
            self.after(800, self._next_question)

    def _next_question(self):
        for btn in self.option_buttons:
            btn.configure(state="normal", fg_color=C["card"])
        self.current_index += 1
        self.show_question()

    def _start_timer(self):
        self._timer_arc.update_arc(self.time_left, self.max_time)
        if self.time_left > 0:
            self.time_left -= 1
            self.after(1000, self._start_timer)
        else:
            self.show_score()

    def show_score(self):
        correct = self.correct_count
        total = len(self.questions)
        pct = int(correct / total * 100) if total else 0

        self.master.progress["definition_progress"]["scores"][self.level_data["level"]] = pct
        if pct >= 50:
            next_level = int(self.level_data["level"]) + 1
            if next_level not in self.master.progress["definition_progress"]["unlocked"]:
                self.master.progress["definition_progress"]["unlocked"].append(next_level)
        save_progress(self.master.progress)

        if pct >= 50:
            self._show_success(correct, total, pct)
        else:
            self._show_fail(correct, total, pct)

    def _show_success(self, correct, total, pct):
        elapsed = int(time.time() - self.level_start_time)
        minutes, seconds = divmod(elapsed, 60)

        for w in self.winfo_children():
            w.destroy()

        self.configure(fg_color=C["success_bg"])

        confetti = Confetti(self, width=APP_WIDTH, height=APP_HEIGHT)
        confetti.place(x=0, y=0)

        panel = GlowCard(self, width=680, height=500, corner_radius=24, fg_color=C["card"])
        panel.place(relx=0.5, rely=0.5, anchor="center")

        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")

        ctk.CTkLabel(panel, text=f"Level {level_num}  ·  {level_title}",
                     font=("Helvetica", 14), text_color=C["text_muted"]).pack(pady=(28, 2))
        ctk.CTkLabel(panel, text="🎉  You Passed!",
                     font=("Helvetica", 40, "bold"), text_color=C["accent_glow"]).pack(pady=(4, 2))

        stars_text = "★" * _score_stars(pct) + "☆" * (3 - _score_stars(pct))
        ctk.CTkLabel(panel, text=stars_text,
                     font=("Helvetica", 30), text_color=C["gold"]).pack(pady=(2, 16))

        stats = GlowCard(panel, fg_color=C["surface"], corner_radius=12)
        stats.pack(padx=30, fill="x")

        row = ctk.CTkFrame(stats, fg_color="transparent")
        row.pack(pady=14, padx=20)
        for label, value, color in [
            ("Score", f"{pct}%", C["accent_glow"]),
            ("Correct", f"{correct}/{total}", C["green"]),
            ("Time", f"{minutes}m {seconds}s", C["teal"]),
        ]:
            col_frame = ctk.CTkFrame(row, fg_color="transparent", width=160)
            col_frame.pack(side="left", padx=12)
            ctk.CTkLabel(col_frame, text=value, font=("Helvetica", 22, "bold"),
                         text_color=color).pack()
            ctk.CTkLabel(col_frame, text=label, font=("Helvetica", 11),
                         text_color=C["text_muted"]).pack()

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(pady=22)

        current_level = int(self.level_data.get("level", 1))
        next_level_num = current_level + 1
        next_path = resource_path(
            os.path.join(LEVELS_DEFINITIONS_DIR, f"academic{next_level_num}.json")
        )
        can_next = os.path.exists(next_path)

        def do_retry():
            self.master.show_definition_mode(self.level_path)

        def do_next():
            if can_next:
                self.master.show_definition_mode(next_path)
            else:
                self.master.show_definition_level_select()

        ModernButton(btn_row, text="Retry", variant="secondary",
                     width=150, height=46, font=("Helvetica", 15),
                     command=do_retry).pack(side="left", padx=8)

        next_btn = ModernButton(btn_row, text="Next Level ▶", variant="primary",
                                width=180, height=46, font=("Helvetica", 15, "bold"),
                                command=do_next)
        next_btn.pack(side="left", padx=8)
        if not can_next:
            next_btn.configure(state="disabled", fg_color=C["text_muted"])

        ModernButton(btn_row, text="Level Select", variant="ghost",
                     width=160, height=46, font=("Helvetica", 15),
                     command=self.master.show_definition_level_select).pack(side="left", padx=8)

    def _show_fail(self, correct, total, pct):
        for w in self.winfo_children():
            w.destroy()

        self.configure(fg_color=C["fail_bg"])

        panel = GlowCard(self, width=700, height=500, corner_radius=24, fg_color=C["surface"])
        panel.place(relx=0.5, rely=0.5, anchor="center")

        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")

        ctk.CTkLabel(panel, text=f"Level {level_num}  ·  {level_title}",
                     font=("Helvetica", 14), text_color=C["text_muted"]).pack(pady=(28, 2))
        ctk.CTkLabel(panel, text="⚠  Try Again",
                     font=("Helvetica", 38, "bold"), text_color=C["red"]).pack(pady=(4, 2))
        ctk.CTkLabel(panel, text="Keep going — you'll get it!",
                     font=("Helvetica", 14), text_color=C["text_dim"]).pack(pady=(2, 14))

        stats = GlowCard(panel, fg_color=C["card"], corner_radius=12)
        stats.pack(padx=30, fill="x")
        ctk.CTkLabel(stats, text=f"Correct: {correct} / {total}",
                     font=("Helvetica", 18, "bold"), text_color=C["text"]).pack(pady=10)

        if self.wrong_words:
            wrong_outer = GlowCard(panel, fg_color=C["card"], corner_radius=10)
            wrong_outer.pack(fill="x", padx=28, pady=(12, 4))
            ctk.CTkLabel(wrong_outer, text="Words to review:",
                         font=("Helvetica", 13, "bold"), text_color=C["red"]).pack(
                             anchor="w", padx=12, pady=(8, 4))
            grid_f = ctk.CTkFrame(wrong_outer, fg_color="transparent")
            grid_f.pack(padx=12, pady=(0, 10))
            for idx, w in enumerate(self.wrong_words[:12]):
                r, c_ = divmod(idx, 3)
                chip = ctk.CTkFrame(grid_f, fg_color=C["red_dim"], corner_radius=8,
                                    width=170, height=34)
                chip.grid(row=r, column=c_, padx=5, pady=5)
                ctk.CTkLabel(chip, text=w, font=("Helvetica", 13, "bold"),
                             text_color=C["text"]).place(relx=0.5, rely=0.5, anchor="center")

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(pady=20)

        ModernButton(btn_row, text="Retry Level", variant="primary",
                     width=180, height=46, font=("Helvetica", 15, "bold"),
                     command=lambda: self.master.show_definition_mode(self.level_path)).pack(
                         side="left", padx=10)
        ModernButton(btn_row, text="Level Select", variant="ghost",
                     width=180, height=46, font=("Helvetica", 15),
                     command=self.master.show_definition_level_select).pack(side="left", padx=10)


# ── App Controller ─────────────────────────────────────────────────────────────

class EngageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.geometry(f"{screen_width}x{screen_height}")
        self.resizable(False, False)
        self.title("EngageEnglish")
        self.attributes("-fullscreen", True)
        self.focus_force()
        self.lift()
        self.configure(fg_color=C["bg"])

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.progress = load_progress()
        self.current_frame = None
        self.show_main_menu()

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def switch_frame(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(fill="both", expand=True)

    def show_main_menu(self):
        self.switch_frame(MainMenuFrame)

    def show_game_modes(self):
        self.switch_frame(GameModesFrame)

    def show_level_select(self):
        self.switch_frame(LevelSelectFrame)

    def show_definition_level_select(self):
        self.switch_frame(DefinitionLevelSelectFrame)

    def show_game(self, level_path, hp=None):
        self.switch_frame(GameFrame, level_path, hp)

    def show_definition_mode(self, level_path):
        self.switch_frame(DefinitionMatchFrame, level_path)

    def scale_font(self, base_size):
        return int(self.screen_height * (base_size / 1080))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _scan_levels(directory):
    levels = []
    if os.path.isdir(directory):
        for fn in sorted(os.listdir(directory)):
            if fn.lower().endswith(".json") and "progress" not in fn.lower():
                try:
                    with open(resource_path(os.path.join(directory, fn)),
                              "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    levels.append((
                        data.get("level", 0),
                        data.get("title", "Untitled"),
                        os.path.join(directory, fn),
                    ))
                except Exception:
                    continue
    levels.sort(key=lambda x: x[0])
    return levels


def _score_stars(pct):
    if pct >= 90:
        return 3
    if pct >= 70:
        return 2
    if pct >= 50:
        return 1
    return 0


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.isdir(LEVELS_DIR):
        os.makedirs(LEVELS_DIR, exist_ok=True)
    app = EngageApp()
    app.mainloop()
