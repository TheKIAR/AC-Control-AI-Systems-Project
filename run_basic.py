"""Basic GUI launcher. Double-click or run: python run_basic.py"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
for p in (str(SRC), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import tkinter as tk
    TK_AVAILABLE = True
except ImportError:
    tk = None
    TK_AVAILABLE = False

try:
    from fuzzy_logic.fuzzy_system import FuzzySystem
    from fopl.advisor import build_advisor
    from reinforcement_learning.agent import RLAgent
    from reinforcement_learning.env import RLEnvironment
    from reinforcement_learning.trainer import RLTrainer
    from data_driven.generator import DataGenerator
    from data_driven.pipeline import DataPipeline
except ImportError:
    from src.fuzzy_logic.fuzzy_system import FuzzySystem
    from src.fopl.advisor import build_advisor
    from src.reinforcement_learning.agent import RLAgent
    from src.reinforcement_learning.env import RLEnvironment
    from src.reinforcement_learning.trainer import RLTrainer
    from src.data_driven.generator import DataGenerator
    from src.data_driven.pipeline import DataPipeline


def compute(temperature=22, episodes=5, points=5, method="supervised"):
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

    advisor = build_advisor(temperature, occupied=True)

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
        "minimum": min(flat),
        "maximum": max(flat),
        "mean": sum(flat) / len(flat),
        "band": advisor.get("band", "?"),
        "conclusions": advisor.get("conclusions", []),
    }


def format_result(result):
    lines = [
        f"Temperature : {result['temperature']} C  ->  {result['fuzzy_result']}",
        f"Room band   : {result['band']}",
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
    """Plain white GUI: basic controls on top, plain text results below."""

    def __init__(self):
        super().__init__()
        self.title("AI Systems Project (Basic)")
        self.geometry("640x560")
        self.minsize(520, 480)
        self.configure(bg="#ffffff")

        self.temp_var = tk.IntVar(value=22)
        self.rl_var = tk.IntVar(value=5)
        self.data_var = tk.IntVar(value=5)
        self.method_var = tk.StringVar(value="supervised")

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

        buttons = tk.Frame(panel, bg="#ffffff")
        buttons.pack(fill="x", pady=(10, 0))
        tk.Button(buttons, text="Run", width=12,
                  command=self.run_all).pack(side="left")
        tk.Button(buttons, text="Reset", width=12,
                  command=self.reset_all).pack(side="left", padx=(8, 0))

        self.output = tk.Text(self, height=20, wrap="word", bg="#ffffff",
                              fg="#000000", relief="solid", borderwidth=1)
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.output.insert("1.0", "Press Run to evaluate all four AI modules.")
        self.output.configure(state="disabled")

        self.run_all()

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
                             int(self.data_var.get()), self.method_var.get())
        except Exception as exc:
            self._show(f"Error: {type(exc).__name__}: {exc}")
            return
        self._show(format_result(result))

    def reset_all(self):
        self.temp_var.set(22)
        self.rl_var.set(5)
        self.data_var.set(5)
        self.method_var.set("supervised")
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
