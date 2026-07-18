import logger
import algo
import entity

ONE_LAYER_CIRCLE = [(1,-1),(1,0),(1,1),(0,-1),(0,0),(0,1),(-1,-1),(-1,0),(-1,1)]

def get_one_layer_pts(pos, rows, cols):
    '''
    Pass in a position to return all points around that position
    '''
    pts = []
    for r,c in ONE_LAYER_CIRCLE:
        row = pos[0] + r
        col = pos[1] + c
        if row > -1 and col > -1 and row < rows and col < cols:
            pts.append([row,col])
    return pts

def key_to_direction(key):
    return ONE_LAYER_CIRCLE[int(key)-1]

def get_max_entity(entitylist):
    '''Returns the index and the entity with the largest layer'''
    return max(enumerate(entitylist), key=lambda x: x[1].layer)

def get_new_pos(currpos, key):
    '''Pass a position and a direction key to get a new position'''
    return currpos[0] + ONE_LAYER_CIRCLE[key-1][0],currpos[1] + ONE_LAYER_CIRCLE[key-1][1]

def find_last_position(direction_key, start_row, start_col, entitylayer):
    '''
    Returns the final position of an object traveling in a direction
    It will stop inside a monster or barrel
    It will stop before a wall
    '''
    direction = ONE_LAYER_CIRCLE[int(direction_key)-1]
    objr = start_row
    objc = start_col

    while True:
        r,c = objr + direction[0], objc + direction[1]
        if entitylayer:
            maxlayer = max([x.layer for x in entitylayer[r][c]])
            if (maxlayer == entity.Layer.MONST_LAYER or
                maxlayer == entity.Layer.BARREL_LAYER):
                objr, objc = r, c
                break
            elif maxlayer == entity.Layer.WALL_LAYER:
                break
        objr, objc = r, c
    return objr,objc

def get_max_layer(entitylist):
    return max([int(x.layer) for x in entitylist])

def get_path_pts(entitylayer, start_row, start_col, end_row, end_col):
    # construct a grid of [0-1] (makes sure path to end point is valid)
    grid = [[1 if get_max_layer(elist) > entity.Layer.MONST_LAYER
             else 0
            for elist in row]
            for row in entitylayer]
    returncode, pts = algo.astar(grid, (start_row,start_col), (end_row,end_col))
    if returncode != 1:
        logger.Logger.log(f'Error: failed to find path -> {returncode}')
        return grid, []
    return grid, pts
