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
import typeid
import color

Logger = logging.getLogger(__name__)

class Player(e.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.PLAYER,
                         name='Player',
                         glyph='@',
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.LARGE,
                         fg=color.COLOR.WHITE)
        self.levelrows = 0
        '''Rows for mental map'''
        self.levelcols = 0
        '''Columns for mental map'''
        self.eyes = config.PLAYERFOV
        '''How far the FOV will check, also enables eye status effects'''
        self.blockinglayer = e.Layer.MONSTER_LAYER
        '''For FOV, highest level (exclusive) to see through'''
        self.speed = e.Speed.MEDIUM
        '''Speed component'''
        self.Health = component.Health(health=config.PLAYERHEALTH)
        '''Health component'''
        self.Brain = brain.FOVBrain(self.eyes, self.blockinglayer)
        '''Player brain for game interactions'''
        self.Charge = component.Charge(self.speed)
        '''Player can run'''
        self.Leveling = component.Leveling()
        '''Player can level up'''
        self.Inventory = component.Inventory(autopickuplist=['Dart', 'Arrow', 'Rune'])
        '''Inventory component'''
        self.Combat = component.Combat()

    def init(self):
        '''Initialize player data'''
        self.Inventory.equip(ability.Fist())

    def update_mental_map(self, curr_level):
        '''Update the mental map of the player'''
        self.Brain.update_mental_map(curr_level, self.row, self.col, self.status)

