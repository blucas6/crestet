import entity
import logger
import utility
import color
import component

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
        self.light = False
        '''Controls whether the light is on'''

    def update_state(self, levelmanager):
        '''Update the map based on the light state'''
        if self.light:
            points = utility.get_one_layer_pts((self.row,self.col),
                                               levelmanager.levelrows, levelmanager.levelcols)
            logger.Logger.log(f'{self} {self.pos()} pts: {points}')
            for pt in points:
                levelmanager.Levels[self.z].LightLayer[pt[0]][pt[1]] = 1
    
    def on_top(self, levelmanager):
        self.light = not self.light
        logger.Logger.log(f'Light toggled {self} {self.light}')
        self.update_state(levelmanager)
    
