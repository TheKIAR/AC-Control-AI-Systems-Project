# AI Systems Project

This project implements four different AI systems: a fuzzy logic-based system, a first-order-logic knowledge advisor, a reinforcement learning-based system, and a data-driven method for generating AI. Each system is designed to address specific tasks and challenges, showcasing the versatility of AI techniques.

## Project Structure

```
ai-systems-project
├── src
│   ├── fuzzy_logic          # Fuzzy logic system implementation
│   ├── fopl                 # FOPL smart-room advisor (knowledge base + forward chaining)
│   ├── reinforcement_learning # Reinforcement learning system implementation
│   ├── data_driven          # Data generation methods
│   ├── common               # Common utilities and configuration
│   └── main.py              # Entry point for the application
├── notebooks                # Jupyter notebooks for experiments
├── data                     # Data directories for raw and processed data
├── models                   # Directories for storing trained models
├── experiments              # Documentation for experiments conducted
├── tests                    # Unit tests for each system
├── scripts                  # Shell scripts to run each system
├── requirements.txt         # Project dependencies
├── setup.py                 # Packaging and dependency management
├── .gitignore               # Version control exclusions
└── README.md                # Project documentation
```

## Fuzzy Logic System

The fuzzy logic system is designed to control air conditioning using fuzzy logic principles. It includes:

- **FuzzySystem**: Implements the fuzzy logic control system.
- **Rules**: Defines fuzzy rules for decision-making.

## FOPL Smart-Room Advisor

A First-Order Predicate Logic system for room climate + energy policy
(`src/fopl/`: `knowledge_base.py` kernel with variables, negation and
forward chaining; `advisor.py` 13-rule policy). From temperature, occupancy,
night and energy-saver facts it derives actions (AC_HIGH/ECO/OFF/STANDBY,
heater, lights, blinds, windows, overheat alert) with a fired-rule
explanation trace. Temperature bands match the fuzzy controller.

## Reinforcement Learning System

The reinforcement learning system simulates an agent interacting with an environment. It includes:

- **RLAgent**: Implements the learning agent.
- **RLEnvironment**: Simulates the environment for the agent.
- **RLTrainer**: Manages the training process for the agent.

## Data-Driven Method

The data-driven method focuses on generating data using various techniques. It includes:

- **DataGenerator**: Implements methods for data generation.
- **Pipeline**: Defines the data processing pipeline.

## Getting Started

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd ai-systems-project
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   Pinned: `matplotlib==3.11.2`, `numpy==2.5.3`, `pytest==9.1.1`.

4. Run the app (GUI is default):
   ```
   python run_gui.py
   ```
   - Double-click `run_gui.py` or `run_gui.bat` (Windows) to open the GUI.
   - Console only (headless): `python run_gui.py --console` or `python src/main.py --console`

## GUI Layout

- **Header** with Dark/Light toggle (top-right) and in-memory app icon.
- **Controls** (full width): Fuzzy temperature (10–35), RL episodes (1–20),
  Data points (3–20) sliders each with −/+ steppers + Data method combo +
  Room-state checkboxes (Occupied / Night / Energy saver, feeding the FOPL
  advisor) + one-click presets (Cold 14° / Normal 22° / Heat 32°) +
  full-width `Run All Demo` button + `Reset` button + `Enter` key shortcut.
  Runs execute in background with a determinate progress bar, so the GUI
  never freezes.
- **Output Summary** dark card with Fuzzy decision, RL avg/best reward,
  data min/max/mean, FOPL action count, run time — plus `Export Report (.zip)`.
- **Outputs stacked full-width, one per line:**
  1. Fuzzy Logic — blue→green→red gradient + dotted temp line with label
     (live preview when the temperature slider moves).
  2. Reinforcement Learning — Rewards by Episode.
  3. Data Pipeline — Transformed values.
  4. Logic (FOPL) — advisor conclusions + fired-rule trace.

All runs also save PNGs + `summary.txt` + `logic_inference.txt` to `outputs/`:
`fuzzy_system.png`, `reinforcement_learning.png`, `data_pipeline.png`.

## Share as .exe (Windows)

No Python needed on the other PC. Build from the project folder:

```
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name AISystemsProject --paths src --icon assets\app.ico --hidden-import matplotlib.backends.backend_tkagg --exclude-module torch --exclude-module tensorflow --exclude-module keras --exclude-module sklearn --exclude-module scipy --exclude-module pandas --exclude-module IPython --exclude-module notebook --exclude-module jedi run_gui.py
```

Double-click `dist\AISystemsProject.exe` (~39MB). First launch takes
10–20s. `outputs/` and `AI-Systems-Report-*.zip` files are created next
to the exe.

## Experiments

Refer to the `notebooks` directory for Jupyter notebooks containing experiments and results related to each AI system.

## Testing

Unit tests are provided in the `tests` directory. You can run the tests using:
```
pytest tests/
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.