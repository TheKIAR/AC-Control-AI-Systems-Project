# AI Systems Project

A Python educational AI project that demonstrates four approaches:

- **Fuzzy logic** for temperature control
- **First-Order Predicate Logic (FOPL)** for a smart-room advisor
- **Q-learning-style reinforcement learning** in a small discrete environment
- **Data generation and processing** for supervised and unsupervised examples

The project includes a Tkinter/Matplotlib desktop GUI, a console mode, experiments, and automated tests.

## Features

### Fuzzy Logic
The temperature controller uses bounded membership functions for:

- Cold
- Comfortable
- Hot

It converts the strongest membership into an action:

| Temperature condition | Action |
|---|---|
| Cold | Increase Temperature |
| Comfortable | Maintain Temperature |
| Hot | Decrease Temperature |

### FOPL Smart-Room Advisor
The `src/fopl/` package contains a small forward-chaining knowledge base. It combines temperature bands with occupancy, night, and energy-saver facts to derive room-control actions and an explanation trace.

### Reinforcement Learning
The RL module contains:

- `RLAgent` — Q-table based agent
- `RLEnvironment` — discrete environment with a goal state
- `RLTrainer` — training and evaluation

Training rewards are retained so the GUI can plot them.

### Data-Driven Pipeline
The project includes deterministic supervised and unsupervised sample generation, cleaning, transformation, and JSON save/load support.

## Project Structure

```text
AI-Systems-Project/
├── assets/                 # Application assets
├── data/                   # Small checked-in sample data
├── docs/                   # Project documentation
├── experiments/            # Experiment notes
├── notebooks/              # Jupyter experiments
├── scripts/                # Optional shell launchers
├── src/
│   ├── common/
│   ├── data_driven/
│   ├── fopl/
│   ├── fuzzy_logic/
│   ├── reinforcement_learning/
│   └── main.py
├── tests/
├── requirements.txt
├── run_gui.py
├── run_gui.bat
├── run_gui.ps1
├── setup.py
└── README.md
```

## Requirements

- Python 3.10+
- Tkinter for the desktop GUI
- Dependencies listed in `requirements.txt`

## Run

Clone the repository, then:

```bash
python -m pip install -r requirements.txt
python run_gui.py
```

For console mode:

```bash
python run_gui.py --console
```

You can also run:

```bash
python src/main.py --console
```

The GUI lets you adjust temperature, RL episode count, data-point count, and the data-generation method. Running the demo generates charts and a text summary in the local `outputs/` directory.

## Testing

Run all tests with:

```bash
pytest
```

The tests cover fuzzy decisions and memberships, reinforcement-learning behavior, data generation/pipeline behavior, FOPL behavior, and visual-output generation.

## Windows Executable

The repository includes an application icon and Windows launcher scripts. If you want to distribute a standalone executable, build it locally with PyInstaller rather than committing the generated `build/` or `dist/` directories.

## Notes

This is an educational project rather than a production HVAC controller. The fuzzy and reinforcement-learning components are intentionally small so their algorithms can be inspected and studied easily.

Generated runtime output is ignored by Git. Keep credentials, API keys, and machine-specific configuration outside the repository.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
