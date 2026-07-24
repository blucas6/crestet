import entity as e
import color
import component

class Arrow(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=18,
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
    spawn = True
    def __init__(self):
        super().__init__(typeid=10,
                         name='Fruit',
                         glyph='&',
                         color=color.Color().green,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.Edible = component.Edible(self, nutrition=5)

class Wood(e.Entity):
    def __init__(self):
        super().__init__(typeid=11,
                         name='Wood',
                         glyph='#',
                         color=color.Color().yellow,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.Attack = component.Attack(name='Wood', damage=1)
        self.ItemType = component.ItemType.HAND

class Sword(e.Entity):
    spawn = True
    def __init__(self):
        super().__init__(typeid=13,
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
        super().__init__(typeid=15,
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

