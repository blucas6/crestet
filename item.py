import entity as e
import color
import component

class DartStack(e.Entity):
    def __init__(self):
        super().__init__(
            name='Dart Stack',
            glyph='≡',
            color=color.Color().red,
            layer=e.Layer.OBJECT_LAYER,
            size=e.Size.VERY_SMALL)
        self.Stack = component.Stack(Dart)

class Dart(e.Entity):
    def __init__(self):
        super().__init__(name='Dart',
                         glyph=')',
                         color=color.Color().red,
                         layer=e.Layer.OBJECT_LAYER,
                         size=e.Size.VERY_SMALL)
        self.Stackable = component.Stackable(DartStack)
