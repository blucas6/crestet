import unittest
import entity
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

# configure the logger here since not running from main
logging.basicConfig(
    level = logging.INFO,
    filename = 'test.log',
    filemode = 'w',
    format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

Logger = logging.getLogger(__name__)

class TestSuite(unittest.TestCase):
    '''
    Crestet Unit Test Suite
    '''
    display = False
    '''Run the unit tests with the display'''
    turn_delay = 0.3
    '''Turn delay for running with a display'''

    @classmethod
    def setUpClass(cls):
        '''Set up the entire environment'''
        Logger.info('=== UNIT TEST SETUP ===')

        # make small arena
        config.LEVELROWS = 8
        config.LEVELCOLS = 20

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
        data['0']['plants'] = 0
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
        data['0']['plants'] = 0

        with open(config.SIM_LEVEL_CONFIG, 'w+') as jfile:
            json.dump(data, jfile, indent=4)

        # set the new config file
        config.LEVEL_CONFIG_FILE = config.SIM_LEVEL_CONFIG

        # load the environment
        TestSuite.environment = environment.Environment(
            seed='', display=TestSuite.display, timing=False)
        TestSuite.environment.start()

        if not TestSuite.environment.Game.running:
            print('FAILED to start the environment')
            exit()

        # if not running with a display, still configure it so unit tests can
        # check the display buffer
        if not TestSuite.display:
            termrows, termcols = config.LEVELROWS+config.LEVELORIGIN[0], config.LEVELCOLS+config.LEVELORIGIN[1]
            TestSuite.environment.Game.Display.init(termrows, termcols, config.LEVELORIGIN)

    @classmethod
    def tearDownClass(cls):
        '''Clean up the environment at the end'''
        TestSuite.environment.end()

    def setUp(self):
        '''Reset the environment before every test'''
        Logger.info('')
        Logger.info('')
        Logger.info(f'EXECUTING: {self._testMethodName}')
        TestSuite.environment.reset(new_seed=True)

    def loop(self, action=''):
        '''Runs a single loop of the game, with rendering'''
        if self.display:
            TestSuite.environment.render()
            time.sleep(self.turn_delay)
        TestSuite.environment.Game.game_loop(str(action))
        if self.display:
            TestSuite.environment.render()
            time.sleep(self.turn_delay)

    def test_place_player_valid(self):
        '''Checks that entities are placed correctly'''
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        self.assertIn(player, entitylayer[1][1])
        self.assertEqual(tower.Floor().name, entitylayer[1][1][0].name)
        self.assertEqual(2, len(entitylayer[1][1]))

    def test_place_entity_invalid_wall(self):
        '''Checks that entities cannot be placed in walls'''
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestSuite.environment.Game.LevelManager
        wll = wall.Sandstone()
        levelmanager.place_entity(0, wll, (0,0))
        self.assertTrue(TestSuite.environment.Game.running)
        self.assertNotIn(wll, entitylayer[0][0])
        self.assertEqual(1, len(levelmanager.Levels[0].EntityLayer[0][0]))

    def test_place_entity_invalid_level(self):
        '''Checks that entities cannot be placed in levels that don't exist'''
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
        '''Checks that the player can move correctly'''
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        for _ in range(4):
            self.loop(6)
        self.assertEqual(player.pos(), [1, 5, 0, 1])
        self.assertIn(player, entitylayer[1][5])

    def test_move_invalid(self):
        '''Checks that the player cannot move into a wall'''
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        self.loop(4)
        self.assertEqual(player.pos(), [1, 1, 0, 1])
        self.assertIn(player, entitylayer[1][1])

    def test_push_barrel_valid(self):
        '''Checks that the player can move a barrel'''
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
        '''Checks that the player cannot move the barrel into a wall'''
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
        '''Checks that the player can throw an object'''
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
        '''Checks that the player cannot throw an object if not equipped'''
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        dart = item.Dart()
        self.loop(6)
        self.loop('t4')
        self.assertNotEqual(dart.pos(), [1, 1, 0, 1])
        self.assertNotIn(dart, entitylayer[1][1])
        self.assertEqual(1, len(entitylayer[1][1]))

    def test_light_layer(self):
        '''Checks that the lights add to the light layer'''
        levelmanager = TestSuite.environment.Game.LevelManager
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        light = tower.Light()
        levelmanager.place_entity(0, light, (3,3))
        self.loop('.')
        pts = utility.get_one_layer_pts((3,3), len(lightlayer), len(lightlayer[0]))
        for pt in pts:
            self.assertTrue(lightlayer[pt[0]][pt[1]])

    def test_light_off(self):
        '''Checks that the lights can be turned off'''
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
        '''Checks that a barrel can be broken'''
        player = TestSuite.environment.Game.LevelManager.Player
        entitylayer = TestSuite.environment.Game.LevelManager.Levels[0].EntityLayer
        levelmanager = TestSuite.environment.Game.LevelManager
        player.Combat.accuracy = 100
        barrel = tower.Barrel()
        levelmanager.place_entity(0, barrel, (1,2))
        self.loop('F6')
        self.assertEqual(item.Wood().name, entitylayer[1][2][1].name)

    def test_fov_barrel_memory(self):
        '''Checks that barrels can be remembered'''
        player = TestSuite.environment.Game.LevelManager.Player
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        menumanager = TestSuite.environment.Game.MenuManager
        display = TestSuite.environment.Game.Display
        levelmanager = TestSuite.environment.Game.LevelManager
        player.Brain.sightrange = 2
        player.Brain.fovmemory = brain.FOVMemory.OBJECTS_BARRELS
        row = 1
        col = 4
        r,c = display.level_to_screen_pos(row, col)
        levelmanager.place_entity(0, tower.Barrel(), (row,col))
        self.loop('.')
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        self.assertEqual(display.unknownglyph, screenbuffer[r][c])
        for _ in range(2):
            self.loop(6)
        for _ in range(2):
            self.loop(4)
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        self.assertEqual('0', screenbuffer[r][c])

    def test_fov_hidden_object(self):
        '''Checks that the FOV will not reveal hidden objects'''
        player = TestSuite.environment.Game.LevelManager.Player
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        menumanager = TestSuite.environment.Game.MenuManager
        display = TestSuite.environment.Game.Display
        levelmanager = TestSuite.environment.Game.LevelManager
        player.Brain.sightrange = 2
        row = 1
        col = 4
        levelmanager.place_entity(0, item.Dart(), (row,col))
        levelmanager.place_entity(0, tower.Barrel(), (row,col))
        self.loop('.')
        for _ in range(2):
            self.loop(6)
        for _ in range(2):
            self.loop(4)
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        r,c = display.level_to_screen_pos(row, col)
        self.assertEqual(display.unknownglyph, screenbuffer[r][c])

    def test_fov_blind_barrel(self):
        '''Checks that barrels will be hidden when blinded'''
        player = TestSuite.environment.Game.LevelManager.Player
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        menumanager = TestSuite.environment.Game.MenuManager
        display = TestSuite.environment.Game.Display
        levelmanager = TestSuite.environment.Game.LevelManager
        messager = TestSuite.environment.Game.Messager
        row = 1
        col = 4
        r,c = display.level_to_screen_pos(row, col)
        levelmanager.place_entity(0, tower.Barrel(), (row,col))
        self.loop('.')
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        self.assertEqual('0', screenbuffer[r][c])
        player.apply_status(messager, entity.StatusEffect.BLIND)
        self.loop('.')
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        self.assertEqual(' ', screenbuffer[r][c])

    def test_fov_blind_object_memory(self):
        '''Checks that objects will be remembered when blinded'''
        player = TestSuite.environment.Game.LevelManager.Player
        lightlayer = TestSuite.environment.Game.LevelManager.Levels[0].LightLayer
        menumanager = TestSuite.environment.Game.MenuManager
        display = TestSuite.environment.Game.Display
        levelmanager = TestSuite.environment.Game.LevelManager
        messager = TestSuite.environment.Game.Messager
        row = 1
        col = 4
        r,c = display.level_to_screen_pos(row, col)
        levelmanager.place_entity(0, item.Dart(), (row,col))
        self.loop('.')
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        self.assertEqual(')', screenbuffer[r][c])
        player.apply_status(messager, entity.StatusEffect.BLIND)
        self.loop('.')
        screenbuffer, _ = display.prepare_buffers(
            player.Brain.mentalmap, lightlayer, menumanager, player.status
        )
        self.assertEqual(')', screenbuffer[r][c])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-d', '--display', action='store_true',
                        help='Turns the display on\n'\
                                'Display is off by default')
    args,unknown = parser.parse_known_args()
    TestSuite.display = args.display
    # reset args to not interfere with unittest args
    sys.argv = [sys.argv[0]] + unknown
    unittest.main()