import color
import config
import copy
import enum
import component
import entity as e

class FOVMemory(enum.Enum):
    '''
    Types of FOV Memory:
        0: remember nothing
        1: remember only the object layer
        2: remember everything
    '''
    NOTHING = 0,
    OBJECTS = 1,
    EVERYTHING = 2

class Player(e.Entity):
    def __init__(self):
        self.Health = component.Health(health=6)
        '''Health component'''
        self.mentalmap = []
        '''Entity map for output to the screen'''
        self.fovpoints = []
        '''Used for simple FOV'''
        self.fovmemory = FOVMemory.OBJECTS
        '''Decides the type of FOV the player gets'''
        self.sightrange = config.PLAYERFOV
        '''How far the FOV will check'''
        self.blockinglayer = e.Layer.MONST_LAYER
        '''For FOV, highest level (exclusive) to see through'''
        self.Brain = component.Brain(self.sightrange, self.blockinglayer)
        '''Player brain for game interactions'''
        #self.Inventory = Inventory()
        '''Inventory component'''
        self.speed = e.Speed.AVERAGE
        '''Speed component'''
        self.attackspeed = e.AttackSpeed.AVERAGE
        '''Attack speed'''
        self.throwspeed = e.AttackSpeed.AVERAGE
        #self.Charge = Charge(self.speed)
        '''Player can run'''
        super().__init__(name='Player',
                         glyph='@',
                         color=color.Color().white,
                         layer=e.Layer.MONST_LAYER,
                         size=e.Size.LARGE)

    def init(self, levelrows, levelcols):
        '''Initialize player data'''
        self.mentalmap = [[[] for _ in range(levelcols)] for _ in range(levelrows)]

    def update_mental_map(self, level):
        '''Updates the mental map of the player'''
        # get FOV points for player
        pts = self.Brain.getFOV(level, [self.row,self.col])

        # optional types of FOV memory
        if self.fovmemory == FOVMemory.NOTHING:
            # always clear previous points
            self.mentalmap = [[[] for _ in range(len(level.EntityLayer[row]))]
                                    for row in range(len(level.EntityLayer))]
        elif self.fovmemory == FOVMemory.EVERYTHING:
            # just add new seen points
            for pt in pts:
                self.mentalmap[pt[0]][pt[1]] = copy.deepcopy(
                                                    level.EntityLayer[pt[0]][pt[1]]
                                                    )
        elif self.fovmemory == FOVMemory.OBJECTS:
            for r,row in enumerate(level.EntityLayer):
                for c,col in enumerate(row):
                    if (r,c) in pts:
                        self.mentalmap[r][c] = copy.deepcopy(level.EntityLayer[r][c])
                    elif self.mentalmap[r][c]:
                        # seen before, but not in current FOV
                        # only add the object layer
                        self.mentalmap[r][c] = []
                        for entity in level.EntityLayer[r][c]:
                            if (entity.layer == e.Layer.OBJECT_LAYER or
                                entity.layer == e.Layer.WALL_LAYER):
                                self.mentalmap[r][c].append(entity)

        # add light layer to FOV
        for r,row in enumerate(level.LightLayer):
            for c,col in enumerate(row):
                if col:
                    self.mentalmap[r][c] = level.EntityLayer[r][c]




