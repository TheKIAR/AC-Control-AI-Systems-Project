from .fuzzy_system import COLD_MAX, COMFORT_MAX


def create_fuzzy_rule(name, conditions, output):
    return {"name": name, "conditions": conditions, "output": output}


def create_rules():
    # Same 20/24 borders as FuzzySystem and fopl/advisor.py.
    # "warm" covers FOPL Warm (24-28) + Hot (>=28): both need cooling,
    # which FOPL refines into AC_ECO vs AC_HIGH.
    return [
        create_fuzzy_rule("cold", [lambda value: value < COLD_MAX], "Increase Temperature"),
        create_fuzzy_rule("warm", [lambda value: value > COMFORT_MAX], "Decrease Temperature"),
        create_fuzzy_rule("stable", [lambda value: COLD_MAX <= value <= COMFORT_MAX], "Maintain Temperature"),
    ]


def evaluate_rule(rule, inputs):
    if isinstance(inputs, dict):
        input_value = inputs.get("input_value", inputs.get("temperature", 0))
    else:
        input_value = inputs

    return rule["output"] if all(condition(input_value) for condition in rule["conditions"]) else False
