import unittest
import wall
import tower
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
    display = False
    turn_delay = 0.1

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

        TestMovement.environment = environment.Environment(seed='',
                                                           display=TestMovement.display,
                                                           timing=False)
        TestMovement.environment.start()
        if not TestMovement.environment.Game.running:
            print('FAILED to start the environment')
            exit()

    @classmethod
    def tearDownClass(cls):
        TestMovement.environment.end()

    def setUp(self):
        TestMovement.environment.reset(new_seed=True)

    def loop(self, action=''):
        if self.display:
            TestMovement.environment.render()
            time.sleep(self.turn_delay)
        TestMovement.environment.Game.game_loop(str(action))

    def test_place_player_valid(self):
        player = TestMovement.environment.Game.LevelManager.Player
        entitylayer = TestMovement.environment.Game.LevelManager.Levels[0].EntityLayer
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        self.assertIn(player, entitylayer[1][1])
        self.assertEqual(tower.Floor().name, entitylayer[1][1][0].name)
        self.assertEqual(2, len(entitylayer[1][1]))

    def test_place_entity_invalid_wall(self):
        entitylayer = TestMovement.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestMovement.environment.Game.LevelManager
        wll = wall.Sandstone()
        levelmanager.place_entity(0, wll, (0,0))
        self.assertTrue(TestMovement.environment.Game.running)
        self.assertNotIn(wll, entitylayer[0][0])
        self.assertEqual(1, len(levelmanager.Levels[0].EntityLayer[0][0]))

    def test_place_entity_invalid_level(self):
        entitylayer = TestMovement.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestMovement.environment.Game.LevelManager
        wll = wall.Sandstone()
        self.assertEqual(2, len(levelmanager.Levels))
        levelmanager.place_entity(5, wll, (0,0))
        self.assertEqual(2, len(levelmanager.Levels))
        self.assertTrue(TestMovement.environment.Game.running)
        self.assertNotIn(wll, entitylayer[0][0])
        self.assertEqual(1, len(levelmanager.Levels[0].EntityLayer[0][0]))

    def test_move_valid(self):
        player = TestMovement.environment.Game.LevelManager.Player
        entitylayer = TestMovement.environment.Game.LevelManager.Levels[0].EntityLayer
        for _ in range(4):
            self.loop(6)
        self.assertEqual(player.pos(), [1, 5, 0, 1])
        self.assertIn(player, entitylayer[1][5])

    def test_move_invalid(self):
        player = TestMovement.environment.Game.LevelManager.Player
        entitylayer = TestMovement.environment.Game.LevelManager.Levels[0].EntityLayer
        for _ in range(4):
            self.loop(4)
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        self.assertIn(player, entitylayer[1][1])

    def test_push_barrel(self):
        player = TestMovement.environment.Game.LevelManager.Player
        levelmanager = TestMovement.environment.Game.LevelManager
        entitylayer = TestMovement.environment.Game.LevelManager.Levels[0].EntityLayer
        barrel = tower.Barrel()
        levelmanager.place_entity(0, barrel, (1,2))
        for _ in range(4):
            self.loop(6)
        self.assertEqual(player.pos(), [1, 5, 0, 1])
        self.assertIn(player, entitylayer[1][5])
        self.assertEqual(2, len(entitylayer[1][5]))
        self.assertEqual(barrel.pos(), [1, 6, 0, 1])
        self.assertIn(barrel, entitylayer[1][6])
        self.assertEqual(2, len(entitylayer[1][6]))


if __name__ == '__main__':
    unittest.main()