import color
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

class FOVMemory(enum.Enum):
    '''
    Types of FOV Memory:
        0: remember nothing
        1: remember only the object layer
        2: remmeber only the objects and barrels
        3: remember everything
    '''
    NOTHING = 0,
    OBJECTS = 1,
    OBJECTS_BARRELS = 2
    EVERYTHING = 3

class Player(e.Entity):
    def __init__(self):
        super().__init__(typeid=1,
                         name='Player',
                         glyph='@',
                         color=color.Color().white,
                         layer=e.Layer.MONSTER_LAYER,
                         size=e.Size.LARGE)
        self.mentalmap = []
        '''Entity map for output to the screen'''
        self.objectmap = []
        '''Entity map for remembered objects'''
        self.levelrows = 0
        '''Rows for mental map'''
        self.levelcols = 0
        '''Columns for mental map'''
        self.fovpoints = []
        '''Used for simple FOV'''
        self.fovmemory = FOVMemory.OBJECTS
        '''Decides the type of FOV the player gets'''
        self.sightrange = config.PLAYERFOV
        '''How far the FOV will check'''
        self.blockinglayer = e.Layer.MONSTER_LAYER
        '''For FOV, highest level (exclusive) to see through'''
        self.speed = e.Speed.AVERAGE
        '''Speed component'''
        self.Health = component.Health(health=config.PLAYERHEALTH)
        '''Health component'''
        self.Brain = component.Brain(self.sightrange, self.blockinglayer)
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
        self.levelrows = levelrows
        self.levelcols = levelcols
        self.clear_memory()
        self.Inventory.equip(ability.Fist())

    def clear_memory(self):
        '''Resets the mental map of the player'''
        self.mentalmap = [[[] for _ in range(self.levelcols)] for _ in range(self.levelrows)]
        self.objectmap = [[[] for _ in range(self.levelcols)] for _ in range(self.levelrows)]

    def update_mental_map(self, level):
        '''Updates the mental map of the player'''

        if not level:
            return

        # get FOV points for player
        pts = self.Brain.getFOV(level, [self.row,self.col])

        # optional types of FOV memory
        if self.fovmemory == FOVMemory.NOTHING:
            # always clear previous points
            self.mentalmap = [[[] for _ in range(len(level.EntityLayer[row]))]
                                    for row in range(len(level.EntityLayer))]
            for pt in pts:
                self.mentalmap[pt[0]][pt[1]] = level.EntityLayer[pt[0]][pt[1]]
        elif self.fovmemory == FOVMemory.OBJECTS:
            for r,row in enumerate(level.EntityLayer):
                for c,col in enumerate(row):
                    # immediate fov view
                    if (r,c) in pts:
                        self.mentalmap[r][c] = level.EntityLayer[r][c]
                        maxlayer = utility.get_max_layer(level.EntityLayer[r][c])
                        # save only objects that are visible
                        if maxlayer < e.Layer.BARREL_LAYER:
                            self.objectmap[r][c] = []
                            for entity in level.EntityLayer[r][c]:
                                if entity.layer == e.Layer.OBJECT_LAYER:
                                    self.objectmap[r][c].append(entity)
                    # memory view
                    elif self.mentalmap[r][c] and self.objectmap[r][c]:
                        self.mentalmap[r][c] = self.objectmap[r][c]
                    elif self.mentalmap[r][c]:
                        # seen before, but not in current FOV
                        # only add the object layer
                        self.mentalmap[r][c] = []
                        maxlayer = utility.get_max_layer(level.EntityLayer[r][c])
                        for entity in level.EntityLayer[r][c]:
                            # walls get saved
                            # objects get saved, but not if covered by barrels
                            if (entity.layer == e.Layer.WALL_LAYER or 
                                entity.layer == e.Layer.STAIR_LAYER or
                                (entity.layer == e.Layer.OBJECT_LAYER and
                                  maxlayer != e.Layer.BARREL_LAYER)):
                                self.mentalmap[r][c].append(entity)
        elif self.fovmemory == FOVMemory.OBJECTS_BARRELS:
            for r,row in enumerate(level.EntityLayer):
                for c,col in enumerate(row):
                    if (r,c) in pts:
                        self.mentalmap[r][c] = level.EntityLayer[r][c]
                    elif self.mentalmap[r][c]:
                        # seen before, but not in current FOV
                        # only add the object layer
                        self.mentalmap[r][c] = []
                        for entity in level.EntityLayer[r][c]:
                            if (entity.layer == e.Layer.STAIR_LAYER or
                                entity.layer == e.Layer.OBJECT_LAYER or
                                entity.layer == e.Layer.BARREL_LAYER or
                                entity.layer == e.Layer.WALL_LAYER):
                                self.mentalmap[r][c].append(entity)
        elif self.fovmemory == FOVMemory.EVERYTHING:
            # just add new seen points
            for pt in pts:
                self.mentalmap[pt[0]][pt[1]] = level.EntityLayer[pt[0]][pt[1]]

        # add light layer to FOV
        for r,row in enumerate(level.LightLayer):
            for c,col in enumerate(row):
                if col:
                    self.mentalmap[r][c] = level.EntityLayer[r][c]

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

    def on_zchange(self):
        self.clear_memory()



