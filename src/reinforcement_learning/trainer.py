class RLTrainer:
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment
        self.is_trained = False

    def train(self, episodes=1, max_steps=100):
        for episode in range(episodes):
            state = self.environment.reset()
            done = False
            total_reward = 0
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
                total_reward += reward
                steps += 1

            print(f"Episode {episode + 1}/{episodes} - Total Reward: {total_reward}")

        self.is_trained = True
        return self.is_trained

    def evaluate(self, episodes=1, max_steps=100):
        total_rewards = 0
        for episode in range(episodes):
            state = self.environment.reset()
            done = False
            steps = 0

            while not done and steps < max_steps:
                action = self.agent.choose_action(state, exploration_rate=0.0)
                result = self.environment.step(action)
                if len(result) == 2:
                    reward, state = result
                elif len(result) == 3:
                    state, reward, done = result
                else:
                    state, reward, done, _ = result
                total_rewards += reward
                done = self.environment.is_terminal_state(state)
                steps += 1

        average_reward = total_rewards / episodes
        print(f"Average Reward over {episodes} episodes: {average_reward}")
        return average_reward