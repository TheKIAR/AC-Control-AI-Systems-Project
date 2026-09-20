import random


class RLAgent:
    def __init__(self, action_space=None):
        self.action_space = [0, 1] if action_space is None else list(action_space)
        self.q_table = {}

    @property
    def q_values(self):
        # Kept for backward compatibility; the Q-table is the single source.
        return self.q_table

    def choose_action(self, state, exploration_rate=0.0):
        state_key = tuple(state) if isinstance(state, list) else state
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * len(self.action_space)

        q_vals = self.q_table[state_key]
        if random.random() < exploration_rate:
            return random.choice(self.action_space)  # Explore
        if len(set(q_vals)) == 1:
            return random.choice(self.action_space)
        # Return the action itself, not its table index.
        return self.action_space[q_vals.index(max(q_vals))]  # Exploit

    def learn(self, state, action, reward, next_state, learning_rate=0.2, discount_factor=0.5):
        state_key = tuple(state) if isinstance(state, list) else state
        next_state_key = tuple(next_state) if isinstance(next_state, list) else next_state

        if state_key not in self.q_table:
            self.q_table[state_key] = [0] * len(self.action_space)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = [0] * len(self.action_space)

        action_index = self.action_space.index(action) if action in self.action_space else 0
        best_next_action = self.q_table[next_state_key].index(max(self.q_table[next_state_key]))
        td_target = reward + discount_factor * self.q_table[next_state_key][best_next_action]
        td_delta = td_target - self.q_table[state_key][action_index]
        updated_value = self.q_table[state_key][action_index] + learning_rate * td_delta
        self.q_table[state_key][action_index] = max(-2.0, min(2.0, updated_value))

        return self.q_table[state_key][action_index]