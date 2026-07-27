import color
import brain
import tower
import ability
import item
import utility
import config
import copy
import enum
import component
import entity as e
import logging

Logger = logging.getLogger(__name__)

class Player(e.Entity):
    def __init__(self):
        super().__init__(typeid=1,
                         name='Player',
                         glyph='@',
                         color=color.Color().white,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.LARGE)
        self.levelrows = 0
        '''Rows for mental map'''
        self.levelcols = 0
        '''Columns for mental map'''
        self.eyes = config.PLAYERFOV
        '''How far the FOV will check, also enables eye status effects'''
        self.blockinglayer = e.Layer.MONSTER_LAYER
        '''For FOV, highest level (exclusive) to see through'''
        self.speed = e.Speed.AVERAGE
        '''Speed component'''
        self.Health = component.Health(health=config.PLAYERHEALTH)
        '''Health component'''
        self.Brain = brain.Brain(self.eyes, self.blockinglayer)
        '''Player brain for game interactions'''
        self.Charge = component.Charge(self.speed)
        '''Player can run'''
        self.Leveling = component.Leveling()
        '''Player can level up'''
        self.Inventory = component.Inventory(autopickuplist=['Dart', 'Arrow', 'Rune'])
        '''Inventory component'''
        self.Combat = component.Combat()

    def init(self, levelrows, levelcols):
        '''Initialize player data'''
        self.Brain.setup_mental(levelrows, levelcols)
        self.Inventory.equip(ability.Fist())

    def on_placed(self, levelmanager, messager):
        '''
        Activates when an entity is placed on a square
        Checks the rest of the entities already on the square
        '''
        super().on_placed(levelmanager, messager)
        entitylist = levelmanager.Levels[self.z].EntityLayer[self.row][self.col]
        for ent in entitylist:
            # check to auto eat anything
            if hasattr(ent, 'Edible') and hasattr(self, 'Health'):
                ent.Edible.get_eaten(levelmanager, messager, self)

    def update_mental_map(self, curr_level):
        self.Brain.update_mental_map(curr_level, self.row, self.col, self.status)

