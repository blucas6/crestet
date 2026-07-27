import entity
import color
import component

class Bite(entity.Entity):
    def __init__(self):
        super().__init__(typeid=12,
                         name='Bite',
                         glyph='X',
                         color=color.Color().magenta,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Bite', damage=3)
        self.ItemType = component.ItemType.ABILITY

class Fist(entity.Entity):
    def __init__(self):
        super().__init__(typeid=25,
                         name='Fist',
                         glyph='X',
                         color=color.Color().magenta,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Fist', damage=1)
        self.ItemType = component.ItemType.ABILITY

class Peck(entity.Entity):
    def __init__(self):
        super().__init__(typeid=27,
                         name='Peck',
                         glyph='X',
                         color=color.Color().magenta,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Peck', damage=1)
        self.ItemType = component.ItemType.ABILITY

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        entitylayer = levelmanager.Levels[z].EntityLayer
        for ent in entitylayer[row][col]:
            ent.apply_status(messager, entity.StatusEffect.BLIND)

