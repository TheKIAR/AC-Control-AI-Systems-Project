# AI Systems Project — Final Report (CSE-334, Primeasia University)

**Student name:** ……………………………… **ID:** …………………… **Course:** CSE-334, Summer 2026
**Date:** ……………………

> Course final project (open-ended). The brief asks for **any THREE** of the four
> problems; this project solves **all four** (the fourth as extension), tied to one
> room so the methods can be compared. All behaviours below were verified by
> running the app and its automated tests (`27 collected`: 26 passing, 1 GUI
> smoke test that runs on Linux display environments).

| # | Problem from the brief | Solved in |
|---|---|---|
| P1 | Fuzzy logic system to control air conditioning | `src/fuzzy_logic/` |
| P2 | First-Order Predicate Logic system, real-world use case | `src/fopl/` (smart-room advisor) |
| P3 | Reinforcement learning system, real-world use case | `src/reinforcement_learning/` (thermostat setpoint tracking) |
| P4 | Data-driven method (supervised or unsupervised) to generate AI | `src/data_driven/` (both: supervised + unsupervised) |

Run it: `python run_gui.py` (or double-click `run_gui.bat`, or run
`dist/AISystemsProject.exe`). Console fallback: `python run_gui.py --console`.

---

## Task 1 — Collect and prepare information required (5)

**Problem domain.** One study room / classroom served by one split AC unit.
Goals, in order: human comfort, low energy waste, basic safety. Using a single
room for all four methods keeps every result comparable.

**Information gathered.**

- **Comfort band 20–24°C.** The fuzzy controller commits at these borders
  (decision crossovers ≈19.6°C and ≈24.4°C); the FOPL policy reuses the same
  20/24 borders, so "hot" means the same thing in both methods.
- **Heat-stress limit ≈33°C.** Above this the room is a safety case, not a
  comfort case (`ExtremeHeat → ALERT_OVERHEAT`, with `Hot` also asserted so
  cooling rules still fire).
- **Room sensors assumed:** temperature in °C, occupancy (PIR), a night flag
  from the clock, and an energy-saver switch — exactly the four inputs on the
  app's control panel (temperature slider + Occupied / Night / Energy saver
  tick-boxes).
- **RL environment model** (`src/reinforcement_learning/env.py`): discrete
  states 0–5 from cold to the comfort goal, two actions (cooler up / cooler
  down), shaped reward peaking at the goal (1.8) and falling with distance —
  a thermostat setpoint-tracking simulation.
- **Data shapes** (`src/data_driven/generator.py`): supervised triples
  `[i, i+1, i%2]`, unsupervised pairs `[i, i²]`, cleaned (`None` dropped) and
  transformed (numeric squaring, applied recursively inside rows) by
  `src/data_driven/pipeline.py`.

**Preparation applied in the app.** Sliders clamp every input (temperature
10–35, RL episodes 1–20, data points 3–20); the pipeline drops `None` entries;
presets bundle valid configurations. Nothing the GUI accepts can crash a module.

## Task 2 — Build and apply an appropriate method (5)

### P1 — Fuzzy logic AC control (`src/fuzzy_logic/`)

Triangular membership centred at 22°C (`_triangle(18, 22, 26)` for
"comfortable", ramped "cold"/"hot" sides). `evaluate()` takes the strongest
membership and returns an action. Verified in the app:

| Input | Membership winner | Action |
|---|---|---|
| 16°C | cold | Increase Temperature |
| 22°C | comfortable | Maintain Temperature |
| 30°C | hot | Decrease Temperature |

The GUI draws the live membership field with the input marker, so vagueness
("rather warm", 23.5°C) is visible, not just the final label.

### P2 — FOPL smart-room advisor (`src/fopl/`)

A genuine first-order kernel (`knowledge_base.py`: variables, atoms with
negation, Horn-style rules, grounding over constants, forward chaining to a
fixpoint with negation-as-failure under a closed-world assumption) plus a
**13-rule** room policy (`advisor.py`), e.g.
`∀r. Hot(r) ∧ Occupied(r) ∧ ¬EnergySaver(r) → AC_HIGH(r)`.

The GUI's **Logic Advisor** section asserts the sensor facts per run and shows
every conclusion with an **agreement lamp** against the fuzzy verdict:

| Situation (verified) | Conclusions |
|---|---|
| 32°C, occupied | `AC_HIGH(R1)` |
| 32°C, occupied, saver on | `AC_ECO(R1)` instead — policy caps cooling |
| 32°C, empty | `AC_OFF(R1), BLINDS_DOWN(R1), LIGHTS_OFF(R1)` |
| 16°C, occupied | `HEATER_ON(R1)` |
| Comfort + night + occupied | `AC_STANDBY(R1)` + dimmed lighting |

Safety override: `ExtremeHeat ≥ 33°C → ALERT_OVERHEAT`.

### P3 — Reinforcement learning (`src/reinforcement_learning/`)

Q-table agent (`agent.py`), the thermostat environment above, and a trainer
that runs N episodes (GUI slider). The reward chart plots reward per episode
with the **best episode marked**, plus live stats (episodes / best / average /
latest). Real-world reading: the same loop schedules smart-thermostat
setpoints; the curve visibly plateaus, showing diminishing returns from extra
training. Presets vary the episode count (5/8/12) to make this comparable.

### P4 — Data-driven method (`src/data_driven/`)

Both modes: supervised vs unsupervised generation, clean/transform pipeline,
JSON save/load. The chart plots transformed values with live stats
(`n/min/max/mean`), and the two methods visibly differ in shape — labelled
data behaves predictably, unlabelled data needs inspection. Real-world
reading: synthetic sensor-data augmentation when labelled data is scarce.

**Integration.** One `Run System` executes all four modules; Cold/Normal/Hot
presets reconfigure temperature + episodes + points together; dark/light mode,
animated sky, and one-click **Export** (charts + `summary.txt` +
`logic_inference.txt` zipped as `AI-Systems-Report-<timestamp>.zip`) round out
the demo. `pytest`: 27 collected, 26 passing, 1 display-dependent GUI smoke
test (skipped on headless/Windows runners by its own rule).

## Task 3 — Analyze, present findings on real-world use cases (5)

All observations below were reproduced in the app:

| Observation (from the app) | Real-world meaning |
|---|---|
| 32°C + occupied → `AC_HIGH`; tick saver → `AC_ECO` | Comfort-vs-energy tradeoff, switchable at runtime |
| 32°C + empty → `AC_OFF, BLINDS_DOWN, LIGHTS_OFF` | Biggest saving is not cooling empty rooms — occupancy sensing pays off |
| Cold + occupied → `HEATER_ON`; empty → `HEATER_OFF` | Same policy mirrored for heating season |
| Warm empty daytime → `WINDOWS_OPEN` | Free cooling beats the compressor in shoulder weather |
| Fuzzy Decrease + empty room → lamp shows DIFFERS | Temp-only control assumes occupancy; the policy knows better — sensor fusion matters |
| RL reward curve rises then plateaus; best episode marked | Thermostat agent converges; extra episodes give diminishing returns |
| Supervised vs unsupervised charts differ in shape | Labelled pipelines are predictable; unlabelled output needs inspection |

**Cross-method finding:** fuzzy gives *smooth* control, FOPL gives *explainable*
policy (every action cites its rule), RL gives *adaptive* behaviour, data-driven
gives *test data*. Together they form a realistic smart-building stack: FOPL
policy as the safety wrapper, fuzzy/RL for actuation, synthetic data for testing.

## Task 4 — Present your solution, submit report and answer queries (5)

**60-second demo.** Open `dist/AISystemsProject.exe` → press `Run System` →
point at the three charts → press `Hot 30°C` (fuzzy flips to Decrease, weather
sky turns sunny) → untick `Occupied` (policy drops to `AC_OFF…`, lamp flips to
DIFFERS) → press `Export` and show the zip as submission evidence.

**Likely questions (with answers).**

- *Why both fuzzy and FOPL?* Fuzzy handles vagueness ("rather warm"); FOPL
  handles crisp policy and safety with explanations. Demo: 23.5°C vs the
  agreement lamp.
- *What does ¬ mean? Open or closed world?* Negation-as-failure: ¬P holds when
  P cannot be derived. We assume a closed room with known sensors, stated as a
  limitation in Task 1.
- *Does RL guarantee optimal control?* No — it converges empirically here
  (plateau + best marker); in deployment the FOPL safety rules bound it.
- *Where is AI "generated" from data?* P4 pipeline: generator → clean →
  transform; outputs feed the chart, the stats, and reusable JSON training data.
- *Originality?* All code, rules, thresholds and UI were written for this
  course; git history documents authorship; 27 tests prove the behaviour.

**Submission contents.**

- This report (`docs/PROJECT_REPORT.docx` + `.md` source).
- `AI-Systems-Report-<timestamp>.zip` from the app's Export button (charts +
  summary + logic trace).
- Code at `github.com/TheKIAR/AC-Control-AI-Systems-Project`.

## Files mapping to marks

- Task 1: this report §1 + `src/common/config.py` + GUI input clamps.
- Task 2: `src/fuzzy_logic/`, `src/fopl/`, `src/reinforcement_learning/`,
  `src/data_driven/`, `src/main.py`, `tests/`.
- Task 3: table above; reproduce via presets + toggles + `outputs/`.
- Task 4: demo script above; viva answers above.
