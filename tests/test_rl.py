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
        action = self.agent.choose_action(state=[0, 0])
        self.assertIn(action, self.agent.action_space)

    def test_learn(self):
        initial_state = self.env.reset()
        action = self.agent.choose_action(initial_state)
        reward, next_state = self.env.step(action)
        self.agent.learn(initial_state, action, reward, next_state)
        # Check if the agent's Q-values are updated (this is a placeholder for actual checks)
        self.assertIsNotNone(self.agent.q_values)

    def test_training(self):
        self.trainer.train(episodes=10)
        # Check if the training process completes without errors
        self.assertTrue(self.trainer.is_trained)

if __name__ == '__main__':
    unittest.main()