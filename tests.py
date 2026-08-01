import unittest
import time
import os
import environment
import config
import json
import logging

logging.basicConfig(
    level = logging.INFO,
    filename = 'test.log',
    filemode = 'w',
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

class TestMovement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # make small arena
        config.LEVELROWS = 7
        config.LEVELCOLS = 14

        # create .tmp for config files
        if not os.path.exists(os.path.dirname(config.SIM_LEVEL_CONFIG)):
            os.makedirs(os.path.dirname(config.SIM_LEVEL_CONFIG))

        # recreate the config
        data = None
        with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
            data = json.load(jfile)

        data['total_levels'] = 2
        data['0']['floor'] = True
        data['0']['outer_walls'] = True
        data['0']['upstair'] = False
        data['0']['downstair'] = False
        data['0']['min_walls'] = 0
        data['0']['min_barrels'] = 0
        data['0']['lights'] = False
        data['0']['items'] = 0
        data['0']['runes'] = 0
        data['0']['mons'] = False
        data['1']['floor'] = True
        data['1']['outer_walls'] = True
        data['1']['upstair'] = False
        data['1']['downstair'] = False
        data['1']['min_walls'] = 0
        data['1']['min_barrels'] = 0
        data['1']['lights'] = False
        data['1']['items'] = 0
        data['1']['runes'] = 0
        data['1']['mons'] = False

        with open(config.SIM_LEVEL_CONFIG, 'w+') as jfile:
            json.dump(data, jfile, indent=4)

        # set the new config file
        config.LEVEL_CONFIG_FILE = config.SIM_LEVEL_CONFIG

    def setUp(self):
        self.display = False
        self.turn_delay = 0.1
        self.environment = environment.Environment(seed='', display=self.display, timing=False)
        self.environment.start()
        if not self.environment.Game.running:
            print('FAILED to start the environment')
            exit()
        self.environment.reset(new_seed=True)

    def loop(self, action=''):
        if self.display:
            self.environment.render()
            time.sleep(self.turn_delay)
        self.environment.Game.game_loop(str(action))

    def test_move_valid(self):
        player = self.environment.Game.LevelManager.Player
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        for _ in range(4):
            self.loop(6)
        self.environment.end()
        self.assertEqual(player.pos(), [1, 5, 0, 1])

    def test_move_invalid(self):
        player = self.environment.Game.LevelManager.Player
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        for _ in range(4):
            self.loop(4)
        self.environment.end()
        self.assertEqual(player.pos(), [1, 1, 0, 1])

if __name__ == '__main__':
    unittest.main()