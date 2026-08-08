import entity
import item
import utility
import color
import component
import logging

Logger = logging.getLogger(__name__)

class UnknownEntity(entity.Entity):
    def __init__(self):
        super().__init__(typeid=99,
                         name='Unknown',
                         glyph='!',
                         color=color.Color().magenta,
                         layer=entity.Layer.MONSTER_LAYER,
                         size=entity.Size.SMALL)
class UnknownStructure(entity.Entity):
    def __init__(self):
        super().__init__(typeid=98,
                         name='Unknown',
                         glyph='▒',
                         color=color.Color().white,
                         layer=entity.Layer.MONSTER_LAYER,
                         size=entity.Size.SMALL)

class Barrel(entity.Entity):
    '''Barrel entity'''
    def __init__(self):
        super().__init__(typeid=16,
                         name='Barrel',
                         glyph='0',
                         color=color.Color().yellow,
                         layer=entity.Layer.BARREL_LAYER,
                         size=entity.Size.LARGE)
        self.Breakable = component.Breakable(max_dmg=1)
    
    def death(self, levelmanager, animator, messager):
        '''Break the barrel'''
        super().death(levelmanager)
        levelmanager.place_entity(self.z, item.Wood(), (self.row,self.col))

class Floor(entity.Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__(typeid=3,
                         name='Floor',
                         glyph='.',
                         color=color.Color().white,
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.LARGE)

class StairUp(entity.Entity):
    '''Up stair entity'''
    def __init__(self):
        super().__init__(typeid=4,
                         name='Upstair',
                         glyph='<',
                         color=color.Color().white,
                         layer=entity.Layer.STAIR_LAYER,
                         size=entity.Size.VERY_LARGE)

class StairDown(entity.Entity):
    '''Down stair entity'''
    def __init__(self):
        super().__init__(typeid=5,
                         name='Downstair',
                         glyph='>',
                         color=color.Color().white,
                         layer=entity.Layer.STAIR_LAYER,
                         size=entity.Size.VERY_LARGE)

class Light(entity.Entity):
    '''Light entity'''
    def __init__(self):
        super().__init__(typeid=6,
                         name='Light',
                         glyph='+',
                         color=color.Color().bright_yellow,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.SMALL)
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
    
