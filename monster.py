import entity as e
import animation
import config
import color
import component
import utility
import item
import logging
import ability
import brain

Logger = logging.getLogger(__name__)

class Raven(e.Entity):
    difficulty = 3
    def __init__(self):
        super().__init__(typeid=26,
                         name='Raven',
                         glyph='r',
                         color=color.Color().blue,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.SMALL)
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

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng):
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
            rng
        )

class Goblin(e.Entity):
    '''
    Goblin creature
    '''
    difficulty = 2
    def __init__(self):
        super().__init__(typeid=17,
                         name='Goblin',
                         glyph='g',
                         color=color.Color().green,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM)
        self.eyes = config.GOBLIN_SIGHTRANGE
        self.Health = component.Health(health=config.GOBLIN_HEALTH)
        self.Brain = brain.SimpleBrain(sightrange=self.eyes,
                                     blockinglayer=e.Layer.MONSTER_LAYER,
                                     attacks=[e.AttackType.THROW,
                                              e.AttackType.MELEE])
        self.Combat = component.Combat()
        self.Inventory = component.Inventory(autopickuplist=['Dart'])
        self.speed = e.Speed.SLOW
        self.xp = config.GOBLIN_XP

        self.Inventory.equip(ability.Bite())
        for _ in range(5):
            self.Inventory.collect(item.Dart())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng):
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
            rng
        )

class Human(e.Entity):
    '''
    Human
    '''
    def __init__(self):
        super().__init__(typeid=7,
                         name='Human',
                         glyph='@',
                         color=color.Color().white,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM)
        self.Interact = component.Interact()

class Newt(e.Entity):
    '''
    Newt creature
    '''
    difficulty = 1
    def __init__(self):
        super().__init__(typeid=8,
                         name='Newt',
                         glyph='n',
                         color=color.Color().yellow,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM)
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

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine, rng):
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
            rng
        )

class Jelly(e.Entity):
    '''
    Floating jelly creature
    '''
    difficulty = 0
    def __init__(self):
        super().__init__(typeid=9,
                         name='Jelly',
                         glyph='j',
                         color=color.Color().blue,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.MEDIUM)
        self.Health = component.Health(health=config.JELLY_HEALTH)
        self.splashdamage = config.JELLY_SPLASHDMG
        self.xp = 2
        self.Combat = component.Combat()

    def death(self, levelmanager, animator, messager):
        '''
        Generate the explosion on death
        '''
        super().death(levelmanager)
        messager.add_message('It explodes!')
        # queue animation
        frames = {}
        frames['0'] = [
            ['','' ,''],
            ['','*',''],
            ['','' ,'']
        ]
        frames['1'] = [
            ['/' ,'-', '\\'],
            ['|',' ' ,'|'],
            ['\\' ,'-', '/']
        ]
        origin = [self.row-1,self.col-1]
        anim = animation.Animation(
            origin=origin,
            frames=frames, 
            color=color.Color().blue,
            delay=config.EXPLOSION_ANIM_DELAY)
        animator.queueUp(anim)
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

