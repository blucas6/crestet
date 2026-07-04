import config
import item
import monster
import utility 
import copy
import entity
import algo
import tower
import logger
import json
import level
from dataclasses import dataclass

@dataclass
class LevelLayout:
    '''Configuration data for each level'''
    floor: bool
    '''Generate the floor'''
    outer_walls: bool
    '''Generate the outer walls'''
    upstair: bool
    '''Generate an upstairs'''
    downstair: bool
    '''Generate a downstairs'''
    min_walls: int
    '''Minimum amount of walls to place inside'''
    lights: bool
    '''Generate lights'''
    mons: int
    '''Minimum amount of monsters on the level'''
    items: int
    '''Minimum amount of items on the level'''

    upstair_pos: tuple = ()
    '''Location of the upstairs on the level'''
    downstair_pos: tuple = ()
    '''Location of the downstairs on the level'''

class Generator:
    '''Reads from a config file to build all level objects'''
    def __init__(self):
        self.levelrows = 0
        '''How many rows in a level'''
        self.levelcols = 0
        '''How many columns in a level'''
        self.total_levels = 0
        '''Total levels in the game'''
        self.level_layouts: list[LevelLayout] = []
        '''List of all LevelLayout objects'''
        self.light_amount = 0
        '''How many lights to generate in each level'''
        self.wall_shapes = {}
        '''Wall shapes for inner wall generation'''

    def load_config(self, levelrows, levelcols, rng):
        '''Read the config file and load the level layout objects'''
        self.level_layouts = []
        self.levelrows = levelrows
        self.levelcols = levelcols
        self.RNG = rng
        try:
            data = None
            with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
                data = json.load(jfile)

            # set up the generator class members
            self.total_levels = data['total_levels']
            self.light_amount = data['light_amount']
            self.wall_shapes = data['wall_shapes']

            # load each level config
            levellayout = LevelLayout(**data['0'])
            self.level_layouts.append(levellayout)

            # if no level was specified, use the previous level config
            for ix in range(1,self.total_levels):
                if str(ix) in data:
                    levelgen = LevelLayout(**data[str(ix)])
                self.level_layouts.append(copy.deepcopy(levelgen))
            
        except Exception as ex:
            logger.Logger.log(f'Generator parsing error: {ex}')
            raise

    def generate_levels(self, levelmanager: level.LevelManager):
        '''Go through each level layout and set up the level'''

        levelmanager.totallevels = self.total_levels

        for z,level_layout in enumerate(self.level_layouts):
            # keep track of stair positions
            upstair_pos = []
            downstair_pos = []
            # add level to level manager list before building the level
            currlevel = level.Level(rows=self.levelrows, cols=self.levelcols, z=z, rng=self.RNG)
            levelmanager.Levels.append(currlevel)

            if level_layout.floor:
                self.generate_floor(levelmanager, currlevel)
            if level_layout.outer_walls:
                self.generate_outer_walls(levelmanager, currlevel)
            if level_layout.min_walls > 0:
                self.generate_walls(levelmanager, currlevel, level_layout.min_walls)
            if level_layout.upstair:
                # save the upstairs position to the following level's downstairs position
                upstair_pos = self.generate_upstair(levelmanager, currlevel)
                if z+1 < len(self.level_layouts):
                    self.level_layouts[z+1].downstair_pos = upstair_pos
            if level_layout.downstair:
                downstair_pos = self.generate_downstair(levelmanager, currlevel, level_layout)
            if level_layout.lights:
                self.generate_lights(levelmanager, currlevel)
            if upstair_pos and downstair_pos:
                self.generate_clear_path(levelmanager, currlevel, upstair_pos, downstair_pos)
            if level_layout.mons > 0:
                self.generate_mons(levelmanager, currlevel, level_layout.mons)
            if level_layout.items > 0:
                self.generate_items(levelmanager, currlevel, level_layout.items)
            if z == config.PLAYERZ:
                # make sure player can be placed
                levelmanager.place_entity(currlevel.z, tower.Floor(), config.PLAYERPOS, overwrite=True)
                if level_layout.upstair:
                    logger.Logger.log(f'Clearing path for player')
                    # make path for player to upstair
                    self.generate_clear_path(levelmanager, currlevel, config.PLAYERPOS, upstair_pos)
        logger.Logger.log(f'----- FINISHED LEVEL GENERATION -----')

    def generate_floor(self, levelmanager: level.LevelManager, currlevel: level.Level):
        '''Adds floors to the entity array'''
        for r in range(self.levelrows):
            for c in range(self.levelcols):
                levelmanager.place_entity(currlevel.z, tower.Floor(), [r,c], overwrite=True)

    def generate_outer_walls(self, levelmanager: level.LevelManager, currlevel: level.Level):
        '''Adds surrounding walls to the entity array'''
        for r in range(self.levelrows):
            for c in range(self.levelcols):
                if r == 0 or c == 0 or r == self.levelrows-1 or c == self.levelcols-1:
                    levelmanager.place_entity(currlevel.z, tower.Wall(), [r,c], overwrite=True)

    def generate_upstair(self, levelmanager: level.LevelManager, currlevel: level.Level):
        '''Places an upstairs in a random spot, returns the placement'''
        r = self.RNG.randint(1,self.levelrows-2)
        c = self.RNG.randint(1,self.levelcols-2)
        levelmanager.place_entity(currlevel.z, tower.StairUp(), [r,c], overwrite=True)
        logger.Logger.log(f'Placed UPSTAIR z:{currlevel.z}: {(r,c)}')
        return (r,c)
    
    def generate_downstair(self, levelmanager: level.LevelManager, currlevel: level.Level,
                           levellayout: LevelLayout):
        '''Places the downstairs at the designated spot, returns the placement'''
        if not levellayout.downstair_pos:
            logger.Logger.log(f'ERROR: downstair position is empty! z:{currlevel.z}')
            return ()
        levelmanager.place_entity(currlevel.z,
                                  tower.StairDown(),
                                  levellayout.downstair_pos,
                                  overwrite=True)
        return levellayout.downstair_pos

    def generate_clear_path(self, levelmanager:level.LevelManager, currlevel:level.Level, a, b):
        '''Creates a floor path between points a -> b'''
        if not a or not b:
            logger.Logger.log(f'Error: Clearing a path between {a}->{b} cannot be None!')
            return
        grid = [[max([ent.layer for ent in elist]) for elist in row]
                    for row in currlevel.EntityLayer]
        pts = algo.dijkstra(grid, tuple(a), tuple(b), diagonals=False)
        logger.Logger.log(f'Clear Path ({currlevel.z}): {a} -> {b}\n{pts}')
        if pts:
            for pt in pts:
                maxlayer = max([x.layer for x in currlevel.EntityLayer[pt[0]][pt[1]]])
                if maxlayer >= entity.Layer.WALL_LAYER:
                    levelmanager.place_entity(currlevel.z, tower.Floor(), pt, overwrite=True)

    def generate_walls(self, levelmanager:level.LevelManager, currlevel:level.Level, minwalls):
        '''
        Generates walls on the level using predetermined shapes
        Minimum walls counts how many wall spaces need to be covered in the level
        '''
        wallsplaced = 0
        attempt = 0
        # go through until minimum wall amount was reached or max tries
        while wallsplaced < minwalls and attempt < config.MAX_RETRIES:
            attempt += 1
            for r in range(self.levelrows):
                for c in range(self.levelcols): 
                    if self.RNG.randint(1,100) < 10:
                        # grab a shape and rotate it
                        shape = self.wall_shapes[self.RNG.randint(0,len(self.wall_shapes)-1)]
                        times = self.RNG.randint(0,3)
                        for _ in range(times):
                            shape = [list(row) for row in zip(*shape[::-1])]
                        for sr,srows in enumerate(shape):
                            for sc,scols in enumerate(srows):
                                if scols:
                                    pt = [r+sr,c+sc]
                                    levelmanager.place_entity(currlevel.z, tower.Wall(), pt)
                                    wallsplaced += 1
                                    if wallsplaced >= minwalls:
                                        return

    def generate_lights(self, levelmanager:level.LevelManager, currlevel:level.Level):
        '''Add lights to the level'''
        for _ in range(self.light_amount):
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            _,myentity  = utility.get_max_layer(currlevel.EntityLayer[r][c])
            valid = all([False if type(ent) == tower.Light else True for ent in currlevel.EntityLayer[r][c]])
            if myentity.layer < entity.Layer.WALL_LAYER and valid:
                light = tower.Light()
                levelmanager.place_entity(currlevel.z, light, (r,c))
                light.update_state(levelmanager)

    def generate_mons(self, levelmanager: level.LevelManager, currlevel: level.Level, mon_amount):
        '''Add monsters to the level'''
        attempt = 0
        while mon_amount > 0 and attempt < config.MAX_RETRIES:
            attempt += 1
            num = self.RNG.randint(0, 2)
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            if [r,c] == config.PLAYERPOS:
                continue
            if num == 0:
                if levelmanager.place_entity(currlevel.z, monster.Jelly(), (r,c)):
                    mon_amount -= 1
            elif num == 1:
                if levelmanager.place_entity(currlevel.z, monster.Goblin(), (r,c)):
                    mon_amount -= 1
            else:
                if levelmanager.place_entity(currlevel.z, monster.Newt(), (r,c)):
                    mon_amount -= 1
        '''
        for _ in range(1):
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            levelmanager.place_entity(currlevel.z, monster.Human(), (r,c))
        '''

    def generate_items(self, levelmanager: level.LevelManager, currlevel: level.Level, item_amount):
        '''Add items to the level'''
        attempt = 0
        while item_amount > 0 and attempt < config.MAX_RETRIES:
            if self.RNG.randint(0, 1) == 0:
                r = self.RNG.randint(1,self.levelrows-2)
                c = self.RNG.randint(1,self.levelcols-2)
                if levelmanager.place_entity(currlevel.z, tower.Barrel(), (r,c)):
                    item_amount -= 1
            else:
                r = self.RNG.randint(1,self.levelrows-2)
                c = self.RNG.randint(1,self.levelcols-2)
                if levelmanager.place_entity(currlevel.z, item.Fruit(), (r,c)):
                    item_amount -= 1

