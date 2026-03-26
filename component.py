import algo
import entity
import level
import logger
import enum

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
    def __init__(self, parent, nutrition):
        self.parent = parent
        self.nutrition = nutrition
    
    def eat(self, levelmanager, messager, entity):
        if hasattr(entity, 'Health'):
            entity.Health.change_health(self.nutrition)
            messager.add_eat_message(entity, self.parent)
            levelmanager.remove_entity(self.parent)

class ItemType(enum.Enum):
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
                if self.quiver.name != entity.name:
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

    def add_to_bag(self, entity):
        '''Handles adding objects to the bag'''
        logger.Logger.log(f'Adding to bag: {entity}')
        self.contents.append(entity)
        entity.idx = len(self.contents)-1
        # Stack / Stackable items
        if hasattr(entity, 'Stack'):
            entity.Stack.check_entitylist(entity, self.contents)
        elif hasattr(entity, 'Stackable'):
            entity.Stackable.check_entitylist(entity, self.contents)
    
    def unequip(self, entity):
        '''
        Pass in an entity to set the corresponding slot to empty and place
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
        self.add_to_bag(entity)

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
                self.unequip(entity)
            elif not valid:
                messager.add_message('Invalid inventory key!')

class Stackable:
    '''
    Stackable component, entities will combine into the passed in type
    '''
    def __init__(self, stack):
        self.stack = stack
        '''Entity stacked form'''

    def get_stack(self):
        '''Returns the stacked form of the entity'''
        return self.stack()

    def check_entitylist(self, myself, entitylist):
        '''
        Modify entity list if there is a stackable object that works with this object
        Works with any entity list
        Entity (myself) must be placed in the list first
        '''
        for ent in entitylist:
            if ent.id == myself.id:
                continue
            if hasattr(ent, 'Stack') and ent.Stack.unstack == type(myself):
                ent.Stack.add_to_stack()
                entitylist.pop(myself.idx)
                return
            elif type(myself) == type(ent):
                logger.Logger.log(f'Stackable component: ent{ent} myself{myself} {entitylist}')
                stack = ent.Stackable.get_stack()
                stack.Stack.add_to_stack(2)
                entitylist[ent.idx] = stack
                stack.set_pos(myself.row, myself.col, myself.z, ent.idx)
                entitylist.pop(myself.idx)
                logger.Logger.log(f'Stackable component: after {entitylist}')
                return

class Stack:
    '''
    Stack component, if an entity is a stack of entities
    '''
    def __init__(self, unstack):
        self.unstack = unstack
        '''Unstacked single entity form'''
        self.amount = 0
        '''Keep track of amount of entities stacked'''
    
    def add_to_stack(self, am=1):
        '''Add to the amount of stacked entities'''
        self.amount += am

    def get_one(self):
        '''Unstack one entity and return the unstacked single form'''
        self.amount -= 1
        return self.unstack()

    def check_entitylist(self, myself, entitylist):
        '''
        Modify entity list if there is a stackable object that works with this object
        Works with any entity list
        Entity (myself) must be placed in the list first
        '''
        for ent in entitylist:
            if ent.id == myself.id:
                continue
            if hasattr(ent, 'Stackable') and ent.Stackable.stack == type(myself):
                self.add_to_stack()
                entitylist.pop(myself.idx)
                entitylist[ent.idx] = myself
                myself.set_pos(myself.row, myself.col, myself.z, ent.idx)
                return
            elif hasattr(ent, 'Stack') and type(myself) == type(ent):
                entitylist.pop(myself.idx)
                ent.Stack.add_to_stack(self.amount)
                return

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

    def change_health(self, amount):
        '''
        Changes the health bar by an amount

        Returns true if health change causes death
        '''
        self.currenthealth += amount
        if self.alive and self.currenthealth <= 0:
            self.alive = False
            return True
        return False

class Brain:
    '''
    Brain component, if an entity needs to make decisions
    '''
    def __init__(self, sightrange, blockinglayer):
        self.sightrange = sightrange
        '''How far FOV will check'''
        self.blockinglayer = blockinglayer
        '''Highest level (exclusive) FOV will see through'''

    def get_action(self, level, mypos, myz, player, energy):
        '''Returns an action'''
        if player.z == myz:
            # only follow if player is on the same level
            pts = self.getFOV(level, mypos)
            if tuple([player.row,player.col]) in pts:
                return self.move_towards_pt(mypos, [player.row,player.col])
        return '.'
    
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


