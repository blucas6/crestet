import matplotlib.pyplot as plt
import tqdm
import environment
import agent 
import time
import numpy as np
import logger

class Training:
    def __init__(self, seed=None, display=False, timing=False):
        self.num_episodes = 100
        self.training_mode = False
        self.rewards = []
        self.mse_losses = []
        self.avg_q_values = []
        self.display = display
        self.environment = environment.Environment(seed, display, timing)
        logger.Logger.logging = False
        self.agent = agent.Agent(self.environment.obs_size, self.environment.action_size)
        self.turn_delay_secs = 0.0
        self.seed = seed

    def start(self):
        self.environment.start()

    def run(self):
        if not self.environment.Game.running:
            return 

        episode_range = range(self.num_episodes)
        iteratable = episode_range if self.display else tqdm.tqdm(episode_range)

        if not self.training_mode:
            self.agent.load()

        for episode in iteratable:
            episode_rewards = []
            episode_losses = []
            episode_avg_qs = []

            # reset
            done = False
            truncated = False
            obs, _ = self.environment.reset(self.seed)

            if self.display:
                self.environment.render()
                time.sleep(self.turn_delay_secs)

            # episode loop
            while not (done or truncated):

                # sample action
                action_mask = self.environment.get_action_mask()

                action = self.agent.sample_action(obs, action_mask, self.training_mode)
                #action = np.argmax(action_mask)
                
                # step
                next_obs, reward, done, truncated, _ = self.environment.step(action)

                # update agent
                if self.training_mode:
                    self.agent.store(obs, reward, action, next_obs, done)
                    data = self.agent.train()
                    if data is not None:
                        l, q = data
                        episode_losses.append(l)
                        episode_avg_qs.append(q)

                obs = next_obs

                # Record step reward
                episode_rewards.append(reward)

                if self.display:
                    self.environment.render()
                    time.sleep(self.turn_delay_secs)

            self.rewards.append(sum(episode_rewards))
            if self.training_mode:
                self.agent.update()
                avg_loss = sum(episode_losses) / len(episode_losses) if len(episode_losses) > 0 else 0
                avg_q = sum(episode_avg_qs) / len(episode_avg_qs) if len(episode_avg_qs) > 0 else 0
                self.mse_losses.append(avg_loss)
                self.avg_q_values.append(avg_q)
            
            if ((episode+1) % (self.num_episodes // 20) == 0):
                print(np.mean(self.rewards[-self.num_episodes//20:]))

        self.environment.end()
        self.plot()
        self.agent.save()

    def plot(self, window_size=10):
        """
        Plots Rewards, Losses, and Q-Values with an overlaid moving average.
        """
        # Helper function to compute moving average
        def moving_average(data, window):
            if len(data) < window:
                return data  # Not enough data points, return as-is
            # 'valid' mode ensures the moving average doesn't padding-skew early values
            # We prepend with None or pad to keep array sizes aligned with episodes
            return np.convolve(data, np.ones(window)/window, mode='valid')

        # Create 3 subplots stacked vertically on 1 figure
        fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        
        # 1. Plot Rewards
        axs[0].plot(self.rewards, marker='o', linestyle='-', linewidth=1, color='b', alpha=0.3, label='Raw')
        if len(self.rewards) >= window_size:
            ma_rewards = moving_average(self.rewards, window_size)
            # Shift x axis so the MA line aligns with the end of the window
            axs[0].plot(range(window_size - 1, len(self.rewards)), ma_rewards, linestyle='-', linewidth=2.5, color='darkblue', label=f'MA ({window_size} ep)')
        axs[0].set_title("Total Rewards over Episodes", fontsize=12, fontweight='bold')
        axs[0].set_ylabel("Rewards", fontsize=10)
        axs[0].grid(True, linestyle='--', alpha=0.6)
        axs[0].legend(loc='upper left')
        
        # 2. Plot Losses
        if self.training_mode and len(self.mse_losses) > 0:
            axs[1].plot(self.mse_losses, marker='o', linestyle='-', linewidth=1, color='r', alpha=0.3, label='Raw')
            if len(self.mse_losses) >= window_size:
                ma_losses = moving_average(self.mse_losses, window_size)
                axs[1].plot(range(window_size - 1, len(self.mse_losses)), ma_losses, linestyle='-', linewidth=2.5, color='darkred', label=f'MA ({window_size} ep)')
            axs[1].set_title("Average MSE Loss over Episodes", fontsize=12, fontweight='bold')
            axs[1].legend(loc='upper right')
        else:
            axs[1].text(0.5, 0.5, "No Loss Data\n(Training Mode Off or Buffer Not Full)", 
                        horizontalalignment='center', verticalalignment='center', transform=axs[1].transAxes, fontsize=11, color='gray')
        axs[1].set_ylabel("MSE Loss", fontsize=10)
        axs[1].grid(True, linestyle='--', alpha=0.6)
        
        # 3. Plot Avg Q-Values
        if self.training_mode and len(self.avg_q_values) > 0:
            axs[2].plot(self.avg_q_values, marker='o', linestyle='-', linewidth=1, color='g', alpha=0.3, label='Raw')
            if len(self.avg_q_values) >= window_size:
                ma_q = moving_average(self.avg_q_values, window_size)
                axs[2].plot(range(window_size - 1, len(self.avg_q_values)), ma_q, linestyle='-', linewidth=2.5, color='darkgreen', label=f'MA ({window_size} ep)')
            axs[2].set_title("Average Q-Values over Episodes", fontsize=12, fontweight='bold')
            axs[2].legend(loc='upper left')
        else:
            axs[2].text(0.5, 0.5, "No Q-Value Data\n(Training Mode Off or Buffer Not Full)", 
                        horizontalalignment='center', verticalalignment='center', transform=axs[2].transAxes, fontsize=11, color='gray')
        axs[2].set_ylabel("Avg Q-Value", fontsize=10)
        axs[2].set_xlabel("Episodes", fontsize=11)
        axs[2].grid(True, linestyle='--', alpha=0.6)
        
        # Adjust layout to cleanly format margins and prevent overlaps
        plt.tight_layout()
        plt.show()