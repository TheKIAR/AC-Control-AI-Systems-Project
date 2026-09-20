import unittest

from src.fuzzy_logic.fuzzy_system import FuzzySystem
from src.fuzzy_logic.rules import create_rules


class TestFuzzySystem(unittest.TestCase):
    def setUp(self):
        self.fuzzy_system = FuzzySystem()
        self.rules = create_rules()

    def test_cold_temperature(self):
        self.assertEqual(self.fuzzy_system.evaluate(16), "Increase Temperature")

    def test_comfortable_temperature(self):
        self.assertEqual(self.fuzzy_system.evaluate(22), "Maintain Temperature")

    def test_hot_temperature(self):
        self.assertEqual(self.fuzzy_system.evaluate(30), "Decrease Temperature")

    def test_membership_values_are_bounded(self):
        values = self.fuzzy_system.membership(24)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in values.values()))

    def test_set_temperature(self):
        self.fuzzy_system.set_temperature(22)
        self.assertEqual(self.fuzzy_system.current_temperature, 22.0)

    def test_rule_creation(self):
        self.assertEqual(len(self.rules), 3)


if __name__ == "__main__":
    unittest.main()
