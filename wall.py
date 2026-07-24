import entity
import color

class Sandstone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=21,
                         name='Sandstone',
                         glyph='░',
                         color=color.Color().white,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)

class Limestone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=2,
                         name='Limestone',
                         glyph='▒',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)

class Quarrystone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=22,
                         name='Quarrystone',
                         glyph='#',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)

class Rubble(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=23,
                         name='Rubble',
                         glyph='%',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)
