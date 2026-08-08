import config
import utility
import item
import message
import timing
import player
import entity as e
import biosphere
import logging

Logger = logging.getLogger(__name__)

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
        self.Messager: message.Messager = None
        '''Connection to message queue from game'''
    
    def init(self, messager, rng, levelrows, levelcols):
        self.levelrows = levelrows
        self.levelcols = levelcols
        self.Messager = messager
        self.RNG = rng
        self.Levels = []
        self.Player = player.Player()
        self.Player.init()

    def place_player(self, playerpos, playerz):
        '''
        Place the player on the level

        Setting the currentz tells the displayer what level to view
        '''
        self.place_entity(playerz, self.Player, playerpos)
        self.currentz = playerz

    def add_to_level(self, entity, pos, z):
        entity.on_init(self.RNG)
        return self.place_entity(z, entity, pos)

    def place_entity(self, z, entity, pos, overwrite=False):
        '''Place an entity into the level'''

        if not entity:
            Logger.error(f'Error: cannot place null entity')
            return False

        if z < 0 or z >= len(self.Levels):
            return False

        level = self.Levels[z]

        if not self.is_entity_pos_valid(level, entity, pos, overwrite=overwrite):
            Logger.error(f'Error: Entity {entity.name} cannot be placed: {pos} z:{z}')
            return False
        
        r = pos[0]
        c = pos[1]

        # if overwriting, reset the index 
        if overwrite:
            level.EntityLayer[r][c] = [entity]
            entity.set_pos(r, c, level.z, 0)
        # if adding, append to the end
        else:
            # check max entity count, excess objects will be deleted
            entity_amount = len(level.EntityLayer[r][c])
            deleteidx = 0
            while entity_amount+1 > config.LEVELMAX_ENTITIES:
                check_ent = level.EntityLayer[r][c][deleteidx]
                if check_ent.layer == e.Layer.OBJECT_LAYER:
                    Logger.warning(f'CULLING: {check_ent}')
                    self.remove_entity(check_ent)
                entity_amount = len(level.EntityLayer[r][c])
                deleteidx += 1
            # once there is room, place the entity
            level.EntityLayer[r][c].append(entity)
            idx = len(level.EntityLayer[r][c])-1
            entity.set_pos(r, c, level.z, idx)
            # trigger the on placed hook because entity was placed
            entity.on_placed(self, self.Messager)
            # trigger the on top hook because entity was placed on top of other entities
            for ent in level.EntityLayer[r][c]:
                if ent.id != entity.id:
                    ent.on_top(entity, self)
        Logger.debug(f'Entity {entity} placed at {level.EntityLayer[r][c]}')
        return True

    def is_entity_pos_valid(self, level, entity, pos, overwrite=False):
        '''Checks if an entity and a new position would be valid'''
        
        if not pos:
            return False

        if not self.within_level(pos, level.z):
            return False

        # if overwriting, specific position will always work
        if overwrite:
            return True

        # if square already has a high layer, can't place
        maxlayer = utility.get_max_layer(level.EntityLayer[pos[0]][pos[1]])
        if maxlayer >= e.Layer.WALL_LAYER:
            return False
        # barrels and monsters cannot be placed on each other
        if (maxlayer >= e.Layer.BARREL_LAYER and
            (entity.layer == e.Layer.BARREL_LAYER or
             entity.layer == e.Layer.MONSTER_LAYER)):
            return False
        return True

    def get_curr_level(self):
        '''Returns the current level or None if the current z index points to nothing'''
        if self.currentz > -1 and self.currentz < len(self.Levels):
            return self.Levels[self.currentz]
        return None

    def update_level(self, level, energy, animator, messager, menumanager, statemachine, currentturn):
        '''Updates all entities on a single level with a given amount of energy'''
        if not level:
            return

        # clear light layer, do not create a new list just update
        for r in range(self.levelrows):
            for c in range(self.levelcols):
                level.LightLayer[r][c] = 0

        # energy
        for row in level.EntityLayer:
            for entitylist in row:
                for entity in entitylist:
                    entity.energy += energy

        # update loop
        done_turn = False
        while not done_turn:
            done_turn = True
            for row in level.EntityLayer:
                for entitylist in row:
                    # create a manually loop since entities might be removed
                    # during an update loop
                    index = 0
                    currlistsize = len(entitylist)
                    while index < currlistsize:
                        try:
                            entity = entitylist[index]
                        except:
                            Logger.error(f'ERROR: {entitylist}')
                            Logger.error(f'ERROR: idx:{index}')
                            break
                        currlistsize = len(entitylist)
                        if entity.name == 'Newt':
                            Logger.info(f'Current turn: {currentturn} {entity} {entity.turn}')
                        done = self.update_entity(animator,
                                                  messager,
                                                  menumanager,
                                                  statemachine,
                                                  entity,
                                                  currentturn)
                        # some entities need more turns
                        if not done: done_turn = False
                        # entities were removed from the list
                        # restart the index
                        if currlistsize < len(entitylist):
                            index = 0
                        else:
                            index += 1

    def update_player(self, animator, messager, menumanager, statemachine, event, rng):
        '''Updates the player and returns the energy used'''
        Logger.info(f'-------- TURN UPDATE ({self.Player.turn + 1}) ---------')
        self.Player.energy = 100
        self.Player.update_status()
        self.Player.update_state(self)
        Logger.info(f'Player status: {self.Player.status}')
        self.Player.do_action(self, animator, messager, menumanager, statemachine, event, rng)
        self.Player.turn += 1

        # calculate how much energy the player used
        energy = 100 - self.Player.energy
        if energy == 100:
            # player rested
            energy = self.Player.speed
        return energy

    def update_all(self, animator, messager, menumanager, statemachine, energy, currentturn):
        '''Go through all entities and update them'''

        timing.Timing.start('Game Loop')

        Logger.info(f'-- UPDATE ALL {currentturn} --')

        # update the level the player is on
        self.currentz = self.Player.z

        for level in self.Levels:
            self.update_level(level, energy, animator, messager, menumanager, statemachine, currentturn)

        timing.Timing.end()

    def update_entity(self, animator, messager, menumanager, statemachine, entity, currentturn):
        '''Update a single entity'''
        if entity.turn > currentturn:
            return True
        energystart = entity.energy
        entity.update_state(self)
        entity.update_status()
        entity.take_turn(self, animator, messager, menumanager, statemachine, self.RNG) 
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

        level = self.Levels[entity.z]

        if not self.is_entity_pos_valid(level, entity, pos):
            Logger.error(f'Moving entity failed: invalid {entity}')
            return False

        # move is valid - delete old entity
        entity = self.remove_entity(entity)

        # add entity to new position
        self.place_entity(level.z, entity, pos)

        return True
    
    def move_entity_z(self, entity, newz, newpos):
        '''Moves an entity to a new z level'''

        if newz >= len(self.Levels) or newz < 0:
            Logger.error(f'Error: {entity} cannot go past last level!')
            return

        level = self.Levels[newz]

        if not self.is_entity_pos_valid(level, entity, newpos):
            Logger.error(f'Error: {entity} moving to z:{newz} is invalid!')
            return False

        entity = self.remove_entity(entity)

        self.place_entity(level.z, entity, newpos)

        entity.on_zchange(level)

        return True

    def remove_entity(self, entity):
        '''
        Deletes an entity from the current position and returns it
        Uses entity position data to identify the entity
        '''
        r = entity.row
        c = entity.col
        idx = entity.idx
        z = entity.z
        level = self.Levels[z]
        # decrement the index for the other entities on the square
        for ix in range(idx, len(level.EntityLayer[r][c])):
            level.EntityLayer[r][c][ix].idx -= 1
        return level.EntityLayer[r][c].pop(idx)

    def reset_turns(self, turn):
        for level in self.Levels:
            for row in level.EntityLayer:
                for col in row:
                    for ent in col:
                        ent.turn = turn