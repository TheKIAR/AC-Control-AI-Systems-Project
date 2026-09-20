import argparse
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
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    FIGURE_AVAILABLE = True
except Exception:
    FigureCanvasTkAgg = None
    Figure = None
    FIGURE_AVAILABLE = False

try:
    from fuzzy_logic.fuzzy_system import FuzzySystem
    from reinforcement_learning.agent import RLAgent
    from reinforcement_learning.env import RLEnvironment
    from reinforcement_learning.trainer import RLTrainer
    from data_driven.generator import DataGenerator
    from data_driven.pipeline import DataPipeline
except ImportError:
    from src.fuzzy_logic.fuzzy_system import FuzzySystem
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


def generate_visual_outputs(output_dir="outputs", temperature=22, rl_episodes=5,
                            data_points=5, data_method="supervised"):
    """Run all modules headlessly and save PNG + text evidence to output_dir.

    Produces fuzzy_system.png, reinforcement_learning.png, data_pipeline.png,
    summary.txt and logic_inference.txt. Used by tests/test_visuals.py and
    anywhere file output is needed without opening the GUI.
    """
    if not FIGURE_AVAILABLE:
        raise RuntimeError("matplotlib is required to generate visual outputs.")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result = run_demo(temperature, rl_episodes, data_points, data_method)

    # 1. Fuzzy decision levels across a temperature sweep.
    fuzzy_system = FuzzySystem()
    temperatures = [16, 18, 20, 22, 24, 26, 28, 30]
    decision_map = {
        "Increase Temperature": 1,
        "Maintain Temperature": 2,
        "Decrease Temperature": 3,
    }
    fuzzy_values = [decision_map[fuzzy_system.evaluate(t)] for t in temperatures]
    fig = Figure(figsize=(10, 4.2), dpi=100)
    ax = fig.add_subplot(111)
    colors = ["#2ecc71" if v == 1 else "#f39c12" if v == 2 else "#e74c3c"
              for v in fuzzy_values]
    ax.bar(temperatures, fuzzy_values, color=colors)
    ax.axvline(temperature, color="#000000", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Temperature (C)")
    ax.set_ylabel("Decision level")
    ax.set_title("Fuzzy Logic Temperature Control")
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Increase", "Maintain", "Decrease"])
    fig.tight_layout()
    fuzzy_file = output_path / "fuzzy_system.png"
    fig.savefig(fuzzy_file)

    # 2. RL reward curve.
    rewards = result.get("rl_rewards", []) or [0.0]
    fig = Figure(figsize=(10, 4.2), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(list(range(1, len(rewards) + 1)), rewards, marker="o", linewidth=2.2)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Reward")
    ax.set_title("Reinforcement Learning Rewards")
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    rl_file = output_path / "reinforcement_learning.png"
    fig.savefig(rl_file)

    # 3. Data pipeline output.
    y_values = normalize_values(result.get("processed_data", []))
    x_values = list(range(len(y_values)))
    fig = Figure(figsize=(10, 4.2), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x_values, y_values, marker="o", linewidth=2.2)
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Transformed value")
    ax.set_title("Data Pipeline Output")
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    data_file = output_path / "data_pipeline.png"
    fig.savefig(data_file)

    # 4. Text summary with pipeline stats.
    lo = min(y_values)
    hi = max(y_values)
    mean_val = sum(y_values) / len(y_values)
    summary_file = output_path / "summary.txt"
    summary_file.write_text(
        "AI Systems Project Summary\n"
        "========================\n"
        f"Fuzzy result: {result['fuzzy_result']}\n"
        f"RL episodes: {rl_episodes}\n"
        f"Data points: {data_points}\n"
        f"Data method: {data_method}\n"
        f"Pipeline min: {lo:.2f}, max: {hi:.2f}, mean: {mean_val:.2f}\n",
        encoding="utf-8",
    )

    # 5. FOPL advisor trace (P2 evidence).
    try:
        try:
            from fopl.advisor import build_advisor
        except ImportError:
            from src.fopl.advisor import build_advisor
        advisor = build_advisor(temperature, occupied=True)
        lines = [
            "Smart-Room FOPL Advisor",
            "=======================",
            f"Input: {float(temperature):.1f}C ({advisor['band']}), "
            "occupied=True, night=False, energy_saver=False",
            "",
            "Facts:",
            *[f"  {f}" for f in advisor["facts"]],
            "",
            "Conclusions:",
            *[f"  {c}" for c in advisor["conclusions"]],
            "",
            "Fired rules:",
            *[f"  {line}" for line in advisor["fired"]],
        ]
        logic_file = output_path / "logic_inference.txt"
        logic_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        logic_file = None

    out = {
        "fuzzy": fuzzy_file,
        "rl": rl_file,
        "data": data_file,
        "summary": summary_file,
        "fuzzy_decision": result["fuzzy_result"],
        "rl_rewards": result["rl_rewards"],
        "processed_data": result["processed_data"],
    }
    if logic_file is not None:
        out["logic"] = logic_file
    return out


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


class DemoApp(tk.Tk):
    BG = "#070b14"
    PANEL = "#0d1320"
    CARD = "#111a29"
    CARD_2 = "#151f31"
    BORDER = "#24344d"
    TEXT = "#e8eef8"
    MUTED = "#8290a8"
    ACCENT = "#6ee7ff"
    ACCENT_2 = "#9b8cff"
    GREEN = "#39e6a3"
    RED = "#ff5577"
    BLUE = "#4aa8ff"

    THEMES = {
        "dark": {
            "BG": "#070b14",
            "PANEL": "#0d1320",
            "CARD": "#111a29",
            "CARD_2": "#151f31",
            "BORDER": "#24344d",
            "TEXT": "#e8eef8",
            "MUTED": "#8290a8",
            "ACCENT": "#6ee7ff",
            "ACCENT_2": "#9b8cff",
            "GREEN": "#39e6a3",
            "RED": "#ff5577",
            "BLUE": "#4aa8ff",
        },
        "light": {
            "BG": "#e9eef5",
            "PANEL": "#ffffff",
            "CARD": "#ffffff",
            "CARD_2": "#eef3f9",
            "BORDER": "#c3cfdf",
            "TEXT": "#0f1c30",
            "MUTED": "#5b6b84",
            "ACCENT": "#0284c7",
            "ACCENT_2": "#7c3aed",
            "GREEN": "#059669",
            "RED": "#dc2626",
            "BLUE": "#2563eb",
        },
    }

    def __init__(self):
        if not TK_AVAILABLE or not FIGURE_AVAILABLE:
            raise RuntimeError(
                "GUI needs tkinter and matplotlib with the Tk backend."
            )

        super().__init__()
        self.theme = "dark"
        self.title("AI CONTROL // FUTURE SYSTEMS")
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
        self._last_temp = int(self.temp_var.get())

        self._build_ui()
        self._bind_keyboard()
        self._refresh_all()

    def _configure_styles(self):
        self.style.configure(
            "Root.TFrame",
            background=self.BG,
        )
        self.style.configure(
            "Panel.TFrame",
            background=self.PANEL,
        )
        self.style.configure(
            "Card.TFrame",
            background=self.CARD,
        )
        self.style.configure(
            "Title.TLabel",
            background=self.BG,
            foreground=self.TEXT,
            font=("Segoe UI", 24, "bold"),
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=self.BG,
            foreground=self.MUTED,
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Section.TLabel",
            background=self.PANEL,
            foreground=self.TEXT,
            font=("Segoe UI", 11, "bold"),
        )
        self.style.configure(
            "Control.TLabel",
            background=self.PANEL,
            foreground=self.MUTED,
            font=("Segoe UI", 10),
        )
        self.style.configure(
            "Value.TLabel",
            background=self.PANEL,
            foreground=self.ACCENT,
            font=("Consolas", 11, "bold"),
        )
        self.style.configure(
            "Status.TLabel",
            background=self.PANEL,
            foreground=self.GREEN,
            font=("Consolas", 9, "bold"),
        )
        self.style.configure(
            "Action.TButton",
            background=self.CARD_2,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            padding=(12, 8),
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "Action.TButton",
            background=[("active", "#1d2a42"), ("pressed", "#263957")],
            foreground=[("active", self.ACCENT)],
        )
        self.style.configure(
            "Accent.TButton",
            background=self.ACCENT_2,
            foreground="#ffffff",
            borderwidth=0,
            padding=(16, 9),
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", "#8373f0"), ("pressed", "#6f5fe0")],
        )
        self.style.configure(
            "TCombobox",
            fieldbackground=self.CARD_2,
            background=self.CARD_2,
            foreground=self.TEXT,
            arrowcolor=self.ACCENT,
            bordercolor=self.BORDER,
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.CARD_2)],
            foreground=[("readonly", self.TEXT)],
        )
        self.style.configure(
            "Dark.Horizontal.TScale",
            background=self.PANEL,
            troughcolor="#202c42",
            bordercolor=self.BORDER,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
        )
        self.style.configure(
            "Vertical.TScrollbar",
            background=self.CARD_2,
            troughcolor=self.BG,
            bordercolor=self.BORDER,
            arrowcolor=self.MUTED,
        )

    def _apply_theme_colors(self):
        for key, value in self.THEMES[self.theme].items():
            setattr(self, key, value)
        self.configure(bg=self.BG)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self._apply_theme_colors()
        self.style.theme_use("clam")
        self._configure_styles()
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        self._refresh_all()

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
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _build_ui(self):
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
        # Keep the content full-width at any window size. Without this the
        # inner frame keeps its narrow width when maximized/fullscreen and
        # everything looks shifted to the middle.
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfig(self.canvas_window, width=event.width),
        )
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Sticky top bar: title + theme toggle + status stay visible while
        # the controls and charts scroll underneath.
        header = ttk.Frame(self, padding=(22, 14, 22, 10), style="Root.TFrame")
        header.pack(side="top", fill="x", before=self.canvas)

        title_frame = ttk.Frame(header, style="Root.TFrame")
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="AI CONTROL", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            title_frame,
            text="FUZZY LOGIC  /  REINFORCEMENT LEARNING  /  DATA PIPELINE",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        status_frame = tk.Frame(
            header,
            bg=self.PANEL,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        status_frame.pack(side="right", padx=(20, 0))
        tk.Label(
            status_frame,
            text="● ",
            bg=self.PANEL,
            fg=self.GREEN,
            font=("Consolas", 10, "bold"),
        ).pack(side="left", padx=(10, 0), pady=8)
        tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Consolas", 9, "bold"),
        ).pack(side="left", padx=(0, 10), pady=8)

        self.theme_button = ttk.Button(
            header,
            text="🌙  DARK" if self.theme == "light" else "☀  LIGHT",
            command=self.toggle_theme,
            style="Action.TButton",
        )
        self.theme_button.pack(side="right", padx=(0, 4))

        controls = tk.Frame(
            body,
            bg=self.PANEL,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        controls.pack(fill="x", pady=(0, 18))

        tk.Label(
            controls,
            text="CONTROL MATRIX",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Consolas", 11, "bold"),
        ).pack(anchor="w", padx=18, pady=(15, 4))

        tk.Label(
            controls,
            text="Adjust a parameter and the corresponding AI visualization updates immediately.",
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 9),
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
            font=("Consolas", 9, "bold")
        ).pack(side="left")
        combo = ttk.Combobox(
            method_row,
            textvariable=self.method_var,
            values=["supervised", "unsupervised"],
            state="readonly",
            width=18,
            font=("Segoe UI", 10),
        )
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", self._on_settings_changed)

        action_row = tk.Frame(controls, bg=self.PANEL)
        action_row.pack(fill="x", padx=18, pady=(0, 16))
        ttk.Button(
            action_row, text="↻  RUN FULL SYSTEM", command=self.run_demo,
            style="Accent.TButton"
        ).pack(side="left")
        ttk.Button(
            action_row, text="RESET", command=self.reset_controls,
            style="Action.TButton"
        ).pack(side="left", padx=(10, 0))
        tk.Label(
            action_row,
            textvariable=self.fuzzy_result_var,
            bg=self.PANEL,
            fg=self.ACCENT,
            font=("Consolas", 10, "bold"),
        ).pack(side="right")

        preset_row = tk.Frame(controls, bg=self.PANEL)
        preset_row.pack(fill="x", padx=18, pady=(0, 16))
        tk.Label(preset_row, text="QUICK PRESETS", bg=self.PANEL, fg=self.MUTED,
                 font=("Consolas", 9, "bold")).pack(side="left")
        preset_combo = ttk.Combobox(
            preset_row, textvariable=self.preset_var,
            values=["CUSTOM", "FIXED COLD  •  16°C", "FIXED NORMAL  •  22°C", "FIXED HOT  •  30°C"],
            state="readonly", width=24, font=("Segoe UI", 10)
        )
        preset_combo.pack(side="right")
        preset_combo.bind("<<ComboboxSelected>>", self._apply_preset)

        telemetry = tk.Frame(body, bg=self.CARD, highlightbackground=self.BORDER, highlightthickness=1)
        telemetry.pack(fill="x", pady=(0, 14))
        tk.Label(telemetry, textvariable=self.telemetry_var, bg=self.CARD, fg=self.ACCENT,
                 font=("Consolas", 9, "bold"), anchor="w").pack(fill="x", padx=14, pady=10)

        output_title = tk.Frame(body, bg=self.BG)
        output_title.pack(fill="x", pady=(0, 10))
        tk.Label(
            output_title,
            text="LIVE OUTPUTS",
            bg=self.BG,
            fg=self.TEXT,
            font=("Consolas", 12, "bold"),
        ).pack(side="left")
        tk.Label(
            output_title,
            text="3 ACTIVE MODULES",
            bg=self.BG,
            fg=self.MUTED,
            font=("Consolas", 8, "bold"),
        ).pack(side="right")

        self.output_grid = tk.Frame(body, bg=self.BG)
        self.output_grid.pack(fill="both", expand=True)
        self.output_grid.grid_columnconfigure(0, weight=1)
        self.output_grid.grid_rowconfigure(0, weight=1)
        self.output_grid.grid_rowconfigure(1, weight=1)
        self.output_grid.grid_rowconfigure(2, weight=1)

        self.fuzzy_card = self._create_output_card(
            0, 0, "01  FUZZY TEMPERATURE FIELD", "LIVE MEMBERSHIP", self.BLUE
        )
        self.rl_card = self._create_output_card(
            1, 0, "02  REINFORCEMENT LEARNING", "REWARD TRACE", self.ACCENT_2
        )
        self.data_card = self._create_output_card(
            2, 0, "03  DATA PIPELINE", "TRANSFORMED DATA", self.GREEN
        )

        self.fuzzy_chart = self._chart_host(self.fuzzy_card)
        self.rl_chart = self._chart_host(self.rl_card)
        self.data_chart = self._chart_host(self.data_card)

    def _add_slider(self, parent, label, variable, minimum, maximum, suffix, callback):
        row = tk.Frame(parent, bg=self.PANEL)
        row.pack(fill="x", padx=18, pady=7)

        top = tk.Frame(row, bg=self.PANEL)
        top.pack(fill="x")
        tk.Label(
            top, text=label, bg=self.PANEL, fg=self.MUTED,
            font=("Consolas", 9, "bold")
        ).pack(side="left")

        value_label = tk.Label(
            top, text="", bg=self.PANEL, fg=self.ACCENT,
            font=("Consolas", 11, "bold")
        )
        value_label.pack(side="right")

        def update_value(*_):
            try:
                value_label.config(text=f"{int(variable.get())}{suffix}")
            except tk.TclError:
                pass  # label belonged to a pre-theme-toggle layout

        update_value()
        variable.trace_add("write", update_value)

        scale = ttk.Scale(
            row,
            from_=minimum,
            to=maximum,
            orient="horizontal",
            variable=variable,
            command=callback,
            style="Dark.Horizontal.TScale",
        )
        scale.pack(fill="x", pady=(7, 0))
        self._add_step_buttons(row, variable, minimum, maximum, callback)

    def _add_step_buttons(self, parent, variable, minimum, maximum, callback):
        buttons = tk.Frame(parent, bg=self.PANEL)
        buttons.pack(fill="x", pady=(3, 0))

        ttk.Button(
            buttons, text="−", width=4,
            command=lambda: self._step_value(variable, -1, minimum, maximum, callback),
            style="Action.TButton",
        ).pack(side="left")

        ttk.Button(
            buttons, text="+", width=4,
            command=lambda: self._step_value(variable, 1, minimum, maximum, callback),
            style="Action.TButton",
        ).pack(side="left", padx=(6, 0))

        tk.Label(
            buttons, text=f"INTEGER STEP  /  {minimum}—{maximum}",
            bg=self.PANEL, fg="#4f607b", font=("Consolas", 8)
        ).pack(side="right")

    def _step_value(self, variable, amount, minimum, maximum, callback):
        value = max(minimum, min(maximum, int(variable.get()) + amount))
        variable.set(value)
        callback()

    def _create_output_card(self, row, column, title, subtitle, accent=None):
        card = tk.Frame(
            self.output_grid,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        card.grid(row=row, column=column, sticky="nsew", pady=(0, 12))
        if accent is not None:
            tk.Frame(card, bg=accent, height=3).pack(fill="x")
        header = tk.Frame(card, bg=self.CARD)
        header.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(
            header, text=title, bg=self.CARD, fg=self.TEXT,
            font=("Consolas", 10, "bold")
        ).pack(side="left")
        tk.Label(
            header, text=subtitle, bg=self.CARD, fg=self.MUTED,
            font=("Consolas", 8)
        ).pack(side="right")
        return card

    def _chart_host(self, parent):
        host = tk.Frame(parent, bg=self.CARD)
        host.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        return host

    def _make_figure(self, width=10, height=4.2):
        fig = Figure(figsize=(width, height), dpi=100, facecolor=self.CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.CARD)
        return fig, ax

    def _draw_fuzzy(self, temp_value):
        for child in self.fuzzy_chart.winfo_children():
            child.destroy()

        fig, ax = self._make_figure(10, 4.2)

        import numpy as np

        temps = np.linspace(10, 35, 500)

        # Smooth cold -> normal -> hot field.
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
            gradient,
            extent=[10, 35, 0, 1],
            aspect="auto",
            interpolation="bicubic",
            alpha=0.88,
        )

        # The temperature marker is intentionally the only overlay.
        ax.axvline(
            temp_value,
            color="#ffffff",
            linestyle=":",
            linewidth=2.4,
            alpha=0.95,
        )

        ax.set_xlim(10, 35)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasTkAgg(fig, master=self.fuzzy_chart)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._fuzzy_canvas = canvas

    def _draw_line_chart(self, parent, x_values, y_values, title, x_label, y_label, accent):
        for child in parent.winfo_children():
            child.destroy()

        fig, ax = self._make_figure(10, 4.2)
        ax.plot(
            x_values, y_values,
            color=accent,
            linewidth=2.2,
            marker="o",
            markersize=4,
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

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_all(self, result):
        self._draw_fuzzy(result["temperature"])

        rewards = result.get("rl_rewards", [])
        if not rewards:
            rewards = [0.0]
        self._draw_line_chart(
            self.rl_chart,
            list(range(1, len(rewards) + 1)),
            rewards,
            "Reward by episode",
            "Episode",
            "Reward",
            self.ACCENT_2,
        )

        y_values = normalize_values(result.get("processed_data", []))
        self._draw_line_chart(
            self.data_chart,
            list(range(1, len(y_values) + 1)),
            y_values,
            "Processed data stream",
            "Sample",
            "Value",
            self.GREEN,
        )

    def _update_fuzzy_only(self, animate=True):
        temperature = int(self.temp_var.get())
        system = FuzzySystem()
        system.set_temperature(temperature)
        result = system.evaluate(temperature)
        self.fuzzy_result_var.set(f"FUZZY OUTPUT  //  {result.upper()}")
        self._update_telemetry(result)
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
        self._update_telemetry()

    def _update_telemetry(self, fuzzy_result=None):
        if fuzzy_result is None:
            system = FuzzySystem()
            temperature = int(self.temp_var.get())
            system.set_temperature(temperature)
            fuzzy_result = system.evaluate(temperature)
        self.telemetry_var.set(
            f"TEMP {int(self.temp_var.get()):02d}°C   │   "
            f"FUZZY {fuzzy_result.upper():<22} │   "
            f"RL {int(self.rl_var.get()):02d} EP   │   "
            f"DATA {int(self.data_count_var.get()):02d}   │   "
            f"{self.method_var.get().upper():<11} │   ● ONLINE"
        )

    def _apply_preset(self, *_):
        temperatures = {
            "FIXED COLD  •  16°C": 16,
            "FIXED NORMAL  •  22°C": 22,
            "FIXED HOT  •  30°C": 30,
        }
        preset = self.preset_var.get()
        if preset in temperatures:
            self.temp_var.set(temperatures[preset])
            self._update_fuzzy_only()

    def _animate_temperature(self, start, target):
        if self._animation_job is not None:
            try:
                self.after_cancel(self._animation_job)
            except Exception:
                pass
        steps = max(4, min(14, abs(target - start) * 2))
        current = 0
        def step():
            nonlocal current
            current += 1
            progress = current / steps
            smooth = progress * progress * (3 - 2 * progress)
            self._draw_fuzzy(start + (target - start) * smooth)
            if current < steps:
                self._animation_job = self.after(18, step)
            else:
                self._draw_fuzzy(target)
                self._animation_job = None
        step()

    def _refresh_all(self):
        try:
            result = run_demo(
                int(self.temp_var.get()),
                int(self.rl_var.get()),
                int(self.data_count_var.get()),
                self.method_var.get(),
            )
            self.fuzzy_result_var.set(f"FUZZY OUTPUT  //  {result['fuzzy_result'].upper()}")
            self._update_telemetry(result["fuzzy_result"])
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
                int(self.temp_var.get()),
                int(self.rl_var.get()),
                int(self.data_count_var.get()),
                self.method_var.get(),
            )
            self.fuzzy_result_var.set(f"FUZZY OUTPUT  //  {result['fuzzy_result'].upper()}")
            self._render_all(result)
            self.status_var.set("SYSTEM ONLINE  //  LIVE")
        except Exception as exc:
            self.status_var.set("SYSTEM ERROR")
            self._set_error(str(exc))
            if messagebox is not None:
                messagebox.showerror("AI Control Error", f"{type(exc).__name__}: {exc}")

    def reset_controls(self):
        self.temp_var.set(22)
        self.rl_var.set(5)
        self.data_count_var.set(5)
        self.method_var.set("supervised")
        self.preset_var.set("FIXED NORMAL  •  22°C")
        self._refresh_all()

    def _set_error(self, text):
        for host in (self.fuzzy_chart, self.rl_chart, self.data_chart):
            for child in host.winfo_children():
                child.destroy()
            tk.Label(
                host,
                text=f"OUTPUT ERROR\n{text}",
                bg=self.CARD,
                fg=self.RED,
                font=("Consolas", 9),
                justify="left",
            ).pack(expand=True)

    def destroy(self):
        super().destroy()


def console_demo():
    result = run_demo()
    print(f"Fuzzy Logic System evaluated temperature: {result['fuzzy_result']}")
    print("Reinforcement Learning training completed.")
    print(f"Data generation and processing completed: {result['processed_items']} items processed.")


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
