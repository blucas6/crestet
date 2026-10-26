import entity as e
import utility
import color
import component
import typeid

class Corpse(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.CORPSE,
                         name='Corpse',
                         glyph='%',
                         color=color.Color().white,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.MEDIUM)
        self.ItemType = component.ItemType.HAND


class TurtleShell(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.TURTLE_SHELL,
                         name='Turtle Shell',
                         glyph='æ',
                         color=color.Color().grey,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.ItemType = component.ItemType.HAND

class Arrow(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.ARROW,
                         name='Arrow',
                         glyph=')',
                         color=color.Color().blue,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.ItemType = component.ItemType.QUIVER
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
                         color=color.Color().green,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.Edible = component.Edible(self, nutrition=5)

class Wood(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.WOOD,
                         name='Wood',
                         glyph='#',
                         color=color.Color().yellow,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.Attack = component.Attack(name='Wood', damage=1)
        self.ItemType = component.ItemType.HAND
        self.Group = component.Group(
                parent = self,
                unstack_name = 'Wood',
                unstack_glyph = '#',
                stack_name = 'Wood Stack',
                stack_glyph = '#',
            )

class Sword(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.SWORD,
                         name='Sword',
                         glyph='/',
                         color=color.Color().grey,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.Attack = component.Attack(name='Sword', damage=2)
        self.ItemType = component.ItemType.HAND

class Dart(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.DART,
                         name='Dart',
                         glyph=')',
                         color=color.Color().red,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.ItemType = component.ItemType.QUIVER
        self.Group = component.Group(
                parent = self,
                unstack_name = self.name,
                unstack_glyph = self.glyph,
                stack_name = self.name + ' Stack',
                stack_glyph = '≡',
            )

class Gambeson(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=typeid.TID.GAMBESON,
                         name='Gambeson',
                         glyph='[',
                         color=color.Color().white,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.ItemType = component.ItemType.BODY
        self.armor = 1
