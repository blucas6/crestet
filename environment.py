import numpy as np
import logger
import game
import config

class Environment:
    def __init__(self, seed=None, display=False, timing=False):
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
        self.np_random = np.random.default_rng()
        self.Game = game.Game(seed=seed,
                              msgblocking=False,
                              usedisplay=display,
                              timing=timing)

    def start(self):
        '''Start the environment'''
        try:
            self.Game.start()
        except Exception as ex:
            print(f'Failed to start the game environment!!\n {ex}')
            raise

    def get_observation(self):
        '''Returns a 1d np array of size "obs_size"'''
        obs = np.zeros(self.obs_size)

        myobs = self.get_player_fov()
        #myobs = self.get_level_observation()
        #myobs = self.get_curr_inventory()
        #logger.Logger.log(f'AGENT:\n {myobs}')

        return obs

    def reset(self, new_seed=False):
        '''
        Reset the environment to start a brand new episode

        Returns the initial observation and an optional info dict
        '''
        self.Game.reset(new_seed=new_seed)
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

    def get_player_fov(self):
        '''Flattens the player view of the level into a 1D array'''
        entity_layer = self.Game.LevelManager.Player.mentalmap
        obs = [col[ix].typeid if ix < len(col) else 0 for row in entity_layer for col in row for ix in range(config.LEVELMAX_ENTITIES)]
        return obs

    def get_level_observation(self):
        '''Flattens the level entities into a 1D array'''
        currlevel = self.Game.LevelManager.get_curr_level()
        if not currlevel:
            return np.empty(config.LEVELROWS * config.LEVELCOLS * config.LEVELMAX_ENTITIES)
        entity_layer = currlevel.EntityLayer
        obs = [col[ix].typeid if ix < len(col) else 0 for row in entity_layer for col in row for ix in range(config.LEVELMAX_ENTITIES)]
        return obs

    def get_curr_z(self):
        '''Returns the current level z index as a 1D array'''
        return np.array([self.Game.LevelManager.currentz])

    def get_curr_health(self):
        '''Returns the current player health as a 1D array'''
        return np.array([self.Game.LevelManager.Player.Health.currenthealth])

    def get_curr_inventory(self):
        '''Returns the current player inventory as a 1D array'''
        inventory = self.Game.LevelManager.Player.Inventory.get_all_items()
        obs = [item.typeid for item in inventory if item]
        return np.array(obs)

    def get_curr_turn(self):
        '''Returns the current turn as a 1D array'''
        return np.array(self.Game.turn)




