import unittest
import brain
import sys
import argparse
import utility
import item
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

Logger = logging.getLogger(__name__)

class TestSuite(unittest.TestCase):
    display = False
    turn_delay = 0.3

    @classmethod
    def setUpClass(cls):
        Logger.info('=== UNIT TEST SETUP ===')
        # make small arena
        config.LEVELROWS = 7
        config.LEVELCOLS = 12

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

        TestSuite.environment = environment.Environment(seed='',
                                                           display=TestSuite.display,
                                                           timing=False)
        TestSuite.environment.start()
        if not TestSuite.environment.Game.running:
            print('FAILED to start the environment')
            exit()

    @classmethod
    def tearDownClass(cls):
        TestSuite.environment.end()

    def setUp(self):
        Logger.info('')
        Logger.info('')
        Logger.info(f'EXECUTING: {self._testMethodName}')
        TestSuite.environment.reset(new_seed=True)

    def loop(self, action=''):
        if self.display:
            TestSuite.environment.render()
            time.sleep(self.turn_delay)
        TestSuite.environment.Game.game_loop(str(action))
        if self.display:
            TestSuite.environment.render()
            time.sleep(self.turn_delay)

    def test_place_player_valid(self):
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        self.assertIn(player, entitylayer[1][1])
        self.assertEqual(tower.Floor().name, entitylayer[1][1][0].name)
        self.assertEqual(2, len(entitylayer[1][1]))

    def test_place_entity_invalid_wall(self):
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestSuite.environment.Game.LevelManager
        wll = wall.Sandstone()
        levelmanager.place_entity(0, wll, (0,0))
        self.assertTrue(TestSuite.environment.Game.running)
        self.assertNotIn(wll, entitylayer[0][0])
        self.assertEqual(1, len(levelmanager.Levels[0].EntityLayer[0][0]))

    def test_place_entity_invalid_level(self):
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestSuite.environment.Game.LevelManager
        wll = wall.Sandstone()
        self.assertEqual(2, len(levelmanager.Levels))
        levelmanager.place_entity(5, wll, (0,0))
        self.assertEqual(2, len(levelmanager.Levels))
        self.assertTrue(TestSuite.environment.Game.running)
        self.assertNotIn(wll, entitylayer[0][0])
        self.assertEqual(1, len(levelmanager.Levels[0].EntityLayer[0][0]))

    def test_move_valid(self):
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        for _ in range(4):
            self.loop(6)
        self.assertEqual(player.pos(), [1, 5, 0, 1])
        self.assertIn(player, entitylayer[1][5])

    def test_move_invalid(self):
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        self.loop(4)
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        self.assertIn(player, entitylayer[1][1])

    def test_push_barrel_valid(self):
        player = TestSuite.environment.Game.LevelManager.Player
        levelmanager = TestSuite.environment.Game.LevelManager
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
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

    def test_push_barrel_invalid(self):
        player = TestSuite.environment.Game.LevelManager.Player
        levelmanager = TestSuite.environment.Game.LevelManager
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        self.loop(6)
        barrel = tower.Barrel()
        levelmanager.place_entity(0, barrel, (1,1))
        self.loop(4)
        self.assertTrue(TestSuite.environment.Game.running)
        self.assertEqual(player.pos(), [1, 2, 0, 1])
        self.assertIn(player, entitylayer[1][2])
        self.assertEqual(2, len(entitylayer[1][2]))
        self.assertEqual(barrel.pos(), [1, 1, 0, 1])
        self.assertIn(barrel, entitylayer[1][1])
        self.assertEqual(2, len(entitylayer[1][1]))

    def test_throw_valid(self):
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        dart = item.Dart()
        player.Inventory.equip(dart)
        self.loop(6)
        self.loop('t4')
        self.assertEqual(dart.pos(), [1, 1, 0, 1])
        self.assertIn(dart, entitylayer[1][1])
        self.assertEqual(2, len(entitylayer[1][1]))

    def test_throw_invalid(self):
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        dart = item.Dart()
        self.loop(6)
        self.loop('t4')
        self.assertNotEqual(dart.pos(), [1, 1, 0, 1])
        self.assertNotIn(dart, entitylayer[1][1])
        self.assertEqual(1, len(entitylayer[1][1]))

    def test_light_layer(self):
        levelmanager = TestSuite.environment.Game.LevelManager
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        light = tower.Light()
        levelmanager.place_entity(0, light, (3,3))
        self.loop('.')
        pts = utility.get_one_layer_pts((3,3), len(lightlayer), len(lightlayer[0]))
        for pt in pts:
            self.assertTrue(lightlayer[pt[0]][pt[1]])

    def test_light_off(self):
        levelmanager = TestSuite.environment.Game.LevelManager
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        light = tower.Light()
        levelmanager.place_entity(0, light, (3,3))
        self.loop(3)
        self.loop(3)
        pts = utility.get_one_layer_pts((3,3), len(lightlayer), len(lightlayer[0]))
        for pt in pts:
            self.assertFalse(lightlayer[pt[0]][pt[1]])

    def test_barrel_break(self):
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestSuite.environment.Game.LevelManager
        player.Combat.accuracy = 100
        barrel = tower.Barrel()
        levelmanager.place_entity(0, barrel, (1,2))
        self.loop('F6')
        self.assertEqual(item.Wood().name, entitylayer[1][2][1].name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-d', '--display', action='store_true',
                        help='Turns the display on\n'\
                                'Display is off by default')
    args,unknown = parser.parse_known_args()
    TestSuite.display = args.display
    sys.argv = [sys.argv[0]] + unknown
    unittest.main()