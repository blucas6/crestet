import entity as e
import color
import component

class Wood(e.Entity):
    def __init__(self):
        super().__init__(name='Wood',
                         glyph='#',
                         color=color.Color().yellow,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.Attack = component.Attack(name='Wood', damage=1)
        self.ItemType = component.ItemType.HAND

class Bite(e.Entity):
    def __init__(self):
        super().__init__(name='Bite',
                         glyph='?',
                         color=color.Color().magenta,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.Attack = component.Attack(name='Bite', damage=1)
        self.ItemType = component.ItemType.ABILITY

class Sword(e.Entity):
    def __init__(self):
        super().__init__(name='Sword',
                         glyph='/',
                         color=color.Color().blue,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.SMALL)
        self.Attack = component.Attack(name='Sword', damage=2)
        self.ItemType = component.ItemType.HAND

class DartStack(e.Entity):
    def __init__(self):
        super().__init__(
            name='Dart Stack',
            glyph='≡',
            color=color.Color().red,
            layer=e.Layer.OBJECT_LAYER,
            size=e.Size.VERY_SMALL)
        self.Stack = component.Stack(Dart)
        self.ItemType = component.ItemType.QUIVER

    def on_placed(self, levelmanager):
        level = levelmanager.Levels[self.z]
        entitylist = level.EntityLayer[self.row][self.col]
        self.Stack.check_entitylist(self, entitylist)

class Dart(e.Entity):
    def __init__(self):
        super().__init__(name='Dart',
                         glyph=')',
                         color=color.Color().red,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.Stackable = component.Stackable(DartStack)
        self.ItemType = component.ItemType.QUIVER

    def on_placed(self, levelmanager):
        '''Check new square for other darts or dart stacks'''
        level = levelmanager.Levels[self.z]
        entitylist = level.EntityLayer[self.row][self.col]
        self.Stackable.check_entitylist(self, entitylist)

