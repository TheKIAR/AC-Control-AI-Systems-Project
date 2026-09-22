"""Basic GUI launcher. Double-click or run: python run_basic.py"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _resource_path(*parts):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base).joinpath(*parts)
    return ROOT.joinpath(*parts)


def _apply_basic_icon(window):
    try:
        png = _resource_path("assets", "app_basic.png")
        if png.exists():
            img = tk.PhotoImage(file=str(png))
            window.iconphoto(True, img)
            window._icon_image = img
            return True
    except Exception:
        pass
    try:
        ico = _resource_path("assets", "app_basic.ico")
        if ico.exists():
            window.iconbitmap(str(ico))
            return True
    except Exception:
        pass
    return False

try:
    import tkinter as tk
    TK_AVAILABLE = True
except ImportError:
    tk = None
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
    from fopl.advisor import build_advisor
    from reinforcement_learning.agent import RLAgent
    from reinforcement_learning.env import RLEnvironment
    from reinforcement_learning.trainer import RLTrainer
    from data_driven.generator import DataGenerator
    from data_driven.pipeline import DataPipeline
    from version import __version__ as APP_VERSION
except ImportError:
    from src.fuzzy_logic.fuzzy_system import FuzzySystem
    from src.fopl.advisor import build_advisor
    from src.reinforcement_learning.agent import RLAgent
    from src.reinforcement_learning.env import RLEnvironment
    from src.reinforcement_learning.trainer import RLTrainer
    from src.data_driven.generator import DataGenerator
    from src.data_driven.pipeline import DataPipeline
    try:
        from version import __version__ as APP_VERSION
    except ImportError:
        try:
            from src.version import __version__ as APP_VERSION
        except ImportError:
            APP_VERSION = "1.0.0"


def compute(temperature=22, episodes=5, points=5, method="supervised",
            occupied=True, night=False, energy_saver=False):
    """Run all four modules once, return plain values (no GUI, no plots)."""
    fuzzy = FuzzySystem()
    fuzzy.set_temperature(temperature)
    fuzzy_result = fuzzy.evaluate(temperature)

    env = RLEnvironment()
    agent = RLAgent(action_space=[0, 1])
    trainer = RLTrainer(agent, env)
    trainer.train(episodes=episodes, max_steps=100)
    rewards = [float(r) for r in trainer.rewards]

    generator = DataGenerator(method=method)
    raw = generator.generate_data(num_samples=points)
    processed = DataPipeline(raw).process(raw)
    flat = []
    for item in processed:
        if isinstance(item, bool):
            continue
        if isinstance(item, (int, float)):
            flat.append(float(item))
        elif isinstance(item, (list, tuple)):
            flat.extend(float(v) for v in item
                        if isinstance(v, (int, float)) and not isinstance(v, bool))
    flat = flat or [0.0]

    advisor = build_advisor(temperature, occupied=occupied, night=night,
                              energy_saver=energy_saver)

    return {
        "temperature": temperature,
        "episodes": episodes,
        "points": points,
        "method": method,
        "fuzzy_result": fuzzy_result,
        "rewards": rewards,
        "best": max(rewards),
        "average": sum(rewards) / len(rewards),
        "count": len(flat),
        "flat": flat,
        "minimum": min(flat),
        "maximum": max(flat),
        "mean": sum(flat) / len(flat),
        "band": advisor.get("band", "?"),
        "conclusions": advisor.get("conclusions", []),
        "occupied": occupied,
        "night": night,
        "energy_saver": energy_saver,
    }


def format_result(result):
    lines = [
        f"Temperature : {result['temperature']} C  ->  {result['fuzzy_result']}",
        f"Room band   : {result['band']}  "
        f"(occupied={result.get('occupied', True)}, "
        f"night={result.get('night', False)}, "
        f"saver={result.get('energy_saver', False)})",
        f"Policy      : {', '.join(result['conclusions']) or 'no actions'}",
        "",
        f"RL episodes : {result['episodes']}  |  best {result['best']:.2f}  |  "
        f"average {result['average']:.2f}",
        "Rewards     : " + ", ".join(f"{r:.2f}" for r in result["rewards"]),
        "",
        f"Data        : {result['points']} points ({result['method']})  |  "
        f"n={result['count']}  min={result['minimum']:.2f}  "
        f"max={result['maximum']:.2f}  mean={result['mean']:.2f}",
    ]
    return "\n".join(lines)


class BasicApp(tk.Tk):
    """Plain white GUI: basic controls on top, charts plus text below."""

    def __init__(self):
        super().__init__()
        self.title(f"AI Systems Project (Basic) v{APP_VERSION}")
        self.geometry("1020x760")
        self.minsize(760, 600)
        self.configure(bg="#ffffff")

        self.temp_var = tk.IntVar(value=22)
        self.rl_var = tk.IntVar(value=5)
        self.data_var = tk.IntVar(value=5)
        self.method_var = tk.StringVar(value="supervised")
        self.occupied_var = tk.BooleanVar(value=True)
        self.night_var = tk.BooleanVar(value=False)
        self.saver_var = tk.BooleanVar(value=False)

        panel = tk.Frame(self, bg="#ffffff")
        panel.pack(fill="x", padx=12, pady=12)

        self._row(panel, "Temperature (10-35 C):", self.temp_var, 10, 35)
        self._row(panel, "RL episodes (1-20):", self.rl_var, 1, 20)
        self._row(panel, "Data points (3-20):", self.data_var, 3, 20)

        method_row = tk.Frame(panel, bg="#ffffff")
        method_row.pack(fill="x", pady=2)
        tk.Label(method_row, text="Data method:", bg="#ffffff", fg="#000000",
                 width=22, anchor="w").pack(side="left")
        tk.OptionMenu(method_row, self.method_var, "supervised", "unsupervised").pack(side="left")

        advisor_row = tk.Frame(panel, bg="#ffffff")
        advisor_row.pack(fill="x", pady=2)
        tk.Label(advisor_row, text="Room (FOPL advisor):", bg="#ffffff", fg="#000000",
                 width=22, anchor="w").pack(side="left")
        for text, var in (("Occupied", self.occupied_var),
                          ("Night", self.night_var),
                          ("Energy saver", self.saver_var)):
            tk.Checkbutton(advisor_row, text=text, variable=var,
                           command=self.run_all,
                           bg="#ffffff", fg="#000000",
                           selectcolor="#dddddd",
                           activebackground="#ffffff",
                           activeforeground="#000000").pack(side="left", padx=(0, 12))

        buttons = tk.Frame(panel, bg="#ffffff")
        buttons.pack(fill="x", pady=(10, 0))
        tk.Button(buttons, text="Run", width=12,
                  command=self.run_all).pack(side="left")
        tk.Button(buttons, text="Reset", width=12,
                  command=self.reset_all).pack(side="left", padx=(8, 0))

        self.output = tk.Text(self, height=10, wrap="word", bg="#ffffff",
                              fg="#000000", relief="solid", borderwidth=1)
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.output.insert("1.0", "Press Run to evaluate all four AI modules.")
        self.output.configure(state="disabled")

        charts = tk.Frame(self, bg="#ffffff")
        charts.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for column in range(3):
            charts.grid_columnconfigure(column, weight=1, uniform="basic")
        self.fuzzy_host = tk.Frame(charts, bg="#ffffff")
        self.fuzzy_host.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self.rl_host = tk.Frame(charts, bg="#ffffff")
        self.rl_host.grid(row=0, column=1, sticky="nsew", padx=6)
        self.data_host = tk.Frame(charts, bg="#ffffff")
        self.data_host.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        led_frame = tk.Frame(self, bg="#ffffff", relief="solid", borderwidth=1)
        led_frame.pack(fill="x", padx=12, pady=(0, 12))
        tk.Label(led_frame, text="FOPL POLICY", bg="#ffffff", fg="#555555",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=8, pady=(6, 2))
        led_row = tk.Frame(led_frame, bg="#ffffff")
        led_row.pack(fill="x", padx=8, pady=(0, 8))
        led_row.grid_columnconfigure(tuple(range(11)), weight=1, uniform="leds")
        self._leds = {}
        for col, (predicate, short, color) in enumerate((
            ("AC_HIGH", "HIGH", "#0099cc"),
            ("AC_ECO", "ECO", "#007700"),
            ("AC_OFF", "A-OFF", "#555555"),
            ("AC_STANDBY", "STBY", "#0000cc"),
            ("HEATER_ON", "HEAT", "#cc5500"),
            ("HEATER_OFF", "H-OFF", "#555555"),
            ("LIGHTS_OFF", "L-OFF", "#555555"),
            ("DIM_LIGHTS", "DIM", "#997700"),
            ("BLINDS_DOWN", "BLIND", "#6600cc"),
            ("WINDOWS_OPEN", "WIN", "#007700"),
            ("ALERT_OVERHEAT", "ALERT", "#cc0000"),
        )):
            cell = tk.Frame(led_row, bg="#ffffff")
            cell.grid(row=0, column=col, sticky="nsew")
            dot = tk.Canvas(cell, bg="#ffffff", width=22, height=22,
                            highlightthickness=0, bd=0)
            dot.pack()
            item = dot.create_oval(4, 4, 18, 18, fill="#ffffff",
                                   outline="#888888", width=2)
            tk.Label(cell, text=short, bg="#ffffff", fg="#555555",
                     font=("Consolas", 7, "bold")).pack()
            self._leds[predicate] = (dot, item, color)

        self.run_all()
        try:
            self.update_idletasks()
        except Exception:
            pass
        _apply_basic_icon(self)

    def _plain_figure(self, title):
        fig = Figure(figsize=(3.1, 2.6), dpi=100, facecolor="#ffffff")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#ffffff")
        ax.set_title(title, fontsize=10, color="#000000")
        ax.tick_params(colors="#000000", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#888888")
        return fig, ax

    def _show_figure(self, host, fig):
        for child in host.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        if not FIGURE_AVAILABLE:
            tk.Label(host, text="(charts need matplotlib)", bg="#ffffff",
                     fg="#000000").pack(expand=True)
            return
        canvas = FigureCanvasTkAgg(fig, master=host)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    def _draw_charts(self, result):
        levels = {"Increase Temperature": 1, "Maintain Temperature": 2,
                  "Decrease Temperature": 3}
        system = FuzzySystem()
        temps = [16, 18, 20, 22, 24, 26, 28, 30]
        values = [levels[system.evaluate(t)] for t in temps]
        fig, ax = self._plain_figure("Fuzzy decisions")
        bars = ax.bar(temps, values,
                      color=["#000000" if t == result["temperature"] else "#999999"
                             for t in temps],
                      edgecolor="#ffffff", linewidth=0.6)
        ax.set_xlabel("Temperature (C)", fontsize=8, color="#000000")
        ax.set_ylabel("Decision", fontsize=8, color="#000000")
        ax.set_yticks([1, 2, 3])
        ax.set_yticklabels(["Increase", "Maintain", "Decrease"], fontsize=7)
        ax.grid(axis="y", linestyle=":", alpha=0.5, color="#888888")
        headline = {"Increase Temperature": "▲ INCREASE",
                    "Maintain Temperature": "● MAINTAIN",
                    "Decrease Temperature": "▼ DECREASE"}[result["fuzzy_result"]]
        # Pinned top-left above headroom the bars never reach (all tall
        # Decrease bars stand on the right), so the verdict can never hide
        # behind a bar the way a centered overlay did.
        ax.set_ylim(0, 3.7)
        ax.text(15.8, 3.32, headline, ha="left", va="center",
                fontsize=12, fontweight="bold", color="#000000")
        # Exact-temperature marker: bar highlighting only lands on even
        # temperatures, so odd inputs (e.g. 23) showed nothing. This dashed
        # line always marks precisely where the input is.
        ax.axvline(result["temperature"], color="#000000", linestyle="--",
                   linewidth=1.5)
        fig.tight_layout()
        self._show_figure(self.fuzzy_host, fig)

        rewards = result["rewards"]
        episodes = list(range(1, len(rewards) + 1))
        average = sum(rewards) / len(rewards)
        best_i = max(range(len(rewards)), key=lambda i: rewards[i])
        fig, ax = self._plain_figure("RL rewards")
        ax.plot(episodes, rewards, marker="o", color="#0000cc", label="reward")
        ax.axhline(average, linestyle="--", color="#888888", linewidth=1.2,
                   label=f"average {average:.2f}")
        ax.scatter([episodes[best_i]], [rewards[best_i]], color="#000000",
                   s=80, zorder=5, label=f"best {rewards[best_i]:.2f}")
        ax.scatter([episodes[best_i]], [rewards[best_i]], color="#0000cc",
                   s=34, zorder=6)
        ax.set_xlabel("Episode", fontsize=8, color="#000000")
        ax.set_ylabel("Reward", fontsize=8, color="#000000")
        ax.grid(True, linestyle="--", alpha=0.4, color="#888888")
        ax.legend(fontsize=7, loc="best", framealpha=0.9)
        fig.tight_layout()
        self._show_figure(self.rl_host, fig)

        y_values = result.get("flat", [0.0])
        mean_val = sum(y_values) / len(y_values)
        fig, ax = self._plain_figure("Data output")
        ax.plot(list(range(len(y_values))), y_values, marker="o", color="#007700",
                label="value")
        ax.axhline(mean_val, linestyle="--", color="#888888", linewidth=1.2,
                   label=f"mean {mean_val:.2f}")
        ax.set_xlabel("Sample", fontsize=8, color="#000000")
        ax.set_ylabel("Value", fontsize=8, color="#000000")
        ax.grid(True, linestyle="--", alpha=0.4, color="#888888")
        ax.legend(fontsize=7, loc="best", framealpha=0.9)
        fig.tight_layout()
        self._show_figure(self.data_host, fig)

    def _row(self, parent, label, variable, minimum, maximum):
        row = tk.Frame(parent, bg="#ffffff")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, bg="#ffffff", fg="#000000",
                 width=22, anchor="w").pack(side="left")
        tk.Scale(row, from_=minimum, to=maximum, orient="horizontal",
                 variable=variable, bg="#ffffff", fg="#000000",
                 highlightthickness=0, length=300).pack(side="left")
        tk.Label(row, textvariable=variable, bg="#ffffff", fg="#000000",
                 width=4).pack(side="left")

    def _show(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")

    def run_all(self):
        try:
            result = compute(int(self.temp_var.get()), int(self.rl_var.get()),
                             int(self.data_var.get()), self.method_var.get(),
                             occupied=bool(self.occupied_var.get()),
                             night=bool(self.night_var.get()),
                             energy_saver=bool(self.saver_var.get()))
        except Exception as exc:
            self._show(f"Error: {type(exc).__name__}: {exc}")
            return
        self._show(format_result(result))
        try:
            self._draw_charts(result)
        except Exception as exc:
            self._show(format_result(result) + f"\n\nCharts unavailable: {exc}")
        try:
            active = set()
            for conclusion in result["conclusions"]:
                active.add(conclusion.split("(")[0])
            for predicate, (canvas, item, color) in self._leds.items():
                if predicate in active:
                    canvas.itemconfig(item, fill=color, outline=color)
                else:
                    canvas.itemconfig(item, fill="#ffffff", outline="#888888")
        except Exception:
            pass

    def reset_all(self):
        self.temp_var.set(22)
        self.rl_var.set(5)
        self.data_var.set(5)
        self.method_var.set("supervised")
        self.occupied_var.set(True)
        self.night_var.set(False)
        self.saver_var.set(False)
        self.run_all()


def main():
    if not TK_AVAILABLE:
        print("tkinter is not available.")
        print(format_result(compute()))
        return False
    try:
        app = BasicApp()
        app.mainloop()
        return True
    except Exception as exc:
        print(f"Could not open basic GUI ({type(exc).__name__}: {exc}).")
        print(format_result(compute()))
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
