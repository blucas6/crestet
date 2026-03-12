
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
