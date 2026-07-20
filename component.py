import algo
import config
import entity
import level
import enum
import utility
import logging

Logger = logging.getLogger(__name__)

class Leveling:
    '''Leveling component, if an entity can level up'''
    def __init__(self):
        self.curr_level = 1
        '''Current level'''
        self.xp = 0
        '''Current amount of experience points'''
        self.nextlv = 1
        '''Amount of experience points for the next level'''
        self.scale_factor = 2
        '''How much the next level will increase by'''

    def level_up(self, parent_entity, messager):
        '''Activates when the entity goes to the next level'''
        self.curr_level += 1
        messager.add_level_up_message(parent_entity)
        # health restore
        if hasattr(parent_entity, 'Health'):
            parent_entity.Health.restore_max_health()

    def gain_xp(self, xp, parent_entity, messager):
        '''Send experience points to the component'''
        self.xp += xp
        while self.xp >= self.nextlv:
            self.xp -= self.nextlv
            self.nextlv *= self.scale_factor
            self.level_up(parent_entity, messager)

class Interact:
    def __init__(self):
        pass

    def talk(self, statemachine, menumanager):
        statemachine.new_state('interact')
        menumanager.load_interact('Hello, how are you doing?')
        statemachine.callback = self.on_choice

    def on_choice(self, statemachine, menumanager, event):
        Logger.info(f'GOT MY ANSWER: {event}')
        menumanager.showinteract = False
        statemachine.new_state('doneinteract')

class Edible:
    '''Edible component, if an item can be eaten'''
    def __init__(self, parent_entity, nutrition):
        self.parent_entity = parent_entity
        self.nutrition = nutrition
    
    def get_eaten(self, levelmanager, messager, entity_eater):
        '''Called when another entity eats this entity'''
        if hasattr(entity_eater, 'Health'):
            entity_eater.Health.change_health(self.nutrition)
            messager.add_eat_message(entity_eater, self.parent_entity)
            levelmanager.remove_entity(self.parent_entity)

class ApplyInfo(enum.Enum):
    '''
    Used to request more information for applying a certain item
    Necessary to get user input for the player
    '''
    NONE = 0
    DIRECTION = 1

class ItemType(enum.Enum):
    '''
    Inventory needs to know types of items to slot them correctly
    No equip sends straight to the bag
    '''
    QUIVER = 0
    HEAD = 1
    BODY = 2
    FEET = 3
    HAND = 4
    ABILITY = 5
    NOEQUIP = 6

class Inventory:
    '''
    Inventory component, for entities that can hold items
    '''
    def __init__(self, autopickuplist=[]):
        self.quiver = None
        '''Item in quiver'''
        self.mainHand = None
        '''Item in main hand'''
        self.offHand = None
        '''Item in off hand'''
        self.head = None
        '''Item on head'''
        self.body = None
        '''Item on body'''
        self.feet = None
        '''Item on feet'''
        self.ability = None
        '''Not items, but will be used as an attack if weaponless'''
        self.contents = []
        '''Contents of bag'''
        self.maxcontents = 10
        '''Max amount of items in bag'''
        self.cost = 1
        '''Cost of using the inventory'''
        self.autopickuplist = autopickuplist
        '''Items that should be picked up automatically'''

    def get_all_items(self):
        return [self.quiver, self.mainHand, self.offHand, self.head, self.body,
                self.feet, self.ability] + self.contents

    def autopickup(self, levelmanager, entitylist):
        '''
        Check entity list for any items to pick up
        '''
        idx = 0
        while idx < len(entitylist):
            ent = entitylist[idx]
            # check if any names match
            for name in self.autopickuplist:
                if name in ent.name:
                    self.collect(ent)
                    # this modifies the entity list size
                    levelmanager.remove_entity(entitylist[idx])
                    idx -= 1
            idx += 1

    def show(self):
        '''Print the inventory to logger'''
        Logger.info('Inventory')
        Logger.info(f' Quiver: {self.quiver}')
        Logger.info(f' Main Hand: {self.mainHand}')
        Logger.info(f' Off Hand: {self.offHand}')
        Logger.info(f' Head: {self.head}')
        Logger.info(f' Body: {self.body}')
        Logger.info(f' Feet: {self.feet}')
        Logger.info(f' Bag:')
        for ent in self.contents:
            Logger.info(f'  {ent.name}')
        Logger.info(f'Inventory end')
    
    def get_entity_from_key(self, char):
        '''
        For a certain key, return the item in the inventory
        
        Returns None if the key does not correspond to an inventory item
        '''
        entity = None
        try:
            if char == 'Q':
                entity = self.quiver
            elif char == 'M':
                entity = self.mainHand
            elif char == 'O':
                entity = self.offHand
            elif char == 'H':
                entity = self.head
            elif char == 'B':
                entity = self.body
            elif char == 'F':
                entity = self.feet
            elif char == 'A':
                entity = self.ability
            else:
                key = ord(char) - 97
                Logger.info(f'Inventory key: {key} {char}')
                if key < len(self.contents):
                    entity = self.contents[key]
                else:
                    raise
        except Exception:
            return None, False
        return entity, True

    def equip(self, entity):
        '''
        Pass in an entity to place it in the correct slot
        '''

        if not hasattr(entity, 'ItemType'):
            return
        
        if entity.ItemType == ItemType.NOEQUIP:
            return
        
        # delete an entity if it came from the bag, it will be placed
        for ix,ent in enumerate(self.contents):
            if ent.id == entity.id:
                del self.contents[ix]
                break
        # QUIVER
        if entity.ItemType == ItemType.QUIVER and (not self.quiver or self.quiver.id != entity.id):
            if self.quiver:
                self.add_to_bag(self.quiver)
            self.quiver = entity
        # WEARABLE
        elif entity.ItemType == ItemType.HEAD and (not self.head or self.head.id != entity.id):
            if self.head:
                self.add_to_bag(self.head)
            self.head = entity
        elif entity.ItemType == ItemType.BODY and (not self.body or self.body.id != entity.id):
            if self.body:
                self.add_to_bag(self.body)
            self.body = entity
        elif entity.ItemType == ItemType.FEET and (not self.feet or self.feet.id != entity.id):
            if self.feet:
                self.add_to_bag(self.feet)
            self.feet = entity
        # MAIN / OFF HAND
        elif entity.ItemType == ItemType.HAND:
            # equipping the main hand does nothing
            # equipping the off hand, send it to the main hand
            # send the main hand to the bag
            if self.offHand and self.offHand.id == entity.id:
                if self.mainHand:
                    self.add_to_bag(self.mainHand)
                self.mainHand = entity
                self.offHand = None
            # equipping from the bag, send it to the main hand
            # send the main hand to the off hand
            elif not self.mainHand or self.mainHand.id != entity.id:
                if self.offHand:
                    self.add_to_bag(self.offHand)
                if self.mainHand:
                    self.offHand = self.mainHand
                self.mainHand = entity
        # ABILITY
        elif entity.ItemType == ItemType.ABILITY and (not self.ability or self.ability != entity.id):
            self.ability = entity
    
    def unequip(self, entity):
        '''
        Pass in an entity and set the corresponding slot to empty and place
        the entity into the bag
        '''
        if self.quiver and self.quiver.id == entity.id:
            self.quiver = None
        elif self.head and self.head.id == entity.id:
            self.head = None
        elif self.body and self.body.id == entity.id:
            self.body = None
        elif self.feet and self.feet.id == entity.id:
            self.feet = None
        elif self.mainHand and self.mainHand.id == entity.id:
            self.mainHand = None
        elif self.offHand and self.offHand.id == entity.id:
            self.offHand = None
        self.add_to_bag(entity) 

    def collect(self, entity):
        '''Entrance for items being added into the inventory'''
        Logger.info(f'Collecting: {entity}')

        # try to add it to the quiver
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.QUIVER:
            if self.add_to_quiver(entity):
                return

        # default to bag
        self.add_to_bag(entity)

    def add_to_bag(self, entity):
        '''Handles adding objects directly to the bag'''

        # check for grouping first before adding to bag
        if hasattr(entity, 'Group'):
            for ent in self.contents:
                if hasattr(ent, 'Group'):
                    if ent.Group.group_up(entity):
                        Logger.info(f'Inventory grouped: {ent} {entity}')
                        return

        # default is add to bag
        self.contents.append(entity)

    def get_damage(self):
        '''Based on the slot information calculate the damage'''
        damage = 0
        if self.mainHand and hasattr(self.mainHand, 'Attack'):
            damage += self.mainHand.Attack.damage
        if self.offHand and hasattr(self.offHand, 'Attack'):
            damage += self.offHand.Attack.damage
        if self.ability and hasattr(self.ability, 'Attack'):
            damage += self.ability.Attack.damage
        return damage
    
    def drop(self):
        '''Place an entity to the ground'''
        pass

    def action(self, parent, levelmanager, messager, event, animator, row, col, z):
        '''Handle an inventory action'''
        action = event[0]
        key = event[1]
        cmd = event[2:]
        entity,valid = self.get_entity_from_key(key)
        if entity is None or not valid:
            messager.add_message('Invalid inventory key!')
            return
        # Equip
        if action == 'e':
            Logger.info(f'Equipping: {entity}')
            self.equip(entity)
        # Unequip
        elif action == 'u':
            Logger.info(f'Unequipping: {entity}')
            self.unequip(entity)
        # Apply
        elif action == 'a':
            Logger.info(f'Applying: {entity}')
            self.apply(entity, cmd, parent, levelmanager, messager, animator, row, col, z)

    def apply(self, entity, cmd, parent, levelmanager, messager, animator, row, col, z):
        '''Trigger the apply on an entity'''
        entity.on_apply(cmd, parent, levelmanager, messager, animator, row, col, z)

    def get_apply_info(self, char):
        entity = None
        if char == 'Q':
            entity = self.quiver
        elif char == 'M':
            entity = self.mainHand
        elif char == 'O':
            entity = self.offHand
        elif char == 'H':
            entity = self.head
        elif char == 'B':
            entity = self.body
        elif char == 'F':
            entity = self.feet
        elif char == 'A':
            entity = self.ability
        else:
            key = ord(char) - 97
            Logger.info(f'Inventory key: {key} {char}')
            if key < len(self.contents):
                entity = self.contents[key]
            else:
                raise
        if hasattr(entity, 'ApplyInfo'):
            return entity.ApplyInfo
        return None

    def add_to_quiver(self, entity):
        '''Tries to add an item to the quiver, returns False if it cannot'''
        # try to slot it
        if self.quiver is None:
            self.quiver = entity
            return True
        # try to group on it
        elif hasattr(self.quiver, 'Group'):
            if self.quiver.Group.group_up(entity):
                return True
        return False
    
    def has_ammo(self):
        '''Simple check if there is ammo for the quiver to shoot'''
        if self.quiver is None:
            return False
        return True
    
    def fire_quiver(self):
        '''
        Returns the entity being fired from the quiver
        Returns None if there is no entity
        '''
        if self.quiver is None:
            return None
        elif hasattr(self.quiver, 'Group'):
            entity = self.quiver.Group.pop_one()
            if entity.id == self.quiver.id:
                self.quiver = None
            return entity
        else:
            entity = self.quiver
            self.quiver = None
            return entity 

class Group:
    '''Group component, if an entity can group up with others of the same type'''
    def __init__(self, parent, unstack_name, unstack_glyph, stack_name, stack_glyph):
        self.parent = parent
        '''Parent entity of the component'''
        self.amount = 1
        '''Current amount of the entities in the group'''
        self.unstack_name = unstack_name
        '''Name of the entity when not stacked'''
        self.unstack_glyph = unstack_glyph
        '''Glyph of the entity when not stacked'''
        self.stack_name = stack_name
        '''Name of the entity when stacked'''
        self.stack_glyph = stack_glyph
        '''Glyph of the entity when stacked'''
        self.stacked = False
        '''Tracks if the entity is stacked or not'''

    def pop_one(self):
        '''
        Returns one of the entities in the stack
        Will unstack itself if there are less than 2 entities
        '''
        if self.stacked:
            self.amount -= 1
            if self.amount < 2:
                self.unstack()
            return type(self.parent)()
        else:
            return self.parent

    def stack(self):
        '''Turn the parent entity into it's stacked form'''
        self.stacked = True
        self.parent.name = self.stack_name
        self.parent.glyph = self.stack_glyph

    def unstack(self):
        '''Turn the parent entity into it's regular form'''
        self.stacked = False
        self.parent.name = self.unstack_name 
        self.parent.glyph = self.unstack_glyph 

    def group_up(self, new_entity):
        '''
        Add the entity passed in to the stack if able, otherwise return False
        '''
        if type(new_entity) == type(self.parent) and hasattr(new_entity, 'Group'):
            self.amount += new_entity.Group.amount
            if not self.stacked:
                self.stack()
            return True
        return False

    def check_square(self, entity, levelmanager):
        '''
        Pass an entity and remove it if it gets added to this stack
        '''
        level = levelmanager.Levels[entity.z]
        entitylist = level.EntityLayer[entity.row][entity.col]
        if not entity in entitylist:
            return
        if self.group_up(entity):
            levelmanager.remove_entity(entity)

class Health:
    '''
    Health component, if an entity needs a health bar
    '''
    def __init__(self, health):
        self.maxhealth = health
        '''Maximum for the health bar'''
        self.currenthealth = health
        '''Counter for current health'''
        self.alive = True
        '''True if health bar is above 0'''

    def __repr__(self):
        return f'({self.currenthealth}/{self.maxhealth})'

    def restore_max_health(self):
        '''Gives the entity full health'''
        self.currenthealth = self.maxhealth

    def change_health(self, amount):
        '''
        Changes the health bar by an amount

        Returns true if health change causes death
        '''
        if self.currenthealth + amount >= self.maxhealth:
            self.currenthealth = self.maxhealth
        else:
            self.currenthealth += amount
        if self.alive and self.currenthealth <= 0:
            self.alive = False
            return True
        return False

class BrainState(enum.Enum):
    '''Used to keep track of what state the brain is in'''
    IDLE = 0
    '''Do nothing'''
    MOVE = 1
    '''Move around randomly'''

class Brain:
    '''
    Brain component, if an entity needs to make decisions
    '''
    def __init__(self, sightrange, blockinglayer, attacks=[]):
        self.sightrange = sightrange
        '''How far FOV will check'''
        self.blockinglayer = blockinglayer
        '''Highest level (exclusive) FOV will see through'''
        self.attacks = attacks
        '''List of AttackType enums'''
        self.state = BrainState.IDLE

    def get_action(self, currlevel, mypos, energy, rng, speed, inventory=None):
        '''Returns an action'''

        # not enough energy
        if energy < speed:
            return '5'

        pts = self.getFOV(currlevel, mypos)
        playerpos = self.find_player(currlevel, pts)

        # if the player is near, try to attack
        if playerpos:
            # go through possible attacks
            for attack in self.attacks:
                if (attack == entity.AttackType.THROW and
                    self.throw_attack_possible(mypos, playerpos, inventory)):
                    return self.throw_attack(mypos, playerpos)
                elif attack == entity.AttackType.MELEE:
                    return self.find_path(currlevel.EntityLayer, mypos, playerpos)

        # move around
        if self.state == BrainState.MOVE:
            actions = ['1', '2', '3', '4', '6', '7', '8', '9']
            rows = len(currlevel.EntityLayer)
            cols = len(currlevel.EntityLayer[0])
            # get which moves are legal
            possible_actions = []
            for key in actions:
                direction = utility.key_to_direction(key)
                r,c = mypos[0] + direction[0], mypos[1] + direction[1]
                if (r < len(currlevel.EntityLayer) and r >= 0 and
                    c < len(currlevel.EntityLayer[r]) and c >= 0):
                    if utility.get_max_layer(currlevel.EntityLayer[r][c]) < entity.Layer.MONST_LAYER:
                        possible_actions.append(key)
            # pick a random move
            move = possible_actions[rng.randint(0, len(possible_actions)-1)]
            if rng.randint(*config.MONS_IDLE) == 0:
                self.state = BrainState.IDLE
            return move

        # rest if not able to do anything
        if rng.randint(*config.MONS_IDLE) == 0:
            self.state = BrainState.MOVE
        return '.'

    def throw_attack_possible(self, mypos, playerpos, inventory):
        '''Check if the player is reachable by a throw'''
        if not inventory.has_ammo():
            return False
        drow = abs(mypos[0] - playerpos[0])
        dcol = abs(mypos[1] - playerpos[1])
        if drow == 0 or dcol == 0 or drow == dcol:
            return True
        return False

    def throw_attack(self, mypos, playerpos):
        '''Get the throw command'''
        d = self.move_towards_pt(mypos, playerpos)
        return 't' + str(d)

    def find_player(self, currlevel, pts):
        '''In a set of FOV points, check if the player exists'''
        for pt in pts:
            for ent in currlevel.EntityLayer[pt[0]][pt[1]]:
                if ent.name == 'Player':
                    return pt
        return None

    def find_path(self, entitylayer, mypos, playerpos):
        '''Finds a path using A* to the player position'''
        # create the 1,0 grid
        grid = [[1 if max([int(x.layer) for x in elist]) > entity.Layer.OBJECT_LAYER else 0
                    for elist in row]
                    for row in entitylayer]
        # set the source/dest positions to open
        grid[mypos[0]][mypos[1]] = 0
        grid[playerpos[0]][playerpos[1]] = 0
        # call A* to get a set of pts
        returncode, pts = algo.astar(grid, mypos, playerpos)
        if returncode != 1:
            Logger.error(f'Error: brain failed to find path -> {returncode}')
            return '.'
        return self.move_towards_pt(mypos, pts[1])
    
    def move_towards_pt(self, mypos, otherpos):
        '''Moves towards a point on the map'''
        if otherpos[0] > mypos[0]:
            if otherpos[1] > mypos[1]:
                return '3'
            elif otherpos[1] < mypos[1]:
                return '1'
            else:
                return '2'
        elif otherpos[0] < mypos[0]:
            if otherpos[1] > mypos[1]:
                return '9'
            elif otherpos[1] < mypos[1]:
                return '7'
            else:
                return '8'
        else:
            if otherpos[1] > mypos[1]:
                return '6'
            elif otherpos[1] < mypos[1]:
                return '4'
        return '.'
    
    def getFOV(self, level, mypos):
        '''Use FOV algorithm to get which points are visible'''
        if not level:
            return []
        grid = [[max([int(x.layer) for x in level.EntityLayer[r][c]]) if level.EntityLayer[r][c] else 0
                 for c in range(len(level.EntityLayer[r]))]
                    for r in range(len(level.EntityLayer))]
        return algo.RecursiveShadow(grid,
                               mypos,
                               self.sightrange,
                               int(self.blockinglayer))

class Attack:
    '''
    Attack component, if an entity can be used as an attack
    '''
    def __init__(self, name, damage):
        self.name = name
        '''name of the attack'''
        self.damage = damage
        '''amount of damage the attack does'''

class Charge:
    '''
    Charge component, if an entity can run and charge
    '''
    def __init__(self, speed):
        self.charging = False
        '''If entity is currently charging'''
        self.distance = 0
        '''Distance covered by charge, needed for damage'''
        self.entityspeed = speed
        '''Keeps track of entity speed'''
        self.cost = round(speed/2)
        '''Energy cost for charging move'''

    def start(self, direction):
        '''Start the charge, sets direction'''
        self.charging = True
        self.direction = direction
    
    def end(self):
        '''Ends the charge, returns how much damage was dealt'''
        self.charging = False
        dmg = self.distance
        self.distance = 0
        return dmg


