# Viva Demo Map — which button answers which question

Run `dist/AISystemsProject.exe` (or `python run_gui.py`). Every answer below
is a visible click, not just words.

## Fuzzy logic (P1)

- **"Show it working"** → drag the temperature slider, or press the
  `Cold 16°C` / `Normal 22°C` / `Hot 30°C` preset buttons. The headline flips
  ▲ INCREASE / ● MAINTAIN / ▼ DECREASE and the dotted marker glides.
- **"What about vague values?"** → set 23–24°C. Membership is split, the
  strongest wins — point at the gradient field behind the marker.

## FOPL policy (P2)

- **"Show a rule firing"** → set 30°C with Occupied ticked: the `AC_HIGH`
  LED lights.
- **"What does the saver switch do?"** → tick `Energy saver`: `AC_HIGH`
  drops out, `AC_ECO` lights. That is `¬EnergySaver` (negation-as-failure:
  assumed absent unless the box is ticked — the closed-world assumption).
- **"Empty room?"** → untick `Occupied` at 30°C: `A-OFF` + `BLIND` + `L-OFF`
  light together. Biggest real-world saving, one click.
- **"Night? Extreme heat?"** → tick `Night` at 22°C for `DIM`; set 35°C for
  `HIGH` + red `ALERT`.
- **"Prove every LED works"** → the 9-step sweep in the project notes lights
  all 11 across scenarios (verified 11/11).

## Reinforcement learning (P3)

- **"Show it learning"** → drag RL episodes 5 → 12, press Run: the reward
  curve, best-episode ring, dashed average and best/avg/latest stats update.
- **"Is it optimal?"** → point at the plateau: it converges empirically;
  extra episodes flatten out (diminishing returns).

## Data pipeline (P4)

- **"Supervised vs unsupervised?"** → flip the method dropdown, press Run:
  chart shape plus n/min/max/mean stats change immediately.

## Closing

- **"Give me the evidence"** → press `Export`: a timestamped ZIP with all
  three charts, the summary and the logic trace lands in `outputs/`.
- **"Did you write this?"** → `git log` shows authorship per change;
  `pytest` runs 27 checks (26 pass, 1 display-only smoke test).
