import entity
import color
import utility
import typeid

'''░ ▒ ▓'''

class Sandstone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.SANDSTONE,
                         name='Sandstone',
                         glyph='░',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)

class Limestone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.LIMESTONE,
                         name='Limestone',
                         glyph='▓',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)

'''
class Quarrystone(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.QUARRYSTONE,
                         name='Quarrystone',
                         glyph='#',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)
'''
class Rubble(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.RUBBLE,
                         name='Rubble',
                         glyph='#',
                         color=color.Color().grey,
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)
