import numpy
import game

class Environment:
    def __init__(self, seed=None, display=False):
        '''
        Initialize the environment

        At a minimum needs to have self.obs_size and self.action_size and
        maxsteps. Obs size represents the total length of an observation.
        Action size represents the number of discrete actions possible in the
        environment.
        '''
        self.obs_size = 2
        self.action_size = 9
        self.maxsteps = 10
        self.current_step = 0
        self.np_random = numpy.random.default_rng()
        self.Game = game.Game(seed=seed,
                              msgblocking=False,
                              usedisplay=display,
                              timing=False)

    def start(self):
        try:
            self.Game.start()
        except Exception as ex:
            print(f'Failed to start the game environment!! {ex}')
            raise

    def get_observation(self):
        '''Returns a 1d numpy array of size "obs_size"'''
        obs = numpy.zeros(self.obs_size)

        self.fill_observation(obs)
        return obs

    def reset(self, seed=None):
        '''
        Reset the environment to start a brand new episode

        Returns the initial observation and an optional info dict
        '''
        if seed is not None:
            self.np_random = numpy.random.default_rng(seed)

        self.Game.game_setup()

        self.current_step = 0
        return self.get_observation(), {}

    def step(self, action):
        '''
        Takes in an int action and applies it to the environment

        Returns the next observation, the reward associated with this action, if
        the episode is complete or not, if maxsteps is reached, and optional
        info.
        '''
        self.current_step += 1
        reward = 0
        done = False
        truncated = self.current_step >= self.maxsteps

        self.Game.game_loop(str(action))

        return self.get_observation(), reward, done, truncated, {}

    def render(self):
        '''Renders the environment visually for evaluation purposes'''
        self.Game.render()

    def end(self):
        '''Close the game environment'''
        self.Game.end()

    def fill_observation(self, obs):
        curr_level = self.Game.LevelManager.get_curr_level()
        if not curr_level:
            return
        for row in curr_level.EntityLayer:
            for col in row:
                for entity in col:
                    pass
