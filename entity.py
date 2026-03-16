import itertools
import animation
import config
import utility
import algo
import logger
import enum

class MoveAction(enum.Enum):
    INVALID = 0
    NOENERGY = 1
    ATTACKED = 2
    MOVED = 3
    PUSHED = 4

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
        3: not stackable, can be pushed
        3: not stackable, FOV cannot see through them
    '''
    FLOOR_LAYER = 0
    OBJECT_LAYER = 1
    MONST_LAYER = 2
    BARREL_LAYER = 3
    WALL_LAYER = 4

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
            return MoveAction.MOVED
        else:
            return MoveAction.INVALID

    def movement(self, levelmanager, animator, messager, key):
        '''
        Handle the movement action
        Returns the result of the movement request
            0: invalid
            1: no energy
            2: moved
            3: attacked
            4: pushed
        '''
        # find next position
        row,col = utility.get_new_pos((self.row,self.col), key)
        # check energy cost
        if self.energy < self.speed:
            logger.Logger.log(f'[{self.name}|{self.id}]: movement not enough energy')
            return MoveAction.NOENERGY
        # check validity
        if not levelmanager.within_level((row,col), self.z):
            return MoveAction.INVALID
        # if the entity is able to attack
        # check if there is an entity to attack
        entitylayer = levelmanager.Levels[self.z].EntityLayer
        eidx,entity = utility.get_max_layer(entitylayer[row][col])
        # anything on the monster layer should be able to be attacked
        if entity.layer == Layer.MONST_LAYER:
            self.energy -= self.speed
            # calculate damage
            damage = self.get_damage()
            self.attack(levelmanager, animator, messager, entity, damage)
            return MoveAction.ATTACKED
        # anything on the barrel layer should be pushed
        elif entity.layer == Layer.BARREL_LAYER:
            # check if entity can be pushed
            nrow,ncol = utility.get_new_pos((row,col), key)
            if levelmanager.move_entity(entity, (nrow,ncol)):
                # if pushed, then move
                self.move(levelmanager, (row,col))
                return MoveAction.PUSHED
            else:
                return MoveAction.INVALID
        # otherwise just move normally
        return self.move(levelmanager, (row,col))

    def attack(self, levelmanager, animator, messager, entity, damage):
        '''Attack the entity passed in'''
        if hasattr(entity, 'Health'):
            logger.Logger.log(f'{self} dealing damage to {entity}: {damage} ')
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
                levelmanager.place_entity(self.z, entity, (objr,objc))
            elif target:
                # set to the target position
                levelmanager.place_entity(self.z,
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

    def moveZ(self, levelmanager, messager, incrementz):
        '''Move an to another z level'''
        if self.energy < self.speed:
            return
        # make sure there is a stairwell
        for ent in levelmanager.Levels[self.z].EntityLayer[self.row][self.col]:
            if ent.name == 'Upstair' and incrementz > 0:
                if levelmanager.move_entity_z(self, self.z + incrementz, [self.row,self.col]):
                    messager.add_message('You walk up the stairs')
                    self.energy -= self.speed
                    return
            elif ent.name == 'Downstair' and incrementz < 0:
                if levelmanager.move_entity_z(self, self.z + incrementz, [self.row,self.col]):
                    messager.add_message('You walk down the stairs')
                    self.energy -= self.speed
                    return
        # stairwell not on this space
        if incrementz > 0:
            messager.add_message("Can't go up here")
        else:
            messager.add_message("Can't go down here")

    def handle_inventory(self, levelmanager, messager, event):
        '''Talks to the inventory component'''
        self.Inventory.show()
        if self.energy >= self.Inventory.cost:
            self.energy -= self.Inventory.cost
            self.Inventory.action(levelmanager, messager, event)

    def handle_charging(self, levelmanager, animator, messager, event):
        '''Talks to the charge component'''
        # already charging
        if self.Charge.charging:
            result = self.movement(levelmanager, animator, messager, self.Charge.direction)
            if result == MoveAction.INVALID:
                self.Charge.end()
            elif result == MoveAction.MOVED:
                self.Charge.distance += 1
        # start the charge
        elif event[0] == '5':
            self.Charge.start(int(event[1]))
            result = self.movement(levelmanager, animator, messager, self.Charge.direction)
            if result == MoveAction.INVALID:
                self.Charge.end()
            elif result == MoveAction.MOVED:
                self.Charge.distance += 1

    def get_damage(self):
        '''Base method, called when attacking from movement'''
        if hasattr(self, 'Inventory'):
            return self.Inventory.get_damage()
        return 0

    def fight(self, levelmanager, animator, messager, event):
        '''Purposely attack in a direction'''
        if not event[1].isdigit():
            return
        # find next position
        row,col = utility.get_new_pos((self.row,self.col), int(event[1]))
        entitylayer = levelmanager.Levels[self.z].EntityLayer
        eidx,entity = utility.get_max_layer(entitylayer[row][col])
        # monsters or barrels can be damaged
        if entity.layer == Layer.MONST_LAYER or entity.layer == Layer.BARREL_LAYER:
            self.energy -= self.speed
            # calculate damage
            damage = self.get_damage()
            self.attack(levelmanager, animator, messager, entity, damage)
            return MoveAction.ATTACKED
        return MoveAction.INVALID

    def do_action(self, levelmanager, animator, messager, event):
        '''Pass an event for the entity to preform a certain action'''
        logger.Logger.log(f'Do action [{self.name}|{self.id}]: {event} energy:{self.energy}')

        # Run
        # currently charging
        if hasattr(self, 'Charge') and self.Charge.charging:
            self.handle_charging(levelmanager, animator, messager, event)
        # starting the charge
        elif hasattr(self, 'Charge') and len(event) > 1 and event[0] == '5':
            self.handle_charging(levelmanager, animator, messager, event)
        # Walk
        elif event.isdigit():
            self.movement(levelmanager, animator, messager, int(event))
        # Z
        elif event == '<': 
            self.moveZ(levelmanager, messager, 1)
        elif event == '>':
            self.moveZ(levelmanager, messager, -1)
        # Inventory
        elif (hasattr(self, 'Inventory') and
            len(event) > 1 and
            (event[0] == 'e' or event[0] == 'u')):
            self.handle_inventory(levelmanager, messager, event)
        # Throw
        elif event[0] == 't' and len(event) > 1:
            self.fire(levelmanager, animator, messager, event)
        # Fight
        elif event[0] == 'F' and len(event) > 1:
            self.fight(levelmanager, animator, messager, event)
        # Rest
        elif event == '.':
            self.energy = 0

