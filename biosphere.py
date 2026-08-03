import item
import component
import utility
import entity
import color
import logging
import enum

Logger = logging.getLogger(__name__)

class PlantStage(enum.Enum):
    SPROUT = 0
    GROWTH = 1
    FRUIT = 2


class Plant(entity.Entity):
    def __init__(self):
        super().__init__(typeid=80,
                         name='Plant',
                         glyph='.',
                         color=color.Color().green,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        #self.Edible = component.Edible(self, nutrition=5)
        self.PlantStage = PlantStage.SPROUT
        self.nutrients = 0
        self.sprout = 2
        self.growth = 6
        self.fruit = 10

    def on_init(self, rng):
        self.nutrients = rng.randint(0,11)
        self.advance()

    def update_state(self, levelmanager):
        self.advance()

    def change_to(self, plantstage):
        if plantstage == PlantStage.FRUIT:
            self.name = 'Fruit'
            self.glyph = '&'
            self.Edible = component.Edible(self, nutrition=5)
        elif plantstage == PlantStage.GROWTH:
            self.name = 'Growth'
            self.glyph = '"'
            self.Edible = None
        elif plantstage == PlantStage.SPROUT:
            self.name = 'Sprout'
            self.glyph = '*'
            self.Edible = None

    def advance(self, amount=1):
        self.nutrients += amount
        if self.nutrients > self.fruit:
            self.nutrients = self.fruit + 1

        if self.nutrients > self.fruit and self.PlantStage != PlantStage.FRUIT:
            self.change_to(PlantStage.FRUIT)
        elif self.nutrients > self.growth and self.PlantStage != PlantStage.GROWTH:
            self.change_to(PlantStage.GROWTH)
        elif self.nutrients > self.sprout and self.PlantStage != PlantStage.SPROUT:
            self.change_to(PlantStage.SPROUT)