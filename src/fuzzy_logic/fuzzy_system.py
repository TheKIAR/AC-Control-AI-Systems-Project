class FuzzySystem:
    def __init__(self):
        self.temperature = 22  # Default temperature
        self.current_temperature = 22

    def evaluate(self, input_value=None):
        # Fuzzy logic evaluation logic goes here
        # This is a placeholder for the actual fuzzy logic implementation
        value = self.current_temperature if input_value is None else input_value
        if value < 20:
            return "Increase Temperature"
        elif value > 24:
            return "Decrease Temperature"
        else:
            return "Maintain Temperature"

    def set_temperature(self, new_temperature):
        self.temperature = new_temperature
        self.current_temperature = new_temperature
        return f"Temperature set to {self.temperature}°C"