import entity
import utility
import color

class Wall(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(name='Wall',
                         glyph='░',
                         color=color.Color().white,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)

class Floor(entity.Entity):
    '''Floor entity'''
    def __init__(self):
        super().__init__(name='Floor',
                         glyph='.',
                         color=color.Color().white,
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.LARGE)

class StairUp(entity.Entity):
    '''Up stair entity'''
    def __init__(self):
        super().__init__(name='Upstair',
                         glyph='<',
                         color=color.Color().white,
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.VERY_LARGE)

class StairDown(entity.Entity):
    '''Down stair entity'''
    def __init__(self):
        super().__init__(name='Downstair',
                         glyph='>',
                         color=color.Color().white,
                         layer=entity.Layer.FLOOR_LAYER,
                         size=entity.Size.VERY_LARGE)

class Light(entity.Entity):
    '''Light entity'''
    def __init__(self):
        super().__init__(name='Light',
                         glyph='+',
                         color=color.Color().yellow,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.SMALL)
        #self.Activate = Activate(True)
        '''Controls whether the light is on'''

    def update(self, entitylayer, playerpos, lightlayer, *args):
        '''Turn the light on if it is active'''
        if self.Activate.active:
            points = utility.get_one_layer_pos(self.pos)
            for pt in points:
                lightlayer[pt[0]][pt[1]] = 1
    
