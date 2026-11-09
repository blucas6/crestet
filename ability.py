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
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=1)

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
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=4)

class Bite(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BITE,
                         name='Bite',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=2)

class Fist(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.FIST,
                         name='Fist',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=1)

class Peck(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.PECK,
                         name='Peck',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=2)

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        '''Abilities get applied on damage'''
        entitylayer = levelmanager.Levels[z].EntityLayer
        for ent in entitylayer[row][col]:
            ent.apply_status(messager, entity.StatusEffect.BLIND, levelmanager)

