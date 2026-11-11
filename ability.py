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
                                               melee_damage=1,
                                               melee_you_action='lick',
                                               melee_it_action='licks')

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
                                               melee_damage=4,
                                               melee_you_action='claw',
                                               melee_it_action='claws')

class Bite(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BITE,
                         name='Bite',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=2,
                                               melee_you_action='bite',
                                               melee_it_action='bites')

class Fist(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.FIST,
                         name='Fist',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=1,
                                               melee_you_action='punch',
                                               melee_it_action='punches')

class Peck(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.PECK,
                         name='Peck',
                         glyph=config.ABILITY_GLYPH,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.PINK)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.ABILITY,
                                               melee_damage=2,
                                               melee_you_action='peck',
                                               melee_it_action='pecks')

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        '''Abilities get applied on damage'''
        entitylayer = levelmanager.Levels[z].EntityLayer
        for ent in entitylayer[row][col]:
            ent.apply_status(messager, entity.StatusEffect.BLIND, levelmanager)

