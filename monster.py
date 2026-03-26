import entity as e
import animation
import config
import color
import component
import utility
import item

class Human(e.Entity):
    '''
    Human
    '''
    def __init__(self):
        super().__init__(name='Human',
                         glyph='@',
                         color=color.Color().white,
                         layer=e.Layer.MONST_LAYER,
                         size=e.Size.MEDIUM)
        self.Interact = component.Interact()

class Newt(e.Entity):
    '''
    Newt creature
    '''
    def __init__(self):
        self.Health = component.Health(health=config.NEWT_HEALTH)
        self.Brain = component.Brain(sightrange=config.NEWT_SIGHTRANGE,
                                     blockinglayer=e.Layer.MONST_LAYER)
        self.Inventory = component.Inventory()
        self.speed = e.Speed.SLOW
        self.attackspeed = e.AttackSpeed.SLOW
        super().__init__(name='Newt',
                         glyph='n',
                         color=color.Color().yellow,
                         layer=e.Layer.MONST_LAYER,
                         size=e.Size.MEDIUM)
        self.Inventory.equip(item.Bite())

    def take_turn(self, levelmanager, animator, messager, menumanager, statemachine):
        '''Uses brain to select an action'''
        self.do_action(
            levelmanager,
            animator,
            messager,
            menumanager,
            statemachine,
            self.Brain.get_action(
                levelmanager.get_curr_level(),
                [self.row,self.col],
                self.z,
                levelmanager.Player,
                self.energy
            )
        )

class Jelly(e.Entity):
    '''
    Floating jelly creature
    '''
    def __init__(self):
        super().__init__(name='Jelly',
                         glyph='j',
                         color=color.Color().blue,
                         layer=e.Layer.MONST_LAYER,
                         size=e.Size.MEDIUM)
        self.Health = component.Health(health=config.JELLY_HEALTH)
        self.splashdamage = config.JELLY_SPLASHDMG

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
                self.deal_damage(levelmanager, animator, messager, entity, self.splashdamage)
