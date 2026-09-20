# filepath: ai-systems-project/src/main.py

import argparse
import os
import subprocess
import sys
from pathlib import Path

# --- Robust path bootstrap: works no matter the cwd or venv ---
# Allows both `python src/main.py` and `python -m src.main` / installed package.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_DIR = Path(__file__).resolve().parent
for _p in (str(_SRC_DIR), str(_PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Do NOT force matplotlib.use("Agg") globally: it breaks Tk embedding.
# Figure.savefig() works on any backend, so leave backend auto-selected.
import matplotlib.pyplot as plt # type: ignore

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
    TK_AVAILABLE = True
except ImportError:  # Python built without Tk
    tk = None  # type: ignore
    ttk = None  # type: ignore
    messagebox = None  # type: ignore
    TK_AVAILABLE = False

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # type: ignore
except Exception:  # headless / no Tk backend
    FigureCanvasTkAgg = None  # type: ignore

from matplotlib.figure import Figure # type: ignore

try:
    from fuzzy_logic.fuzzy_system import FuzzySystem
    from reinforcement_learning.agent import RLAgent
    from reinforcement_learning.env import RLEnvironment
    from reinforcement_learning.trainer import RLTrainer
    from data_driven.generator import DataGenerator
    from data_driven.pipeline import DataPipeline
except ImportError:  # fallback when imported as src.main (tests, notebooks)
    from src.fuzzy_logic.fuzzy_system import FuzzySystem
    from src.reinforcement_learning.agent import RLAgent
    from src.reinforcement_learning.env import RLEnvironment
    from src.reinforcement_learning.trainer import RLTrainer
    from src.data_driven.generator import DataGenerator
    from src.data_driven.pipeline import DataPipeline


def generate_visual_outputs(output_dir="outputs", temperature=22, rl_episodes=5, data_points=5, data_method="supervised"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fuzzy_system = FuzzySystem()
    fuzzy_system.set_temperature(temperature)
    fuzzy_decision = fuzzy_system.evaluate(temperature)

    temperatures = [16, 18, 20, 22, 24, 26, 28, 30]
    decision_map = {
        "Increase Temperature": 1,
        "Maintain Temperature": 2,
        "Decrease Temperature": 3,
    }
    fuzzy_values = []
    for temp in temperatures:
        fuzzy_system.set_temperature(temp)
        fuzzy_values.append(decision_map[fuzzy_system.evaluate(temp)])

    fig = Figure(figsize=(6.5, 4), dpi=120)
    ax = fig.add_subplot(111)
    colors = ["#2ecc71" if v == 1 else "#f39c12" if v == 2 else "#e74c3c" for v in fuzzy_values]
    ax.bar(temperatures, fuzzy_values, color=colors)
    ax.axvline(temperature, color="#000000", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Decision level")
    ax.set_title("Fuzzy Logic Temperature Control")
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Increase", "Maintain", "Decrease"])
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    fuzzy_file = output_path / "fuzzy_system.png"
    fig.savefig(fuzzy_file)
    try:
        plt.close(fig)
    except Exception:
        pass

    rewards = []
    env = RLEnvironment()
    agent = RLAgent(action_space=[0, 1])
    trainer = RLTrainer(agent, env)
    for episode in range(1, rl_episodes + 1):
        state = env.reset()
        done = False
        total_reward = 0
        steps = 0
        while not done and steps < 100:  # step cap: agent can get stuck
            action = agent.choose_action(state, exploration_rate=0.1)
            result = env.step(action)
            if len(result) == 2:
                reward, next_state = result
                done = env.is_terminal_state(next_state)
            else:
                next_state, reward, done = result
            agent.learn(state, action, reward, next_state)
            state = next_state
            total_reward += reward
            steps += 1
        rewards.append(total_reward)

    rewards = [round(float(r), 2) for r in rewards]

    fig = Figure(figsize=(6.5, 4), dpi=120)
    ax = fig.add_subplot(111)
    ax.plot(list(range(1, rl_episodes + 1)), rewards, marker="o", color="#1f77b4", linewidth=2.5)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Reward")
    ax.set_title("Reinforcement Learning Rewards")
    ax.grid(True, linestyle="--", alpha=0.35)
    fig.tight_layout()
    rl_file = output_path / "reinforcement_learning.png"
    fig.savefig(rl_file)
    try:
        plt.close(fig)
    except Exception:
        pass

    generator = DataGenerator(method=data_method)
    raw_data = generator.generate_data(num_samples=data_points)
    pipeline = DataPipeline(raw_data)
    processed = pipeline.process(raw_data)

    def normalize_values(items):
        values = []
        for item in items:
            if isinstance(item, (int, float)):
                values.append(float(item))
            elif isinstance(item, (list, tuple)):
                for element in item:
                    if isinstance(element, (int, float)):
                        values.append(float(element))
            elif isinstance(item, dict):
                for value in item.values():
                    if isinstance(value, (int, float)):
                        values.append(float(value))
        return values or [0.0]

    y_values = normalize_values(processed)
    x_values = list(range(len(y_values)))

    fig = Figure(figsize=(6.5, 4), dpi=120)
    ax = fig.add_subplot(111)
    ax.plot(x_values, y_values, marker="o", color="#2e7d32", linewidth=2.5)
    ax.fill_between(x_values, y_values, 0, color="#2e7d32", alpha=0.18)
    ax.set_xlabel("Sample index")
    ax.set_ylabel("Transformed value")
    ax.set_title("Data Pipeline Output")
    ax.grid(True, linestyle="--", alpha=0.35)
    fig.tight_layout()
    data_file = output_path / "data_pipeline.png"
    fig.savefig(data_file)
    try:
        plt.close(fig)
    except Exception:
        pass

    summary_file = output_path / "summary.txt"
    summary_file.write_text(
        "AI Systems Project Summary\n"
        "========================\n"
        f"Fuzzy result: {fuzzy_decision}\n"
        f"RL episodes: {rl_episodes}\n"
        f"Data points: {data_points}\n"
        f"Data method: {data_method}\n",
        encoding="utf-8",
    )

    return {
        "fuzzy": fuzzy_file,
        "rl": rl_file,
        "data": data_file,
        "summary": summary_file,
        "fuzzy_decision": fuzzy_decision,
        "rl_rewards": rewards,
        "processed_data": processed,
    }


def run_demo(temp_value=22, rl_episodes=5, data_points=5, data_method="supervised"):
    fuzzy_system = FuzzySystem()
    fuzzy_system.set_temperature(temp_value)
    fuzzy_result = fuzzy_system.evaluate(temp_value)

    rl_environment = RLEnvironment()
    rl_agent = RLAgent(action_space=[0, 1])
    rl_trainer = RLTrainer(rl_agent, rl_environment)
    rl_trainer.train(episodes=rl_episodes)

    datagen = DataGenerator(method=data_method)
    raw_data = datagen.generate_data(num_samples=data_points)
    pipeline = DataPipeline(raw_data)
    processed_data = pipeline.process(raw_data)

    output_path = Path(__file__).resolve().parent.parent / "outputs"
    files = generate_visual_outputs(output_path, temp_value, rl_episodes, data_points, data_method)

    return {
        "temperature": temp_value,
        "fuzzy_result": fuzzy_result,
        "processed_items": len(processed_data),
        "output_path": output_path,
        "files": files,
        "data_method": data_method,
        "rl_episodes": rl_episodes,
        "data_points": data_points,
        "rl_rewards": files.get("rl_rewards", []),
        "processed_data": files.get("processed_data", processed_data),
    }


class DemoApp(tk.Tk):
    def __init__(self):
        if not TK_AVAILABLE or FigureCanvasTkAgg is None:
            raise RuntimeError(
                "GUI needs tkinter + matplotlib Tk backend. "
                "Reinstall Python with 'tcl/tk and IDLE' checked and run: pip install matplotlib"
            )
        super().__init__()
        self.title("AI Systems Project")
        self.geometry("1100x820")
        self.minsize(900, 700)
        self.configure(bg="#f5f7fb")
        self.resizable(True, True)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Dashboard.TFrame", background="#f5f7fb")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Card.TLabelframe", background="#ffffff", borderwidth=1, relief="solid")
        self.style.configure("Card.TLabelframe.Label", background="#ffffff", foreground="#1f2937", font=("Segoe UI", 10, "bold"))
        self.style.configure("Action.TButton", background="#2563eb", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
        self.style.map("Action.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")])
        self.style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff", foreground="#1f2937")
        self.style.configure("TScale", background="#f5f7fb")
        self.style.configure("TLabel", background="#ffffff", foreground="#1f2937")
        self.style.configure("TFrame", background="#ffffff")

        self.temp_var = tk.IntVar(value=22)
        self.rl_var = tk.IntVar(value=5)
        self.data_count_var = tk.IntVar(value=5)
        self.method_var = tk.StringVar(value="supervised")

        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        outer = ttk.Frame(self, padding=16, style="Dashboard.TFrame")
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg="#f3f6fb", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scroll_frame = ttk.Frame(self.canvas, padding=(4, 4), style="Dashboard.TFrame")
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # MouseWheel (Windows/macOS) + Button-4/5 (Linux)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        header = ttk.Label(self.scroll_frame, text="AI Systems Project", font=("Segoe UI", 22, "bold"), foreground="#111827")
        header.pack(anchor="w", pady=(8, 12), padx=8)

        controls = ttk.LabelFrame(self.scroll_frame, text="Controls", padding=(14, 12), style="Card.TLabelframe")
        controls.pack(fill="x", padx=6, pady=(0, 14))

        row1 = ttk.Frame(controls)
        row1.pack(fill="x", pady=(4, 8))
        ttk.Label(row1, text="Fuzzy temperature:", width=18, anchor="w").pack(side="left")
        ttk.Scale(row1, from_=10, to=35, orient="horizontal", variable=self.temp_var, length=260).pack(side="left", padx=(8, 10))
        ttk.Label(row1, textvariable=self.temp_var, font=("Segoe UI", 10, "bold")).pack(side="left")

        row2 = ttk.Frame(controls)
        row2.pack(fill="x", pady=(4, 8))
        ttk.Label(row2, text="RL episodes:", width=18, anchor="w").pack(side="left")
        ttk.Scale(row2, from_=1, to=20, orient="horizontal", variable=self.rl_var, length=260).pack(side="left", padx=(8, 10))
        ttk.Label(row2, textvariable=self.rl_var, font=("Segoe UI", 10, "bold")).pack(side="left")

        row3 = ttk.Frame(controls)
        row3.pack(fill="x", pady=(4, 8))
        ttk.Label(row3, text="Data points:", width=18, anchor="w").pack(side="left")
        ttk.Scale(row3, from_=3, to=20, orient="horizontal", variable=self.data_count_var, length=260).pack(side="left", padx=(8, 10))
        ttk.Label(row3, textvariable=self.data_count_var, font=("Segoe UI", 10, "bold")).pack(side="left")

        row4 = ttk.Frame(controls)
        row4.pack(fill="x", pady=(4, 8))
        ttk.Label(row4, text="Data method:", width=18, anchor="w").pack(side="left")
        combo = ttk.Combobox(row4, textvariable=self.method_var, values=["supervised", "unsupervised"], state="readonly", width=18)
        combo.pack(side="left", padx=(8, 0))

        button_row = ttk.Frame(controls)
        button_row.pack(fill="x", pady=(12, 0))
        ttk.Button(button_row, text="Run All Demo", command=self.run_demo, style="Action.TButton").pack(side="left")
        ttk.Button(button_row, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=(10, 0))

        self.result_box = tk.Text(self.scroll_frame, height=7, width=120, wrap="word", bg="#f8fafc", fg="#1f2937", relief="flat", borderwidth=1, highlightthickness=1)
        self.result_box.insert("1.0", "Press Run All Demo to generate results and charts.")
        self.result_box.configure(state="disabled")
        self.result_box.pack(fill="x", padx=6, pady=(0, 14))

        self.chart_holder = ttk.Frame(self.scroll_frame, style="Dashboard.TFrame")
        self.chart_holder.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        self.chart_holder.grid_columnconfigure(0, weight=1)
        self.chart_holder.grid_columnconfigure(1, weight=1)

    def _on_close(self):
        try:
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        except Exception:
            pass
        self.destroy()

    def _on_mousewheel(self, event):
        try:
            delta = int(-1 * (event.delta / 120)) if getattr(event, "delta", 0) else 0
            if delta:
                self.canvas.yview_scroll(delta, "units")
        except Exception:
            pass

    def _on_mousewheel_linux(self, event):
        try:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def _render_chart_in_frame(self, frame, title, x_vals, y_vals, x_label, y_label, color="#60a5fa"):
        for widget in frame.winfo_children():
            widget.destroy()
        if FigureCanvasTkAgg is None:
            ttk.Label(frame, text="Chart unavailable (Tk backend missing)").pack()
            return
        fig = Figure(figsize=(5.5, 3.2), dpi=110, facecolor="#f8fafc")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#ffffff")
        ax.plot(x_vals, y_vals, marker="o", color=color, linewidth=2.4, markersize=4)
        ax.fill_between(x_vals, y_vals, 0, color=color, alpha=0.12)
        ax.set_title(title, fontsize=10, weight="bold", color="#1f2937")
        ax.set_xlabel(x_label, fontsize=9, color="#475569")
        ax.set_ylabel(y_label, fontsize=9, color="#475569")
        ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.35, color="#cbd5e1")
        ax.tick_params(colors="#475569")
        for spine in ax.spines.values():
            spine.set_color("#cbd5e1")
        ax.margins(x=0.05, y=0.15)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_fuzzy_chart(self, frame, temp_value):
        for widget in frame.winfo_children():
            widget.destroy()
        if FigureCanvasTkAgg is None:
            ttk.Label(frame, text="Chart unavailable (Tk backend missing)").pack()
            return

        temps = list(range(8, 38, 1))

        def low_zone(t):
            return max(0.0, min(1.0, 1.0 - abs((t - 15) / 10.0))) if t <= 25 else 0.0

        def neutral_zone(t):
            return max(0.0, min(1.0, 1.0 - abs((t - 22) / 8.0)))

        def high_zone(t):
            return max(0.0, min(1.0, 1.0 - abs((t - 30) / 10.0))) if t >= 15 else 0.0

        low_vals = [low_zone(t) for t in temps]
        neutral_vals = [neutral_zone(t) for t in temps]
        high_vals = [high_zone(t) for t in temps]

        fig = Figure(figsize=(5.5, 3.2), dpi=110, facecolor="#f8fafc")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#ffffff")

        for t, low, neutral, high in zip(temps, low_vals, neutral_vals, high_vals):
            x = [t, t]
            y = [0, 1.0]
            ax.plot(x, y, color=(0.0, 0.45 + 0.55 * low, 1.0), alpha=0.22 + low * 0.6, linewidth=8)
            ax.plot(x, y, color=(0.0, 0.8 + 0.2 * neutral, 0.25 + 0.55 * neutral), alpha=0.18 + neutral * 0.7, linewidth=8)
            ax.plot(x, y, color=(1.0, 0.4 + 0.25 * high, 0.15 + 0.4 * high), alpha=0.14 + high * 0.7, linewidth=8)

        ax.plot(temps, low_vals, color="#60a5fa", linewidth=2.2, alpha=0.9, label="Low zone")
        ax.plot(temps, neutral_vals, color="#22c55e", linewidth=2.2, alpha=0.9, label="Neutral zone")
        ax.plot(temps, high_vals, color="#ef4444", linewidth=2.2, alpha=0.9, label="High zone")
        ax.axvline(temp_value, color="#111827", linestyle="--", linewidth=1.5, label=f"Input {temp_value}°C")
        ax.set_xlabel("Temperature (°C)", fontsize=9, color="#475569")
        ax.set_ylabel("Membership", fontsize=9, color="#475569")
        ax.set_title("Fuzzy Logic Temperature Zones", fontsize=10, weight="bold", color="#1f2937")
        ax.set_ylim(0, 1.15)
        ax.set_xlim(8, 36)
        ax.grid(True, linestyle="--", alpha=0.35, color="#dfe7f1")
        ax.tick_params(colors="#475569")
        for spine in ax.spines.values():
            spine.set_color("#dfe7f1")
        ax.legend(frameon=False, fontsize=8)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_all_charts(self, run_result):
        for child in self.chart_holder.winfo_children():
            child.destroy()

        left = ttk.LabelFrame(self.chart_holder, text="Fuzzy Logic", padding=(10, 8), style="Card.TLabelframe")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        right = ttk.LabelFrame(self.chart_holder, text="Reinforcement Learning", padding=(10, 8), style="Card.TLabelframe")
        right.grid(row=0, column=1, sticky="nsew", pady=(0, 12))
        bottom = ttk.LabelFrame(self.chart_holder, text="Data Pipeline", padding=(10, 8), style="Card.TLabelframe")
        bottom.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.chart_holder.grid_rowconfigure(0, weight=1)
        self.chart_holder.grid_rowconfigure(1, weight=1)
        self.chart_holder.grid_columnconfigure(0, weight=1)
        self.chart_holder.grid_columnconfigure(1, weight=1)

        self._render_fuzzy_chart(left, run_result["temperature"])

        rewards = run_result.get("rl_rewards", [1] * run_result.get("rl_episodes", 1))
        self._render_chart_in_frame(right, "Rewards by Episode", list(range(1, len(rewards) + 1)), rewards, "Episode", "Reward", "#2563eb")

        processed = run_result.get("processed_data", [])

        def normalize_values(items):
            values = []
            for item in items:
                if isinstance(item, (int, float)):
                    values.append(float(item))
                elif isinstance(item, (list, tuple)):
                    for element in item:
                        if isinstance(element, (int, float)):
                            values.append(float(element))
                elif isinstance(item, dict):
                    for value in item.values():
                        if isinstance(value, (int, float)):
                            values.append(float(value))
            return values or [0.0]

        y_vals = normalize_values(processed)
        x_vals = list(range(len(y_vals)))

        fig = Figure(figsize=(10.5, 3.2), dpi=110, facecolor="#f8fafc")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#ffffff")
        ax.plot(x_vals, y_vals, marker="o", color="#10b981", linewidth=2.6, markersize=4)
        ax.fill_between(x_vals, y_vals, 0, color="#10b981", alpha=0.18)
        ax.set_title("Data Pipeline Output", fontsize=10, weight="bold", color="#1f2937")
        ax.set_xlabel("Sample index", fontsize=9, color="#475569")
        ax.set_ylabel("Transformed value", fontsize=9, color="#475569")
        ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.35, color="#dfe7f1")
        ax.tick_params(colors="#475569")
        for spine in ax.spines.values():
            spine.set_color("#dfe7f1")
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=bottom)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _set_result_text(self, text):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", text)
        self.result_box.configure(state="disabled")

    def _refresh_all(self):
        # Initial placeholder: build the 3-panel layout once so startup
        # looks the same as after "Run All Demo" (avoids rendering
        # a full-width chart directly into chart_holder).
        try:
            temp = int(self.temp_var.get())
        except Exception:
            temp = 22
        try:
            self._render_all_charts({
                "temperature": temp,
                "rl_rewards": [0.0],
                "rl_episodes": 1,
                "processed_data": [0.0],
            })
            self._set_result_text("Press Run All Demo to generate results and charts.")
        except Exception:
            pass

    def run_demo(self):
        try:
            temp_value = int(self.temp_var.get())
            rl_episodes = int(self.rl_var.get())
            data_points = int(self.data_count_var.get())
        except Exception:
            if messagebox is not None:
                messagebox.showerror("Invalid input", "Sliders returned an invalid value.")
            return
        data_method = self.method_var.get()

        try:
            result = run_demo(temp_value, rl_episodes, data_points, data_method)
        except Exception as exc:
            if messagebox is not None:
                messagebox.showerror("Demo failed", f"{type(exc).__name__}: {exc}")
            self._set_result_text(f"Demo failed: {exc}")
            return
        summary = (
            f"Fuzzy: {result['fuzzy_result']}\n"
            f"Temperature: {result['temperature']}°C\n"
            f"RL episodes: {result['rl_episodes']}\n"
            f"Data method: {result['data_method']}\n"
            f"Processed data points: {result['processed_items']}\n"
            f"Output folder: {result['output_path']}"
        )
        self._set_result_text(summary)
        try:
            self._render_all_charts(result)
        except Exception as exc:
            if messagebox is not None:
                messagebox.showerror("Chart failed", f"{type(exc).__name__}: {exc}")

    def open_output_folder(self):
        output_dir = Path(__file__).resolve().parent.parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(output_dir))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(output_dir)])
            else:
                subprocess.Popen(["xdg-open", str(output_dir)])
        except Exception as exc:
            if messagebox is not None:
                messagebox.showinfo("Output folder", str(output_dir) + "\n(" + str(exc) + ")")
            else:
                print(output_dir)


def console_demo():
    temperature = 22
    rl_episodes = 5
    data_points = 5
    data_method = "supervised"

    result = run_demo(temperature, rl_episodes, data_points, data_method)
    print(f"Fuzzy Logic System evaluated temperature: {result['fuzzy_result']}")
    print("Reinforcement Learning training completed.")
    print(f"Data generation and processing completed: {result['processed_items']} items processed.")
    output_path = result['output_path']
    print(f"Saved graphical outputs to: {output_path}")
    for key in ("fuzzy", "rl", "data"):
        print(f"- {result['files'][key].name}")


def launch_gui():
    """Open the GUI. Returns True if the GUI ran, False if it fell back."""
    if not TK_AVAILABLE:
        print("tkinter is not available. Install Python with 'tcl/tk and IDLE' checked.")
        print("Falling back to console demo...")
        console_demo()
        return False
    if FigureCanvasTkAgg is None:
        print("matplotlib Tk backend is missing. Run: pip install matplotlib")
        print("Falling back to console demo...")
        console_demo()
        return False
    try:
        app = DemoApp()
        app.mainloop()
        return True
    except Exception as exc:  # TclError = no display, plus any startup error
        print(f"Could not open GUI window ({type(exc).__name__}: {exc}).")
        print("Run from a normal Windows PowerShell/desktop session, not SSH/headless.")
        print("Falling back to console demo...")
        console_demo()
        return False


def main():
    parser = argparse.ArgumentParser(description="AI Systems Project")
    parser.add_argument("--gui", action="store_true", help="Open the graphical interface (default)")
    parser.add_argument("--console", action="store_true", help="Run console demo only, no window")
    parser.add_argument("--no-gui", action="store_true", help="Same as --console")
    args = parser.parse_args()

    # Default = GUI every time. Use --console / --no-gui for headless mode.
    if args.console or args.no_gui:
        console_demo()
        return

    launch_gui()


if __name__ == "__main__":
    main()