class RLTrainer:
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment
        self.is_trained = False
        self.rewards = []

    def train(self, episodes=1, max_steps=100):
        self.rewards = []

        for episode in range(episodes):
            state = self.environment.reset()
            done = False
            total_reward = 0.0
            steps = 0

            while not done and steps < max_steps:
                action = self.agent.choose_action(state, exploration_rate=0.1)
                result = self.environment.step(action)

                if len(result) == 2:
                    reward, next_state = result
                    done = self.environment.is_terminal_state(next_state)
                elif len(result) == 3:
                    next_state, reward, done = result
                else:
                    next_state, reward, done, _ = result

                self.agent.learn(state, action, reward, next_state)
                state = next_state
                total_reward += float(reward)
                steps += 1

            self.rewards.append(round(total_reward, 2))

        self.is_trained = True
        return self.is_trained

    def evaluate(self, episodes=1, max_steps=100):
        if episodes <= 0:
            raise ValueError("episodes must be greater than zero")

        total_rewards = 0.0

        for _ in range(episodes):
            state = self.environment.reset()
            done = False
            steps = 0

            while not done and steps < max_steps:
                action = self.agent.choose_action(state, exploration_rate=0.0)
                result = self.environment.step(action)

                if len(result) == 2:
                    reward, next_state = result
                    done = self.environment.is_terminal_state(next_state)
                elif len(result) == 3:
                    next_state, reward, done = result
                else:
                    next_state, reward, done, _ = result

                state = next_state
                total_rewards += float(reward)
                steps += 1

            if not done:
                continue

        return total_rewards / episodes
