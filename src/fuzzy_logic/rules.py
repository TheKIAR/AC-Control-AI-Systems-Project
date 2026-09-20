def create_fuzzy_rule(name, conditions, output):
    return {"name": name, "conditions": conditions, "output": output}


def create_rules():
    return [
        create_fuzzy_rule("cold", [lambda value: value < 20], "Increase Temperature"),
        create_fuzzy_rule("warm", [lambda value: value > 24], "Decrease Temperature"),
        create_fuzzy_rule("stable", [lambda value: 20 <= value <= 24], "Maintain Temperature"),
    ]


def evaluate_rule(rule, inputs):
    if isinstance(inputs, dict):
        input_value = inputs.get("input_value", inputs.get("temperature", 0))
    else:
        input_value = inputs

    return rule["output"] if all(condition(input_value) for condition in rule["conditions"]) else False
