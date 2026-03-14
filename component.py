import algo

class Stackable:
    '''
    Stackable component, entities will combine into the passed in type
    '''
    def __init__(self, stack):
        self.stack = stack
        '''Entity stacked form'''

    def get_stack(self):
        '''Returns the stacked form of the entity'''
        return self.stack()

class Stack:
    '''
    Stack component, if an entity is a stack of entities
    '''
    def __init__(self, unstack):
        self.unstack = unstack
        '''Unstacked single entity form'''
        self.amount = 0
        '''Keep track of amount of entities stacked'''
    
    def add_to_stack(self, am=1):
        '''Add to the amount of stacked entities'''
        self.amount += am

    def get_one(self):
        '''Unstack one entity and return the unstacked single form'''
        self.amount -= 1
        return self.unstack()

class Health:
    '''
    Health component, if an entity needs a health bar
    '''
    def __init__(self, health):
        self.maxhealth = health
        '''Maximum for the health bar'''
        self.currenthealth = health
        '''Counter for current health'''
        self.alive = True
        '''True if health bar is above 0'''

    def change_health(self, amount):
        '''
        Changes the health bar by an amount

        Returns true if health change causes death
        '''
        self.currenthealth += amount
        if self.alive and self.currenthealth <= 0:
            self.alive = False
            return True
        return False

class Brain:
    '''
    Brain component, if an entity needs to make decisions
    '''
    def __init__(self, sightrange, blockinglayer):
        self.sightrange = sightrange
        '''How far FOV will check'''
        self.blockinglayer = blockinglayer
        '''Highest level (exclusive) FOV will see through'''

    def get_action(self, level, mypos, myz, player, energy):
        '''Returns an action'''
        if player.z == myz:
            # only follow if player is on the same level
            pts = self.getFOV(level, mypos)
            if tuple([player.row,player.col]) in pts:
                return self.move_towards_pt(mypos, [player.row,player.col])
        return '.'
    
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
    
    def getFOV(self, level, mypos):
        '''Use FOV algorithm to get which points are visible'''
        grid = [[max([int(x.layer) for x in level.EntityLayer[r][c]]) if level.EntityLayer[r][c] else 0
                 for c in range(len(level.EntityLayer[r]))]
                    for r in range(len(level.EntityLayer))]
        return algo.RecursiveShadow(grid,
                               mypos,
                               self.sightrange,
                               int(self.blockinglayer))


