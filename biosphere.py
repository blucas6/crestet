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
    DECAY = 3

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
        self.sprout = 10
        self.growth = 80
        self.fruit = 100
        self.decay = 150
        self.growth_glyphs = ['*', '"']
        self.growth_glyph = '*'
        self.sprout_glyphs = ['.', ',', '`']
        self.sprout_glyph = '.'

    def on_init(self, rng):
        self.nutrients = rng.randint(0, self.fruit)
        self.growth_glyph = self.growth_glyphs[rng.randint(0,len(self.growth_glyphs))-1]
        self.sprout_glyph = self.sprout_glyphs[rng.randint(0,len(self.sprout_glyphs))-1]
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
            self.glyph = self.growth_glyph
            self.Edible = None
        elif plantstage == PlantStage.SPROUT:
            self.PlantStage = PlantStage.SPROUT
            self.name = 'Sprout'
            self.glyph = self.sprout_glyph
            self.color = color.Color().green
            self.Edible = None
        elif plantstage == PlantStage.DECAY:
            self.PlantStage = PlantStage.DECAY
            self.name = 'Ripe Fruit'
            self.glyph = '&'
            self.color = color.Color().grey
            self.Edible = component.Edible(self, nutrition=1)
            self.nutrients = 0

    def get_stage(self):
        if self.nutrients > self.decay:
            return PlantStage.DECAY
        if self.nutrients > self.fruit:
            return PlantStage.FRUIT
        if self.nutrients > self.growth:
            return PlantStage.GROWTH
        if self.nutrients > self.sprout:
            return PlantStage.SPROUT

    def advance(self, rng, amount=1):
        self.nutrients += amount

        stage = self.get_stage()
        if self.PlantStage != stage:
            if stage != PlantStage.FRUIT:
                self.change_to(stage)
            elif rng.randint(1,50) == 1:
                self.change_to(stage)
            else:
                self.nutrients -= amount
