import entity as e
import color
import typeid
import animation
import config
import component
import utility
import item
import logging
import ability
import brain

Logger = logging.getLogger(__name__)

class GoblinLeader(e.Entity):
    difficulty = 4
    pack = 2
    packtype = ['Goblin']
    def __init__(self):
        super().__init__(typeid=typeid.TID.GOBLINLEADER,
                         name='Goblin Leader',
                         glyph='G',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.GREEN)
        self.Health = component.Health(health=config.GOBLINLEADER_HEALTH)
        self.eyes = config.GOBLINLEADER_SIGHTRANGE
        self.xp = config.GOBLINLEADER_XP
        self.Brain = brain.SimpleBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.MELEE])
        self.speed = e.Speed.SLOW
        self.Combat = component.Combat()
        self.Inventory = component.Inventory()

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng, generator):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.Levels[self.z],
                [self.row,self.col],
                self.energy,
                rng,
                self.speed,
                self.status,
                self.Inventory
            ),
            rng,
            generator
        )

    def on_init(self, rng):
        if rng.randint(0,1):
            self.Inventory.equip(item.ShortSword())

class Snail(e.Entity):
    difficulty = 4
    def __init__(self):
        super().__init__(typeid=typeid.TID.SNAIL,
                         name='Snail',
                         glyph='s',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.GREY)
        self.Health = component.Health(health=config.SNAIL_HEALTH)
        self.eyes = config.SNAIL_SIGHTRANGE
        self.xp = config.SNAIL_XP
        self.Brain = brain.SimpleBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.MELEE])
        self.speed = e.Speed.CRAWLING
        self.Combat = component.Combat()
        self.Inventory = component.Inventory()
        self.Inventory.equip(ability.Lick())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng, generator):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.Levels[self.z],
                [self.row,self.col],
                self.energy,
                rng,
                self.speed,
                self.status,
                self.Inventory
            ),
            rng,
            generator
        )
    
    def death(self, levelmanager, animator, messager):
        super().death(levelmanager)
        if levelmanager.RNG.randint(0,1) == 0:
            shell = item.SnailShell()
            levelmanager.place_entity(self.z, shell, (self.row,self.col))
        else:
            utility.corpse_drop(levelmanager, item.Corpse(), self.fg, self.name, self.pos())

class Lynx(e.Entity):
    difficulty = 4
    def __init__(self):
        super().__init__(typeid=typeid.TID.LYNX,
                         name='Lynx',
                         glyph='f',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.RED)
        self.Health = component.Health(health=config.LYNX_HEALTH)
        self.eyes = config.LYNX_SIGHTRANGE
        self.xp = config.LYNX_XP
        self.Brain = brain.SimpleBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.MELEE])
        self.speed = e.Speed.AVERAGE
        self.Combat = component.Combat()
        self.Inventory = component.Inventory()
        self.Inventory.equip(ability.Claw())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng, generator):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.Levels[self.z],
                [self.row,self.col],
                self.energy,
                rng,
                self.speed,
                self.status,
                self.Inventory
            ),
            rng,
            generator
        )

    def death(self, levelmanager, animator, messager):
        super().death(levelmanager)
        if levelmanager.RNG.randint(0,1) == 0:
            stone = item.PreciousStone()
            levelmanager.place_entity(self.z, stone, (self.row,self.col))
        else:
            utility.corpse_drop(levelmanager, item.Corpse(), self.fg, self.name, self.pos())

class Raven(e.Entity):
    difficulty = 3
    def __init__(self):
        super().__init__(typeid=typeid.TID.RAVEN,
                         name='Raven',
                         glyph='r',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.SMALL,
                         fg=color.COLOR.BLUE)
        self.eyes = config.RAVEN_SIGHTRANGE
        self.Health = component.Health(health=config.RAVEN_HEALTH)
        self.Brain = brain.SimpleBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.MELEE])
        self.Combat = component.Combat()
        self.Inventory = component.Inventory(autopickuplist=['Seed'])
        self.speed = e.Speed.MEDIUM
        self.xp = config.RAVEN_XP

        self.Inventory.equip(ability.Peck())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng, generator):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.Levels[self.z],
                [self.row,self.col],
                self.energy,
                rng,
                self.speed,
                self.status,
                self.Inventory
            ),
            rng,
            generator
        )

    def death(self, levelmanager, animator, messager):
        super().death(levelmanager)
        utility.corpse_drop(levelmanager, item.Corpse(), self.fg, self.name, self.pos())

class Goblin(e.Entity):
    '''
    Goblin creature
    '''
    difficulty = 2
    def __init__(self):
        super().__init__(typeid=typeid.TID.GOBLIN,
                         name='Goblin',
                         glyph='g',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.GREEN)
        self.eyes = config.GOBLIN_SIGHTRANGE
        self.Health = component.Health(health=config.GOBLIN_HEALTH)
        self.Brain = brain.PackBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.THROW,
                                              e.AttackType.MELEE],
                                     pack_leader='Goblin Leader')

        self.Combat = component.Combat()
        self.Inventory = component.Inventory(autopickuplist=['Dart'])
        self.Inventory.equip(ability.Bite())
        self.speed = e.Speed.SLOW
        self.xp = config.GOBLIN_XP

    def on_init(self, rng):
        darts = rng.randint(3, 7)
        for _ in range(darts):
            self.Inventory.collect(item.Dart())
        
        if rng.randint(0,10) < 3:
            self.Inventory.equip(item.Gambeson())

        if rng.randint(0,10) < 7:
            self.Inventory.equip(item.BlowPipe())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng, generator):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.Levels[self.z],
                [self.row,self.col],
                self.energy,
                rng,
                self.speed,
                self.status,
                self.Inventory
            ),
            rng,
            generator
        )

    def death(self, levelmanager, animator, messager):
        super().death(levelmanager)
        utility.corpse_drop(levelmanager, item.Corpse(), self.fg, self.name, self.pos())

class Human(e.Entity):
    '''
    Human
    '''
    def __init__(self):
        super().__init__(typeid=typeid.TID.HUMAN,
                         name='Human',
                         glyph='@',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.WHITE)
        self.Interact = component.Interact()

class Newt(e.Entity):
    '''
    Newt creature
    '''
    difficulty = 1
    def __init__(self):
        super().__init__(typeid=typeid.TID.NEWT,
                         name='Newt',
                         glyph='n',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.YELLOW)
        self.eyes = config.NEWT_SIGHTRANGE
        self.Health = component.Health(health=config.NEWT_HEALTH)
        self.Brain = brain.SimpleBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.MELEE])
        self.Inventory = component.Inventory()
        self.speed = e.Speed.VERY_SLOW
        self.xp = config.NEWT_XP
        self.Combat = component.Combat()
        self.Inventory.equip(ability.Bite())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng, generator):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.Levels[self.z],
                [self.row,self.col],
                self.energy,
                rng,
                self.speed,
                self.status
            ),
            rng,
            generator
        )

    def death(self, levelmanager, animator, messager):
        super().death(levelmanager)
        utility.corpse_drop(levelmanager, item.Corpse(), self.fg, self.name, self.pos())

class Jelly(e.Entity):
    '''
    Floating jelly creature
    '''
    difficulty = 0
    def __init__(self):
        super().__init__(typeid=typeid.TID.JELLY,
                         name='Jelly',
                         glyph='j',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.BLUE)
        self.Health = component.Health(health=config.JELLY_HEALTH)
        self.splashdamage = config.JELLY_SPLASHDMG
        self.xp = 2
        self.Combat = component.Combat()

    def death(self, levelmanager, animator, messager):
        '''
        Generate the explosion on death
        '''
        super().death(levelmanager)
        messager.add_burst_message(levelmanager.currentz, self)
        # queue animation
        frames = []
        frames.append([
            ['','' ,''],
            ['','*',''],
            ['','' ,'']
        ])
        frames.append([
            ['/' ,'-', '\\'],
            ['|',' ' ,'|'],
            ['\\' ,'-', '/']
        ])
        delays = [config.EXPLOSION_ANIM_DELAY, config.EXPLOSION_ANIM_DELAY]
        origin = [self.row-1, self.col-1, self.z, self.idx]
        anim = animation.Animation(
            pos=origin,
            frames=frames, 
            delays=delays,
            fg=color.COLOR.BLUE)
        animator.queueUp(levelmanager, anim)
        # spread damage
        points = utility.get_one_layer_pts((self.row,self.col),
                                           levelmanager.levelrows,
                                           levelmanager.levelcols)
        for point in points:
            ptrow = point[0]
            ptcol = point[1]
            # don't damage yourself
            if (ptrow,ptcol) == (self.row,self.col):
                continue
            for entity in levelmanager.Levels[self.z].EntityLayer[ptrow][ptcol]:
                self.Combat.deal_damage(
                    self, levelmanager, animator, messager, entity,
                    True, self.splashdamage, 'jelly')

