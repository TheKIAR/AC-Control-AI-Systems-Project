class RLEnvironment:
    def __init__(self):
        self.state = 0
        self.done = False
        self.goal = 5

    def reset(self):
        self.state = self.initialize_state()
        self.done = False
        return self.state

    def step(self, action):
        next_state = self.get_next_state(action)
        reward = self.calculate_reward(next_state)
        self.done = self.is_terminal_state(next_state)
        self.state = next_state
        return reward, next_state

    def initialize_state(self):
        self.state = 0
        return self.state

    def get_next_state(self, action):
        if action == 0:
            return min(self.state + 1, self.goal)
        return max(self.state - 1, 0)

    def calculate_reward(self, state):
        if state >= self.goal:
            return 1.8
        distance = self.goal - state
        if distance <= 1:
            return 1.0
        if distance <= 2:
            return 0.7
        return max(0.1, 0.45 - (distance * 0.07))

    def is_terminal_state(self, state):
        return state >= self.goal