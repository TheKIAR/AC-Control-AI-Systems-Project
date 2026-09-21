import argparse
import math
import random
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = Path(__file__).resolve().parent
for _p in (str(_SRC_DIR), str(_PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TK_AVAILABLE = True
except ImportError:
    tk = None
    ttk = None
    messagebox = None
    TK_AVAILABLE = False

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # type: ignore
    from matplotlib.figure import Figure # type: ignore
    FIGURE_AVAILABLE = True
except Exception:
    FigureCanvasTkAgg = None
    Figure = None
    FIGURE_AVAILABLE = False

try:
    from fuzzy_logic.fuzzy_system import FuzzySystem, COLD_MAX, COMFORT_MAX
    from reinforcement_learning.agent import RLAgent
    from reinforcement_learning.env import RLEnvironment
    from reinforcement_learning.trainer import RLTrainer
    from data_driven.generator import DataGenerator
    from data_driven.pipeline import DataPipeline
except ImportError:
    from src.fuzzy_logic.fuzzy_system import FuzzySystem, COLD_MAX, COMFORT_MAX
    from src.reinforcement_learning.agent import RLAgent
    from src.reinforcement_learning.env import RLEnvironment
    from src.reinforcement_learning.trainer import RLTrainer
    from src.data_driven.generator import DataGenerator
    from src.data_driven.pipeline import DataPipeline


def normalize_values(items):
    values = []
    for item in items:
        if isinstance(item, (int, float)):
            values.append(float(item))
        elif isinstance(item, (list, tuple)):
            values.extend(float(v) for v in item if isinstance(v, (int, float)))
        elif isinstance(item, dict):
            values.extend(float(v) for v in item.values() if isinstance(v, (int, float)))
    return values or [0.0]


def run_demo(temp_value=22, rl_episodes=5, data_points=5, data_method="supervised"):
    fuzzy_system = FuzzySystem()
    fuzzy_system.set_temperature(temp_value)
    fuzzy_result = fuzzy_system.evaluate(temp_value)

    env = RLEnvironment()
    agent = RLAgent(action_space=[0, 1])
    trainer = RLTrainer(agent, env)
    trainer.train(episodes=rl_episodes, max_steps=100)

    generator = DataGenerator(method=data_method)
    raw_data = generator.generate_data(num_samples=data_points)
    pipeline = DataPipeline(raw_data)
    processed_data = pipeline.process(raw_data)

    return {
        "temperature": temp_value,
        "fuzzy_result": fuzzy_result,
        "processed_items": len(processed_data),
        "data_method": data_method,
        "rl_episodes": rl_episodes,
        "data_points": data_points,
        "rl_rewards": trainer.rewards,
        "processed_data": processed_data,
    }


def _rounded_rect(canvas, x1, y1, x2, y2, radius, fill, outline="", width=1):
    # NOTE: outline must default to "" (no stroke). The previous default of
    # None made Tk fall back to a black 1px arc outline, which showed up as
    # dark notches at every rounded corner and arc joint.
    r = min(radius, max(1, (x2 - x1) / 2), max(1, (y2 - y1) / 2))
    canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90,
                      fill=fill, outline=outline, width=width)
    canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90,
                      fill=fill, outline=outline, width=width)
    canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90,
                      fill=fill, outline=outline, width=width)
    canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90,
                      fill=fill, outline=outline, width=width)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline="")
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline="")


class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command, bg, fg, hover, width=120, height=38, radius=14,
                 parent_bg=None, **kwargs):
        if parent_bg is None:
            try:
                parent_bg = master.cget("bg")
            except tk.TclError:
                # ttk containers (e.g. header) have no -bg option; fall
                # back to the window background so the rounded corners
                # blend in instead of crashing.
                parent_bg = master.winfo_toplevel().cget("bg")
        super().__init__(master, width=width, height=height, bg=parent_bg,
                         highlightthickness=0, bd=0, **kwargs)
        self._text = text
        self._command = command
        self._bg = bg
        self._fg = fg
        self._hover = hover
        self._radius = radius
        self._draw(False)
        self.bind("<Enter>", lambda e: self._draw(True))
        self.bind("<Leave>", lambda e: self._draw(False))
        self.bind("<Button-1>", lambda e: self._click())

    def _draw(self, hover):
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        fill = self._hover if hover else self._bg
        _rounded_rect(self, 2, 2, w-2, h-2, self._radius, fill)
        self.create_text(w/2, h/2, text=self._text, fill=self._fg,
                         font=("Segoe UI", 10, "bold"))

    def _click(self):
        if callable(self._command):
            self._command()


class RoundedPanel(tk.Frame):
    def __init__(self, master, bg, panel_bg, radius=20, border=None, **kwargs):
        super().__init__(master, bg=bg, bd=0, highlightthickness=0, **kwargs)
        self._panel_bg = panel_bg
        self._border = border or panel_bg
        self._radius = radius
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._inset = max(6, radius // 2)
        self.inner = tk.Frame(self, bg=panel_bg, bd=0, highlightthickness=0)
        # NOTE: inner must be packed, not placed. place()d children report
        # zero requested size, which collapsed every rounded card to 1px and
        # left the whole window blank. pack() lets the content size the panel.
        self.inner.pack(fill="both", expand=True, padx=self._inset, pady=self._inset)
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        w = max(self.winfo_width(), 4)
        h = max(self.winfo_height(), 4)
        self._canvas.delete("all")
        # Two fill-only layers (rim behind, panel inset) instead of one
        # stroked shape: a 1px outline stroke overhangs the arc joints and
        # leaves dark ticks on the panel corners.
        _rounded_rect(
            self._canvas, 1, 1, w - 1, h - 1,
            self._radius, self._border
        )
        pad = 2
        _rounded_rect(
            self._canvas, 1 + pad, 1 + pad, w - 1 - pad, h - 1 - pad,
            max(1, self._radius - pad), self._panel_bg
        )


class DemoApp(tk.Tk):
    BG = "#17181c"
    PANEL = "#22252b"
    CARD = "#2a2e36"
    CARD_2 = "#343943"
    BORDER = "#4a505a"
    TEXT = "#f5f3ef"
    MUTED = "#aeb2ba"
    ACCENT = "#35cfe5"
    ACCENT_2 = "#35cfe5"
    GREEN = "#35cfe5"
    RED = "#79dce8"
    BLUE = "#35cfe5"
    SKY = "#0b1a2a"

    THEMES = {
        "dark": {"BG":"#0d1117","PANEL":"#151b23","CARD":"#1b2430","CARD_2":"#24303d","BORDER":"#334252","TEXT":"#e8f7fa","MUTED":"#91a8b0","ACCENT":"#35cfe5","ACCENT_2":"#35cfe5","GREEN":"#35cfe5","RED":"#79dce8","BLUE":"#35cfe5","SKY":"#0b1a2a"},
        "light": {"BG":"#edf7f9","PANEL":"#f8fcfd","CARD":"#ffffff","CARD_2":"#e7f3f6","BORDER":"#b9d5db","TEXT":"#18343a","MUTED":"#607d84","ACCENT":"#079bb3","ACCENT_2":"#079bb3","GREEN":"#079bb3","RED":"#3e9cac","BLUE":"#079bb3","SKY":"#d9edf4"},
    }

    def __init__(self):
        if not TK_AVAILABLE or not FIGURE_AVAILABLE:
            raise RuntimeError(
                "GUI needs tkinter and matplotlib with the Tk backend."
            )

        super().__init__()
        self.theme = "dark"
        self.title("AI Control System")
        self.geometry("1240x1000")
        self.minsize(980, 760)
        self.configure(bg=self.BG)
        self.resizable(True, True)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        self.temp_var = tk.IntVar(value=22)
        self.rl_var = tk.IntVar(value=5)
        self.data_count_var = tk.IntVar(value=5)
        self.method_var = tk.StringVar(value="supervised")
        self.preset_var = tk.StringVar(value="CUSTOM")
        self.status_var = tk.StringVar(value="SYSTEM READY")
        self.fuzzy_result_var = tk.StringVar(value="")
        self.telemetry_var = tk.StringVar(value="")
        self._animation_job = None
        self._pulse_job = None
        self._pulse_level = 0
        self._scroll_job = None
        self._refit_job = None
        self._fig_width = 10.0
        self._fitted_width = 0
        self._last_result = None
        self._fade_gen = 0
        self._weather = None
        self._weather_parts = []
        self._sky_canvas = None
        self._status_dot = None
        self._last_temp = int(self.temp_var.get())
        self._reset_chart_slots()

        self._build_ui()
        self._bind_keyboard()
        self._refresh_all()
        tk.Misc.lower(self._frame_canvas)
        self._start_frame_animation()

    def _configure_styles(self):
        self.style.configure("Root.TFrame", background=self.BG)
        self.style.configure("Panel.TFrame", background=self.PANEL)
        self.style.configure("Card.TFrame", background=self.CARD)
        self.style.configure(
            "Title.TLabel", background=self.BG, foreground=self.TEXT,
            font=("Segoe UI", 21, "bold")
        )
        self.style.configure(
            "Subtitle.TLabel", background=self.BG, foreground=self.MUTED,
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "Section.TLabel", background=self.PANEL, foreground=self.TEXT,
            font=("Segoe UI", 11, "bold")
        )
        self.style.configure(
            "Control.TLabel", background=self.PANEL, foreground=self.MUTED,
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "Value.TLabel", background=self.PANEL, foreground=self.ACCENT,
            font=("Segoe UI", 11, "bold")
        )
        self.style.configure(
            "Status.TLabel", background=self.PANEL, foreground=self.GREEN,
            font=("Segoe UI", 9, "bold")
        )
        self.style.configure(
            "Action.TButton", background=self.CARD_2, foreground=self.TEXT,
            bordercolor=self.BORDER, lightcolor=self.BORDER,
            darkcolor=self.BORDER, padding=(12, 8),
            font=("Segoe UI", 10, "bold")
        )
        self.style.map(
            "Action.TButton",
            background=[("active", "#1f3340"), ("pressed", "#294452")],
            foreground=[("active", self.ACCENT)],
        )
        self.style.configure(
            "Accent.TButton", background=self.ACCENT_2, foreground="#ffffff",
            borderwidth=0, padding=(16, 9), font=("Segoe UI", 10, "bold")
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", "#16aec4"), ("pressed", "#079bb3")],
        )
        self.style.configure(
            "TCombobox", fieldbackground=self.CARD_2, background=self.CARD_2,
            foreground=self.TEXT, arrowcolor=self.ACCENT,
            bordercolor=self.BORDER
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.CARD_2)],
            foreground=[("readonly", self.TEXT)],
        )
        self.style.configure(
            "Modern.Horizontal.TScale", background=self.PANEL,
            troughcolor="#1b2b34", bordercolor=self.BORDER,
            lightcolor=self.ACCENT, darkcolor=self.ACCENT
        )
        self.style.configure(
            "Vertical.TScrollbar", background=self.CARD_2,
            troughcolor=self.BG, bordercolor=self.BORDER,
            arrowcolor=self.MUTED
        )

    def _apply_theme_colors(self):
        for key, value in self.THEMES[self.theme].items():
            setattr(self, key, value)
        self.configure(bg=self.BG)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        try:
            self.unbind_all("<MouseWheel>")
        except Exception:
            pass
        if self._animation_job is not None:
            try:
                self.after_cancel(self._animation_job)
            except Exception:
                pass
            self._animation_job = None
        self._stop_pulse()
        if getattr(self, "_scroll_job", None) is not None:
            try:
                self.after_cancel(self._scroll_job)
            except Exception:
                pass
            self._scroll_job = None
        if getattr(self, "_refit_job", None) is not None:
            try:
                self.after_cancel(self._refit_job)
            except Exception:
                pass
            self._refit_job = None
        # Dip the window opacity, rebuild under cover, fade back in: the
        # light/dark swap reads as one smooth transition instead of a pop.
        self._fade_gen = getattr(self, "_fade_gen", 0) + 1
        self._fade_out(self._fade_gen, 1.0)

    def _fade_out(self, gen, alpha):
        if gen != getattr(self, "_fade_gen", 0):
            return
        try:
            if not self.winfo_exists():
                return
            alpha = max(0.35, alpha - 0.22)
            self.attributes("-alpha", alpha)
        except Exception:
            pass
        if alpha <= 0.36:
            self._finish_toggle(gen)
        else:
            try:
                self.after(14, lambda: self._fade_out(gen, alpha))
            except Exception:
                pass

    def _finish_toggle(self, gen):
        if gen != getattr(self, "_fade_gen", 0):
            return
        self._apply_theme_colors()
        self.style.theme_use("clam")
        self._configure_styles()
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        self._bind_keyboard()
        self._refresh_all()
        self._start_frame_animation()
        self._fade_in(gen, 0.35)

    def _fade_in(self, gen, alpha):
        if gen != getattr(self, "_fade_gen", 0):
            return
        try:
            if not self.winfo_exists():
                return
            alpha = min(1.0, alpha + 0.22)
            self.attributes("-alpha", alpha)
        except Exception:
            return
        if alpha < 1.0:
            try:
                self.after(14, lambda: self._fade_in(gen, alpha))
            except Exception:
                pass

    def _bind_keyboard(self):
        self.bind("<Up>", lambda e: self._keyboard_temp(1))
        self.bind("<Down>", lambda e: self._keyboard_temp(-1))
        self.bind("<Left>", lambda e: self._keyboard_step(-1))
        self.bind("<Right>", lambda e: self._keyboard_step(1))
        self.bind("<r>", lambda e: self.run_demo())
        self.bind("<R>", lambda e: self.run_demo())
        self.bind("<space>", lambda e: self.run_demo())
        self.bind("<Escape>", lambda e: self.reset_controls())

    def _keyboard_temp(self, amount):
        self.temp_var.set(max(10, min(35, int(self.temp_var.get()) + amount)))
        self._update_fuzzy_only()

    def _keyboard_step(self, amount):
        self._step_value(self.rl_var, amount, 1, 20, self._on_settings_changed)

    def _on_mousewheel(self, event):
        # Glide instead of jumping: animate toward the target position over
        # ~100ms. A new wheel tick cancels the previous glide mid-flight.
        try:
            notch = (event.delta / 120.0) if getattr(event, "delta", 0) else 0.0
            if notch:
                # Negated: wheel-up (positive delta) must move the view up.
                self._smooth_scroll_by(-notch * 48.0)
        except Exception:
            pass

    def _smooth_scroll_by(self, pixels):
        try:
            top, bottom = self.canvas.yview()
        except Exception:
            return
        if (top <= 0.0 and pixels < 0) or (bottom >= 1.0 and pixels > 0):
            return
        try:
            height = float(str(self.canvas.cget("scrollregion")).split()[3])
        except Exception:
            height = 1000.0
        target = min(1.0, max(0.0, top + pixels / max(height, 1.0)))
        self._glide_to(target)

    def _glide_to(self, target, frames=6):
        if getattr(self, "_scroll_job", None) is not None:
            try:
                self.after_cancel(self._scroll_job)
            except Exception:
                pass
            self._scroll_job = None
        try:
            start = self.canvas.yview()[0]
        except Exception:
            return
        delta = target - start
        if abs(delta) < 1e-4:
            return
        step_no = 0

        def glide():
            nonlocal step_no
            step_no += 1
            progress = min(1.0, step_no / frames)
            eased = progress * progress * (3 - 2 * progress)
            try:
                self.canvas.yview_moveto(start + delta * eased)
            except Exception:
                self._scroll_job = None
                return
            if step_no < frames:
                self._scroll_job = self.after(16, glide)
            else:
                self._scroll_job = None

        glide()

    def _rounded_panel(self, parent, bg=None, radius=18):
        outer = RoundedPanel(
            parent, self.BG if bg is None else bg, self.CARD,
            radius=radius, border=self.BORDER
        )
        return outer, outer.inner

    def _build_ui(self):
        self._create_frame_animation()
        self.canvas = tk.Canvas(self, bg=self.BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        body = ttk.Frame(self.canvas, padding=(22, 10, 22, 22), style="Root.TFrame")
        self.canvas_window = self.canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: (self.canvas.itemconfig(self.canvas_window, width=event.width),
                           self._schedule_refit()),
        )
        self.unbind_all("<MouseWheel>")
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

        header = ttk.Frame(self, padding=(22, 14, 22, 10), style="Root.TFrame")
        header.pack(side="top", fill="x", before=self.canvas)

        title_frame = ttk.Frame(header, style="Root.TFrame")
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="AI Control", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_frame,
            text="Fuzzy logic, reinforcement learning and data processing",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        status_shell = RoundedPanel(
            header, self.BG, self.CARD, radius=14, border=self.BORDER,
            width=170, height=38
        )
        status_shell.pack(side="right", padx=(12, 0))
        status_frame = status_shell.inner
        self._status_dot = tk.Label(
            status_frame, text="●", bg=self.CARD, fg=self.GREEN,
            font=("Segoe UI", 10, "bold")
        )
        self._status_dot.pack(side="left", padx=(10, 4), pady=8)
        tk.Label(
            status_frame, textvariable=self.status_var, bg=self.CARD,
            fg=self.TEXT, font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=(0, 10), pady=8)


        self.theme_button = RoundedButton(
            header,
            text="Light" if self.theme == "dark" else "Dark",
            command=self.toggle_theme,
            bg=self.CARD_2, fg=self.TEXT, hover="#2d3b48",
            width=118, height=38, radius=16
        )
        self.theme_button.pack(side="right", padx=(0, 4))

        # Live sky strip: the weather animation lives here, in plain sight
        # above the controls (a full-window background would hide behind the
        # opaque panels, which is why the old one was invisible).
        sky_shell, sky_inner = self._rounded_panel(body, bg=self.BG, radius=18)
        sky_shell.pack(fill="x", pady=(0, 14))
        self._sky_canvas = tk.Canvas(sky_inner, bg=self.SKY, height=96,
                                     highlightthickness=0, bd=0)
        self._sky_canvas.pack(fill="x")

        controls_shell, controls = self._rounded_panel(body, bg=self.BG, radius=20)
        controls_shell.pack(fill="x", pady=(0, 18), ipady=4)

        tk.Label(
            controls, text="Controls", bg=self.PANEL, fg=self.TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=18, pady=(15, 4))

        tk.Label(
            controls,
            text="Change the values below to update the results.",
            bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", padx=18, pady=(0, 14))

        self._add_slider(
            controls, "FUZZY TEMPERATURE", self.temp_var, 10, 35, "°C",
            self._on_temperature_changed
        )
        self._add_slider(
            controls, "RL EPISODES", self.rl_var, 1, 20, "",
            self._on_settings_changed
        )
        self._add_slider(
            controls, "DATA POINTS", self.data_count_var, 3, 20, "",
            self._on_settings_changed
        )

        method_row = tk.Frame(controls, bg=self.PANEL)
        method_row.pack(fill="x", padx=18, pady=(3, 16))
        tk.Label(
            method_row, text="DATA METHOD", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")
        combo = ttk.Combobox(
            method_row, textvariable=self.method_var,
            values=["supervised", "unsupervised"], state="readonly",
            width=18, font=("Segoe UI", 10)
        )
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", self._on_settings_changed)

        action_row = tk.Frame(controls, bg=self.PANEL)
        action_row.pack(fill="x", padx=18, pady=(0, 16))
        RoundedButton(
            action_row, text="Run System", command=self.run_demo,
            bg=self.ACCENT, fg="#ffffff", hover="#6a9fff",
            width=128, height=40, radius=16
        ).pack(side="left")
        RoundedButton(
            action_row, text="Reset", command=self.reset_controls,
            bg=self.CARD_2, fg=self.TEXT, hover="#2d3b48",
            width=88, height=40, radius=16
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            action_row, textvariable=self.fuzzy_result_var,
            bg=self.PANEL, fg=self.ACCENT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right")

        preset_row = tk.Frame(controls, bg=self.PANEL)
        preset_row.pack(fill="x", padx=18, pady=(0, 16))
        tk.Label(
            preset_row, text="Presets", bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")
        for text, temp in (
            ("Cold 16°C", 16),
            ("Normal 22°C", 22),
            ("Hot 30°C", 30),
        ):
            RoundedButton(
                preset_row, text=text,
                command=lambda t=temp, label=text: self._apply_preset_value(label, t),
                bg=self.CARD_2, fg=self.TEXT, hover="#2d3b48",
                width=116, height=36, radius=14
            ).pack(side="left", padx=(10, 0))

        output_title = tk.Frame(body, bg=self.BG)
        output_title.pack(fill="x", pady=(0, 10))
        tk.Label(
            output_title, text="Results", bg=self.BG, fg=self.TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        tk.Label(
            output_title, text="Live", bg=self.BG, fg=self.MUTED,
            font=("Segoe UI", 8, "bold")
        ).pack(side="right")

        self.output_grid = tk.Frame(body, bg=self.BG)
        self.output_grid.pack(fill="both", expand=True)
        self.output_grid.grid_columnconfigure(0, weight=1)
        self.output_grid.grid_rowconfigure(0, weight=3)
        self.output_grid.grid_rowconfigure(1, weight=1)
        self.output_grid.grid_rowconfigure(2, weight=1)

        self.fuzzy_card = self._create_output_card(
            0, 0, "Fuzzy Temperature", "Live", self.BLUE
        )
        self.rl_card = self._create_output_card(
            1, 0, "Reinforcement Learning", "Reward", self.ACCENT_2
        )
        self.data_card = self._create_output_card(
            2, 0, "Data Processing", "Processed Data", self.GREEN
        )

        self.fuzzy_chart = self._chart_host(self.fuzzy_card)
        self.rl_chart = self._chart_host(self.rl_card)
        self.data_chart = self._chart_host(self.data_card)
        self._reset_chart_slots()
        self._start_pulse()

    @staticmethod
    def _blend(color_a, color_b, t):
        # Linear RGB blend: t=0 -> color_a, t=1 -> color_b.
        def channel(a, b):
            return int(round(a + (b - a) * t))

        r1, g1, b1 = int(color_a[1:3], 16), int(color_a[3:5], 16), int(color_a[5:7], 16)
        r2, g2, b2 = int(color_b[1:3], 16), int(color_b[3:5], 16), int(color_b[5:7], 16)
        return f"#{channel(r1, r2):02x}{channel(g1, g2):02x}{channel(b1, b2):02x}"

    def _start_pulse(self):
        self._stop_pulse()
        self._pulse_level = 0
        self._pulse_tick()

    def _stop_pulse(self):
        if getattr(self, "_pulse_job", None) is not None:
            try:
                self.after_cancel(self._pulse_job)
            except Exception:
                pass
            self._pulse_job = None

    def _pulse_tick(self):
        # Glow fade instead of a hard blink: ramp the dot GREEN -> MUTED
        # and back over a ping-pong ramp.
        try:
            if self._status_dot is not None and self._status_dot.winfo_exists():
                steps = 8
                level = self._pulse_level % (2 * steps)
                t = level / steps if level <= steps else (2 * steps - level) / steps
                self._status_dot.configure(fg=self._blend(self.GREEN, self.MUTED, t))
                self._pulse_level += 1
                self._pulse_job = self.after(110, self._pulse_tick)
            else:
                self._pulse_job = None
        except Exception:
            self._pulse_job = None

    def _create_frame_animation(self):
        # A single visible border sweep: modern, clean, and intentionally prominent.
        self._frame_canvas = tk.Canvas(
            self, bg=self.BG, highlightthickness=0, bd=0
        )
        self._frame_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # NOTE: Canvas.lift()/lower() without args hit the canvas-ITEM ops
        # (need a tag) and crash. Window stacking needs Misc.lower -- and
        # the frame belongs behind the widgets anyway (it is opaque, so on
        # top it would cover the whole UI and only its border would show).
        tk.Misc.lower(self._frame_canvas)
        self._frame_phase = 0
        self.bind("<Configure>", self._resize_frame_animation, add="+")

    def _resize_frame_animation(self, _event=None):
        # Static repaint only: never start the loop from here, otherwise
        # every resize/scroll Configure event spawns its own infinite
        # 32ms chain and they pile up into hundreds of timers.
        try:
            self._paint_frame()
        except Exception:
            pass

    def _start_frame_animation(self):
        if getattr(self, "_frame_job", None):
            try:
                self.after_cancel(self._frame_job)
            except Exception:
                pass
        self._frame_job = None
        # Generation counter: loops from a previous layout (e.g. before a
        # theme toggle rebuilt the widgets) die quietly instead of piling up.
        self._frame_gen = getattr(self, "_frame_gen", 0) + 1
        self._frame_phase = 0
        self._animate_frame(self._frame_gen)

    def _paint_frame(self):
        if not self.winfo_exists():
            return
        c = self._frame_canvas
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)
        c.delete("all")

        # Static thin border + one clearly moving segment.
        inset = 3
        c.create_rectangle(
            inset, inset, w - inset, h - inset,
            outline="#4a505a", width=2
        )

        perimeter = 2 * (w - 2 * inset) + 2 * (h - 2 * inset)
        distance = (self._frame_phase * 5) % perimeter
        segment = 230

        def point_at(d):
            top = w - 2 * inset
            side = h - 2 * inset
            if d < top:
                return inset + d, inset
            d -= top
            if d < side:
                return w - inset, inset + d
            d -= side
            if d < top:
                return w - inset - d, h - inset
            d -= top
            return inset, h - inset - d

        # Draw the moving segment as short connected pieces so corners are smooth.
        pieces = 14
        points = []
        for i in range(pieces + 1):
            points.append(point_at((distance + segment * i / pieces) % perimeter))
        for i in range(pieces):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            c.create_line(
                x1, y1, x2, y2,
                fill="#35cfe5", width=7, capstyle="round"
            )

        self._frame_phase += 1

    @staticmethod
    def _weather_for_temp(temperature):
        # Same 20/24 borders as the fuzzy controller: cold -> snow,
        # comfort -> rain, warm/hot -> sun.
        if temperature < COLD_MAX:
            return "snow"
        if temperature > COMFORT_MAX:
            return "sun"
        return "rain"

    def _spawn_weather(self, mode):
        parts = []
        if mode == "snow":
            for _ in range(36):
                parts.append({
                    "bx": random.random(), "by": random.random(),
                    "spd": 0.0016 + random.random() * 0.0022,
                    "sway": 0.008 + random.random() * 0.022,
                    "ph": random.random() * 6.28,
                    "r": random.choice((1, 1, 2, 2, 3)),
                    "shade": random.choice(("flake0", "flake0", "flake1", "flake2")),
                })
        elif mode == "rain":
            for _ in range(55):
                parts.append({
                    "bx": random.random(), "by": random.random(),
                    "spd": 0.011 + random.random() * 0.009,
                    "drift": 0.0012,
                    "len": 9 + random.random() * 8,
                })
        else:  # sun: slow rising golden motes
            for _ in range(24):
                parts.append({
                    "bx": random.random(), "by": random.random(),
                    "spd": 0.0012 + random.random() * 0.0018,
                    "ph": random.random() * 6.28,
                    "r": random.choice((1, 2, 2, 3)),
                })
        self._weather = mode
        self._weather_parts = parts

    def _paint_weather(self, c, w, h):
        c.delete("all")
        try:
            temperature = float(self.temp_var.get())
        except Exception:
            temperature = COMFORT_MAX
        mode = self._weather_for_temp(temperature)
        if mode != self._weather:
            self._spawn_weather(mode)
        phase = self._frame_phase
        mid_y = h / 2.0
        if mode == "snow":
            shades = {
                "flake0": "#ffffff", "flake1": "#d7e9f2", "flake2": "#a9c9da",
            } if self.theme == "dark" else {
                "flake0": "#5f8ba3", "flake1": "#7fa9c0", "flake2": "#a9c9da",
            }
            for p in self._weather_parts:
                x = ((p["bx"] + p["sway"] * math.sin(phase * 0.05 + p["ph"])) % 1.0) * w
                y = ((p["by"] + phase * p["spd"]) % 1.0) * h
                r = p["r"]
                c.create_oval(x - r, y - r, x + r, y + r,
                              fill=shades[p["shade"]], outline="")
        elif mode == "rain":
            color = self.ACCENT
            for p in self._weather_parts:
                x = ((p["bx"] + phase * p["drift"]) % 1.0) * w
                y = ((p["by"] + phase * p["spd"]) % 1.0) * h
                ln = p["len"]
                c.create_line(x, y, x - ln * 0.35, y + ln, fill=color, width=1)
        else:
            gold, soft = "#f5b942", "#e08a2e"
            cx, cy = w - 70, mid_y
            sun_r = min(30.0, mid_y - 8.0)
            glow = sun_r + 10 + 4 * math.sin(phase * 0.08)
            c.create_oval(cx - glow, cy - glow, cx + glow, cy + glow,
                          fill="", outline=gold, width=1)
            c.create_oval(cx - sun_r, cy - sun_r, cx + sun_r, cy + sun_r,
                          fill=gold, outline="")
            for p in self._weather_parts:
                x = ((p["bx"] + 0.004 * math.sin(phase * 0.04 + p["ph"])) % 1.0) * w
                y = ((p["by"] - phase * p["spd"]) % 1.0) * h
                r = p["r"]
                c.create_oval(x - r, y - r, x + r, y + r,
                              fill=soft if int(phase + p["ph"] * 10) % 2 else gold,
                              outline="")

        # Condition badge: small canvas-drawn icon + label, left side.
        badge = {"snow": ("SNOW", "#ffffff" if self.theme == "dark" else "#3d748c"),
                 "rain": ("RAIN", self.ACCENT),
                 "sun": ("SUNNY", "#e08a2e")}[mode]
        label, tint = badge[0], badge[1]
        ix, iy = 34, mid_y
        if mode == "snow":
            for angle in (0, 60, 120):
                dx = 9 * math.cos(math.radians(angle))
                dy = 9 * math.sin(math.radians(angle))
                c.create_line(ix - dx, iy - dy, ix + dx, iy + dy, fill=tint, width=2)
        elif mode == "rain":
            for dx in (-8, 0, 8):
                c.create_line(ix + dx, iy - 9, ix + dx - 4, iy + 9, fill=tint, width=2)
        else:
            c.create_oval(ix - 8, iy - 8, ix + 8, iy + 8, fill=tint, outline="")
            for angle in range(0, 360, 45):
                dx = 13 * math.cos(math.radians(angle))
                dy = 13 * math.sin(math.radians(angle))
                c.create_line(ix + dx * 0.8, iy + dy * 0.8, ix + dx, iy + dy,
                              fill=tint, width=2)
        c.create_text(58, mid_y,
                      text=f"{label}  ·  {temperature:g}°C",
                      anchor="w", fill=self.TEXT, font=("Consolas", 15, "bold"))

    def _paint_sky(self):
        canvas = getattr(self, "_sky_canvas", None)
        if canvas is None:
            return
        try:
            if not canvas.winfo_exists():
                return
        except Exception:
            return
        w = max(canvas.winfo_width(), 2)
        h = max(canvas.winfo_height(), 2)
        if w < 10 or h < 10:
            return
        try:
            self._paint_weather(canvas, w, h)
        except Exception:
            pass

    def _animate_frame(self, gen=None):
        # Single loop only: stale generations (pre-toggle leftovers) exit
        # without rescheduling, and a dead canvas stops the loop instead of
        # spamming background errors every 32ms.
        if gen is None:
            gen = getattr(self, "_frame_gen", 0)
        if gen != getattr(self, "_frame_gen", 0):
            return
        try:
            self._paint_frame()
        except Exception:
            self._frame_job = None
            return
        try:
            self._paint_sky()
        except Exception:
            pass
        self._frame_job = self.after(25, lambda g=gen: self._animate_frame(g))

    def _add_slider(self, parent, label, variable, minimum, maximum, suffix, callback):
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", padx=18, pady=7)

        top = tk.Frame(row, bg=self.PANEL)
        top.pack(fill="x")
        tk.Label(
            top, text=label, bg=self.PANEL, fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")

        value_label = tk.Label(
            top, text="", bg=self.PANEL, fg=self.ACCENT,
            font=("Segoe UI", 11, "bold")
        )
        value_label.pack(side="right")

        def update_value(*_):
            try:
                value_label.config(text=f"{int(variable.get())}{suffix}")
            except tk.TclError:
                pass

        update_value()
        variable.trace_add("write", update_value)

        def on_scale(_value=None):
            try:
                value = max(minimum, min(maximum, int(round(float(variable.get())))))
                if int(variable.get()) != value:
                    variable.set(value)
                callback()
            except (TypeError, ValueError, tk.TclError):
                pass

        scale = ttk.Scale(
            row, from_=minimum, to=maximum, orient="horizontal",
            variable=variable, command=on_scale,
            style="Modern.Horizontal.TScale"
        )
        scale.pack(fill="x", pady=(7, 0))
        self._add_step_buttons(row, variable, minimum, maximum, callback)

    def _add_step_buttons(self, parent, variable, minimum, maximum, callback):
        buttons = tk.Frame(parent, bg=self.PANEL)
        buttons.pack(fill="x", pady=(3, 0))

        RoundedButton(
            buttons, text="−",
            command=lambda: self._step_value(variable, -1, minimum, maximum, callback),
            bg=self.CARD_2, fg=self.TEXT, hover="#2d3b48",
            width=42, height=32, radius=13
        ).pack(side="left")
        RoundedButton(
            buttons, text="+",
            command=lambda: self._step_value(variable, 1, minimum, maximum, callback),
            bg=self.CARD_2, fg=self.TEXT, hover="#2d3b48",
            width=42, height=32, radius=13
        ).pack(side="left", padx=(6, 0))
        tk.Label(
            buttons, text=f"INTEGER STEP  /  {minimum}—{maximum}",
            bg=self.PANEL, fg="#4f607b", font=("Segoe UI", 8)
        ).pack(side="right")

    def _step_value(self, variable, amount, minimum, maximum, callback):
        value = max(minimum, min(maximum, int(variable.get()) + amount))
        variable.set(value)
        callback()

    def _create_output_card(self, row, column, title, subtitle, accent=None):
        shell, card = self._rounded_panel(self.output_grid, bg=self.BG, radius=20)
        shell.grid(row=row, column=column, sticky="nsew", pady=(0, 12))
        if accent is not None:
            # A small rounded accent pill, rather than a sharp top stripe.
            pill = tk.Canvas(card, bg=self.CARD, height=7, highlightthickness=0, bd=0)
            pill.pack(fill="x", padx=18, pady=(10, 0))
            _rounded_rect(pill, 0, 1, 72, 6, 3, accent)
        header = tk.Frame(card, bg=self.CARD, bd=0, highlightthickness=0)
        header.pack(fill="x", padx=18, pady=(8, 6))
        tk.Label(
            header, text=title, bg=self.CARD, fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")
        tk.Label(
            header, text=subtitle, bg=self.CARD, fg=self.MUTED,
            font=("Segoe UI", 8)
        ).pack(side="right")
        return card

    def _chart_host(self, parent):
        host = tk.Frame(parent, bg=self.CARD)
        host.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        return host

    def _embed_canvas(self, fig, host):
        # A freshly created Tk canvas paints default white for one
        # event-loop cycle before matplotlib blits into it - that is the
        # white box flashing on every animation frame. Painting the raw
        # widget in the card color first makes the swap invisible.
        canvas = FigureCanvasTkAgg(fig, master=host)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=self.CARD, highlightthickness=0, bd=0)
        widget.pack(fill="both", expand=True)
        return canvas

    def _make_figure(self, width=10, height=4.2):
        fig = Figure(figsize=(width, height), dpi=100, facecolor=self.CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.CARD)
        return fig, ax

    def _reset_chart_slots(self):
        for name in (
            "_fuzzy_fig", "_fuzzy_ax", "_fuzzy_marker", "_fuzzy_canvas",
            "_rl_fig", "_rl_ax", "_rl_canvas",
            "_data_fig", "_data_ax", "_data_canvas",
        ):
            setattr(self, name, None)

    @staticmethod
    def _widget_alive(widget):
        try:
            return widget is not None and widget.winfo_exists()
        except Exception:
            return False

    def _slot_canvas_widget(self, canvas):
        try:
            if canvas is not None:
                return canvas.get_tk_widget()
        except Exception:
            pass
        return None

    def _draw_fuzzy(self, temp_value):
        # Persistent figure: only the marker line moves. Recreating the
        # widget every frame caused the visible jump/flash.
        widget = self._slot_canvas_widget(self._fuzzy_canvas)
        if (self._fuzzy_fig is None or self._fuzzy_marker is None
                or not self._widget_alive(widget)):
            self._build_fuzzy_figure(temp_value)
        try:
            self._fuzzy_marker.set_xdata([temp_value, temp_value])
            self._fuzzy_glow.set_xdata([temp_value, temp_value])
            self._fuzzy_canvas.draw_idle()
        except Exception:
            pass

    def _build_fuzzy_figure(self, temp_value):
        for child in self.fuzzy_chart.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

        fig, ax = self._make_figure(getattr(self, "_fig_width", 10.0), 4.2)

        import numpy as np # type: ignore

        temps = np.linspace(10, 35, 500)
        gradient = np.zeros((40, 500, 3))
        cold = np.array([0.18, 0.55, 1.00])
        normal = np.array([0.18, 0.90, 0.58])
        hot = np.array([1.00, 0.22, 0.34])

        for i, value in enumerate(temps):
            if value <= 22:
                ratio = (value - 10) / 12
                color = cold * (1 - ratio) + normal * ratio
            else:
                ratio = (value - 22) / 13
                color = normal * (1 - ratio) + hot * ratio
            gradient[:, i, :] = color

        ax.imshow(
            gradient, extent=[10, 35, 0, 1], aspect="auto",
            interpolation="bicubic", alpha=0.88
        )
        glow = ax.axvline(
            temp_value, color=self.ACCENT, linewidth=12, alpha=0.14
        )
        marker = ax.axvline(
            temp_value, color="#ffffff", linestyle=":",
            linewidth=3.0, alpha=1.0
        )
        ax.set_xlim(10, 35)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        fig.tight_layout(pad=0.5)
        self._fuzzy_fig = fig
        self._fuzzy_ax = ax
        self._fuzzy_marker = marker
        self._fuzzy_glow = glow
        self._fuzzy_canvas = self._embed_canvas(fig, self.fuzzy_chart)

    def _schedule_refit(self):
        # Debounced: after a resize/fullscreen settles, rebuild the figures
        # at the real pixel width so charts stay crisp instead of stretching.
        if getattr(self, "_refit_job", None) is not None:
            try:
                self.after_cancel(self._refit_job)
            except Exception:
                pass
        try:
            self._refit_job = self.after(300, self._refit_charts)
        except Exception:
            pass

    def _refit_charts(self):
        self._refit_job = None
        try:
            if not self.winfo_exists():
                return
            result = getattr(self, "_last_result", None)
            if result is None:
                return
            width_px = self.fuzzy_chart.winfo_width()
            if width_px < 200:
                return
            if abs(width_px - getattr(self, "_fitted_width", 0)) < 60:
                return
            self._fitted_width = width_px
            self._fig_width = min(16.0, max(6.0, width_px / 100.0))
            # Drop the cached figures; the draw paths rebuild them at the
            # new width with the same data (no retraining, no flicker since
            # widgets are replaced under cover of draw_idle).
            self._fuzzy_fig = None
            self._fuzzy_marker = None
            self._rl_fig = None
            self._data_fig = None
            self._render_all(result)
        except Exception:
            pass

    def _draw_line_chart(self, parent, x_values, y_values, title, x_label, y_label, accent):
        # Persistent figure per chart: replot into the same axes instead of
        # destroying the widget, so refreshes never flash or jump.
        if parent is self.rl_chart:
            tag = "rl"
        elif parent is self.data_chart:
            tag = "data"
        else:
            tag = None
        canvas = getattr(self, f"_{tag}_canvas", None) if tag else None
        widget = self._slot_canvas_widget(canvas)
        if (tag is None or getattr(self, f"_{tag}_fig", None) is None
                or not self._widget_alive(widget)):
            for child in parent.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
            fig, ax = self._make_figure(getattr(self, "_fig_width", 10.0), 4.2)
            if tag:
                setattr(self, f"_{tag}_fig", fig)
                setattr(self, f"_{tag}_ax", ax)
                setattr(self, f"_{tag}_canvas", self._embed_canvas(fig, parent))
                canvas = getattr(self, f"_{tag}_canvas")
        else:
            fig = getattr(self, f"_{tag}_fig")
            ax = getattr(self, f"_{tag}_ax")
            try:
                ax.clear()
            except Exception:
                pass
            ax.set_facecolor(self.CARD)
        ax.plot(
            x_values, y_values, color=accent, linewidth=2.2,
            marker="o", markersize=4
        )
        ax.fill_between(x_values, y_values, 0, color=accent, alpha=0.08)
        ax.set_title(title, color=self.TEXT, fontsize=10, loc="left", pad=10)
        ax.set_xlabel(x_label, color=self.MUTED, fontsize=8)
        ax.set_ylabel(y_label, color=self.MUTED, fontsize=8)
        ax.tick_params(colors=self.MUTED, labelsize=8)
        ax.grid(True, color=self.BORDER, alpha=0.65, linestyle="--", linewidth=0.6)
        for spine in ax.spines.values():
            spine.set_color(self.BORDER)
        fig.tight_layout(pad=1.2)

        if canvas is None:
            self._embed_canvas(fig, parent)
        else:
            try:
                canvas.draw_idle()
            except Exception:
                pass

    def _render_all(self, result):
        self._last_result = result
        self._draw_fuzzy(result["temperature"])

        rewards = result.get("rl_rewards", []) or [0.0]
        self._draw_line_chart(
            self.rl_chart, list(range(1, len(rewards) + 1)), rewards,
            "Reward by episode", "Episode", "Reward", self.ACCENT_2
        )

        y_values = normalize_values(result.get("processed_data", []))
        self._draw_line_chart(
            self.data_chart, list(range(1, len(y_values) + 1)), y_values,
            "Processed data stream", "Sample", "Value", self.GREEN
        )

    def _update_fuzzy_only(self, animate=True):
        temperature = int(self.temp_var.get())
        system = FuzzySystem()
        system.set_temperature(temperature)
        result = system.evaluate(temperature)
        self.fuzzy_result_var.set(f"FUZZY OUTPUT  //  {result.upper()}")
        if animate and hasattr(self, "_last_temp") and self._last_temp != temperature:
            self._animate_temperature(self._last_temp, temperature)
        else:
            self._draw_fuzzy(temperature)
        self._last_temp = temperature
        self.status_var.set("FUZZY FIELD LIVE")

    def _on_temperature_changed(self, *_):
        self._update_fuzzy_only()

    def _on_settings_changed(self, *_):
        self.preset_var.set("CUSTOM")
        self.status_var.set("PARAMETER CHANGED  //  RUN SYSTEM TO REFRESH")

    def _apply_preset_value(self, name, temperature):
        self.preset_var.set(name)
        self.temp_var.set(temperature)
        self._update_fuzzy_only()

    def _animate_temperature(self, start, target):
        if self._animation_job is not None:
            try:
                self.after_cancel(self._animation_job)
            except Exception:
                pass

        steps = max(8, min(24, abs(target - start) * 2))
        current = 0

        def step():
            nonlocal current
            current += 1
            progress = current / steps
            smooth = progress * progress * (3 - 2 * progress)
            self._draw_fuzzy(start + (target - start) * smooth)
            if current < steps:
                self._animation_job = self.after(22, step)
            else:
                self._draw_fuzzy(target)
                self._animation_job = None

        step()

    def _refresh_all(self):
        try:
            result = run_demo(
                int(self.temp_var.get()), int(self.rl_var.get()),
                int(self.data_count_var.get()), self.method_var.get()
            )
            self.fuzzy_result_var.set(f"FUZZY OUTPUT  //  {result['fuzzy_result'].upper()}")
            self._render_all(result)
            self.status_var.set("SYSTEM ONLINE  //  LIVE")
        except Exception as exc:
            self.status_var.set("SYSTEM ERROR")
            self._set_error(str(exc))

    def run_demo(self):
        self.status_var.set("PROCESSING  //  AI MODULES ACTIVE")
        self.update_idletasks()
        try:
            result = run_demo(
                int(self.temp_var.get()), int(self.rl_var.get()),
                int(self.data_count_var.get()), self.method_var.get()
            )
            self.fuzzy_result_var.set(f"FUZZY OUTPUT  //  {result['fuzzy_result'].upper()}")
            self._render_all(result)
            self.status_var.set("SYSTEM ONLINE  //  LIVE")
        except Exception as exc:
            self.status_var.set("SYSTEM ERROR")
            self._set_error(str(exc))
            if messagebox is not None:
                messagebox.showerror(
                    "AI Control Error", f"{type(exc).__name__}: {exc}"
                )

    def reset_controls(self):
        self.temp_var.set(22)
        self.rl_var.set(5)
        self.data_count_var.set(5)
        self._last_temp = 22
        self.method_var.set("supervised")
        self.preset_var.set("◉  NORMAL 22°")
        self._refresh_all()

    def _set_error(self, text):
        for host in (self.fuzzy_chart, self.rl_chart, self.data_chart):
            for child in host.winfo_children():
                child.destroy()
            tk.Label(
                host, text=f"OUTPUT ERROR\n{text}", bg=self.CARD, fg=self.RED,
                font=("Segoe UI", 9), justify="left"
            ).pack(expand=True)

    def destroy(self):
        self._stop_pulse()
        for job in (getattr(self, "_animation_job", None), getattr(self, "_frame_job", None),
                    getattr(self, "_scroll_job", None), getattr(self, "_refit_job", None)):
            if job is not None:
                try:
                    self.after_cancel(job)
                except Exception:
                    pass
        super().destroy()


def console_demo():
    result = run_demo()
    print(f"Fuzzy Logic System evaluated temperature: {result['fuzzy_result']}")
    print("Reinforcement Learning training completed.")
    print(
        f"Data generation and processing completed: "
        f"{result['processed_items']} items processed."
    )


def launch_gui():
    if not TK_AVAILABLE:
        print("tkinter is not available. Install Python with 'tcl/tk and IDLE' checked.")
        return False
    if not FIGURE_AVAILABLE:
        print("matplotlib Tk backend is missing. Run: pip install matplotlib")
        return False

    try:
        app = DemoApp()
        app.mainloop()
        return True
    except Exception as exc:
        print(f"Could not open GUI window ({type(exc).__name__}: {exc}).")
        return False


def main():
    parser = argparse.ArgumentParser(description="AI Systems Project")
    parser.add_argument("--gui", action="store_true", help="Open the graphical interface")
    parser.add_argument("--console", action="store_true", help="Run console demo only")
    parser.add_argument("--no-gui", action="store_true", help="Same as --console")
    args = parser.parse_args()

    if args.console or args.no_gui:
        console_demo()
        return

    launch_gui()


if __name__ == "__main__":
    main()