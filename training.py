import matplotlib.pyplot as plt
import tqdm
import environment
import agent 
import time

class Training:
    def __init__(self, seed=None, display=False):
        self.num_episodes = 10
        self.training_mode = False 
        self.rewards = []
        self.display = display
        self.environment = environment.Environment(seed, display)
        self.agent = agent.Agent(self.environment.obs_size, self.environment.action_size)
        self.turn_delay_secs = 0.1

    def start(self):
        self.environment.start()

    def run(self):
        if not self.environment.Game.running:
            return 

        episode_range = range(self.num_episodes)
        iteratable = episode_range if self.display else tqdm.tqdm(episode_range)

        for episode in iteratable:

            # reset
            done = False
            truncated = False
            obs,_ = self.environment.reset()

            if not self.training_mode and self.display:
                self.environment.render()
                time.sleep(self.turn_delay_secs)

            # episode loop
            while not (done or truncated):

                # sample action
                action = self.agent.sample_action(obs, self.training_mode)

                # step
                next_obs, reward, done, truncated, _ = self.environment.step(action)

                # update agent
                if self.training_mode:
                    self.agent.store(obs, reward, action, next_obs)
                    self.agent.train()

                obs = next_obs

                if not self.training_mode and self.display:
                    self.environment.render()
                    time.sleep(self.turn_delay_secs)

        self.environment.end()
        self.plot()

    def plot(self):
        # plot rewards
        plt.figure(figsize=(8, 6))
        plt.plot(self.rewards, marker='o', linestyle='-', linewidth=2)
        plt.title("Rewards over Episodes", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Episodes", fontsize=12)
        plt.ylabel("Rewards", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.show()
