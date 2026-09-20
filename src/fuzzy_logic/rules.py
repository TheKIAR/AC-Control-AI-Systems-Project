def create_fuzzy_rule(name, conditions, output):
    return {
        'name': name,
        'conditions': conditions,
        'output': output
    }


def create_rules():
    return [
        create_fuzzy_rule("cool", [lambda value: value < 20], "Increase Temperature"),
        create_fuzzy_rule("warm", [lambda value: value > 24], "Decrease Temperature"),
        create_fuzzy_rule("stable", [lambda value: 20 <= value <= 24], "Maintain Temperature"),
    ]


def evaluate_rule(rule, inputs):
    if isinstance(inputs, dict):
        input_value = inputs.get('input_value', inputs.get('temperature', 0))
    else:
        input_value = inputs

    for condition in rule['conditions']:
        if not condition(input_value):
            return False
    return rule['output']


def example_condition(input_value):
    return input_value > 10


def example_output():
    return "Action taken based on fuzzy rule"

# Example usage
if __name__ == "__main__":
    rule1 = create_fuzzy_rule("Rule 1", [example_condition], example_output)
    inputs = {'input_value': 15}
    result = evaluate_rule(rule1, inputs)
    print(result)  # Should print "Action taken based on fuzzy rule" if conditions are met