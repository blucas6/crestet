import algo
import animation
import config
import entity
import level
import enum
import utility
import logging

Logger = logging.getLogger(__name__)

class Combat:
    '''Combat component, every entity that can engage in damage must have one'''
    def __init__(self):
        self.critical = 1
        '''Critical hit'''
        self.accuracy = 60
        '''Roll under this number to hit on a melee attack'''
        self.throw_accuracy = 40
        '''Roll under this number to hit on a ranged attack'''
        self.resistances = {}
        '''Resistance library'''
        self.evade = 10
        '''Roll under this to evade the attack'''

    def get_damage_melee(self, rng, parent):
        '''Return the damage a melee attack does'''
        dmg = 0
        success = False
        roll = rng.randint(1,100)
        if hasattr(parent, 'Charge') and parent.Charge.charging:
            potential_dmg = parent.Charge.end()
            if roll <= self.accuracy:
                dmg = potential_dmg
                success = True
        elif hasattr(parent, 'Inventory'):
            if roll <= self.accuracy:
                dmg = parent.Inventory.calculate_damage()
                success = True
        Logger.info(f"COMBAT: ({roll}) dmg:{dmg} {'HIT' if roll <= self.accuracy else 'MISS'}")
        return success, dmg

    def take_damage(self, inventory, damage):
        '''Return the damage actually taken after subtracting for armor and resistances'''
        reduction = 0
        if inventory.head and hasattr(inventory.head, 'armor'):
            reduction += inventory.head.armor
        if inventory.body and hasattr(inventory.body, 'armor'):
            reduction += inventory.body.armor
        if inventory.feet and hasattr(inventory.feet, 'armor'):
            reduction += inventory.feet.armor
        damage -= reduction
        if damage <= 0:
            return 1
        return damage

    def throw(self, levelmanager, animator, projectile, direction_key, rng, start_row, start_col, z):
        '''
        Send an object flying through the air, if the accuracy check succeeds, stop the
        object at a target otherwise keep going until something blocks the trajectory
        '''
        success = False
        entitylayer = levelmanager.Levels[z].EntityLayer
        direction = utility.ONE_LAYER_CIRCLE[int(direction_key)-1]
        objr = start_row
        objc = start_col
        # figure out where it lands
        while True:
            r,c = objr + direction[0], objc + direction[1]
            if r < 0 or c < 0 or r >= len(entitylayer) or c >= len(entitylayer[0]):
                break
            if entitylayer:
                maxlayer = utility.get_max_layer(entitylayer[r][c])
                if (maxlayer == entity.Layer.MONSTER_LAYER or
                    maxlayer == entity.Layer.BARREL_LAYER):
                    objr, objc = r, c
                    # stop only if it passes the accuracy check
                    if rng.randint(1,100) <= self.throw_accuracy:
                        success = True
                        break
                elif maxlayer == entity.Layer.WALL_LAYER:
                    break
            objr, objc = r, c

        # place the object in it's final spot
        levelmanager.place_entity(z, projectile, (objr,objc))

        # create the animation
        grid,pts = utility.get_path_pts(entitylayer, start_row, start_col, objr, objc)
        frames = {}
        for idx,pt in enumerate(pts):
            frames[str(idx)] = [['' for _ in row] for row in grid]
            frames[str(idx)][pt[0]][pt[1]] = projectile.glyph
        origin = [0,0]
        delay = config.THROW_ANIM_DELAY
        anim = animation.Animation(origin, frames, projectile.color, delay=delay)
        animator.queueUp(anim)
        Logger.info(f'throwing object')
        return success, objr,objc

    def attack_range(self, parent, levelmanager, animator, messager, projectile, direction_key, rng, start_row, start_col, z):
        '''Start a ranged attack by throwing a projectile'''
        # throw
        success, objr, objc = self.throw(levelmanager, animator, projectile, direction_key, rng, start_row, start_col, z)
        # get damage
        damage = 0
        if hasattr(projectile, 'Attack'):
            damage = projectile.Attack.damage
        else:
            damage = projectile.size * 2
        # deal damage
        for ent in levelmanager.Levels[z].EntityLayer[objr][objc]:
            self.deal_damage(parent, levelmanager, animator, messager, ent, success, damage, 'range')

    def attack_melee(self, parent, levelmanager, animator, messager, victim, rng):
        '''Attack the entity passed in'''
        # get damage
        if hasattr(parent, 'Inventory') or hasattr(parent, 'Charge'):
            success, damage = self.get_damage_melee(rng, parent)
            self.deal_damage(parent, levelmanager, animator, messager, victim, success, damage, 'melee')
            # check for any special effects
            if success and hasattr(parent, 'Inventory'):
                parent.Inventory.apply_ability(parent, levelmanager, messager, animator, victim.row, victim.col, victim.z)

    def deal_damage(self, parent, levelmanager, animator, messager, victim, success, damage, dmg_type):
        '''Send damage to an entity and specify the damage type'''

        # victim must have a health bar to take damage and for a 'miss'
        if hasattr(victim, 'Health'):
            # missed
            if not success:
                messager.add_miss_message(parent, victim)
                return

            # only create a notification for actual attacks
            if dmg_type == 'melee' or dmg_type == 'range':
                messager.add_damage_message(parent, victim)

            # send damage to the victim Combat component for defense
            if hasattr(victim, 'Combat') and hasattr(victim, 'Inventory'):
                damage = victim.Combat.take_damage(victim.Inventory, damage)

            Logger.info(f'{parent} dealing damage to {victim}: {damage} ')
            # check for kill
            if victim.Health.change_health(-damage):
                victim.death(levelmanager, animator, messager)
                messager.add_kill_message(parent, victim)
                # gain xp
                if hasattr(parent, 'Leveling') and hasattr(victim, 'xp'):
                    parent.Leveling.gain_xp(victim.xp, parent, messager)

        # or victim must be breakable
        elif hasattr(victim, 'Breakable'):
            # missed
            if not success:
                messager.add_miss_message(parent, victim)
                return

            Logger.info(f'{parent} hitting {victim} : {damage}')

            # only create a notification for actual attacks
            if dmg_type == 'melee' or dmg_type == 'range':
                messager.add_damage_message(parent, victim)

            # check for break
            if victim.Breakable.change_dmg(damage):
                victim.death(levelmanager, animator, messager)
                messager.add_break_message(parent, victim)

class Breakable:
    '''Objects that can break (instead of dying)'''
    def __init__(self, max_dmg):
        self.max_dmg = max_dmg
        '''Max amount of damage before breaking'''
        self.current_dmg = 0
        '''Current damage taken'''
        self.broken = False
        '''Is it broken'''
    
    def change_dmg(self, dmg):
        '''
        Pass in a damage to add it to the current damage toll
        Returns true if damage causes it to break
        '''
        self.current_dmg += dmg
        if self.current_dmg < 0:
            self.current_dmg = 0
        if self.current_dmg >= self.max_dmg:
            self.broken = True
            return True
        return False

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
        # increase max health
        if hasattr(parent_entity, 'Health'):
            parent_entity.Health.maxhealth += self.curr_level
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
            #messager.add_eat_message(entity_eater, self.parent_entity)
            if not hasattr(self.parent_entity, 'PlantStage'):
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

    def remove_from_bag(self, entity):
        '''Delete an entity from the bag'''
        for ix,ent in enumerate(self.contents):
            if ent.id == entity.id:
                del self.contents[ix]
                break

    def equip(self, entity):
        '''
        Pass in an entity to place it in the correct slot
        '''

        if not hasattr(entity, 'ItemType'):
            return
        
        if entity.ItemType == ItemType.NOEQUIP:
            return
        
        # delete an entity if it came from the bag, it will be placed
        self.remove_from_bag(entity)

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

        # try to add it to the correct slot
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.QUIVER:
            if self.add_to_quiver(entity):
                return
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.HAND:
            if self.mainHand is None:
                self.mainHand = entity
                return
            if self.offHand is None:
                self.offHand = entity
                return
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.BODY:
            if self.body is None:
                self.body = entity
                return
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.HEAD:
            if self.head is None:
                self.head = entity
                return
        if hasattr(entity, 'ItemType') and entity.ItemType == ItemType.FEET:
            if self.feet is None:
                self.feet = entity
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

    def drop(self, parent, levelmanager, entity):
        '''Place an entity to the ground'''
        self.remove_from_bag(entity)
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

        levelmanager.place_entity(parent.z, entity, (parent.row,parent.col))

    
    def pickup(self, parent, levelmanager):
        '''Pick up ONE entity from the ground'''
        entitylist = levelmanager.Levels[parent.z].EntityLayer[parent.row][parent.col]
        for ent in entitylist:
            if ent.layer == entity.Layer.OBJECT_LAYER:
                self.collect(ent)
                levelmanager.remove_entity(ent)
                break

    def action(self, parent, levelmanager, messager, event, animator, row, col, z):
        '''Handle an inventory action'''
        action = event[0]
        if len(event) > 1:
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
            # Drop
            elif action == 'd':
                Logger.info(f'Drop: {entity}')
                self.drop(parent, levelmanager, entity)
        else:
            # Pick up
            if action == ',':
                Logger.info(f'Pick up')
                self.pickup(parent, levelmanager)

    def apply(self, entity, cmd, parent, levelmanager, messager, animator, row, col, z):
        '''Trigger the apply on an entity'''
        remove = entity.on_apply(cmd, parent, levelmanager, messager, animator, row, col, z)
        if remove is None:
            messager.add_message('Nothing happens')
        elif remove:
            self.contents = [item for item in self.contents if item.id != entity.id]

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

    def calculate_damage(self):
        '''Get the damage based off of the inventory objects'''
        dmg = 0
        if self.mainHand and hasattr(self.mainHand, 'Attack'):
            dmg += self.mainHand.Attack.damage
            if self.offHand and hasattr(self.offHand, 'Attack'):
                dmg += self.offHand.Attack.damage
        elif self.ability and hasattr(self.ability, 'Attack'):
            dmg += self.ability.Attack.damage
        return dmg

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

    def apply_ability(self, parent, levelmanager, messager, animator, row, col, z):
        '''If using an ability, activate the special effect'''
        if self.mainHand is None and self.offHand is None and self.ability:
            self.ability.on_apply('', parent, levelmanager, messager, animator, row, col, z)

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
