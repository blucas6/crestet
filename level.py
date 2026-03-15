import logger
import timing
import algo
import config
import item
import player
import utility
import tower
import entity as e
import monster

class Level:
    def __init__(self, rows, cols, z, rng):
        self.rows = rows 
        '''Total height of the level'''
        self.cols = cols 
        '''Total width of the level'''
        self.z = z
        '''Level index'''
        self.EntityLayer = [[[] for _ in range(self.cols)]
                                for _ in range(self.rows)]
        '''Holds all entities on the level'''
        self.LightLayer = [[0 for _ in range(self.cols)]
                                for _ in range(self.rows)]
        '''Tracks all lit spaces on level'''
        self.RNG = rng
        '''Random generator with optional seed'''


class LevelManager:
    '''
    Contains all level objects and handles all level interactions
    '''
    def __init__(self):
        self.totallevels = 0
        '''Total amount of levels in tower'''
        self.currentz = -1
        '''Current z level the player is on'''
        self.levelrows = 0
        '''Each level row amount'''
        self.levelcols = 0
        '''Each level column amount'''
        self.RNG = 0
        '''Seed for the game'''
        self.Levels: list[Level] = []
        '''Holds all level objects'''
        self.Player: player.Player = None
        '''Player object'''
    
    def init(self, totallevels, currentz, levelrows, levelcols, rng):
        self.totallevels = totallevels
        self.levelrows = levelrows
        self.levelcols = levelcols
        self.RNG = rng
        self.currentz = currentz
        self.Levels = []
        for z in range(self.totallevels):
            self.Levels.append(
                    Level(rows=levelrows, cols=levelcols, z=z, rng=self.RNG)
                    )
        self.Player = player.Player()
        self.Player.init(levelrows, levelcols)

    def level_setup_default(self, playerpos):
        '''Load a default map on all levels'''
        downstairpos = []
        upstairpos = []
        for z,level in enumerate(self.Levels):
            self.generate_surrounding_walls(level)
            #self.generate_walls(level)
            if z == 0:
                downstairpos = self.generate_upstair(level)
                self.generate_clear_path(level, playerpos, downstairpos)
                # add player
                self.place_entity(self.Levels[0], self.Player, playerpos)
            elif z == self.totallevels-1:
                self.generate_downstair(level, downstairpos)
            else:
                downstairplaced = self.generate_downstair(level, downstairpos)
                downstairpos = self.generate_upstair(level)
                self.generate_clear_path(level, downstairplaced, downstairpos)
            self.generate_light(level)
            self.generate_mons(level)
            self.generate_items(level)

    def generate_downstair(self, level, downstairpos):
        '''Places the downstairs at the designated spot, returns the placement'''
        self.place_entity(level, tower.StairDown(), downstairpos, overwrite=True)
        return downstairpos

    def generate_upstair(self, level):
        '''Places an upstairs in a random spot, returns the placement'''
        r = self.RNG.randint(1,self.levelrows-2)
        c = self.RNG.randint(1,self.levelcols-2)
        self.place_entity(level, tower.StairUp(), [r,c], overwrite=True)
        return [r,c]
    
    def generate_clear_path(self, level, a, b):
        '''Creates a floor path between points a -> b'''
        if not a or not b:
            logger.Logger.log(f'Error: Clearing a path between {a}->{b} cannot be None!')
            return
        logger.Logger.log(f'Clear Path: {a} -> {b}')
        grid = [[max([ent.layer for ent in elist]) for elist in row]
                    for row in level.EntityLayer]
        pts = algo.dijkstra(grid, tuple(a), tuple(b), diagonals=False)
        if pts:
            for pt in pts:
                maxlayer = max([x.layer for x in level.EntityLayer[pt[0]][pt[1]]])
                if maxlayer >= e.Layer.WALL_LAYER:
                    self.place_entity(level, tower.Floor(), pt, overwrite=True)

    def generate_surrounding_walls(self, level):
        '''Adds surrounding walls and floor to a blank entity array'''
        for r in range(self.levelrows):
            for c in range(self.levelcols):
                # check if within the array or on the border
                if r == 0 or c == 0 or r == self.levelrows-1 or c == self.levelcols-1:
                    self.place_entity(level, tower.Wall(), [r,c], overwrite=True)
                else:
                    self.place_entity(level, tower.Floor(), [r,c], overwrite=True)

    def generate_mons(self, level):
        for _ in range(5):
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            self.place_entity(level, monster.Jelly(), (r,c))
        for _ in range(5):
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            self.place_entity(level, monster.Newt(), (r,c))

    def generate_items(self, level):
        for _ in range(2):
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            self.place_entity(level, item.Dart(), (r,c))

    def generate_light(self, level):
        for _ in range(5):
            r = self.RNG.randint(1,self.levelrows-2)
            c = self.RNG.randint(1,self.levelcols-2)
            light = tower.Light()
            self.place_entity(level, light, (r,c))
            light.update_state(self)

    def generate_walls(self, level, minwalls=config.MINIMUM_WALLS):
        '''
        Generates walls on the level using predetermined shapes
        Minimum walls counts how many wall spaces need to be covered in the level
        '''
        wallshapes = []
        wallL = [
            ['0','',''],
            ['0','',''],
            ['0','0','0']
        ]
        wallPlus = [
            ['','0',''],
            ['0','0','0'],
            ['','0','']
        ]
        wallLine = [
            ['','0',''],
            ['','0',''],
            ['','0','']
        ]
        wallCorner = [
            ['','',''],
            ['0','',''],
            ['0','0','']
        ]
        wallshapes.append(wallL)
        wallshapes.append(wallPlus)
        wallshapes.append(wallLine)
        wallshapes.append(wallCorner)
        wallsplaced = 0
        maxiterations = 100
        # go through until minimum wall amount was reached or max tries
        while wallsplaced < minwalls and maxiterations > 0:
            maxiterations -= 1
            for r in range(self.levelrows):
                for c in range(self.levelcols): 
                    if self.RNG.randint(1,100) < 10:
                        # grab a shape and rotate it
                        shape = wallshapes[self.RNG.randint(0,len(wallshapes)-1)]
                        times = self.RNG.randint(0,3)
                        for _ in range(times):
                            shape = [list(row) for row in zip(*shape[::-1])]
                        for sr,srows in enumerate(shape):
                            for sc,scols in enumerate(srows):
                                if scols:
                                    pt = [r+sr,c+sc]
                                    self.place_entity(level, tower.Wall(), pt)
                                    wallsplaced += 1

    def place_entity(self, level, entity, pos, overwrite=False):
        '''Place an entity into the level'''

        if not self.is_entity_pos_valid(level, entity, pos, overwrite=overwrite):
            logger.Logger.log(f'Error: Entity {entity.name} cannot be placed at {pos} z:{level.z}')
            return
        
        r = pos[0]
        c = pos[1]

        # if overwriting, reset the index 
        if overwrite:
            level.EntityLayer[r][c] = [entity]
            entity.set_pos(r, c, level.z, 0)
        # if adding, append to the end
        else:
            level.EntityLayer[r][c].append(entity)
            idx = len(level.EntityLayer[r][c])-1
            entity.set_pos(r, c, level.z, idx)
            # trigger the on placed hook because entity was placed
            entity.on_placed(self)
            # trigger the on top hook because entity was placed on top of other entities
            for ent in level.EntityLayer[r][c]:
                if ent.id != entity.id:
                    ent.on_top(self)
        #logger.Logger.log(f'Entity {entity.name} placed at {entity.pos()}')

    def is_entity_pos_valid(self, level, entity, pos, overwrite=False):
        '''Checks if an entity and a new position would be valid'''

        if not self.within_level(pos, level.z):
            return False

        # if overwriting, specific position will always work
        if overwrite:
            return True

        # run a check if an entity is on a higher layer than 0-1
        if entity.layer > e.Layer.OBJECT_LAYER:
            if level.EntityLayer[pos[0]][pos[1]]:
                maxlayer = max([x.layer for x in level.EntityLayer[pos[0]][pos[1]]])
                if entity.layer <= maxlayer:
                    return False 
        return True

    def get_curr_level(self):
        '''Returns the current level or None if the current z index points to nothing'''
        if self.currentz > -1 and self.currentz < len(self.Levels):
            return self.Levels[self.currentz]
        return None

    def update_level(self, animator, messager, event):
        '''
        Go through all entities and update them
        '''

        timing.Timing().start('Game Loop')

        logger.Logger.log('----------TURN UPDATE-----------')

        self.Player.energy = 100
        self.Player.do_action(self, animator, messager, event)

        # update the level the player is on
        self.currentz = self.Player.z

        level = self.get_curr_level()
        if not level:
            return

        # clear light layer
        level.LightLayer = [[0 for _ in range(self.levelcols)]
                                for _ in range(self.levelrows)]

        energy = 100 - self.Player.energy
        if energy == 100:
            energy = self.Player.speed
        logger.Logger.log(f'Player energy: {energy}')

        done_turn = False
        while not done_turn:
            done_turn = True
            for row in level.EntityLayer:
                for entitylist in row:
                    for entity in entitylist:
                        done_turn = self.update_entity(animator, messager, entity, energy)

        # update light layer
        for row in level.EntityLayer:
            for entitylist in row:
                for entity in entitylist:
                    if entity.name == 'Light':
                        entity.update_state(self)

        timing.Timing().end()

    def update_entity(self, animator, messager, entity, energy):
        entity.energy += energy
        energystart = entity.energy
        entity.take_turn(self, animator, messager, energy)
        energyend = entity.energy
        if entity.energy == 0 or energystart == energyend:
            entity.turn += 1
            return True
        return False

    def within_level(self, pos, z):
        '''Returns if a position is valid within the map'''
        if (z > -1 and z < len(self.Levels) and
            pos[0] < len(self.Levels[z].EntityLayer) and 
            pos[1] < len(self.Levels[z].EntityLayer[0])
            and pos[0] >= 0 and pos[1] >= 0):
            return True
        return False

    def move_entity(self, entity, pos):
        '''Moves an entity from one place to a new position if valid'''

        #logger.Logger.log(f'Moving entity: {entity.name}|{entity.id}')
        level = self.Levels[entity.z]

        if not self.is_entity_pos_valid(level, entity, pos):
            logger.Logger.log(f'Moving entity failed: invalid {entity.name}|{entity.id}')
            return False

        # move is valid - delete old entity
        entity = self.remove_entity(entity)

        # add entity to new position
        self.place_entity(level, entity, pos)

        return True
    
    def move_entity_z(self, entity, newz, newpos):
        '''Moves an entity to a new z level'''

        if newz >= len(self.Levels) or newz < 0:
            logger.Logger.log(f'Error: {entity} cannot go past last level!')
            return

        level = self.Levels[newz]

        if not self.is_entity_pos_valid(level, entity, newpos):
            logger.Logger.log(f'Error: {entity} moving to z:{newz} is invalid!')
            return False

        entity = self.remove_entity(entity)

        self.place_entity(level, entity, newpos)
        return True

    def remove_entity(self, entity):
        '''Deletes an entity from the current position and returns it'''
        r = entity.row
        c = entity.col
        idx = entity.idx
        z = entity.z
        level = self.Levels[z]
        # decrement the index for the other entities on the square
        for ix in range(idx, len(level.EntityLayer[r][c])):
            level.EntityLayer[r][c][ix].idx -= 1
        return level.EntityLayer[r][c].pop(idx)


