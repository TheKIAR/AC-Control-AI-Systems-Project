# AI Systems Project — Final Report (CSE-334, Primeasia University)

> Course final project (open-ended, original work). This draft is mapped to the
> four marking tasks (5 marks each per problem). Problems solved: **P1** fuzzy
> AC control, **P2** FOPL smart-room advisor, **P3** RL setpoint tracking,
> **P4** data-driven generation (any three satisfy the brief; the fourth is
> included as extension). Edit names/IDs/date before submitting on 24.09.26.

---

## 1. Task 1 — Information collected and prepared (5)

**Problem domain.** A single study room / classroom served by one split AC
unit. Goal: comfort (20–24°C), low energy waste, basic safety. This one room
ties all four methods together, so results are comparable.

**Information gathered.**
- Comfort band 20–24°C (matches the fuzzy controller thresholds in
  `src/fuzzy_logic/rules.py`); heat-stress concern above ~33°C.
- Room sensors assumed: temperature (°C), occupancy (PIR), clock (night flag),
  energy-saver switch — the four inputs on the app's Controls panel.
- RL environment model (`src/reinforcement_learning/env.py`): states 0–5
  (cold → comfort goal), actions {cooler+, cooler−}, shaped reward peaking at
  the goal state — a thermostat setpoint-tracking simulation.
- Data: synthetic supervised triples `(i, i+1, i%2)` and unsupervised pairs
  `[i, i²]` from `src/data_driven/generator.py`, cleaned/transformed by
  `src/data_driven/pipeline.py`.

**Preparation.** Sensor ranges validated in-GUI (sliders clamp: temp 10–35,
episodes 1–20, points 3–20); pipeline drops `None` entries; FOPL bands reuse
the fuzzy thresholds so the methods agree on what "hot" means.

## 2. Task 2 — Method built and applied (5)

### P1 — Fuzzy logic AC control (`src/fuzzy_logic/`)
Triangular membership over Low/Neutral(≈22°C)/High zones; rules such as
*cool → Increase Temperature, warm → Decrease, stable → Maintain*.
GUI output 1 shows the blue→green→red zone gradient with the dotted input line.

### P2 — FOPL smart-room advisor (`src/fopl/`) ⭐ new
A genuine first-order kernel (`knowledge_base.py`: variables, atoms with ¬,
Horn-style rules, grounding over constants, forward chaining to fixpoint with
negation-as-failure) plus a 13-rule room policy (`advisor.py`), e.g.
`∀r. Hot(r) ∧ Occupied(r) ∧ ¬EnergySaver(r) → AC_HIGH(r)`.
Sensor facts are asserted per run; every conclusion ships with the fired-rule
trace (GUI output 4 + `outputs/logic_inference.txt`). Safety override:
`ExtremeHeat ≥ 33°C → ALERT_OVERHEAT`.

### P3 — Reinforcement learning (`src/reinforcement_learning/`)
Q-learning-style agent (`agent.py`) in the thermostat environment; trainer
runs N episodes (GUI slider). Output 2 plots reward per episode — the agent
learns to reach and hold the comfort goal. Real-world reading: the same loop
drives smart-thermostat setpoint schedules.

### P4 — Data-driven method (`src/data_driven/`)
Supervised vs unsupervised generation + clean/transform pipeline; output 3
plots transformed values with min/max/mean in the summary. Real-world reading:
synthetic sensor-data augmentation for training when labelled data is scarce.

**Integration.** One `Run All Demo` executes all four (background thread +
progress bar), saves `outputs/*.png`, `summary.txt`, `logic_inference.txt`,
and one-click `Export Report (.zip)`. 22 automated tests (`pytest tests/`).

## 3. Task 3 — Analysis and real-world findings (5)

| Observation (from the app) | Real-world meaning |
|---|---|
| 32°C + occupied → `AC_HIGH`; +saver → `AC_ECO` | Policy tradeoff: comfort vs energy, switchable at runtime |
| 32°C + empty → `AC_OFF, BLINDS_DOWN, LIGHTS_OFF` | Biggest saving is *not cooling empty rooms* — occupancy sensing pays off |
| Warm empty daytime → `WINDOWS_OPEN` | Free cooling beats compressor use in shoulder weather |
| RL reward curve rises then plateaus | Thermostat agent converges; extra episodes give diminishing returns |
| Supervised vs unsupervised outputs differ in shape | Labelled data gives predictable pipelines; unlabelled needs inspection |

**Cross-method finding:** fuzzy gives *smooth* control, FOPL gives
*explainable* policy (every action cites its rule), RL gives *adaptive*
behaviour, data-driven gives *test data*. Together: FOPL policy as the safety
wrapper, fuzzy/RL for actuation, synthetic data for testing — a realistic
smart-building stack.

## 4. Task 4 — Presentation, demo script and likely queries (5)

**60-second demo.** Open `dist\AISystemsProject.exe` → press
`🔥 Heat 32°` preset → watch progress bar → point at outputs 1–4 →
toggle `Energy saver` and re-run to show `AC_HIGH → AC_ECO` →
`Export Report (.zip)` for submission evidence.

**Likely questions.**
- *Why both fuzzy and FOPL?* Fuzzy handles vagueness ("rather warm");
  FOPL handles crisp policy/safety with explanations. Demo: 23.5°C.
- *What does ¬ mean / open vs closed world?* Negation-as-failure: we assume
  closed rooms/sensors (report states the assumption + its limits).
- *Does RL guarantee optimal control?* No — it converges empirically here
  (reward curve); FOPL safety rules bound its authority in a real deployment.
- *Where is the AI "generated" from data?* P4 pipeline: generator →
  clean → transform; outputs feed the chart + stats, reusable as training data.
- *Originality?* All code, rules, thresholds and UI written for this course;
  no copied blocks; tests prove the behaviour.

## Files mapping to marks

- Task 1: this section + `src/common/config.py`, GUI input validation.
- Task 2: `src/fuzzy_logic/`, `src/fopl/`, `src/reinforcement_learning/`,
  `src/data_driven/`, `src/main.py`, `tests/` (22 passing).
- Task 3: tables above; reproduce via presets + `outputs/`.
- Task 4: demo script above; deliver `AI-Systems-Report-*.zip` + this report.
