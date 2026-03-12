import heapq
import heapq
import logger

def debugGrid(grid, pts):
    for row in grid:
        logger.Logger.log(row)
    logger.Logger.log('-------------------')
    for r,row in enumerate(grid):
        line = '['
        for c,col in enumerate(row):
            if (r,c) in pts:
                line += 'X'
            else:
                line += str(col)
            if not c == len(row)-1:
                line += ', '
        line += ']'
        logger.Logger.log(line)
    logger.Logger.log('==========')

class Cell:
    '''A* cell object'''
    def __init__(self):
        self.parent_i = 0
        '''Parent cell's row index'''
        self.parent_j = 0
        '''Parent cell's column index'''
        self.f = float('inf')
        '''Total cost of the cell (g + h)'''
        self.g = float('inf')
        '''Cost from start to this cell'''
        self.h = 0
        '''Heuristic cost from this cell to destination'''

def is_valid(grid, row, col):
    '''Check if a cell is valid (within the grid)'''
    return ((row >= 0) and (row < len(grid)) and
            (col >= 0) and (col < len(grid[row])))

def is_unblocked(grid, row, col):
    '''Check if a cell is unblocked'''
    return grid[row][col] == 0

def is_destination(row, col, dest):
    '''Check if a cell is the destination'''
    return row == dest[0] and col == dest[1]

def calculate_h_value(row, col, dest):
    '''
    Calculate the heuristic value of a cell
    (Euclidean distance to destination)
    '''
    return ((row - dest[0]) ** 2 + (col - dest[1]) ** 2) ** 0.5

def trace_path(cell_details, dest):
    '''
    Trace the path from source to destination
    '''
    path = []
    row = dest[0]
    col = dest[1]

    # Trace the path from destination to source using parent cells
    while not (cell_details[row][col].parent_i == row 
               and cell_details[row][col].parent_j == col):
        path.append((row, col))
        temp_row = cell_details[row][col].parent_i
        temp_col = cell_details[row][col].parent_j
        row = temp_row
        col = temp_col

    # Add the source cell to the path
    path.append((row, col))
    # Reverse the path to get the path from source to destination
    path.reverse()
    return 1, path

def astar(grid, src, dest, debug=False):
    '''
    A* search algorithm

    return [ success_code, [list of points]]

    success codes:
        1 = success
        -1 = failure
        2 = invalid source/dest
        3 = blocked source/dest
        4 = already at destination
    '''

    # Check if the source and destination are valid
    if (not is_valid(grid, src[0], src[1]) or
        not is_valid(grid, dest[0], dest[1])):
        if debug:
            debugGrid(grid, [])
        return 2, []

    # Check if the source and destination are unblocked
    if (not is_unblocked(grid, src[0], src[1]) or not
        is_unblocked(grid, dest[0], dest[1])):
        if debug:
            debugGrid(grid, [])
        return 3, []

    # Check if we are already at the destination
    if is_destination(src[0], src[1], dest):
        if debug:
            debugGrid(grid, [])
        return 4, []

    # Initialize the closed list (visited cells)
    closed_list = [[False for _ in row] for row in grid]
    # Initialize the details of each cell
    cell_details = [[Cell() for _ in row] for row in grid]

    # Initialize the start cell details
    i = src[0]
    j = src[1]
    cell_details[i][j].f = 0
    cell_details[i][j].g = 0
    cell_details[i][j].h = 0
    cell_details[i][j].parent_i = i
    cell_details[i][j].parent_j = j

    # Initialize the open list (cells to be visited) with the start cell
    open_list = []
    heapq.heappush(open_list, (0.0, i, j))

    # Initialize the flag for whether destination is found
    found_dest = False

    # Main loop of A* search algorithm
    while len(open_list) > 0:
        # Pop the cell with the smallest f value from the open list
        p = heapq.heappop(open_list)

        # Mark the cell as visited
        i = p[1]
        j = p[2]
        closed_list[i][j] = True

        # For each direction, check the successors
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dir in directions:
            new_i = i + dir[0]
            new_j = j + dir[1]

            # If the successor is valid, unblocked, and not visited
            if (is_valid(grid, new_i, new_j) and
                is_unblocked(grid, new_i, new_j) and
                not closed_list[new_i][new_j]):

                # If the successor is the destination
                if is_destination(new_i, new_j, dest):
                    # Set the parent of the destination cell
                    cell_details[new_i][new_j].parent_i = i
                    cell_details[new_i][new_j].parent_j = j
                    # Trace and print the path from source to destination
                    code, points = trace_path(cell_details, dest)
                    if debug:
                        debugGrid(grid, points)
                    return code, points
                else:
                    # Calculate the new f, g, and h values
                    g_new = cell_details[i][j].g + 1.0
                    h_new = calculate_h_value(new_i, new_j, dest)
                    f_new = g_new + h_new

                    # If the cell is not in the open list or the new f value is smaller
                    if cell_details[new_i][new_j].f == float('inf') or cell_details[new_i][new_j].f > f_new:
                        # Add the cell to the open list
                        heapq.heappush(open_list, (f_new, new_i, new_j))
                        # Update the cell details
                        cell_details[new_i][new_j].f = f_new
                        cell_details[new_i][new_j].g = g_new
                        cell_details[new_i][new_j].h = h_new
                        cell_details[new_i][new_j].parent_i = i
                        cell_details[new_i][new_j].parent_j = j

    # If the destination is not found after visiting all cells
    if not found_dest:
        return -1, []

def testAStar():
    grid = [
        [0, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1, 0, 1, 0],
        [1, 0, 0, 1, 1, 1, 0, 1, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 1, 1],
        [0, 1, 1, 0, 0, 0, 1, 0, 0, 1]
    ]
    src = [8, 0]
    dest = [0, 0]
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            if [r,c] == src:
                print('S', end='')
            elif [r,c] == dest:
                print('D', end='')
            else:
                print(grid[r][c], end='')
        print()
    print('-----------')
    code, points = astar(grid, src, dest)
    if code == 1:
        print('Found destination')
    else:
        print(f'Failed -> {code}')
    print(points)
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            if [r,c] == src:
                print('S', end='')
            elif [r,c] == dest:
                print('D', end='')
            elif tuple([r,c]) in points:
                print('x', end='')
            else:
                print(grid[r][c], end='')
        print()

def dijkstra(grid: list, start: tuple, end: tuple, diagonals=True):
    rows, cols = len(grid), len(grid[0])
    heap = []

    # (total_cost, current_node, path_so_far)
    heapq.heappush(heap, (0, start, [start])) 
    visited = set()
    cost_so_far = {start: 0}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonals:
        directions.extend([(-1,-1), (1,1), (-1,1), (1,-1)])

    while heap:
        cost, (x, y), path = heapq.heappop(heap)

        if (x, y) == end:
            return path

        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)

            if 0 <= nx < rows and 0 <= ny < cols:
                new_cost = cost + grid[nx][ny]
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))

    return None

MULT = [
            [1,  0,  0, -1, -1,  0,  0,  1],
            [0,  1, -1,  0,  0, -1,  1,  0],
            [0,  1,  1,  0,  0, -1, -1,  0],
            [1,  0,  0,  1, -1,  0,  0, -1]
        ]

def RecursiveShadow(grid: list, pos: list, radius: int, blockingLayer: int=1,
                    debug=False):
    '''
    Returns a list of tuples that are viewable from the current position

    All points are viewable, including the blockingLayer value
    '''
    pts = set()
    pts.add((pos[0],pos[1]))
    for oct in range(8):
        castLight(grid, pos[1], pos[0], 1, 1.0, 0.0, radius,
                  MULT[0][oct], MULT[1][oct], MULT[2][oct], MULT[3][oct], pts,
                  blockingLayer)
    if debug:
        debugGrid(grid, pts)
    return pts

def castLight(grid, cx, cy, row, start, end, radius, xx, xy, yx, yy, pts,
              blockingLayer):
    if start < end:
        return
    radius_squared = radius*radius
    for j in range(row, radius+1):
        dx, dy = -j-1, -j
        blocked = False
        while dx <= 0:
            dx += 1
            X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
            l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
            if not (0 <= X < len(grid[0]) and 0 <= Y < len(grid)):
                continue
            if start < r_slope:
                continue
            elif end > l_slope:
                break
            else:
                if dx*dx + dy*dy < radius_squared:
                    pts.add((Y,X))
                if blocked:
                    if notValid(grid, X, Y, blockingLayer):
                        new_start = r_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if notValid(grid, X, Y, blockingLayer) and j < radius:
                        blocked = True
                        castLight(grid, cx, cy, j+1, start, l_slope, radius,
                                  xx, xy, yx, yy, pts, blockingLayer)
                        new_start = r_slope
        if blocked:
            break

def notValid(grid, x, y, blockingLayer):
    return (x < 0 or y < 0 or x >= len(grid[0]) or y >= len(grid)
            or grid[y][x] > blockingLayer)

def testDijkstras():
    grid = [
        [0,0,0,0,9,0],
        [0,2,9,9,9,0],
        [0,2,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,0,0,0,0]
    ]
    start = (5,3)
    end = (4,3)
    pts = dijkstra(grid, start, end)
    for r in grid:
        for c in r:
            print(c,end='')
        print()
    print('-----------')
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            if (r,c) in pts:
                print('x',end='')
            else:
                print(col,end='')
        print()

def testRecursiveShadow():
    grid = [
        [0,0,0,0,9,0],
        [0,2,9,9,9,0],
        [0,2,0,0,0,0],
        [0,0,0,0,0,0],
        [0,0,9,9,0,0],
        [0,0,0,9,0,0]
    ]
    start = (2,2)
    pts = RecursiveShadow(grid, start, 3, 1)
    print(pts)
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            if (r,c) == start:
                print('@', end='')
            else:
                print(col,end='')
        print()
    print('-----------')
    for r,row in enumerate(grid):
        for c,col in enumerate(row):
            # if (r,c) == start:
            #     print('@', end='')
            if (r,c) in pts:
                print('x',end='')
            else:
                print(col,end='')
        print()

if __name__ == '__main__':
    # testRecursiveShadow()
    # testDijkstras()
    testAStar()
