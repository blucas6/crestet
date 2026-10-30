import entity
import utility
import color
import typeid

'''░ ▒ ▓'''

class Sandstone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.SANDSTONE,
                         name='Sandstone',
                         glyph='░',
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE,
                         fg=color.COLOR.GREY)

class Limestone(entity.Entity):
    '''Wall entity'''
    def __init__(self):
        super().__init__(typeid=typeid.TID.LIMESTONE,
                         name='Limestone',
                         glyph='▓',
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE,
                         fg=color.COLOR.GREY)

'''
class Quarrystone(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.QUARRYSTONE,
                         name='Quarrystone',
                         glyph='#',
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE)
'''
class Rubble(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.RUBBLE,
                         name='Rubble',
                         glyph='#',
                         layer=entity.Layer.WALL_LAYER,
                         size=entity.Size.VERY_LARGE,
                         fg=color.COLOR.GREY)
