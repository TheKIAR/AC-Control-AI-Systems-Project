# AI Systems Project — Final Report

**CSE-334: Project — Department of CSE, Primeasia University**

**Project Title:** Integrated AI Systems for Smart Room and Air-Conditioning Control  
**Student Name:** Md. Ragib Ashhab  
**Student ID:** __________________  
**Semester:** Summer 2026  
**Submission Date:** 24 September 2026

## 1. Introduction

This project develops an integrated artificial intelligence system for a smart room/air-conditioning use case. The course brief requires the student to solve **any three of four** open-ended AI problems. This project addresses the three selected problems directly:

1. Fuzzy logic-based AI system to control air conditioning.
2. First-Order Predicate Logic (FOPL)-based AI system for a real-world use case.
3. Reinforcement-learning-based AI system for a real-world use case.

A data-driven module is also included as an extension for generating and preparing experimental data.

The system uses one common room scenario so that the methods can be demonstrated consistently. The application provides a graphical interface where temperature, occupancy, night condition, energy-saving preference, and RL training episodes can be changed before running the integrated AI pipeline.

## 2. Objectives

- Develop a fuzzy logic controller for an air-conditioning system.
- Develop a FOPL knowledge base and inference system for smart-room decisions.
- Develop a reinforcement-learning agent for thermostat setpoint tracking.
- Collect and prepare information required by the selected AI methods.
- Analyze the methods using a real-world-inspired room scenario.
- Present the solution and explain the results during project demonstration and viva.
- Include a data-driven extension to support experimentation and AI-data preparation.

---

# Task 1 — Collect and Prepare Information Required (5 Marks)

## 1.1 Problem Information

The selected real-world environment is a study room/classroom containing one split AC unit. The important inputs are room temperature, occupancy, night condition, and energy-saving preference.

The main objectives are:

- maintaining human comfort;
- avoiding unnecessary energy use; and
- applying basic safety and operating rules.

Using one common room scenario allows the fuzzy, FOPL, and reinforcement-learning methods to be compared under related conditions.

## 1.2 Information and Assumptions

The fuzzy controller uses temperature as its primary input and divides the room condition into cold, comfortable, and hot regions. The comfortable region is centred around 22°C.

The FOPL policy uses crisp conditions such as **Hot, Cold, Occupied, Night,** and **EnergySaver**. An extreme-temperature condition is treated as a safety case.

For reinforcement learning, the room is represented as a small discrete thermostat environment. States represent different temperature conditions, while actions represent moving the control toward a cooler or warmer setpoint. The reward is higher when the agent reaches the desired comfort state and lower when it remains far from that state.

The data-driven extension generates small supervised and unsupervised datasets and applies cleaning and transformation before visualization.

## 1.3 Data Preparation

The GUI validates user-controlled ranges such as temperature, RL episode count, and data-point count. The data pipeline removes invalid `None` entries and applies numerical transformations.

The selected room assumptions are kept consistent across the AI modules so that their outputs can be demonstrated and discussed as parts of one smart-room system.

---

# Task 2 — Build and Apply an Appropriate Method (5 Marks)

## 2.1 Fuzzy Logic-Based AC Control

The fuzzy module is implemented in `src/fuzzy_logic/`. It uses triangular membership functions for **cold, comfortable,** and **hot** temperature conditions. The comfortable membership is centred at approximately 22°C.

The controller evaluates the temperature and selects the strongest membership condition to produce an AC control action.

| Input Temperature | Fuzzy Condition | Action |
|---|---|---|
| 16°C | Cold | Increase Temperature |
| 22°C | Comfortable | Maintain Temperature |
| 30°C | Hot | Decrease Temperature |

The fuzzy approach is appropriate because room temperature is continuous. A temperature near a boundary does not always need to be treated as completely cold or completely hot. Membership functions provide a smoother representation of these conditions.

## 2.2 First-Order Predicate Logic Smart-Room Advisor

The FOPL implementation is located in `src/fopl/`. It represents facts, predicates, variables, rules, and conclusions and applies forward chaining over the room knowledge base.

A representative policy rule is:

**Hot(r) AND Occupied(r) AND NOT EnergySaver(r) → AC_HIGH(r)**

Other rules handle energy-saving operation, empty-room shutdown, heating, night operation, lighting, blinds, and safety conditions.

Example conclusions include:

| Room Condition | Example FOPL Conclusion |
|---|---|
| Hot + Occupied | AC_HIGH |
| Hot + Occupied + Energy Saver | AC_ECO |
| Hot + Empty | AC_OFF and energy-saving actions |
| Cold + Occupied | HEATER_ON |
| Comfortable + Night + Occupied | AC_STANDBY |

The FOPL method is appropriate because it provides explicit and explainable policy reasoning. A conclusion can be associated with a logical rule rather than being presented as an unexplained output.

## 2.3 Reinforcement Learning Thermostat

The reinforcement-learning module is implemented in `src/reinforcement_learning/`. It contains a discrete environment, a Q-table based agent, and a trainer.

The environment represents thermostat control using discrete states and two control actions. The agent learns action values through repeated episodes. The reward function encourages the agent to reach and remain near the desired comfort state.

The GUI allows the number of training episodes to be changed. The result is shown as a reward-per-episode chart with best, average, and latest reward statistics.

This method is appropriate for a control problem because the agent learns a policy through interaction with an environment and feedback from rewards.

## 2.4 Data-Driven Extension

The data-driven module in `src/data_driven/` is included as an extension. It provides supervised and unsupervised data generation, cleaning, transformation, and JSON-compatible data handling.

It supports experimentation and demonstrates how prepared data can be used as part of an AI development workflow. It is not counted as one of the three required problems for this report.

---

# 3. System Integration

The GUI integrates the three assessed AI methods into one workflow:

```text
Temperature / Room Conditions
          ↓
   Fuzzy Logic Controller
          ↓
   FOPL Smart-Room Policy
          ↓
 Reinforcement Learning
          ↓
Integrated Results and Visualizations
```

The interface also includes:

- Cold / Normal / Hot presets;
- Reset controls;
- dark and light themes;
- rounded modern controls;
- animated visual elements;
- live module-status indicators;
- an AI decision timeline;
- RL reward statistics;
- Auto Mode; and
- report export.

The methods remain separate modules so that each technique can be tested independently while still being demonstrated through one application.

---

# Task 3 — Analyze and Present Findings on Real-World Use Cases (5 Marks)

## 3.1 Fuzzy Control Finding

The fuzzy controller produces different AC actions for cold, comfortable, and hot temperatures.

Its main advantage in this project is the ability to represent gradual temperature conditions instead of depending only on rigid threshold decisions.

For example, a temperature near the comfortable region can be represented through membership rather than forcing an immediate binary cold/hot classification.

## 3.2 FOPL Finding

The FOPL advisor can incorporate information beyond temperature.

For example:

- an empty room can cause cooling and other unnecessary loads to be turned off;
- EnergySaver can change the policy from high cooling to economy cooling; and
- night and occupancy conditions can change the operating policy.

This demonstrates why logical rules are useful when safety, occupancy, energy policy, and explainability are important.

## 3.3 Reinforcement Learning Finding

The RL reward chart shows how the learned policy changes over training episodes.

The best, average, and latest reward statistics help explain the training behaviour and whether additional episodes are producing meaningful improvement.

The result is an educational thermostat simulation. It is **not** claimed to be a production HVAC controller.

## 3.4 Cross-Method Analysis

The three assessed methods solve different aspects of the same smart-room problem:

- **Fuzzy logic** is useful for gradual or uncertain temperature conditions.
- **FOPL** is useful for explicit rules, constraints, safety, and explanations.
- **Reinforcement learning** is useful for learning a control policy from interaction and reward.

The combined demonstration shows that different AI techniques can complement one another rather than replacing one another.

## 3.5 Limitations

The project is a software simulation and does not directly control physical HVAC hardware.

The main limitations are:

1. Sensor readings are simulated through GUI inputs.
2. The RL environment is simplified.
3. The fuzzy controller uses a limited set of temperature memberships.
4. Real buildings have additional variables such as humidity, outdoor temperature, air flow, equipment efficiency, and electricity pricing.
5. Physical deployment would require hardware integration, safety validation, and testing with real sensor data.

Therefore, the project demonstrates the AI methods and their real-world reasoning patterns rather than claiming measured energy savings from a physical building.

---

# Task 4 — Present the Solution, Submit Project Report and Answer Query (5 Marks)

## 4.1 Demonstration Procedure

1. Start the application using `python run_gui.py`.
2. Show the default room condition.
3. Change the temperature to 16°C, 22°C, and 30°C and show the fuzzy decisions.
4. Change Occupied and Energy Saver settings and show the FOPL conclusions.
5. Run reinforcement-learning training and show the reward chart and statistics.
6. Use Auto Mode for an integrated live demonstration if required.
7. Use Export Report to generate the available charts and inference evidence.
8. Explain how each result relates to its corresponding AI method.

## 4.2 Viva Questions and Answers

**Q: Why did you use fuzzy logic for AC control?**  
A: Temperature is a continuous variable and a room can be partly cold, comfortable, or hot near a boundary. Fuzzy membership represents this gradual behaviour.

**Q: Why is FOPL useful in the same project?**  
A: FOPL provides explicit rules and explainable conclusions. It can combine temperature with occupancy, night mode, and energy-saving conditions.

**Q: What is the role of reinforcement learning?**  
A: RL learns a control policy from interaction with a simplified thermostat environment and reward feedback.

**Q: Does the RL result guarantee an optimal real-world AC controller?**  
A: No. The project demonstrates learning in a simplified educational environment. A real HVAC system would require richer state information, physical modelling, safety constraints, and validation.

**Q: What is the real-world use case?**  
A: Smart-room or smart-building control, where temperature, occupancy, operating mode, and energy policy can influence AC and room decisions.

**Q: Why are three methods used instead of only one?**  
A: The course permits any three problems, and the selected methods demonstrate three different AI paradigms: fuzzy reasoning, symbolic logical reasoning, and reinforcement learning.

---

# 5. Originality and Academic Integrity

The implementation, rule design, GUI integration, experiments, and documentation are prepared for this course project.

The repository contains the source code and test structure used to demonstrate the work. External concepts such as fuzzy logic, FOPL, and reinforcement learning are used as academic methods, while the project-specific room rules, software structure, interface, and integration are part of this implementation.

No student work is intentionally copied.

---

# 6. Conclusion

This project demonstrates three required AI problem types through one coherent smart-room scenario.

The fuzzy system controls AC behaviour from temperature, the FOPL advisor applies explicit room policies, and the reinforcement-learning agent learns thermostat control through reward.

A data-driven extension supports experimentation and AI-data preparation.

The final GUI brings the components together so that the methods, results, and reasoning can be demonstrated during the project presentation and viva.

---

# 7. Project File Mapping

### Fuzzy Logic
- `src/fuzzy_logic/fuzzy_system.py`
- `src/fuzzy_logic/rules.py`

### FOPL
- `src/fopl/knowledge_base.py`
- `src/fopl/advisor.py`

### Reinforcement Learning
- `src/reinforcement_learning/env.py`
- `src/reinforcement_learning/agent.py`
- `src/reinforcement_learning/trainer.py`

### Data-Driven Extension
- `src/data_driven/generator.py`
- `src/data_driven/pipeline.py`

### GUI and Integration
- `src/main.py`
- `run_gui.py`

### Tests
- `tests/`

---

# 8. Assessment Rubric Mapping

| Course Task | Report Section | Marks |
|---|---|---:|
| 1. Collect and prepare information required | Task 1 | 5 |
| 2. Build and apply an appropriate method | Task 2 | 5 |
| 3. Analyze and present findings on real-world use cases | Task 3 | 5 |
| 4. Present solution, submit report and answer query | Task 4 | 5 |

**Course:** CSE-334, Project  
**Total project marks specified in the brief:** 60  
**Submission deadline specified in the brief:** 24 September 2026
