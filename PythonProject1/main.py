# main.py
# EngageEnglish v2, 11/11/2025, last modified 2/8/2026, 10:07 PM
# Requirements: pip install customtkinter

import os, sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller .exe"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ✅ Persistent progress file path (same folder as exe)
APP_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
PROGRESS_FILE = os.path.join(APP_DIR, "progress.json")

import time
import customtkinter as ctk
import json
import winsound
import os
import random
import tkinter as tk


# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # try "green" or "dark-blue"

# ---------- UI Constants ----------
APP_BG       = "#1E1E2E"   # dark background
PANEL_BG     = "#2A2A3D"   # dark panels
CARD_BG      = "#3B3B4F"   # card surfaces
BUTTON_BG    = "#4C4C6A"   # button base
BUTTON_HOVER = "#6A6A8C"   # button hover
TEXT         = "#FFFFFF"   # bright text
MUTED        = "#AAAAAA"   # muted text

FONTS = {
    "title": ("Poppins", 48, "bold"),
    "subtitle": ("Nunito", 20),
    "button": ("Poppins", 20, "bold")
}



LEVELS_DIR = "levels"
LEVELS_DEFINITIONS_DIR = "levels_definitions"
FONT_SELFIE  = resource_path("assets/fonts/Selfie_Black.otf")

APP_WIDTH = 1600
APP_HEIGHT = 900

def play_sound(file):
    try:
        winsound.PlaySound(file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except:
        pass  # ignore errors if file is missing

# ---------- Utility: progress handling ----------
def load_progress():
    default = {
        "synonym_progress": {
            "unlocked": [1],
            "scores": {}
        },
        "definition_progress": {
            "unlocked": [1],
            "scores": {}
        },
        "highest_level": 1,
        "last_played": 1,
        "hp": 3
    }
    ...


    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f)
        return default
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # ensure all keys exist
        for key, val in default.items():
            if key not in data:
                data[key] = val
    except Exception:
        data = default
    return data



def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f)

# ---------- Game Modes ----------
class GameModesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["background"])
        self.master = master

        # Title
        ctk.CTkLabel(
            self,
            text="Choose Game Mode",
            font=("Selfie", 45),
            text_color=COLORS["text"]
        ).pack(pady=(60, 20))

        # Subtitle
        ctk.CTkLabel(
            self,
            text="Pick a mode to begin!",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"]
        ).pack(pady=(0, 40))

        # Card container
        card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=16)
        card.pack(pady=40, padx=40)

        # Synonym mode
        StyledButton(
            card,
            text="🔗 Word Synonyms",
            width=320, height=60,
            font=FONTS["button"],
            command=self.master.show_level_select
        ).pack(pady=20)

        # Definition mode
        StyledButton(
            card,
            text="📖 Word Definitions",
            width=320, height=60,
            font=FONTS["button"],
            command=self.master.show_definition_level_select
        ).pack(pady=20)

        # Back button
        StyledButton(
            card,
            text="Back to Menu",
            width=280, height=52,
            font=FONTS["button"],
            command=self.master.show_main_menu
        ).pack(pady=20)




class DefinitionMatchFrame(ctk.CTkFrame):
    def __init__(self, master, level_path):
        super().__init__(master, fg_color=APP_BG)
        self.master = master
        self.level_path = level_path
        self.wrong_words = []
        self.level_start_time = time.time()

        # Load questions from JSON
        with open(resource_path(level_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.level_data = data
        self.questions = data.get("questions", [])
        random.shuffle(self.questions)
        self.current_index = 0
        self.correct_count = 0

        self.level_data = data
        all_questions = data.get("questions", [])
        random.shuffle(all_questions)

        level_num = int(self.level_data.get("level", 1))
        # Start at 10, increase by 5 each level
        num_questions = 10 + (level_num - 1) * 5
        self.questions = all_questions[:num_questions]

        self.current_index = 0
        self.correct_count = 0

        # Title
        ctk.CTkLabel(
            self,
            text=f"Level {data.get('level', '')}: {data.get('title', '')}",
            font=("Helvetica", 28, "bold"),
            text_color=TEXT
        ).pack(pady=20)

        # Question card
        question_card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)
        question_card.pack(pady=20, padx=40, fill="x")

        self.question_label = ctk.CTkLabel(
            question_card,
            text="",
            font=("Helvetica", 26, "bold"),
            text_color=TEXT,
            wraplength=800,
            justify="center"
        )
        self.question_label.pack(pady=20)

        # Item counter (words left)
        self.item_counter_label = ctk.CTkLabel(
            self,
            text=f"Remaining: {len(self.questions) - self.current_index}/{len(self.questions)}",
            font=("Helvetica", 16, "bold"),
            text_color=TEXT
        )
        self.item_counter_label.pack(pady=(5, 10))

        # Options grid
        options_frame = ctk.CTkFrame(self, fg_color=PANEL_BG, corner_radius=12)
        options_frame.pack(pady=30)

        self.option_buttons = []
        # In __init__:
        for i in range(4):
            btn = StyledButton(
                options_frame,
                text="",
                width=400, height=80,
                font=("Poppins", 20, "bold")
                # ❌ no command here
            )
            row, col = divmod(i, 2)
            btn.grid(row=row, column=col, padx=30, pady=30)
            self.option_buttons.append(btn)

        self.show_question()

        # Quit / Return to Menu button
        quit_frame = ctk.CTkFrame(self, fg_color=APP_BG)
        quit_frame.pack(pady=20)

        StyledButton(
            quit_frame,
            text="Quit",
            width=240, height=52,
            command=self.master.show_main_menu
        ).pack()


        level_num = int(self.level_data.get("level", 1))
        base_time = 150
        self.max_time = max(20, base_time - (level_num - 1) * 5)
        self.time_left = self.max_time

        # --- Timer circle (above HP bar) ---
        self.canvas = tk.Canvas(self, width=100, height=100,
                                bg=self.cget("fg_color"),
                                highlightthickness=0)
        self.canvas.configure(background=self.cget("fg_color"))
        self.canvas.pack(pady=(10, 0))

        self.arc = self.canvas.create_arc(8, 8, 92, 92, start=90, extent=360,
                                          style="arc", outline="red", width=6)
        self.clock_text = self.canvas.create_text(50, 50, text=f"{self.time_left}",
                                                  font=("Helvetica", 12, "bold"), fill="red")

        # --- HP bar (below timer) ---
        level_num = int(self.level_data.get("level", 1))

        # Scale HP per level: base 3 + 1 per level
        self.max_hp = 3 + (level_num - 1)
        self.hp = self.max_hp  # start full each level


        hp_frame = ctk.CTkFrame(self, fg_color="#FF80AB", corner_radius=8)
        hp_frame.pack(pady=(5, 10))

        self.hp_label = ctk.CTkLabel(hp_frame, text=f"HP: {self.hp}/{self.max_hp}",
                                     font=("Helvetica", 25, "bold"), text_color="#228B22")
        self.hp_label.pack(side="left", padx=6)

        self.hp_bar = ctk.CTkProgressBar(hp_frame, width=265, height=20)
        self.hp_bar.pack(side="left", padx=6)
        self.hp_bar.set(self.hp / self.max_hp)

        # Start timer loop
        self.update_timer_circle()

    def update_timer_circle(self):
        if self.time_left > 0:
            self.time_left -= 1

            # Update arc extent (shrinks as time decreases)
            angle = (self.time_left / self.max_time) * 360
            self.canvas.itemconfig(self.arc, extent=angle)

            # Update center text
            self.canvas.itemconfig(self.clock_text, text=f"{self.time_left}")

            # Schedule next tick
            self.after(1000, self.update_timer_circle)
        else:
            self.show_score()
            return

    def show_question(self):
        if self.current_index >= len(self.questions):
            self.show_score()
            return

        q = self.questions[self.current_index]
        self.question_label.configure(
            text=f"What word is being described here?\n\n\n{q['definition']}"
        )

        # Shuffle options
        options = q["options"][:]
        random.shuffle(options)

        # Assign shuffled options to buttons
        for i, opt in enumerate(options):
            self.option_buttons[i].configure(
                text=opt,
                command=lambda choice=opt: self.check_answer(choice)
            )


        # Update item counter
        remaining = len(self.questions) - self.current_index
        total = len(self.questions)
        self.item_counter_label.configure(text=f"Remaining: {remaining}/{total}")


    def update_hp_bar(self):
        ratio = max(self.hp / self.max_hp, 0)
        self.hp_bar.set(ratio)
        self.hp_label.configure(text=f"HP: {self.hp}/{self.max_hp}")

    def check_answer(self, selected):
        q = self.questions[self.current_index]
        if selected == q["answer"]:
            self.correct_count += 1
            play_sound(resource_path("levels/correct.wav"))
        else:
            self.hp -= 1
            self.update_hp_bar()
            play_sound(resource_path("levels/wrong.wav"))
            # ✅ record the missed word
            self.wrong_words.append(q["answer"])

        if self.hp <= 0:
            self.show_score()
            return

        self.current_index += 1
        if self.current_index < len(self.questions):
            self.show_question()
        else:
            self.show_score()

    def show_score(self):
        correct = self.correct_count
        total = len(self.questions)
        pct = int((correct / total) * 100)

        # Save progress
        self.master.progress["definition_progress"]["scores"][self.level_data["level"]] = pct
        if pct >= 50:
            next_level = self.level_data["level"] + 1
            if next_level not in self.master.progress["definition_progress"]["unlocked"]:
                self.master.progress["definition_progress"]["unlocked"].append(next_level)
        save_progress(self.master.progress)

        # ✅ use the tracked wrong words directly
        wrong_words = self.wrong_words

        # Route to proper screen
        if pct >= 50:
            self.show_definition_success_screen(correct, total, pct, wrong_words)
        else:
            self.show_definition_fail_screen(correct, total, pct, wrong_words)


    def show_definition_fail_screen(self, correct, total, pct, wrong_words):
            # Clear current UI
            for widget in self.winfo_children():
                widget.destroy()

            self.configure(fg_color="#121212")
            panel = ctk.CTkFrame(self, fg_color="#1E1A1A", corner_radius=0)
            panel.pack(fill="both", expand=True)

            level_num = int(self.level_data.get("level", 1))
            level_title = self.level_data.get("title", "")
            ctk.CTkLabel(panel, text=f"Level {level_num}: {level_title}",
                         font=("Helvetica", 22, "bold"), text_color="#FF8888").pack(pady=(8, 4))
            ctk.CTkLabel(panel, text="⚠️ Try Again",
                         font=("Helvetica", 34, "bold"), text_color="#FF5555").pack(pady=(12, 6))
            ctk.CTkLabel(panel, text="You’re close — keep practicing!",
                         font=("Helvetica", 14), text_color="#DD9999").pack(pady=(0, 12))

            stats_frame = ctk.CTkFrame(panel, fg_color="#2A1A1A", corner_radius=8)
            stats_frame.pack(pady=12, padx=20, fill="x")
            ctk.CTkLabel(stats_frame, text=f"Correct: {correct} / {total}",
                         font=("Helvetica", 16, "bold"), text_color="#FFBBBB").pack(pady=10)

            if wrong_words:
                bad_frame = ctk.CTkFrame(panel, fg_color="#3A1A1A", corner_radius=8)
                bad_frame.pack(fill="x", padx=18, pady=(12, 16))
                ctk.CTkLabel(bad_frame, text="Words you got wrong:",
                             font=("Helvetica", 14, "bold"), text_color="#FFAAAA").pack(anchor="w", padx=10,
                                                                                        pady=(8, 4))
                grid = ctk.CTkFrame(bad_frame, fg_color="#3A1A1A")
                grid.pack(padx=10, pady=(4, 12))
                for idx, w in enumerate(wrong_words):
                    r, c = divmod(idx, 2)
                    card = ctk.CTkFrame(grid, width=260, height=56, fg_color="#5A2A2A", corner_radius=8)
                    card.grid(row=r, column=c, padx=8, pady=8)
                    ctk.CTkLabel(card, text=w, font=("Helvetica", 14, "bold"),
                                 text_color="#FFDDDD").place(relx=0.5, rely=0.5, anchor="center")

            btn_frame = ctk.CTkFrame(panel, fg_color="#1E1A1A")
            btn_frame.pack(pady=(12, 20))

            StyledButton(btn_frame, text="Retry Level", width=260, height=52,
                         command=lambda: self.master.show_definition_mode(self.level_path)).pack(side="left", padx=16)
            StyledButton(btn_frame, text="Return to Level Selection", width=220, height=48,
                         command=self.master.show_definition_level_select).pack(side="left", padx=16)

    def show_definition_success_screen(self, correct, total, pct, wrong_words):
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(fg_color="#F48FB1")
        panel = ctk.CTkFrame(self, fg_color="#F48FB1", corner_radius=12)
        panel.pack(fill="both", expand=True, padx=40, pady=40)

        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")
        ctk.CTkLabel(panel, text=f"Level {level_num}: {level_title}",
                     font=("Helvetica", 24, "bold"), text_color="#880E4F").pack(pady=(8, 4))

        ctk.CTkLabel(panel, text="🎉 You Passed! 🎉",
                     font=("Helvetica", 34, "bold"), text_color="#AD1457").pack(pady=(12, 10))
        ctk.CTkLabel(panel, text="You did well! Keep it up!",
                     font=("Helvetica", 14), text_color="#6A1B9A").pack(pady=(0, 12))

        # Stats frame
        stats_frame = ctk.CTkFrame(panel, fg_color="#F8BBD0", corner_radius=8)
        stats_frame.pack(pady=12, padx=20, fill="x")

        elapsed = int(time.time() - self.level_start_time)
        minutes, seconds = divmod(elapsed, 60)

        ctk.CTkLabel(stats_frame, text=f"Correct: {correct}", font=("Helvetica", 16, "bold"),
                     text_color="#880E4F").grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=f"Total: {total}", font=("Helvetica", 16, "bold"),
                     text_color="#880E4F").grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkLabel(stats_frame, text=f"Score: {pct}%", font=("Helvetica", 16, "bold"),
                     text_color="#880E4F").grid(row=0, column=2, padx=20, pady=10)

        ctk.CTkLabel(stats_frame, text=f"Time: {minutes}m {seconds}s", font=("Helvetica", 16, "bold"),
                     text_color="#880E4F").grid(row=1, column=0, columnspan=3, pady=10)

        # Buttons frame
        btn_frame = ctk.CTkFrame(panel, fg_color="#F48FB1")
        btn_frame.pack(pady=(30, 20))

        def retry_level():
            self.master.show_definition_mode(self.level_path)

        def next_level():
            current_level = int(self.level_data.get("level", 1))
            next_level_num = current_level + 1
            next_path = resource_path(os.path.join(LEVELS_DEFINITIONS_DIR, f"academic{next_level_num}.json"))
            if os.path.exists(next_path):
                if next_level_num not in self.master.progress.get("unlocked", []):
                    self.master.progress.setdefault("unlocked", []).append(next_level_num)
                    save_progress(self.master.progress)
                self.master.show_definition_mode(next_path)
            else:
                tk.messagebox.showinfo("No Next Level", f"academic{next_level_num}.json not found.")
                self.master.show_definition_level_select()

        def to_menu():
            self.master.show_definition_level_select()

        ctk.CTkButton(btn_frame, text="Retry Level", width=220, height=52,
                      fg_color="#2B2B2B", text_color="#FFFFFF",
                      command=retry_level).pack(side="left", padx=16)

        next_btn = ctk.CTkButton(btn_frame, text="Next Level", width=220, height=52,
                                 fg_color="#2B2B2B", text_color="#FFFFFF",
                                 command=next_level)
        next_btn.pack(side="left", padx=16)

        ctk.CTkButton(btn_frame, text="Return to Level Selection", width=260, height=52,
                      fg_color="#2B2B2B", text_color="#FFFFFF",
                      command=to_menu).pack(side="left", padx=16)


# ---------- Definition Level Selection ----------
class DefinitionLevelSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=APP_BG)

        # Header
        ctk.CTkLabel(
            self,
            text="Definition Levels",
            font=FONTS["title"],
            text_color=TEXT
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            self,
            text="Unlock levels step by step",
            font=FONTS["subtitle"],
            text_color=MUTED
        ).pack(pady=(0, 20))

        # Full-width scrollable grid
        panel = ctk.CTkScrollableFrame(self, fg_color=APP_BG, corner_radius=0)
        panel.pack(padx=40, pady=20, fill="both", expand=True)

        levels = []
        if os.path.isdir("levels_definitions"):
            for fn in sorted(os.listdir("levels_definitions")):
                if fn.lower().endswith(".json"):
                    try:
                        with open(resource_path(os.path.join("levels_definitions", fn)), "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        levels.append((data.get("level", 0),
                                       data.get("title", "Untitled"),
                                       os.path.join("levels_definitions", fn)))
                    except Exception:
                        continue

        if not levels:
            ctk.CTkLabel(panel, text="No definition levels found", text_color=TEXT).pack(pady=20)
        else:
            for i, (level_num, title, path) in enumerate(levels):
                unlocked = level_num in master.progress["definition_progress"]["unlocked"]

                # Card outer (grid stretches full width)
                card_outer = ctk.CTkFrame(panel, fg_color=PANEL_BG, corner_radius=16)
                r, c = divmod(i, 4)  # 4 cards per row to use space better
                card_outer.grid(row=r, column=c, padx=20, pady=20, sticky="nsew")

                # Card inner
                card_inner = ctk.CTkFrame(card_outer, fg_color=CARD_BG, corner_radius=12,
                                          width=280, height=140)
                card_inner.pack(padx=6, pady=6, fill="both", expand=True)

                # Title
                ctk.CTkLabel(
                    card_inner,
                    text=f"Level {level_num} — {title}",
                    font=FONTS["subtitle"],
                    text_color=TEXT
                ).pack(pady=(12, 6))

                # Play / Locked state
                if unlocked:
                    StyledButton(
                        card_inner,
                        text="▶ Play",
                        width=200, height=44,
                        font=FONTS["button"],
                        command=lambda p=path: master.show_definition_mode(p)
                    ).pack(pady=10)
                else:
                    ctk.CTkLabel(
                        card_inner,
                        text="🔒 Locked",
                        font=FONTS["button"],
                        text_color=MUTED
                    ).pack(pady=10)

        # Back button
        StyledButton(
            self,
            text="⬅ Back to Menu",
            width=220, height=48,
            font=FONTS["button"],
            command=master.show_main_menu
        ).pack(pady=20)




class EngageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Detect monitor resolution dynamically
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Lock app to detected resolution
        self.geometry(f"{screen_width}x{screen_height}")
        self.resizable(False, False)
        self.title("EngageEnglish")
        self.attributes("-fullscreen", True)
        self.focus_force()
        self.lift()
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        self.configure(fg_color=APP_BG)

        # Store resolution for scaling
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Progress handling
        self.progress = load_progress()
        self.current_frame = None
        self.show_main_menu()

    def scale_font(self, base_size):
        #Scale font size relative to screen height.
        return int(self.screen_height * (base_size / 1080))  #1080p = design baseline

    def toggle_fullscreen(self, event=None):
        current = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current)

    def switch_frame(self, frame_class, *args):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args)
        self.current_frame.pack(fill="both", expand=True)

    def show_main_menu(self):
        self.switch_frame(MainMenuFrame)

    def show_game(self, level_path, hp=None):
        self.switch_frame(GameFrame, level_path, hp)

    def show_level_select(self):
        self.switch_frame(LevelSelectFrame)

    def show_definition_mode(self, level_path):
        self.switch_frame(DefinitionMatchFrame, level_path)

    def show_game_modes(self):
        self.switch_frame(GameModesFrame)

    def show_definition_level_select(self):
        self.switch_frame(DefinitionLevelSelectFrame)

    def show_definition_level_select(self):
        self.switch_frame(DefinitionLevelSelectFrame)


class StyledButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=14,
            fg_color="#2B2B2B",       # default dark gray
            text_color="#FFFFFF",     # white text
            hover_color="#CE93D8",    # cyan glow on hover
            **kwargs
        )
        self.default_color = "#2B2B2B"
        self.hover_target = "#CE93D8"   # neon cyan
        self.steps = 20
        self.current_step = 0
        self.hovering = False
        self.animating = False

        # Bind hover events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def _fade_color(self, start, end, step, total):
        s = tuple(int(start[i:i+2], 16) for i in (1, 3, 5))
        e = tuple(int(end[i:i+2], 16) for i in (1, 3, 5))
        ratio = step / total
        rgb = tuple(int(s[i] + (e[i]-s[i]) * ratio) for i in range(3))
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def animate(self):
        if self.hovering:
            if self.current_step < self.steps:
                self.current_step += 1
        else:
            if self.current_step > 0:
                self.current_step -= 1

        # Smooth glow effect
        new_color = self._fade_color(self.default_color, self.hover_target,
                                     self.current_step, self.steps)
        self.configure(fg_color=new_color)

        if (self.hovering and self.current_step < self.steps) or \
           (not self.hovering and self.current_step > 0):
            self.after(30, self.animate)
        else:
            self.animating = False

    def on_enter(self, event=None):
        self.hovering = True
        if not self.animating:
            self.animating = True
            self.animate()

    def on_leave(self, event=None):
        self.hovering = False
        if not self.animating:
            self.animating = True
            self.animate()




class AnimatedBackground(ctk.CTkFrame):
    def __init__(self, master, colors=None, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors or ["#FF80AB", "#80DEEA", "#FFF176", "#81D4FA", "#CE93D8"]
        self.current_index = 0
        self.next_index = 1
        self.steps = 100
        self.step = 0
        self.animate_bg()

    def _fade_color(self, start, end, step, total):
        s = tuple(int(start[i:i+2], 16) for i in (1, 3, 5))
        e = tuple(int(end[i:i+2], 16) for i in (1, 3, 5))
        ratio = step / total
        rgb = tuple(int(s[i] + (e[i]-s[i]) * ratio) for i in range(3))
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def animate_bg(self):
        new_color = self._fade_color(self.colors[self.current_index],
                                     self.colors[self.next_index],
                                     self.step, self.steps)
        self.configure(fg_color=new_color)

        # Update child canvases to match
        for child in self.winfo_children():
            if isinstance(child, tk.Canvas):
                child.configure(bg=new_color)

        self.step += 1
        if self.step > self.steps:
            self.step = 0
            self.current_index = self.next_index
            self.next_index = (self.next_index + 1) % len(self.colors)

        self.after(50, self.animate_bg)


class AnimatedPanel(ctk.CTkFrame):
    def __init__(self, master, colors=None, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = colors or ["#FF80AB", "#80DEEA", "#FFF176", "#81D4FA", "#CE93D8"]
        self.current_index = 0
        self.next_index = 1
        self.steps = 100
        self.step = 0
        self.animate_bg()

    def _fade_color(self, start, end, step, total):
        s = tuple(int(start[i:i+2], 16) for i in (1, 3, 5))
        e = tuple(int(end[i:i+2], 16) for i in (1, 3, 5))
        ratio = step / total
        rgb = tuple(int(s[i] + (e[i]-s[i]) * ratio) for i in range(3))
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def animate_bg(self):
        new_color = self._fade_color(self.colors[self.current_index],
                                     self.colors[self.next_index],
                                     self.step, self.steps)
        self.configure(fg_color=new_color)

        self.step += 1
        if self.step > self.steps:
            self.step = 0
            self.current_index = self.next_index
            self.next_index = (self.next_index + 1) % len(self.colors)

        self.after(50, self.animate_bg)






# ---------- UI Constants ----------
COLORS = {
    "background": "#1E1E2E",
    "panel": "#2A2A3D",
    "card": "#3B3B4F",
    "button": "#4C4C6A",
    "hover": "#6A6A8C",
    "text": "#FFFFFF",
    "muted": "#AAAAAA"
}

FONTS = {
    "title": ("Poppins", 48, "bold"),
    "subtitle": ("Nunito", 20),
    "button": ("Poppins", 20, "bold")
}

# ---------- Main Menu ----------
class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["background"])

        # Title
        ctk.CTkLabel(
            self,
            text="EngageEnglish",
            font=("Selfie", 80),
            text_color=COLORS["text"]
        ).pack(pady=(80, 20))

        # Subtitle
        ctk.CTkLabel(
            self,
            text="Developed by @wawa.jett_wonyoung",
            font=FONTS["subtitle"],
            text_color=COLORS["muted"]
        ).pack(pady=(0, 40))

        # Control card
        card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=16)
        card.pack(pady=40, padx=40)

        StyledButton(
            card,
            text="▶ Play",
            width=300, height=60,
            font=FONTS["button"],
            command=master.show_game_modes
        ).pack(pady=20)

        StyledButton(
            card,
            text="❌ Quit",
            width=300, height=60,
            font=FONTS["button"],
            command=master.destroy
        ).pack(pady=20)

        # Footer
        ctk.CTkLabel(
            self,
            text="EngageEnglish, 2025-2026",
            font=("Nunito", 14),
            text_color=COLORS["muted"]
        ).pack(side="bottom", pady=20)




# ---------- Level Selection ----------
class LevelSelectFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=APP_BG)

        # Header
        ctk.CTkLabel(
            self,
            text="Select Level",
            font=FONTS["title"],
            text_color=TEXT
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            self,
            text="Complete a level to unlock the next one",
            font=FONTS["subtitle"],
            text_color=MUTED
        ).pack(pady=(0, 20))

        # Scrollable panel
        panel = ctk.CTkScrollableFrame(self, fg_color=CARD_BG, corner_radius=12)
        panel.pack(padx=32, pady=12, fill="both", expand=True)

        levels = []
        if os.path.isdir("levels"):
            for fn in sorted(os.listdir("levels")):
                if fn.lower().endswith(".json"):
                    try:
                        with open(resource_path(os.path.join("levels", fn)), "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        levels.append((data.get("level", 0),
                                       data.get("title", "Untitled"),
                                       os.path.join("levels", fn)))
                    except Exception:
                        continue

        if not levels:
            ctk.CTkLabel(panel, text="No synonym levels found", text_color=TEXT).pack(pady=20)
        else:
            for i, (level_num, title, path) in enumerate(levels):
                unlocked = level_num in master.progress["synonym_progress"]["unlocked"]

                # Card outer
                card_outer = ctk.CTkFrame(panel, fg_color=PANEL_BG, corner_radius=16)
                r, c = divmod(i, 3)
                card_outer.grid(row=r, column=c, padx=24, pady=24, sticky="nsew")

                # Card inner
                card_inner = ctk.CTkFrame(card_outer, fg_color=CARD_BG, corner_radius=12,
                                          width=360, height=160)
                card_inner.pack(padx=6, pady=6, fill="both", expand=True)

                # Title
                ctk.CTkLabel(
                    card_inner,
                    text=f"Level {level_num} — {title}",
                    font=FONTS["subtitle"],
                    text_color=TEXT
                ).pack(pady=(12, 6))

                # Play / Locked state
                if unlocked:
                    StyledButton(
                        card_inner,
                        text="▶ Play",
                        width=240, height=48,
                        font=FONTS["button"],
                        command=lambda p=path: master.show_game(p)
                    ).pack(pady=8)
                else:
                    ctk.CTkLabel(
                        card_inner,
                        text="🔒 Locked",
                        font=FONTS["button"],
                        text_color=MUTED
                    ).pack(pady=8)

        # Back button
        StyledButton(
            self,
            text="Back to Menu",
            width=220, height=48,
            font=FONTS["button"],
            command=master.show_main_menu
        ).pack(pady=20)


# ---------- Draggable Label ----------
class DraggableLabel(ctk.CTkLabel):
    def __init__(self, master, text, drop_handler, **kwargs):
        super().__init__(master, text=text, **kwargs)
        self.drop_handler = drop_handler
        self.original_pos = (0, 0)
        self.locked = False
        self.match_answer = None
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_motion)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._drag_start_x = 0
        self._drag_start_y = 0

    def _on_press(self, event):
        if self.locked:
            return
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self.lift()

    def _on_motion(self, event):
        if self.locked:
            return
        x = self.winfo_x() + event.x - self._drag_start_x
        y = self.winfo_y() + event.y - self._drag_start_y
        self.place(x=x, y=y)

    def _on_release(self, event):
        if self.locked:
            return
        self.drop_handler(self)

import random

class Confetti(ctk.CTkCanvas):
    def __init__(self, master, width, height, **kwargs):
        super().__init__(master, width=width, height=height,
                         bg="", highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.confetti = []
        self.colors = ["#F48FB1", "#81D4FA", "#FFF176", "#CE93D8", "#80DEEA"]  # Red Velvet pastel palette
        self.create_confetti()
        self.animate()

    def create_confetti(self):
        for _ in range(50):  # number of pieces
            x = random.randint(0, self.width)
            y = random.randint(-self.height, 0)
            size = random.randint(6, 12)
            color = random.choice(self.colors)
            oval = self.create_oval(x, y, x+size, y+size, fill=color, outline="")
            self.confetti.append((oval, random.uniform(1, 3)))  # speed

    def animate(self):
        for oval, speed in self.confetti:
            self.move(oval, 0, speed)
            coords = self.coords(oval)
            if coords[1] > self.height:  # reset if off-screen
                x = random.randint(0, self.width)
                y = random.randint(-50, 0)
                size = coords[2] - coords[0]
                self.coords(oval, x, y, x+size, y+size)
        self.after(30, self.animate)



# ---------- Game Frame ----------
class GameFrame(ctk.CTkFrame):
    def __init__(self, master, level_path, hp=None):
        super().__init__(master, fg_color=APP_BG)
        self.master = master
        self.level_path = level_path

        # Load level data first
        with open(resource_path(level_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.level_data = data
        level_num = int(self.level_data.get("level", 1))

        # HP scaling: base 3 + 1 per level (nerfed to 1 because its too ez for yall)
        base_hp = 3
        scaled_hp = base_hp + (level_num - 1) * 1

        # If hp is passed (retry), use it; otherwise use scaled
        self.hp = hp if hp is not None else scaled_hp
        self.max_hp = self.hp

        # ✅ Now load level pairs and build UI
        self.targets = []
        self.draggables = []
        self.load_level()
        self.build_ui()
        self.level_start_time = time.time()



    def show_game_over(self):
        wrong_words = [d.cget("text") for d in self.draggables if not d.locked]
        correct = sum(1 for d in self.draggables if d.locked)
        total = len(self.draggables)
        pct = int(round((correct / total) * 100)) if total else 0
        return self.show_fail_panel(correct, total, pct, wrong_words)

    def load_level(self):
        with open(resource_path(self.level_path), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.level_data = data

        raw_pairs = data.get("pairs", {})
        all_pairs = list(raw_pairs.items())  # [(word, match), ...]

        level_num = int(self.level_data.get("level", 1))
        base_size = 5
        subset_size = min(base_size + (level_num - 1) * 2, len(all_pairs))

        # ✅ Pick subset of pairs
        chosen = random.sample(all_pairs, subset_size)

        # ✅ Authoritative mapping
        self.word_to_match = dict(chosen)

        # ✅ Separate lists for display
        self.words = list(self.word_to_match.keys())
        self.matches = list(self.word_to_match.values())

    def build_ui(self):
        header = ctk.CTkFrame(self, height=80, fg_color=CARD_BG, corner_radius=8, width=APP_WIDTH)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"Level {self.level_data.get('level', '')}: {self.level_data.get('title', '')}",
                     font=("Helvetica", 20, "bold"), text_color=TEXT).pack(pady=16)

        info = ctk.CTkLabel(self, text=self.level_data.get("instructions", "Match each word to its synonym."),
                            font=("Helvetica", 12), text_color=MUTED)
        info.pack(pady=(6, 8))

        # ✅ Play area frame (maximize vertical space, neat alignment)
        area = ctk.CTkFrame(self, fg_color=APP_BG)
        area.pack(fill="both", expand=True, padx=24, pady=(40, 12))

        # Layout settings
        start_y, spacing = 40, 60  # vertical spacing
        max_rows = 9  # rows per column
        col_spacing = 380  # spacing between columns

        # Left side: draggables (2 vertical columns)
        shuffled_words = self.words[:]
        random.shuffle(shuffled_words)
        for i, word in enumerate(shuffled_words):
            col = 0 if i < max_rows else 1
            row = i % max_rows
            x = 50 + col * col_spacing  # left block neatly aligned
            y = start_y + row * spacing

            d = DraggableLabel(area,
                               text=word,
                               drop_handler=self.check_drop,
                               font=("Helvetica", 16, "bold"),
                               width=270,
                               height=45,
                               fg_color="#81D4FA",
                               corner_radius=12,
                               text_color="#212121")
            d.place(x=x, y=y)
            d.original_pos = (x, y)
            d.match_answer = self.word_to_match[word]
            d.lift()
            self.draggables.append(d)

        # Right side: targets (2 vertical columns)
        shuffled_matches = self.matches[:]
        random.shuffle(shuffled_matches)
        for i, match_text in enumerate(shuffled_matches):
            col = 0 if i < max_rows else 1
            row = i % max_rows
            x = 800 + col * col_spacing
            y = start_y + row * spacing

            box = ctk.CTkFrame(area,
                               width=250,
                               height=40,
                               fg_color="#FFF176",
                               corner_radius=12)
            box.place(x=x, y=y)

            ctk.CTkLabel(box,
                         text=match_text,
                         font=("Arial", 16, "bold"),
                         text_color="#212121").place(relx=0.5, rely=0.5, anchor="center")

            box.match_text = match_text
            box.occupied = False
            self.targets.append(box)

        # ✅ Return button now inside area (aligned below HP bar)
        self.return_button = ctk.CTkButton(area, text="Return to Level Selection",
                                           width=300, height=35,  # match HP bar width
                                           command=self.master.show_level_select)
        self.return_button.place(relx=0.5, rely=0.98, anchor="s")  # centered, directly below

        level_num = int(self.level_data.get("level", 1))
        base_time = 10
        self.max_time = max(20, base_time - (level_num - 1) * 5)
        self.time_left = self.max_time

        # Timer inside area (above HP bar hopefully)
        self.canvas = tk.Canvas(area, width=100, height=100,
                                bg=self.cget("fg_color"),
                                highlightthickness=0)
        self.canvas.configure(background=self.cget("fg_color"))
        self.canvas.place(relx=0.5, rely=0.88, anchor="s")  # moved higher

        self.arc = self.canvas.create_arc(8, 8, 92, 92, start=90, extent=360,
                                          style="arc", outline="red", width=6)
        self.clock_text = self.canvas.create_text(50, 50, text=f"{self.time_left}",
                                                  font=("Helvetica", 12, "bold"), fill="red")

        # HP bar inside area (below timer)
        hp_frame = ctk.CTkFrame(area, fg_color="#FF80AB", corner_radius=8)
        hp_frame.place(relx=0.5, rely=0.93, anchor="s")  # stays lower

        ctk.CTkLabel(hp_frame, text="HP:", font=("Helvetica", 25, "bold"), text_color="#228B22").pack(side="left", padx=6)
        self.hp_bar = ctk.CTkProgressBar(hp_frame, width=265, height=20)
        self.hp_bar.pack(side="left", padx=6)
        self.hp_bar.set(self.hp / self.max_hp)

        # Start timer loop
        self.update_timer_circle()

    def reset_level(self):
        for d in self.draggables:
            d.place(x=d.original_pos[0], y=d.original_pos[1])
            d.locked = False
            d.configure(fg_color="#232323")
        for t in self.targets:
            t.occupied = False
            t.configure(fg_color="#151515")

    def update_timer_circle(self):
        if self.time_left > 0:
            self.time_left -= 1
            angle = (self.time_left / self.max_time) * 360
            self.canvas.itemconfig(self.arc, extent=angle)
            self.canvas.itemconfig(self.clock_text, text=f"{self.time_left}")
            self.after(1000, self.update_timer_circle)
        else:
            # Time’s up → force game over
            self.hp = 0
            self.show_game_over()

    def check_drop(self, widget):
        # Find which target (if any) the draggable was released over.
        wx = widget.winfo_rootx()
        wy = widget.winfo_rooty()
        ww = widget.winfo_width()
        wh = widget.winfo_height()
        center_x = wx + ww / 2
        center_y = wy + wh / 2


        for box in self.targets:
            bx1 = box.winfo_rootx()
            by1 = box.winfo_rooty()
            bx2 = bx1 + box.winfo_width()
            by2 = by1 + box.winfo_height()
            # center point collision
            if (bx1 < center_x < bx2) and (by1 < center_y < by2):
                # if target already occupied -> snap back
                if box.occupied:
                    widget.place(x=widget.original_pos[0], y=widget.original_pos[1])
                    return
                # Flexible checking: compare widget.match_answer to box.match_text (text-based)
                if widget.match_answer == box.match_text:
                    # convert root coords → local coords of widget's parent
                    parent = widget.master

                    relx = box.winfo_rootx() - parent.winfo_rootx() + 12
                    rely = box.winfo_rooty() - parent.winfo_rooty() + 6

                    widget.place(x=relx, y=rely)

                    widget.locked = True
                    box.occupied = True
                    widget.configure(fg_color="#0b8457")
                    box.configure(fg_color="#073d2a")
                    play_sound(resource_path("levels/correct.wav"))

                    # ✅ Auto-check for completion
                    if all(d.locked for d in self.draggables):
                        self.show_score_panel(len(self.draggables), len(self.draggables), 100, [])
                    return

                else:
                    # wrong: flash red then reset to origin
                    widget.configure(fg_color="#7a1a1a")
                    self.after(300, lambda w=widget: w.configure(fg_color="#81D4FA"))
                    widget.place(x=widget.original_pos[0], y=widget.original_pos[1])
                    self.hp -= 1
                    self.hp_bar.set(self.hp / self.max_hp) # assuming max HP is 3
                    play_sound(resource_path("levels/wrong.wav"))

                    if self.hp <= 0:
                        self.show_game_over()
                        return

        # not over any box -> return to origin
        widget.place(x=widget.original_pos[0], y=widget.original_pos[1])

    def submit_answers(self):
        # Count correct (locked items) and collect wrong words for formatted display
        total = len(self.pairs)
        correct = 0
        wrong_words = []
        # if a draggable is locked -> it's correct (we only lock on correct matches)
        # otherwise, it's wrong (could be not placed or placed wrongly)
        for d in self.draggables:
            if d.locked:
                correct += 1
            else:
                wrong_words.append(d.cget("text"))

        # compute percentage
        pct = int(round((correct / total) * 100)) if total else 0
        # show formatted score panel
        self.show_score_panel(correct, total, pct, wrong_words)

    def show_fail_panel(self, correct, total, pct, wrong_words):
        # Clear current UI
        for widget in self.winfo_children():
            widget.destroy()

        # Background: deep charcoal with subtle red accent
        self.configure(fg_color="#121212")
        panel = ctk.CTkFrame(self, fg_color="#1E1A1A", corner_radius=0)
        panel.pack(fill="both", expand=True)

        # Title + headline
        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")
        ctk.CTkLabel(panel, text=f"Level {level_num}: {level_title}",
                     font=("Helvetica", 22, "bold"), text_color="#FF8888").pack(pady=(8, 4))
        ctk.CTkLabel(panel, text="⚠️ Try Again",
                     font=("Helvetica", 34, "bold"), text_color="#FF5555").pack(pady=(12, 6))
        ctk.CTkLabel(panel, text="You’re close, keep practicing!",
                     font=("Helvetica", 14), text_color="#DD9999").pack(pady=(0, 12))

        # Stats
        stats_frame = ctk.CTkFrame(panel, fg_color="#2A1A1A", corner_radius=8)
        stats_frame.pack(pady=12, padx=20, fill="x")
        ctk.CTkLabel(stats_frame, text=f"Correct: {correct} / {total}",
                     font=("Helvetica", 16, "bold"), text_color="#FFBBBB").pack(pady=10)

        # Wrong words
        if wrong_words:
            bad_frame = ctk.CTkFrame(panel, fg_color="#3A1A1A", corner_radius=8)
            bad_frame.pack(fill="x", padx=18, pady=(12, 16))
            ctk.CTkLabel(bad_frame, text="Words you got wrong:",
                         font=("Helvetica", 14, "bold"), text_color="#FFAAAA").pack(anchor="w", padx=10, pady=(8, 4))
            grid = ctk.CTkFrame(bad_frame, fg_color="#3A1A1A")
            grid.pack(padx=10, pady=(4, 12))
            for idx, w in enumerate(wrong_words):
                r, c = divmod(idx, 2)
                card = ctk.CTkFrame(grid, width=260, height=56, fg_color="#5A2A2A", corner_radius=8)
                card.grid(row=r, column=c, padx=8, pady=8)
                ctk.CTkLabel(card, text=w, font=("Helvetica", 14, "bold"),
                             text_color="#FFDDDD").place(relx=0.5, rely=0.5, anchor="center")

        # Buttons
        btn_frame = ctk.CTkFrame(panel, fg_color="#1E1A1A")
        btn_frame.pack(pady=(12, 20))

        def retry():
            # Reset HP to scaled value for this level
            level_num = int(self.level_data.get("level", 1))
            base_hp = 3
            scaled_hp = base_hp + (level_num - 1) * 2
            self.master.show_game(self.level_path, hp=scaled_hp)

        def to_menu():
            self.master.show_level_select()

        StyledButton(btn_frame, text="Retry Level", width=260, height=52, command=retry).pack(side="left", padx=16)
        StyledButton(btn_frame, text="Return to Level Selection", width=220, height=48, command=to_menu).pack(
            side="left", padx=16)

    def show_score_panel(self, correct, total, pct, wrong_words):
        import time
        elapsed = time.time() - self.level_start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"{minutes}m {seconds}s"

        if self.hp <= 0 or self.time_left <= 0:
            return self.show_fail_panel(correct, total, pct, wrong_words)

        # Unlock next level in synonym mode
        current_level = int(self.level_data.get("level", 1))
        next_level_num = current_level + 1

        # Save score for synonym mode
        self.master.progress["synonym_progress"]["scores"][current_level] = pct

        # Unlock next synonym level
        if next_level_num not in self.master.progress["synonym_progress"]["unlocked"]:
            self.master.progress["synonym_progress"]["unlocked"].append(next_level_num)
            self.master.progress["highest_level"] = max(
                self.master.progress.get("highest_level", 1), next_level_num
            )
        save_progress(self.master.progress)

        # Clear current UI
        for widget in self.winfo_children():
            widget.destroy()

        # Red Velvet celebratory background
        panel = ctk.CTkFrame(self, fg_color="#F48FB1", corner_radius=12)
        panel.pack(fill="both", expand=True, padx=40, pady=40)

        level_num = int(self.level_data.get("level", 1))
        level_title = self.level_data.get("title", "")
        ctk.CTkLabel(panel, text=f"Level {level_num}: {level_title}",
                     font=("Helvetica", 24, "bold"), text_color="#880E4F").pack(pady=(8, 4))

        ctk.CTkLabel(panel, text="🎉 You Passed! 🎉",
                     font=("Helvetica", 34, "bold"), text_color="#AD1457").pack(pady=(12, 10))
        ctk.CTkLabel(panel, text="Amazing! Keep up the great work.",
                     font=("Helvetica", 14), text_color="#6A1B9A").pack(pady=(0, 12))

        # --- Stats + HP + Time Panel ---
        stats_frame = ctk.CTkFrame(panel, fg_color="#F8BBD0", corner_radius=8)
        stats_frame.pack(pady=12, padx=20, fill="x")

        # Score / Percentage
        ctk.CTkLabel(stats_frame, text=f"Score: {pct}%", font=("Helvetica", 16, "bold"),
                     text_color="#880E4F").pack(pady=(10, 8))

        # HP: progress + number in a horizontal frame
        hp_frame = ctk.CTkFrame(stats_frame, fg_color="#F8BBD0", corner_radius=8)
        hp_frame.pack(pady=(0, 8))

        ctk.CTkLabel(hp_frame, text="HP:", font=("Helvetica", 16, "bold"), text_color="#228B22").pack(side="left",
                                                                                                      padx=(6, 4))

        self.hp_bar = ctk.CTkProgressBar(hp_frame, width=200, height=16)
        self.hp_bar.pack(side="left", padx=(0, 6))
        self.hp_bar.set(self.hp / self.max_hp)

        # Numeric HP display
        self.hp_label = ctk.CTkLabel(hp_frame, text=f"{self.hp}/{self.max_hp}", font=("Helvetica", 14, "bold"),
                                     text_color="#228B22")
        self.hp_label.pack(side="left")

        # Time Taken
        ctk.CTkLabel(stats_frame, text=f"Time Taken: {time_str}", font=("Helvetica", 16, "bold"),
                     text_color="#880E4F").pack(pady=(4, 12))

        # ✅ Single button frame
        btn_frame = ctk.CTkFrame(panel, fg_color="#F8BBD0", corner_radius=12)
        btn_frame.pack(pady=(12, 20))

        current_level = int(self.level_data.get("level", 1))
        next_level_num = current_level + 1
        next_path = resource_path(os.path.join(LEVELS_DIR, f"level{next_level_num}.json"))
        can_unlock = os.path.exists(next_path)

        def to_menu():
            self.master.show_level_select()

        def do_next():
            if next_level_num not in self.master.progress.get("unlocked", []):
                self.master.progress.setdefault("unlocked", []).append(next_level_num)
                save_progress(self.master.progress)

            if os.path.exists(next_path):
                # Reset HP properly for the new level
                base_hp = 3
                scaled_hp = base_hp + (next_level_num - 1) * 2
                self.master.show_game(next_path, hp=scaled_hp)
            else:
                self.master.show_level_select()

        def retry():
            base_hp = 3
            scaled_hp = base_hp + (current_level - 1) * 2
            self.master.show_game(self.level_path, hp=scaled_hp)

        # 🎵 Buttons side by side
        StyledButton(btn_frame, text="Retry Level", width=220, height=52, command=retry).pack(side="left", padx=16)

        next_btn = StyledButton(btn_frame, text="Next Level", width=220, height=52, command=do_next)
        next_btn.pack(side="left", padx=16)
        if not can_unlock:
            next_btn.configure(state="disabled", fg_color="#A5D6A7")

        StyledButton(btn_frame, text="Return to Level Selection", width=220, height=52, command=to_menu).pack(
            side="left", padx=16)


# ---------- Run ----------
if __name__ == "__main__":
    # create levels dir hint if missing
    if not os.path.isdir(LEVELS_DIR):
        os.makedirs(LEVELS_DIR, exist_ok=True)
    app = EngageApp()
    app.mainloop()
