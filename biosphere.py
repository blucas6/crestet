import item
import component
import utility
import entity
import color
import logging
import enum

Logger = logging.getLogger(__name__)

class PlantStage(enum.IntEnum):
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
        self.PlantStage = PlantStage.SPROUT
        self.nutrients = 0
        self.growth = 80
        self.fruit = 100

    def on_init(self, rng):
        self.nutrients = rng.randint(0, self.fruit)
        self.advance(rng)

    def on_top(self, *_):
        if self.PlantStage >= PlantStage.GROWTH:
            self.change_to(PlantStage.SPROUT)

    def update_state(self, levelmanager):
        self.advance(levelmanager.RNG)

    def change_to(self, plantstage):
        if plantstage == PlantStage.FRUIT:
            self.PlantStage = PlantStage.FRUIT
            self.name = 'Fruit'
            self.glyph = '&'
            self.Edible = component.Edible(self, nutrition=5)
        elif plantstage == PlantStage.GROWTH:
            self.PlantStage = PlantStage.GROWTH
            self.name = 'Growth'
            self.glyph = '*'
            self.Edible = None
        elif plantstage == PlantStage.SPROUT:
            self.PlantStage = PlantStage.SPROUT
            self.nutrients = 0
            self.name = 'Sprout'
            self.glyph = '.'
            self.Edible = None

    def advance(self, rng, amount=1):
        self.nutrients += amount
        if self.nutrients > self.fruit:
            self.nutrients = self.fruit + 1

        if (self.nutrients > self.fruit and
            self.PlantStage == PlantStage.GROWTH and
            rng.randint(1,100) == 1):
            self.change_to(PlantStage.FRUIT)
        elif self.nutrients > self.growth and self.PlantStage == PlantStage.SPROUT:
            self.change_to(PlantStage.GROWTH)