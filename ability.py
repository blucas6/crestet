import entity
import config
import color
import component
import utility
import typeid

class Lick(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.LICK,
                         name='Lick',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.Attack = component.Attack(name='Lick', damage=1)
        self.ItemType = component.ItemType.ABILITY

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        entitylayer = levelmanager.Levels[z].EntityLayer
        for ent in entitylayer[row][col]:
            ent.apply_status(messager, entity.StatusEffect.POISON, levelmanager)

class Claw(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.CLAW,
                         name='Claw',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.Attack = component.Attack(name='Claw', damage=4)
        self.ItemType = component.ItemType.ABILITY

class Bite(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BITE,
                         name='Bite',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.Attack = component.Attack(name='Bite', damage=2)
        self.ItemType = component.ItemType.ABILITY

class Fist(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.FIST,
                         name='Fist',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.Attack = component.Attack(name='Fist', damage=1)
        self.ItemType = component.ItemType.ABILITY

class Peck(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.PECK,
                         name='Peck',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.Attack = component.Attack(name='Peck', damage=2)
        self.ItemType = component.ItemType.ABILITY

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        '''Abilities get applied on damage'''
        entitylayer = levelmanager.Levels[z].EntityLayer
        for ent in entitylayer[row][col]:
            ent.apply_status(messager, entity.StatusEffect.BLIND, levelmanager)

