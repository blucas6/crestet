import item
import component
import utility
import entity
import color
import logging
import enum

Logger = logging.getLogger(__name__)

class PlantStage(enum.IntEnum):
    '''Plant life stages'''
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
                         layer=entity.Layer.PLANT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.PlantStage = PlantStage.SPROUT
        '''Current plant stage'''
        self.nutrients = 0
        '''Current plant nutrients'''
        self.sprout = 10
        '''Level of nutrients to turn to a sprout'''
        self.growth = 80
        '''Level of nutrients to turn to a growth'''
        self.fruit = 100
        '''Level of nutrients to turn to a fruit'''
        self.decay = 150
        '''Level of nutrients to start decaying'''
        self.growth_glyphs = ['*', '"']
        '''Different growth glyphs'''
        self.growth_glyph = '*'
        '''Growth glyph'''
        self.sprout_glyphs = ['.', ',', '`']
        '''Different sprout glyphs'''
        self.sprout_glyph = '.'
        '''Sprout glyph'''

    def on_init(self, rng):
        '''When a plant is placed on the level'''
        self.nutrients = rng.randint(0, self.fruit)
        self.growth_glyph = self.growth_glyphs[rng.randint(0,len(self.growth_glyphs))-1]
        self.sprout_glyph = self.sprout_glyphs[rng.randint(0,len(self.sprout_glyphs))-1]
        self.advance(rng)

    def on_top(self, *_):
        '''When a plant is stepped on'''
        Logger.info(f'Plant ON TOP HOOK {self} {self.PlantStage}')
        if self.PlantStage >= PlantStage.GROWTH:
            self.nutrients = self.sprout
            self.change_to(PlantStage.SPROUT)

    def update_state(self, levelmanager):
        '''Update hook'''
        self.advance(levelmanager.RNG)

    def change_to(self, plantstage):
        '''Change to a different stage'''
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
        '''Get the equivalent stage depending on nutrient level'''
        if self.nutrients > self.decay:
            return PlantStage.DECAY
        if self.nutrients > self.fruit:
            return PlantStage.FRUIT
        if self.nutrients > self.growth:
            return PlantStage.GROWTH
        if self.nutrients > self.sprout:
            return PlantStage.SPROUT

    def advance(self, rng, amount=1):
        '''Add nutrients and check to change stage'''
        self.nutrients += amount

        stage = self.get_stage()
        if self.PlantStage != stage:
            if stage != PlantStage.FRUIT:
                self.change_to(stage)
            elif rng.randint(1,50) == 1:
                self.change_to(stage)
            else:
                self.nutrients -= amount
