import entity
import color
import component
import utility
import typeid

class Bite(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BITE,
                         name='Bite',
                         glyph='X',
                         color=color.Color().magenta,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Bite', damage=3)
        self.ItemType = component.ItemType.ABILITY

class Fist(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.FIST,
                         name='Fist',
                         glyph='X',
                         color=color.Color().magenta,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Fist', damage=1)
        self.ItemType = component.ItemType.ABILITY

class Peck(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.PECK,
                         name='Peck',
                         glyph='X',
                         color=color.Color().magenta,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Peck', damage=1)
        self.ItemType = component.ItemType.ABILITY

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        '''Abilities get applied on damage'''
        entitylayer = levelmanager.Levels[z].EntityLayer
        for ent in entitylayer[row][col]:
            ent.apply_status(messager, entity.StatusEffect.BLIND, levelmanager)

