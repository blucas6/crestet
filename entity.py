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
    VERY_SLOW = 9
    SLOW = 8
    AVERAGE = 7
    FAST = 6
    VERY_FAST = 5

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

    def take_turn(self):
        '''Starting point of an entity's turn'''
        pass

    def move(self, levelmanager, pos):
        '''Entity moves to a new position'''
        # check energy cost
        if self.energy < self.speed:
            return
        if levelmanager.move_entity(self, pos):
            self.energy -= self.speed

    def movement(self, levelmanager, key):
        '''
        Handle the movement action

        If charging and movement becomes invalid, end charge
        '''
        # find next position
        moves = utility.ONE_LAYER_CIRCLE
        row = self.row + moves[key-1][0]
        col = self.col + moves[key-1][1]
        # check validity
        if not levelmanager.within_level((row,col), self.z):
            return
        self.move(levelmanager, (row,col))
        '''
        # check if movement triggers an attack
        attack, entities = self.attack(entityLayer, row, col)
        if not attack:
            # no attack, move normally
            return self.move(row, col, entityLayer)
        # attack took place, return the (possibly) killed entity
        return entities
    '''

    def do_action(self, levelmanager, event):
        '''Pass an event for the entity to preform a certain action'''
        logger.Logger.log(f'Do action [{self.name}|{self.id}]: {event}')

        # Movement Action
        if event.isdigit():
            return self.movement(levelmanager, int(event))
        # Z Action
        elif event == '<' or event == '>':
            #self.moveZ(event, entityLayer)
            pass




