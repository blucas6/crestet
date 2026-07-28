import enum
import tower
import algo
import utility
import entity
import config
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

class BrainState(enum.Enum):
    '''Used to keep track of what state the brain is in'''
    IDLE = 0
    '''Do nothing'''
    MOVE = 1
    '''Move around randomly'''

class Brain:
    '''
    Brain component, if an entity needs to make decisions
    '''
    def __init__(self, sightrange, blockinglayer):
        self.sightrange = sightrange
        '''How far FOV will check'''
        self.blockinglayer = blockinglayer
        '''Highest level (exclusive) FOV will see through'''

    def getFOV(self, level, mypos, status):
        '''Use FOV algorithm to get which points are visible'''
        if not level:
            return []
        if entity.StatusEffect.BLIND in status:
            return []
        grid = [[max([int(x.layer) for x in level.EntityLayer[r][c]]) if level.EntityLayer[r][c] else 0
                 for c in range(len(level.EntityLayer[r]))]
                    for r in range(len(level.EntityLayer))]
        return algo.RecursiveShadow(grid,
                               mypos,
                               self.sightrange,
                               int(self.blockinglayer))

    def level_change(self, *_):
        '''Base case, brain child classes can override this trigger'''
        pass

class SimpleBrain(Brain):
    '''
    For monsters that can move around and attack
    '''
    def __init__(self, sightrange, blockinglayer, attacks=[]):
        super().__init__(sightrange, blockinglayer)

        self.attacks = attacks
        '''List of AttackType enums'''
        self.state = BrainState.IDLE
        '''Current brain state'''

    def get_action(self, currlevel, mypos, energy, rng, speed, status, inventory=None):
        '''Returns an action'''

        # not enough energy
        if energy < speed:
            return '5'

        pts = self.getFOV(currlevel, mypos, status)
        playerpos = self.find_player(currlevel, pts)

        # if the player is near, try to attack
        if playerpos:
            # go through possible attacks
            for attack in self.attacks:
                if (attack == entity.AttackType.THROW and
                    self.throw_attack_possible(mypos, playerpos, inventory)):
                    return self.throw_attack(mypos, playerpos)
                elif attack == entity.AttackType.MELEE:
                    return self.find_path(currlevel.EntityLayer, mypos, playerpos)

        # move around
        if self.state == BrainState.MOVE:
            actions = ['1', '2', '3', '4', '6', '7', '8', '9']
            rows = len(currlevel.EntityLayer)
            cols = len(currlevel.EntityLayer[0])
            # get which moves are legal
            possible_actions = []
            for key in actions:
                direction = utility.key_to_direction(key)
                r,c = mypos[0] + direction[0], mypos[1] + direction[1]
                if (r < len(currlevel.EntityLayer) and r >= 0 and
                    c < len(currlevel.EntityLayer[r]) and c >= 0):
                    if utility.get_max_layer(currlevel.EntityLayer[r][c]) < entity.Layer.MONSTER_LAYER:
                        possible_actions.append(key)
            # pick a random move
            if not possible_actions:
                return '.'
            if len(possible_actions) == 1:
                return possible_actions[0]
            move = possible_actions[rng.randint(0, len(possible_actions)-1)]
            if rng.randint(*config.MONS_IDLE) == 0:
                self.state = BrainState.IDLE
            return move

        # rest if not able to do anything
        if rng.randint(*config.MONS_IDLE) == 0:
            self.state = BrainState.MOVE
        return '.'

    def throw_attack_possible(self, mypos, playerpos, inventory):
        '''Check if the player is reachable by a throw'''
        if not inventory.has_ammo():
            return False
        drow = abs(mypos[0] - playerpos[0])
        dcol = abs(mypos[1] - playerpos[1])
        if drow == 0 or dcol == 0 or drow == dcol:
            return True
        return False

    def throw_attack(self, mypos, playerpos):
        '''Get the throw command'''
        d = self.move_towards_pt(mypos, playerpos)
        return 't' + str(d)

    def find_player(self, currlevel, pts):
        '''In a set of FOV points, check if the player exists'''
        for pt in pts:
            for ent in currlevel.EntityLayer[pt[0]][pt[1]]:
                if ent.name == 'Player':
                    return pt
        return None

    def find_path(self, entitylayer, mypos, playerpos):
        '''Finds a path using A* to the player position'''
        # create the 1,0 grid
        grid = [[1 if max([int(x.layer) for x in elist]) > entity.Layer.OBJECT_LAYER else 0
                    for elist in row]
                    for row in entitylayer]
        # set the source/dest positions to open
        grid[mypos[0]][mypos[1]] = 0
        grid[playerpos[0]][playerpos[1]] = 0
        # call A* to get a set of pts
        returncode, pts = algo.astar(grid, mypos, playerpos)
        if returncode != 1:
            Logger.error(f'Error: brain failed to find path -> {returncode}')
            return '.'
        return self.move_towards_pt(mypos, pts[1])
    
    def move_towards_pt(self, mypos, otherpos):
        '''Moves towards a point on the map'''
        if otherpos[0] > mypos[0]:
            if otherpos[1] > mypos[1]:
                return '3'
            elif otherpos[1] < mypos[1]:
                return '1'
            else:
                return '2'
        elif otherpos[0] < mypos[0]:
            if otherpos[1] > mypos[1]:
                return '9'
            elif otherpos[1] < mypos[1]:
                return '7'
            else:
                return '8'
        else:
            if otherpos[1] > mypos[1]:
                return '6'
            elif otherpos[1] < mypos[1]:
                return '4'
        return '.'

class FOVBrain(Brain):
    '''
    For entities that have memory
    '''
    def __init__(self, sightrange, blockinglayer):
        super().__init__(sightrange, blockinglayer)
        self.mentalmap = []
        '''Current view of the map'''
        self.objectmap = []
        '''All remembered objects (and barrels if set)'''
        self.wallmap = []
        '''All remembered walls'''
        self.fovmemory = FOVMemory.OBJECTS
        '''Decides the type of FOV'''

    def level_change(self, curr_level):
        '''Implement trigger to clear the current memory'''
        self.clear_memory(curr_level.rows, curr_level.cols)
        self.clear_objects(curr_level.rows, curr_level.cols)
        self.clear_walls(curr_level.rows, curr_level.cols)

    def clear_memory(self, rows, cols):
        '''Resets the map memory'''
        self.mentalmap = [[[] for _ in range(cols)] for _ in range(rows)]

    def clear_objects(self, rows, cols):
        '''Resets the object memory'''
        self.objectmap = [[[] for _ in range(cols)] for _ in range(rows)]

    def clear_walls(self, rows, cols):
        '''Resets the wall memory'''
        self.wallmap = [[[] for _ in range(cols)] for _ in range(rows)]

    def update_mental_map(self, level, myrow, mycol, status):
        '''Updates the mental map'''

        if not level:
            return

        # create these maps if they don't exist
        if not self.objectmap:
            self.clear_objects(level.rows, level.cols)
        if not self.wallmap:
            self.clear_walls(level.rows, level.cols)

        # clear the mental map except if remembering everything
        if self.fovmemory != FOVMemory.EVERYTHING or not self.mentalmap:
            self.clear_memory(level.rows, level.cols)

        # get the current FOV points
        fovpts = self.getFOV(level, [myrow,mycol], status)

        # get the current blind points if needed
        blindpts = []
        if entity.StatusEffect.BLIND in status:
            blindpts = utility.get_one_layer_pts((myrow, mycol), level.rows, level.cols)

        # optional types of FOV memory
        if self.fovmemory == FOVMemory.NOTHING:
            self.mental_map_load_FOV(level, fovpts, blindpts, status, myrow, mycol)
        elif self.fovmemory == FOVMemory.OBJECTS:
            self.mental_map_load_FOV(level, fovpts, blindpts, status, myrow, mycol)
            self.object_map_save(level, fovpts, blindpts, status)
            self.wall_map_save(level, fovpts, status)
        elif self.fovmemory == FOVMemory.OBJECTS_BARRELS:
            self.mental_map_load_FOV(level, fovpts, blindpts, status, myrow, mycol)
            self.object_map_save(level, fovpts, blindpts, status)
            self.wall_map_save(level, fovpts, status)
        elif self.fovmemory == FOVMemory.EVERYTHING:
            if entity.StatusEffect.BLIND in status:
                self.clear_memory(level.rows, level.cols)
            self.mental_map_load_FOV(level, fovpts, blindpts, status, myrow, mycol)

        # add light layer to FOV
        if not entity.StatusEffect.BLIND in status:
            for r,row in enumerate(level.LightLayer):
                for c,col in enumerate(row):
                    if col:
                        self.mentalmap[r][c] = level.EntityLayer[r][c]

        # add back objects/walls that are not in current fov
        for r,row in enumerate(self.objectmap):
            for c,col in enumerate(row):
                if self.mentalmap[r][c]:
                    continue
                if self.objectmap[r][c]:
                    self.mentalmap[r][c] = self.objectmap[r][c]
                if self.wallmap[r][c]:
                    self.mentalmap[r][c] = self.wallmap[r][c]

    def mental_map_load_FOV(self, level, fovpts, blindpts, status, myrow, mycol):
        '''Load the mental map with the current vision'''
        # normal vision
        if not entity.StatusEffect.BLIND in status:
            for r,c in fovpts:
                self.mentalmap[r][c] = level.EntityLayer[r][c]
        # blind
        else:
            for r,c in blindpts:
                # add player always
                if myrow == r and mycol == c:
                    for ent in level.EntityLayer[r][c]:
                        if ent.name == 'Player':
                            self.mentalmap[r][c] = [ent]
                # add other nearby objects as blurry
                else:
                    self.mentalmap[r][c] = []
                    for ent in level.EntityLayer[r][c]:
                        if ent.layer == entity.Layer.MONSTER_LAYER:
                            self.mentalmap[r][c].append(tower.UnknownEntity())
                        elif (ent.layer == entity.Layer.WALL_LAYER or
                            ent.layer == entity.Layer.BARREL_LAYER):
                            self.mentalmap[r][c].append(tower.UnknownStructure())
                        elif (ent.layer == entity.Layer.OBJECT_LAYER or 
                              ent.layer == entity.Layer.STAIR_LAYER):
                            self.mentalmap[r][c].append(ent)

    def object_map_save(self, level, fovpts, blindpts, status):
        '''Save objects within view'''
        pts = []
        if entity.StatusEffect.BLIND in status:
            pts = blindpts
        else:
            pts = fovpts
        for r,c in pts:
            maxlayer = utility.get_max_layer(level.EntityLayer[r][c])
            # save only objects/stairs that are visible
            if maxlayer < entity.Layer.BARREL_LAYER:
                self.objectmap[r][c] = []
                for ent in level.EntityLayer[r][c]:
                    if (ent.layer == entity.Layer.OBJECT_LAYER or
                        ent.layer == entity.Layer.STAIR_LAYER):
                        self.objectmap[r][c].append(ent)
            # save barrels only for that type of FOV
            elif self.fovmemory == FOVMemory.OBJECTS_BARRELS:
                self.objectmap[r][c] = []
                for ent in level.EntityLayer[r][c]:
                    if ent.layer == entity.Layer.BARREL_LAYER:
                        self.objectmap[r][c].append(ent)

    def wall_map_save(self, level, fovpts, status):
        '''Save walls in view'''
        if entity.StatusEffect.BLIND in status:
            return
        for r,c in fovpts:
            maxlayer = utility.get_max_layer(level.EntityLayer[r][c])
            # save only objects/stairs that are visible
            if maxlayer == entity.Layer.WALL_LAYER:
                self.wallmap[r][c] = []
                for ent in level.EntityLayer[r][c]:
                    if ent.layer == entity.Layer.WALL_LAYER:
                        self.wallmap[r][c].append(ent)