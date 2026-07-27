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
    def __init__(self, sightrange, blockinglayer, attacks=[]):
        self.sightrange = sightrange
        '''How far FOV will check'''
        self.blockinglayer = blockinglayer
        '''Highest level (exclusive) FOV will see through'''
        self.attacks = attacks
        '''List of AttackType enums'''
        self.state = BrainState.IDLE
        self.mental_map = []
        self.objectmap = []
        self.levelrows = 0
        self.levelcols = 0
        self.fovmemory = FOVMemory.OBJECTS
        '''Decides the type of FOV'''

    def setup_mental(self, levelrows, levelcols):
        self.levelrows = levelrows
        self.levelcols = levelcols
        self.clear_memory()

    def clear_memory(self):
        '''Resets the mental map of the player'''
        self.mentalmap = [[[] for _ in range(self.levelcols)] for _ in range(self.levelrows)]
        self.objectmap = [[[] for _ in range(self.levelcols)] for _ in range(self.levelrows)]

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

    def update_mental_map(self, level, myrow, mycol, status):
        '''Updates the mental map of the player'''

        if not level:
            return

        # get FOV points for player
        pts = self.getFOV(level, [myrow,mycol], status)

        blind_pts = []
        if entity.StatusEffect.BLIND in status:
            blind_pts = utility.get_one_layer_pts((myrow, mycol), level.rows, level.cols)

        # optional types of FOV memory
        if self.fovmemory == FOVMemory.NOTHING:
            # always clear previous points
            self.mentalmap = [[[] for _ in range(len(level.EntityLayer[row]))]
                                    for row in range(len(level.EntityLayer))]
            for pt in pts:
                self.mentalmap[pt[0]][pt[1]] = level.EntityLayer[pt[0]][pt[1]]
        elif self.fovmemory == FOVMemory.OBJECTS:
            for r,row in enumerate(level.EntityLayer):
                for c,_ in enumerate(row):
                    # immediate fov view
                    if not entity.StatusEffect.BLIND in status and (r,c) in pts:
                        self.mentalmap[r][c] = level.EntityLayer[r][c]
                        maxlayer = utility.get_max_layer(level.EntityLayer[r][c])
                        # save only objects that are visible
                        if maxlayer < entity.Layer.BARREL_LAYER:
                            self.objectmap[r][c] = []
                            for ent in level.EntityLayer[r][c]:
                                if ent.layer == entity.Layer.OBJECT_LAYER or ent.layer == entity.Layer.STAIR_LAYER:
                                    self.objectmap[r][c].append(ent)
                    elif entity.StatusEffect.BLIND in status and [r,c] in blind_pts:
                        if myrow == r and mycol == c:
                            for ent in level.EntityLayer[r][c]:
                                if ent.name == 'Player':
                                    self.mentalmap[r][c] = [ent]
                        else:
                            self.mentalmap[r][c] = []
                            for ent in level.EntityLayer[r][c]:
                                if ent.layer == entity.Layer.MONSTER_LAYER:
                                    self.mentalmap[r][c].append(tower.Unknown())
                                elif ent.layer == entity.Layer.WALL_LAYER:
                                    self.mentalmap[r][c].append(ent)
                                elif ent.layer == entity.Layer.BARREL_LAYER:
                                    self.mentalmap[r][c].append(ent)
                                elif ent.layer == entity.Layer.OBJECT_LAYER:
                                    self.mentalmap[r][c].append(ent)
                    # memory view
                    elif self.mentalmap[r][c] and self.objectmap[r][c]:
                        # put back saved objects
                        self.mentalmap[r][c] = self.objectmap[r][c]
                    elif self.mentalmap[r][c]:
                        # seen before, but not in current FOV
                        save = []
                        for ent in self.mentalmap[r][c]:
                            if ent.layer == entity.Layer.WALL_LAYER:
                                save.append(ent)
                        self.mentalmap[r][c] = save
        elif self.fovmemory == FOVMemory.OBJECTS_BARRELS:
            for r,row in enumerate(level.EntityLayer):
                for c,_ in enumerate(row):
                    if (r,c) in pts:
                        self.mentalmap[r][c] = level.EntityLayer[r][c]
                    elif self.mentalmap[r][c]:
                        # seen before, but not in current FOV
                        # only add the object layer
                        self.mentalmap[r][c] = []
                        for ent in level.EntityLayer[r][c]:
                            if (ent.layer == entity.Layer.STAIR_LAYER or
                                ent.layer == entity.Layer.OBJECT_LAYER or
                                ent.layer == entity.Layer.BARREL_LAYER or
                                ent.layer == entity.Layer.WALL_LAYER):
                                self.mentalmap[r][c].append(ent)
        elif self.fovmemory == FOVMemory.EVERYTHING:
            # just add new seen points
            for pt in pts:
                self.mentalmap[pt[0]][pt[1]] = level.EntityLayer[pt[0]][pt[1]]

        # add light layer to FOV
        if not entity.StatusEffect.BLIND in status:
            for r,row in enumerate(level.LightLayer):
                for c,col in enumerate(row):
                    if col:
                        self.mentalmap[r][c] = level.EntityLayer[r][c]
