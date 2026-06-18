import numpy

class Agent:
    def __init__(self, obs_size, action_size):
        self.obs_size = obs_size
        self.action_size = action_size

    def sample_action(self, obs, training_mode):
        return numpy.random.choice(self.action_size)
    
    def store(self, obs, reward, action, next_obs):
        pass

    def train(self):
        pass
