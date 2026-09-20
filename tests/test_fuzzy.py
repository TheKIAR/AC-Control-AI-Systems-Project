import unittest
from src.fuzzy_logic.fuzzy_system import FuzzySystem
from src.fuzzy_logic.rules import create_rules

class TestFuzzySystem(unittest.TestCase):

    def setUp(self):
        self.fuzzy_system = FuzzySystem()
        self.rules = create_rules()

    def test_evaluate(self):
        input_value = 25  # Example input
        expected_output = self.fuzzy_system.evaluate(input_value)
        self.assertIsNotNone(expected_output)

    def test_set_temperature(self):
        temperature = 22  # Example temperature
        self.fuzzy_system.set_temperature(temperature)
        self.assertEqual(self.fuzzy_system.current_temperature, temperature)

    def test_rule_creation(self):
        self.assertGreater(len(self.rules), 0)

if __name__ == '__main__':
    unittest.main()