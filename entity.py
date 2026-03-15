import itertools
import animation
import config
import utility
import algo
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

    def __repr__(self):
        return f'[{self.name}|{self.id}]'

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
        '''
        Starting point of an entity's turn
        Default behavior is to dump all energy and do nothing
        '''
        self.energy = 0
        pass

    def on_placed(self, *_):
        '''Hook gets called when an entity is placed on the level'''
        pass

    def on_top(self, *_):
        '''Hook gets called when another entity is placed in the same square'''
        pass

    def update_state(self, *_):
        '''Gets called after initialization'''
        pass

    def move(self, levelmanager, pos):
        '''Entity moves to a new position'''
        if levelmanager.move_entity(self, pos):
            self.energy -= self.speed

    def movement(self, levelmanager, animator, messager, key):
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
        if entitylayer[row][col]:
            maxlayer = max([x.layer for x in entitylayer[row][col]])
            # anything on the monster layer should be able to be attacked
            if maxlayer == Layer.MONST_LAYER:
                self.energy -= self.speed
                for entity in entitylayer[row][col]:
                    if entity.layer == Layer.MONST_LAYER:
                        self.attack(levelmanager, animator, messager, entity, 1)
                return
        # otherwise just move normally
        self.move(levelmanager, (row,col))

    def attack(self, levelmanager, animator, messager, entity, damage):
        '''Attack the entity passed in'''
        if hasattr(entity, 'Health'):
            logger.Logger.log(f'Dealing damage to {entity}')
            messager.add_damage_message(self, entity)
            self.deal_damage(levelmanager, animator, messager, entity, damage)

    def deal_damage(self, levelmanager, animator, messager, entity, damage):
        '''Some types of damage are not from an attack'''
        if hasattr(entity, 'Health') and entity.Health.change_health(-damage):
            entity.death(levelmanager, animator, messager)
    
    def death(self, levelmanager, *_):
        '''Entities can add to this method to trigger on death actions'''
        logger.Logger.log(f'Death trigger: {self}')
        levelmanager.remove_entity(self)

    def throw(self, levelmanager, animator, messager, entity, direction: tuple=(), target: tuple=()):
        '''
        Child classes should use their own methods to call this base method 

        If direction is included, the entity will be thrown in that direction
        until it hits a wall layer

        If target is included, the entity will be sent directly to that target's
        position
        '''
        # make sure there is enough energy to throw
        if hasattr(self, 'throwspeed') and self.energy >= self.throwspeed:
            objr = self.row
            objc = self.col
            entitylayer = levelmanager.Levels[self.z].EntityLayer
            if direction: 
                # find the final position for the thrown object
                # start object from entity position
                while True:
                    r,c = objr + direction[0], objc + direction[1]
                    if entitylayer:
                        maxlayer = max([x.layer for x in entitylayer[r][c]])
                        # set final position at the monster
                        if maxlayer == Layer.MONST_LAYER:
                            objr, objc = r, c
                            break
                        # set final position before wall
                        elif maxlayer == Layer.WALL_LAYER:
                            break
                    objr, objc = r, c
                levelmanager.place_entity(levelmanager.Levels[self.z], entity, (objr,objc))
            elif target:
                # set to the target position
                levelmanager.place_entity(levelmanager.Levels[self.z],
                                          entity, (target[0],target[1]))
                objr = entity.row
                objc = entity.col
            else:
                logger.Logger.log(f'Error: invalid throw')
                return

            # construct a grid of [0-1] (makes sure path to end point is valid)
            grid = [[1 if max([int(x.layer) for x in elist]) > Layer.MONST_LAYER else 0
                    for elist in row]
                    for row in entitylayer]
            returncode, pts = algo.astar(grid, (self.row,self.col), (objr,objc))
            if returncode != 1:
                logger.Logger.log(f'Error: failed to throw -> {returncode}')
                return

            # create the animation
            frames = {}
            for idx,pt in enumerate(pts):
                frames[str(idx)] = [['' for _ in row] for row in grid]
                frames[str(idx)][pt[0]][pt[1]] = entity.glyph
            origin = [0,0]
            delay = config.THROW_ANIM_DELAY
            anim = animation.Animation(origin, frames, entity.color, delay=delay)
            animator.queueUp(anim)

            # deal damage
            dmg = entity.size * 2
            for ent in entitylayer[objr][objc]:
                self.attack(levelmanager, animator, messager, ent, dmg)

    def do_action(self, levelmanager, animator, messager, event):
        '''Pass an event for the entity to preform a certain action'''
        logger.Logger.log(f'Do action [{self.name}|{self.id}]: {event} energy:{self.energy}')

        # Running
        if event[0] == '5':
            self.energy = 0
            pass
        # Walking 
        elif event.isdigit():
            return self.movement(levelmanager, animator, messager, int(event))
        # Z
        elif event == '<' or event == '>':
            #self.moveZ(event, entityLayer)
            pass
        # Rest
        elif event == '.':
            self.energy = 0
        # Throwing
        elif event[0] == 't':
            return self.fire(levelmanager, animator, messager, event)




