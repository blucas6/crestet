import itertools
import animation
import config
import utility
import algo
import enum
import color
import logging

Logger = logging.getLogger(__name__)

class StatusEffect(enum.Enum):
    '''Entity status effects'''
    NONE = 0
    FROZEN = 1

    def status_lookup(self):
        '''Returns the turn cooldown for status effects'''
        if self == StatusEffect.NONE:
            return 0
        elif self == StatusEffect.FROZEN:
            return 8

class AttackType(enum.Enum):
    '''Possible attack options'''
    THROW = 0
    MELEE = 1

class MoveAction(enum.Enum):
    '''Results of a move request'''
    INVALID = 0
    NOENERGY = 1
    ATTACKED = 2
    MOVED = 3
    PUSHED = 4
    INTERACT = 5

class Speed(enum.IntEnum):
    '''Corresponding energy costs for movements'''
    CRAWLING = 64
    VERY_SLOW = 51
    SLOW = 37
    AVERAGE = 26
    MEDIUM = 15
    FAST = 9
    VERY_FAST = 4
    HYPER = 1

class Layer(enum.IntEnum):
    '''
    Layer Types:
        0-1: stackable, anything with these layers will be placed on top of
            each other
        2: not stackable, entities that move around, FOV can see through them
        3: not stackable, can be pushed
        4: not stackable, FOV cannot see through them
    '''
    FLOOR_LAYER = 0
    STAIR_LAYER = 1
    OBJECT_LAYER = 2
    BARREL_LAYER = 3
    MONST_LAYER = 4
    WALL_LAYER = 5

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

    def __init__(self, typeid, name, glyph, color, layer, size):
        self.id = next(Entity._id_gen)
        '''Unique ID'''
        self.typeid = typeid
        '''ID corresponding to the specific type of entity'''
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
        self.status = {}
        '''Map of current status effects and their respective cooldowns counters'''
        Logger.debug(f'Creating new entity: {self} {self.pos()}')

    def __repr__(self):
        return f'[{self.name}|{self.id}|({self.row},{self.col},{self.z},{self.idx})]'
    
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

    def on_placed(self, levelmanager, messager):
        '''
        Hook gets called when an entity is placed on the level

        Base class checks for Inventory auto pickup
        '''

        # check for auto pickup
        if hasattr(self, 'Inventory'):
            entitylist = levelmanager.Levels[self.z].EntityLayer[self.row][self.col]
            self.Inventory.autopickup(levelmanager, entitylist)

    def on_top(self, entity, levelmanager):
        '''
        Hook gets called when another entity is placed in the same square
        
        Base class checks for stacking
        '''
        if hasattr(self, 'Group'):
            self.Group.check_square(entity, levelmanager)

    def on_zchange(self, *_):
        '''Hook gets called when the entity changes z levels'''
        pass

    def on_apply(self, cmd, parent, levelmanager, messager, *_):
        '''Default attempt to apply an entity'''
        messager.add_message('Nothing happens.')

    def apply_status(self, messager, status_effect):
        '''Add a status effect to the entity'''
        messager.add_status_message(self, status_effect)
        self.status[status_effect] = status_effect.status_lookup()
        self.color = color.Color().toggle_bg(self.color)

    def unapply_status(self, status):
        '''Remove a status effect from an entity'''
        self.color = color.Color().toggle_bg(self.color)

    def update_status(self):
        '''Triggers every turn, updates each status effect'''
        if self.status.keys():
            for status in self.status.keys():
                self.status[status] -= 1
                if self.status[status] <= 0:
                    self.unapply_status(self.status[status])
            self.status = {status: timer for status,timer in self.status.items() if timer > 0}

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

    def movement(self, levelmanager, animator, messager, menumanager, statemachine, key, rng):
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
            return MoveAction.NOENERGY

        # check validity
        if not levelmanager.within_level((row,col), self.z):
            return MoveAction.INVALID

        # if the entity is able to attack
        # check if there is an entity to attack
        entitylayer = levelmanager.Levels[self.z].EntityLayer
        _,entity = utility.get_max_entity(entitylayer[row][col])

        # anything on the monster layer should be able to be attacked
        if entity.layer == Layer.MONST_LAYER:

            # check for interactions
            if self.name == 'Player' and hasattr(entity, 'Interact'):
                self.energy -= 1
                entity.Interact.talk(statemachine, menumanager)
                return MoveAction.INTERACT

            # must attack
            elif hasattr(self, 'Combat'):
                self.energy -= self.speed
                self.Combat.attack_melee(self, levelmanager, animator, messager, entity, rng)
                return MoveAction.ATTACKED
            else:
                return MoveAction.INVALID

        # anything on the barrel layer should be pushed
        elif entity.layer == Layer.BARREL_LAYER:
            # if charging, break the barrel
            if hasattr(self, 'Charge') and self.Charge.charging:
                if not self.fight(levelmanager, animator, messager, key, rng):
                    Logger.error('Invalid charge?')
                self.Charge.end()
                return MoveAction.ATTACKED
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

    def fire(self, levelmanager, animator, messager, event, rng):
        '''Checks the inventory for the quiver item and calls throw()'''
        # need inventory component
        if not hasattr(self, 'Inventory') or not hasattr(self, 'Combat'):
            return
        if event[1].isdigit():
            # get the direction
            if self.energy < self.speed:
                Logger.info(f'[{self.name}|{self.id}]: Firing not enough energy')
                return
            # get the ammo entity
            fired_entity = self.Inventory.fire_quiver()
            if fired_entity is None:
                return
            # throw
            return self.Combat.attack_range(
                            self,
                            levelmanager,
                            animator,
                            messager,
                            fired_entity,
                            event[1],
                            rng,
                            self.row, self.col, self.z)
    
    def death(self, levelmanager, *_):
        '''Entities can add to this method to trigger on death actions'''
        levelmanager.remove_entity(self)

    def moveZ(self, levelmanager, animator, messager, incrementz, rng):
        '''Move an to another z level'''
        if self.energy < self.speed:
            return
        # make sure there is a stairwell
        newz = self.z + incrementz
        for ent in levelmanager.Levels[self.z].EntityLayer[self.row][self.col]:
            if ent.name == 'Upstair' or ent.name == 'Downstair':
                # make sure there is a level to go to
                if newz >= len(levelmanager.Levels):
                    messager.add_message("There is nothing above you.")
                    return
                elif newz < 0:
                    messager.add_message("There is nothing below you.")
                    return
                # check if there are monsters on the next level
                entitylayer = levelmanager.Levels[newz].EntityLayer
                _,an_entity = utility.get_max_entity(entitylayer[self.row][self.col])
                if ((an_entity.layer == Layer.MONST_LAYER or
                    an_entity.layer == Layer.BARREL_LAYER) and
                    hasattr(self, 'Combat')):
                    # auto fight the entity
                    self.energy -= self.speed
                    self.Combat.attack_melee(self, levelmanager, animator, messager, an_entity, rng)
                    return
                else:
                    if levelmanager.move_entity_z(self, newz, [self.row,self.col]):
                        if ent.name == 'Upstair':
                            messager.add_message('You walk up the stairs.')
                        else:
                            messager.add_message('You walk down the stairs.')
                        self.energy -= self.speed
                        return
        # stairwell not on this space
        if incrementz > 0:
            messager.add_message("Can't go up here.")
        else:
            messager.add_message("Can't go down here.")

    def handle_inventory(self, levelmanager, messager, animator, event):
        '''Talks to the inventory component'''
        self.Inventory.show()
        if self.energy >= self.Inventory.cost:
            self.energy -= self.Inventory.cost
            self.Inventory.action(self, levelmanager, messager, event, animator, self.row, self.col, self.z)
            self.Inventory.show()

    def handle_charging(self, levelmanager, animator, messager, menumanager, statemachine, event, rng):
        '''Talks to the charge component'''
        # start the charge
        if event[0] == '5':
            self.Charge.start(int(event[1]))
        result = self.movement(levelmanager, animator, messager, menumanager, statemachine, self.Charge.direction, rng)
        if result == MoveAction.INVALID:
            self.Charge.end()
        elif result == MoveAction.INTERACT:
            self.Charge.end()
        elif result == MoveAction.MOVED:
            self.Charge.distance += 1

    def fight(self, levelmanager, animator, messager, key, rng):
        '''Purposely attack in a direction'''
        # find next position
        row,col = utility.get_new_pos((self.row,self.col), key)
        entitylayer = levelmanager.Levels[self.z].EntityLayer
        eidx,entity = utility.get_max_entity(entitylayer[row][col])
        # monsters or barrels can be damaged
        if ((entity.layer == Layer.MONST_LAYER or
             entity.layer == Layer.BARREL_LAYER) and
            hasattr(self, 'Combat')):
            self.energy -= self.speed
            self.Combat.attack_melee(self, levelmanager, animator, messager, entity, rng)
            return MoveAction.ATTACKED
        return MoveAction.INVALID
    
    def do_action(self, levelmanager, animator, messager, menumanager, statemachine, event, rng):
        '''Pass an event for the entity to preform a certain action'''
        if self.z == levelmanager.currentz:
            Logger.info(f'Do action {self} t:{self.turn}: "{event}" energy:{self.energy}')

        if not isinstance(event, str):
            return

        # check for status effects
        if StatusEffect.FROZEN in self.status:
            Logger.info(f'[{self.name}|{self.id}]: FROZEN')
            self.energy = 0
            return

        # Run
        # currently charging
        if hasattr(self, 'Charge') and self.Charge.charging:
            self.handle_charging(levelmanager,
                                 animator,
                                 messager,
                                 menumanager,
                                 statemachine,
                                 event, rng)
        # starting the charge
        elif hasattr(self, 'Charge') and len(event) > 1 and event[0] == '5':
            self.handle_charging(levelmanager,
                                 animator,
                                 messager,
                                 menumanager,
                                 statemachine,
                                 event, rng)
        # Walk
        elif event.isdigit():
            self.movement(levelmanager,
                          animator,
                          messager,
                          menumanager,
                          statemachine,
                          int(event),
                          rng)
        # Z
        elif event == '<': 
            self.moveZ(levelmanager, animator, messager, 1, rng)
        elif event == '>':
            self.moveZ(levelmanager, animator, messager, -1, rng)
        # Inventory
        elif (hasattr(self, 'Inventory') and
            ((len(event) > 1 and
                (event[0] == 'e' or event[0] == 'u' or event[0] == 'a' or event[0] == 'd')
              ) or
              event[0] == ',')):
            self.handle_inventory(levelmanager, messager, animator, event)
        # Throw
        elif event[0] == 't' and len(event) > 1:
            self.fire(levelmanager, animator, messager, event, rng)
        # Fight
        elif event[0] == 'F' and len(event) > 1 and event[1].isdigit():
            self.fight(levelmanager, animator, messager, int(event[1]), rng)
        # Rest
        elif event == '.':
            self.energy = 0

