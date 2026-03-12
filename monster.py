import entity as e
import color
import component

class Newt(e.Entity):
    '''
    Newt creature
    '''
    def __init__(self):
        self.Health = component.Health(health=3)
        self.Brain = component.Brain(sightrange=5, blockinglayer=e.Layer.MONST_LAYER)
        #self.Inventory = Inventory()
        self.speed = e.Speed.SLOW
        self.attackspeed = e.AttackSpeed.SLOW
        super().__init__(name='Newt',
                         glyph='n',
                         color=color.Color().yellow,
                         layer=e.Layer.MONST_LAYER,
                         size=e.Size.MEDIUM)

    def setup(self):
        super().setup()
        #self.Inventory.equip(Bite())

    def take_turn(self, levelmanager, energy):
        '''Uses brain to select an action'''
        return self.do_action(
                levelmanager,
                self.Brain.get_action(
                    levelmanager.get_curr_level(),
                    [self.row,self.col],
                    self.z,
                    levelmanager.Player,
                    energy
                )
            )
