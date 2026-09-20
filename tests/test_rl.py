import unittest

from src.reinforcement_learning.agent import RLAgent
from src.reinforcement_learning.env import RLEnvironment
from src.reinforcement_learning.trainer import RLTrainer


class TestRLAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RLAgent()
        self.env = RLEnvironment()
        self.trainer = RLTrainer(self.agent, self.env)

    def test_choose_action(self):
        action = self.agent.choose_action(0)
        self.assertIn(action, self.agent.action_space)

    def test_learn_updates_known_state(self):
        initial_state = self.env.reset()
        action = self.agent.choose_action(initial_state)
        reward, next_state = self.env.step(action)
        before = self.agent.q_table.get(initial_state, [0, 0]).copy()
        self.agent.learn(initial_state, action, reward, next_state)
        self.assertIn(initial_state, self.agent.q_table)
        self.assertNotEqual(self.agent.q_table[initial_state], before)

    def test_training_records_rewards(self):
        self.trainer.train(episodes=10)
        self.assertTrue(self.trainer.is_trained)
        self.assertEqual(len(self.trainer.rewards), 10)
        self.assertTrue(all(isinstance(value, float) for value in self.trainer.rewards))

    def test_evaluation_returns_number(self):
        self.trainer.train(episodes=3)
        average = self.trainer.evaluate(episodes=2)
        self.assertIsInstance(average, float)


if __name__ == "__main__":
    unittest.main()
