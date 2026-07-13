import algo
import entity
import level
import logger
import enum

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
        logger.Logger.log(f'GOT MY ANSWER: {event}')
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

class ItemType(enum.Enum):
    '''Inventory needs to know types of items to slot them correctly'''
    QUIVER = 0
    HEAD = 1
    BODY = 2
    FEET = 3
    HAND = 4
    ABILITY = 5

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
        '''Check entity list for any items to pick up'''
        for ent in entitylist:
            if ent.name in self.autopickuplist:
                self.pick_up(levelmanager, ent)

    def show(self):
        '''Print the inventory to logger'''
        logger.Logger.log('Inventory')
        logger.Logger.log(f' Quiver: {self.quiver}')
        logger.Logger.log(f' Main Hand: {self.mainHand}')
        logger.Logger.log(f' Off Hand: {self.offHand}')
        logger.Logger.log(f' Head: {self.head}')
        logger.Logger.log(f' Body: {self.body}')
        logger.Logger.log(f' Feet: {self.feet}')
        logger.Logger.log(f' Bag:')
        for ent in self.contents:
            logger.Logger.log(f'  {ent.name}')
        logger.Logger.log(f'Inventory end')
    
    def get_entity_from_key(self, char):
        '''
        For a certain key, return the item in the inventory
        
        Returns None if the key does not correspond to an inventory item
        '''
        entity = None
        try:
            if char == 'Q':
                entity = self.quiver
                self.quiver = None
            elif char == 'M':
                entity = self.mainHand
                self.mainHand = None
            elif char == 'O':
                entity = self.offHand
                self.offHand = None
            elif char == 'H':
                entity = self.head
                self.head = None
            elif char == 'B':
                entity = self.body
                self.body = None
            elif char == 'F':
                entity = self.feet
                self.feet = None
            elif char == 'A':
                entity = self.ability
                self.ability = None
            else:
                key = ord(char) - 97
                logger.Logger.log(f'Inventory key: {key} {char}')
                if key < len(self.contents):
                    entity = self.contents[key]
                    del self.contents[key]
                else:
                    raise
        except Exception:
            return None, False
        return entity, True

    def equip(self, entity):
        '''Pass in an entity to place it in the correct slot'''
        if not hasattr(entity, 'ItemType'):
            return
        # QUIVER
        if entity.ItemType == ItemType.QUIVER:
            if self.quiver:
                self.add_to_bag(self.quiver)
            self.quiver = entity
        # WEARABLE
        elif entity.ItemType == ItemType.HEAD:
            if self.head:
                self.add_to_bag(self.head)
            self.head = entity
        elif entity.ItemType == ItemType.BODY:
            if self.body:
                self.add_to_bag(self.body)
            self.body = entity
        elif entity.ItemType == ItemType.FEET:
            if self.feet:
                self.add_to_bag(self.feet)
            self.feet = entity
        # MAIN / OFF HAND
        elif entity.ItemType == ItemType.HAND:
            if self.offHand:
                self.add_to_bag(self.offHand)
            if self.mainHand:
                self.offHand = self.mainHand
            self.mainHand = entity
        # ABILITY
        elif entity.ItemType == ItemType.ABILITY:
            self.ability = entity

    def collect(self, entity):
        '''Entrance for items being added into the inventory'''
        logger.Logger.log(f'Collecting: {entity}')

        # try to add it to the quiver
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.QUIVER:
            if self.add_to_quiver(entity):
                return

        # default to bag
        self.add_to_bag(entity)

    def add_to_bag(self, entity):
        '''Handles adding objects to the bag'''

        # check for grouping first before adding to bag
        if hasattr(entity, 'Group'):
            for ent in self.contents:
                if hasattr(ent, 'Group'):
                    if ent.Group.group_up(entity):
                        logger.Logger.log(f'Inventory grouped: {ent} {entity}')
                        return

        # default is add to bag
        self.contents.append(entity)
        entity.idx = len(self.contents)-1

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
    
    def pick_up(self, levelmanager, entity):
        '''Pass in an entity to add it to the bag'''
        ent = levelmanager.remove_entity(entity)
        self.collect(entity)

    def drop(self):
        '''Place an entity to the ground'''
        pass

    def action(self, levelmanager, messager, event):
        '''Handle an inventory action'''
        action = event[0]
        key = event[1]
        # Equip
        if action == 'e':
            entity,valid = self.get_entity_from_key(key)
            logger.Logger.log(f'Equipping: {entity}')
            if entity:
                self.equip(entity)
            elif not valid:
                messager.add_message('Invalid inventory key!')
        # Unequip
        elif action == 'u':
            entity,valid = self.get_entity_from_key(key)
            logger.Logger.log(f'Unequipping: {entity}')
            if entity:
                self.add_to_bag(entity)
            elif not valid:
                messager.add_message('Invalid inventory key!')

    def add_to_quiver(self, entity):
        if self.quiver is None:
            self.quiver = entity
            return True
        elif hasattr(self.quiver, 'Group'):
            if self.quiver.Group.group_up(entity):
                return True
        return False
    
    def has_ammo(self):
        if self.quiver is None:
            return False
        return True
    
    def fire_quiver(self):
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
    def __init__(self, parent, unstack_name, unstack_glyph, stack_name, stack_glyph):
        self.parent = parent
        self.amount = 1
        self.unstack_name = unstack_name
        self.unstack_glyph = unstack_glyph
        self.stack_name = stack_name
        self.stack_glyph = stack_glyph
        self.stacked = False

    def pop_one(self):
        if self.stacked:
            self.amount -= 1
            if self.amount <= 1:
                self.unstack()
            return type(self.parent)()
        else:
            return self.parent

    def stack(self):
        self.stacked = True
        self.parent.name = self.stack_name
        self.parent.glyph = self.stack_glyph

    def unstack(self):
        self.stacked = False
        self.parent.name = self.unstack_name 
        self.parent.glyph = self.unstack_glyph 

    def group_up(self, new_entity):
        if type(new_entity) == type(self.parent) and hasattr(new_entity, 'Group'):
            self.amount += new_entity.Group.amount
            if not self.stacked:
                self.stack()
            return True
        return False

    def check_square(self, entity, levelmanager):
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

    def get_action(self, currlevel, mypos, energy, inventory=None):
        '''Returns an action'''
        pts = self.getFOV(currlevel, mypos)
        playerpos = self.find_player(currlevel, pts)
        if playerpos:
            for attack in self.attacks:
                if (attack == entity.AttackType.THROW and
                    self.throw_attack_possible(mypos, playerpos, inventory)):
                    return self.throw_attack(mypos, playerpos)
                elif attack == entity.AttackType.MELEE:
                    return self.find_path(currlevel.EntityLayer, mypos, playerpos)
        return '.'

    def throw_attack_possible(self, mypos, playerpos, inventory):
        if not inventory.has_ammo():
            return False
        drow = abs(mypos[0] - playerpos[0])
        dcol = abs(mypos[1] - playerpos[1])
        if drow == 0 or dcol == 0 or drow == dcol:
            return True
        return False

    def throw_attack(self, mypos, playerpos):
        d = self.move_towards_pt(mypos, playerpos)
        return 't' + str(d)

    def find_player(self, currlevel, pts):
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
            logger.Logger.log(f'Error: brain failed to find path -> {returncode}')
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


