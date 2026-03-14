import itertools
import utility
import logger
import enum

class AttackSpeed(enum.IntEnum):
    '''Corresponding energy costs for attacking'''
    VERY_SLOW = 7
    SLOW = 6
    AVERAGE = 5
    FAST = 4
    VERY_FAST = 3

class Speed(enum.IntEnum):
    '''Corresponding energy costs for movements'''
    VERY_SLOW = 55
    SLOW = 30
    AVERAGE = 12
    FAST = 5
    VERY_FAST = 3

class Layer(enum.IntEnum):
    '''
    Layer Types:
        0-1: stackable, anything with these layers will be placed on top of
            each other
        2: not stackable, entities that move around, FOV can see through them
        3: not stackable, FOV cannot see through them
    '''
    FLOOR_LAYER = 0
    OBJECT_LAYER = 1
    MONST_LAYER = 2
    WALL_LAYER = 3

class Size(enum.IntEnum):
    '''
    Size Types:
        1: very small, like darts
        2: small, like insects
        3: medium, hobbits or kobolds
        4: large, people
        5: very large, orcs or trolls
        6: giant, yep giants
        7: humongous, titans
    '''
    VERY_SMALL = 1
    SMALL = 2
    MEDIUM = 3
    LARGE = 4
    VERY_LARGE = 5
    GIANT = 6
    HUMONGOUS = 7

class Entity:
    '''
    Base entity class for all objects
    '''

    _id_gen = itertools.count(1)
    '''ID counter for all entities'''

    def __init__(self, name, glyph, color, layer, size):
        self.id = next(Entity._id_gen)
        '''Unique id'''
        self.name = name
        '''Name of entity'''
        self.glyph = glyph
        '''Glyph for display'''
        self.color = color
        '''Color for display'''
        self.row = -1
        '''Row position'''
        self.col = -1
        '''Column position'''
        self.z = -1
        '''Level z index'''
        self.idx = -1
        '''Index in entity layer'''
        self.layer = layer
        '''Layer level at which the entity resides'''
        self.turn = 0
        '''Keeps track of game turns'''
        self.size = size
        '''Size enum for the entity'''
        self.energy = 0
        '''Energy bank'''

    def pos(self):
        '''Used for getting the entire position'''
        return [self.row, self.col, self.z, self.idx]

    def set_pos(self, row=-1, col=-1, z=-1, index=-1):
        '''Sets the position of the entity'''
        if row != -1:
            self.row = row
        if col != -1:
            self.col = col
        if z != -1:
            self.z = z
        if index != -1:
            self.idx = index

    def take_turn(self, *_):
        '''Starting point of an entity's turn'''
        pass

    def move(self, levelmanager, pos):
        '''Entity moves to a new position'''
        if levelmanager.move_entity(self, pos):
            self.energy -= self.speed

    def movement(self, levelmanager, animator, key):
        '''
        Handle the movement action

        If charging and movement becomes invalid, end charge
        '''
        # check energy cost
        if self.energy < self.speed:
            logger.Logger.log(f'[{self.name}|{self.id}]: movement not enough energy')
            return
        # find next position
        moves = utility.ONE_LAYER_CIRCLE
        row = self.row + moves[key-1][0]
        col = self.col + moves[key-1][1]
        # check validity
        if not levelmanager.within_level((row,col), self.z):
            return
        # check if there is an entity to attack
        entitylayer = levelmanager.Levels[self.z].EntityLayer
        maxlayer = max([x.layer for x in entitylayer[row][col]])
        # anything on the monster layer should be able to be attacked
        if maxlayer == Layer.MONST_LAYER:
            self.energy -= self.speed
            for entity in entitylayer[row][col]:
                if maxlayer == Layer.MONST_LAYER:
                    self.attack(levelmanager, animator, entity, 1)
        # otherwise just move normally
        else:
            self.move(levelmanager, (row,col))

    def attack(self, levelmanager, animator, entity, damage):
        '''Attack the entity passed in'''
        if hasattr(entity, 'Health'):
            if entity.Health.change_health(-damage):
                entity.death(levelmanager, animator)
    
    def death(self, levelmanager, *_):
        '''Entities can add to this method to trigger on death actions'''
        levelmanager.remove_entity(self)

    def do_action(self, levelmanager, animator, event):
        '''Pass an event for the entity to preform a certain action'''
        logger.Logger.log(f'Do action [{self.name}|{self.id}]: {event} energy:{self.energy}')

        # Movement Action
        if event.isdigit():
            return self.movement(levelmanager, animator, int(event))
        # Z Action
        elif event == '<' or event == '>':
            #self.moveZ(event, entityLayer)
            pass
        # Rest
        elif event == '.':
            self.energy = 0




