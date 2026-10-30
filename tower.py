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

class Barrel(entity.Entity):
    '''Barrel entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.BARREL,
                         name='Barrel',
                         glyph='0',
                         layer=entity.Layer.BARREL_LAYER,
                         size=entity.Size.LARGE,
                         fg=color.COLOR.YELLOW)
        self.Breakable = component.Breakable(max_dmg=1)
    
    def death(self, levelmanager, animator, messager):
        '''Break the barrel'''
        super().death(levelmanager)
        levelmanager.place_entity(self.z, item.Wood(), (self.row,self.col))

class Floor(entity.Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.FLOOR,
                         name='Floor',
                         glyph='.',
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.LARGE,
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
    
