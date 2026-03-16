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
        for ent in level.EntityLayer[self.row][self.col]:
            if ent.id == self.id:
                continue
            # if there is a stackable entity on the ground, replace it with the stack
            if hasattr(ent, 'Stackable') and ent.Stackable.stack == type(self):
                self.Stack.add_to_stack()
                index = ent.idx
                levelmanager.remove_entity(self)
                level.EntityLayer[self.row][self.col][index] = self 
                self.set_pos(self.row, self.col, level.z, index)
                return
            # if there is a stack on the ground, combine with it
            elif hasattr(ent, 'Stack') and type(self) == type(ent):
                levelmanager.remove_entity(self)
                ent.Stack.add_to_stack(self.Stack.amount)
                return

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
        level = levelmanager.Levels[self.z]
        for ent in level.EntityLayer[self.row][self.col]:
            if ent.id == self.id:
                continue
            # if there is already a stack on the ground, make sure it has the same unstack type
            # and stack with it
            if hasattr(ent, 'Stack') and ent.Stack.unstack == type(self):
                ent.Stack.add_to_stack()
                levelmanager.remove_entity(self)
                return
            # no stack yet, but there is another stackable entity of the same type
            elif type(self) == type(ent):
                # replace the entity in the list with a stack of 2
                stack = ent.Stackable.get_stack()
                stack.Stack.add_to_stack(2)
                index = ent.idx
                level.EntityLayer[self.row][self.col][index] = stack
                stack.set_pos(self.row, self.col, level.z, index)
                levelmanager.remove_entity(self)
                return

