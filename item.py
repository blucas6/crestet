import entity as e
import color
import component
import typeid

class Corpse(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.CORPSE,
                         name='Corpse',
                         glyph='%',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.MEDIUM,
                         fg=color.COLOR.WHITE)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.HAND,
                                               melee_damage=1,
                                               throw_damage=1)

class PreciousStone(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.PRECIOUS_STONE,
                         name='Precious Stone',
                         glyph='`',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL,
                         fg=color.COLOR.GREY)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.QUIVER,
                                               melee_damage=1,
                                               throw_damage=1)

class SnailShell(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.SNAIL_SHELL,
                         name='Snail Shell',
                         glyph='æ',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL,
                         fg=color.COLOR.GREY)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.HAND,
                                               melee_damage=1,
                                               throw_damage=1)

class Arrow(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.ARROW,
                         name='Arrow',
                         glyph=')',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL,
                         fg=color.COLOR.CYAN)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.QUIVER,
                                               throw_damage=1)
        self.Group = component.Group(
                parent = self,
                unstack_name = 'Arrow',
                unstack_glyph = ')',
                stack_name = 'Arrow Stack',
                stack_glyph = '≡',
            )


class Fruit(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.FRUIT,
                         name='Fruit',
                         glyph='&',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL,
                         fg=color.COLOR.GREEN)
        self.Edible = component.Edible(self, nutrition=5)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.HAND,
                                               melee_damage=1,
                                               throw_damage=1)

class Wood(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.WOOD,
                         name='Wood',
                         glyph='#',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL,
                         fg=color.COLOR.YELLOW)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.HAND,
                                               melee_damage=1,
                                               throw_damage=1)
        self.Group = component.Group(parent = self,
                                     unstack_name = 'Wood',
                                     unstack_glyph = '#',
                                     stack_name = 'Wood Stack',
                                     stack_glyph = '#')

class ShortSword(e.Entity):
    #spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.SHORT_SWORD,
                         name='Short Sword',
                         glyph='/',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL,
                         fg=color.COLOR.GREY)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.HAND,
                                               melee_damage=2,
                                               throw_damage=1)

class Dart(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.DART,
                         name='Dart',
                         glyph=')',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL,
                         fg=color.COLOR.RED)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.QUIVER,
                                               throw_damage=1)
        self.Group = component.Group(parent = self,
                                     unstack_name = self.name,
                                     unstack_glyph = self.glyph,
                                     stack_name = self.name + ' Stack',
                                     stack_glyph = '≡')

class Gambeson(e.Entity):
    #spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.GAMBESON,
                         name='Gambeson',
                         glyph='[',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL,
                         fg=color.COLOR.WHITE)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.BODY,
                                               armor=1)

class BlowPipe(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BLOWPIPE,
                         name='BlowPipe',
                         glyph='|',
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL,
                         fg=color.COLOR.RED)
        self.ItemTraits = component.ItemTraits(itemtype=component.ItemType.HAND,
                                               melee_damage=0,
                                               throw_damage=0,
                                               melee_accuracy=0,
                                               throw_accuracy=30,
                                               throw_bonus_items=[typeid.TID.DART])


