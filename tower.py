import entity
import color
import item
import utility
import component
import logging
import typeid

Logger = logging.getLogger(__name__)

class UnknownEntity(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.UNKNOWN,
                         name='Unknown',
                         glyph='!',
                         layer=entity.Layer.MONSTER_LAYER,
                         size=entity.Size.SMALL,
                         fg=color.COLOR.MAGENTA)
class UnknownStructure(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.UNKNOWNSTRUCT,
                         name='Unknown',
                         glyph='▒',
                         layer=entity.Layer.MONSTER_LAYER,
                         size=entity.Size.SMALL,
                         fg=color.COLOR.WHITE)

class Door(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.DOOR,
                         name='Door',
                         glyph='+',
                         layer=entity.Layer.DOOR_LAYER,
                         size=entity.Size.MEDIUM,
                         fg=color.COLOR.YELLOW)
        self.open = False

    def toggle(self, currlevel):
        Logger.info(f'Door toggle {self}')
        if self.open:
            elist = currlevel.EntityLayer[self.row][self.col]
            maxlayer = utility.get_max_layer(elist)
            if maxlayer == entity.Layer.OPENDOOR_LAYER:
                self.open = False
                self.glyph = '+'
                self.layer = entity.Layer.DOOR_LAYER
        else:
            self.open = True
            self.glyph = '■'
            self.layer = entity.Layer.OPENDOOR_LAYER

class Barrel(entity.Entity):
    '''Barrel entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.BARREL,
                         name='Barrel',
                         glyph='0',
                         layer=entity.Layer.BARREL_LAYER,
                         size=entity.Size.LARGE,
                         fg=color.COLOR.YELLOW)
        self.Breakable = component.Breakable(max_dmg=1, smashed_item=item.Wood())
    
    def death(self, levelmanager, animator, messager):
        '''Break the barrel'''
        super().death(levelmanager)

class Floor(entity.Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.FLOOR,
                         name='Floor',
                         glyph='.',
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.LARGE,
                         fg=color.COLOR.GREY)

class WoodFloor(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.WOODFLOOR,
                         name='Wood Floor',
                         glyph='.',
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.SMALL,
                         fg=color.COLOR.WHITE)

class StairUp(entity.Entity):
    '''Up stair entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.STAIRUP,
                         name='Upstair',
                         glyph='<',
                         layer=entity.Layer.STAIR_LAYER,
                         size=entity.Size.VERY_LARGE,
                         fg=color.COLOR.WHITE)

class StairDown(entity.Entity):
    '''Down stair entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.STAIRDOWN,
                         name='Downstair',
                         glyph='>',
                         layer=entity.Layer.STAIR_LAYER,
                         size=entity.Size.VERY_LARGE,
                         fg=color.COLOR.WHITE)

class Light(entity.Entity):
    '''Light entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.LIGHT,
                         name='Light',
                         glyph='+',
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.SMALL,
                         fg=color.COLOR.BRIGHT_YELLOW)
        self.light = True
        '''Controls whether the light is on'''

    def on_init(self, rng, levelmanager):
        self.update_state(levelmanager)

    def update_state(self, levelmanager):
        '''Update the map based on the light state'''
        if self.light and levelmanager.Levels:
            points = utility.get_one_layer_pts((self.row,self.col),
                                               levelmanager.levelrows, levelmanager.levelcols)
            for pt in points:
                levelmanager.Levels[self.z].LightLayer[pt[0]][pt[1]] = 1
    
    def on_top(self, entity, levelmanager):
        '''Trigger the light on or off'''
        self.light = not self.light
        self.update_state(levelmanager)

    
