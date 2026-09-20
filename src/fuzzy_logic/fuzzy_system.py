class FuzzySystem:
    """Small Mamdani-style temperature controller using triangular membership."""

    def __init__(self):
        self.temperature = 22.0
        self.current_temperature = 22.0

    @staticmethod
    def _triangle(value, left, peak, right):
        if value <= left or value >= right:
            return 0.0
        if value == peak:
            return 1.0
        if value < peak:
            return (value - left) / (peak - left)
        return (right - value) / (right - peak)

    @classmethod
    def membership(cls, temperature):
        value = float(temperature)
        return {
            "cold": max(0.0, min(1.0, (22.0 - value) / 6.0)),
            "comfortable": cls._triangle(value, 18.0, 22.0, 26.0),
            "hot": max(0.0, min(1.0, (value - 22.0) / 6.0)),
        }

    def evaluate(self, input_value=None):
        value = self.current_temperature if input_value is None else float(input_value)
        memberships = self.membership(value)
        action_for_set = {
            "cold": "Increase Temperature",
            "comfortable": "Maintain Temperature",
            "hot": "Decrease Temperature",
        }
        return action_for_set[max(memberships, key=memberships.get)]

    def set_temperature(self, new_temperature):
        self.temperature = float(new_temperature)
        self.current_temperature = self.temperature
        return f"Temperature set to {self.temperature:g}°C"
