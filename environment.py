import numpy as np
import game
import config
import heapq
from collections import deque

class Environment:
    def __init__(self, seed=None, display=False, timing=False):
        '''
        Initialize the environment

        At a minimum needs to have self.obs_size and self.action_size and
        maxsteps. Obs size represents the total length of an observation.
        Action size represents the number of discrete actions possible in the
        environment.
        '''
        self.obs_size = 2
        self.action_size = 3
        self.maxsteps = 100
        self.current_step = 0
        self.np_random = np.random.default_rng()
        self.Game = game.Game(seed=seed,
                              msgblocking=False,
                              usedisplay=display,
                              timing=timing)
        
        # Action To String Game Action
        # 1, 2, 3, 4, 6, 7, 8, 9, <, >
        # 2, 4, 6, 8, <, >
        # 1: LEFT DOWN
        # 2: DOWN
        # 3: RIGHT DOWN
        # 4: LEFT
        # 5: NONE
        # 6: RIGHT
        # 7: UP LEFT
        # 8: UP
        # 9: UP RIGHT

        # ABSTRACT ACTIONS
        # Move to Door
        # Move to Closest Dark Cell
        # <
        # >

        # Type IDs
        # Nothing: 0
        # Player: 1
        # Wall: 2
        # Floor: 3
        # Stair Up: 4
        # Stair Down: 5
        # Light: 6

    def start(self):
        '''Start the environment'''
        try:
            self.Game.start()
        except Exception as ex:
            print(f'Failed to start the game environment!!\n {ex}')
            raise

    def get_observation(self):
        '''Returns a 1d np array of size "obs_size"'''
        # myobs = self.get_level_observation()
        # myobs = self.get_curr_inventory()
        
        obs = np.zeros(2)
        return obs

    def find_nearest_dark_tile_coords(self, player_id=1, wall_id=2):
        """Finds the closest dark cell (2) to the player whose path strictly 

        consists of only open floor (0) cells. Excludes map outer borders.
        """
        myobs_raw = self.get_player_fov()
        myobs = np.array(myobs_raw).reshape((10, 20, 10))
        
        # 1. Parse into a unified 2D structural grid
        # 0 = open floor, 1 = hard wall, 2 = dark cell
        grid = np.zeros((10, 20), dtype=int)
        
        is_wall_id = np.any(myobs == wall_id, axis=2)
        is_dark_tile = np.all(myobs == 0, axis=2)
        
        grid[is_wall_id] = 1
        grid[is_dark_tile] = 2
        
        # 2. Locate Player position
        player_indices = np.argwhere(myobs == player_id)
        if len(player_indices) == 0:
            return None
        start = tuple(player_indices[0][:2])
        
        # 3. Setup 8-way BFS path-length search
        neighbors = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
        queue = deque([(start, 0)])
        visited = {start}
        
        best_dark_tile = None
        min_path_distance = float('inf')
        
        while queue:
            current, dist = queue.popleft()
            
            # Since BFS expands uniformly, if our current depth meets or exceeds
            # a previously found valid target distance, we can safely terminate.
            if dist >= min_path_distance:
                break
                
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                
                # Boundary check within the 10x20 space
                if 0 <= neighbor[0] < 10 and 0 <= neighbor[1] < 20:
                    if neighbor in visited:
                        continue
                        
                    tile_value = grid[neighbor[0]][neighbor[1]]
                    
                    # Target Rule: Must be a dark cell (2) and not an outer edge border
                    if tile_value == 2:
                        if 0 < neighbor[0] < 9 and 0 < neighbor[1] < 19:
                            actual_dist = dist + 1
                            if actual_dist < min_path_distance:
                                min_path_distance = actual_dist
                                best_dark_tile = neighbor
                        continue # Path stops here; do not queue or look past a 2
                        
                    # Obstacle Rule: Path cannot pass through a wall (1)
                    if tile_value == 1:
                        continue
                        
                    # Path Rule: If it's a 0, we can expand our path through it
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
                    
        return best_dark_tile

    def get_next_action_astar(self, start_coord, target_coord, wall_id=2):
        """Takes a start (row, col) and target (row, col), runs 8-way A*,
        treating known walls as obstacles while allowing movement through dark cells,
        and returns the next directional step action string.
        """
        if start_coord == target_coord:
            return None
        
        myobs_raw = self.get_player_fov()
        myobs = np.array(myobs_raw).reshape((10, 20, 10))
        
        # --- MODIFIED GRID LOGIC ---
        # A cell is a wall ONLY if it explicitly contains the wall_id.
        # If it's all zeros (dark), it stays 0 (walkable) so A* can plan a path into it.
        # --- FIXED GRID LOGIC ---
        # 1. True if the cell contains the wall_id
        is_wall_id = np.any(myobs == wall_id, axis=2)
        # 2. True if the cell is completely dark (all zeros)
        is_dark_tile = np.all(myobs == 0, axis=2)
        
        # The pathfinder treats BOTH explicit walls and fog/dark cells as un-walkable
        grid = np.zeros((10, 20), dtype=int)
        grid[is_wall_id | is_dark_tile] = 1
        grid[start_coord] = 0
        grid[target_coord] = 0
        
        # Inline A* setup
        def heuristic(a, b):
            return max(abs(a[0] - b[0]), abs(a[1] - b[1])) # Chebyshev 8-way
            
        neighbors = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
        close_set = set()
        came_from = {}
        gscore = {start_coord: 0}
        fscore = {start_coord: heuristic(start_coord, target_coord)}
        oheap = []
        
        heapq.heappush(oheap, (fscore[start_coord], start_coord))
        path = None
        
        while oheap:
            current = heapq.heappop(oheap)[1]
            
            if current == target_coord:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                break
                
            close_set.add(current)
            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                
                if 0 <= neighbor[0] < 10 and 0 <= neighbor[1] < 20:
                    # Target tile itself is allowed even if it has a blocking property
                    if grid[neighbor[0]][neighbor[1]] == 1 and neighbor != target_coord:
                        continue
                else:
                    continue
                    
                if neighbor in close_set:
                    continue
                    
                tentative_g_score = gscore[current] + 1
                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [x[1] for x in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, target_coord)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
                    
        if path and len(path) > 0:
            next_tile = path[0]
            dr = next_tile[0] - start_coord[0]
            dc = next_tile[1] - start_coord[1]
            
            # Numpad notation mapping
            if (dr, dc) == (-1, 0):  return "8"
            if (dr, dc) == (1, 0):   return "2"
            if (dr, dc) == (0, -1):  return "4"
            if (dr, dc) == (0, 1):   return "6"
            if (dr, dc) == (-1, -1): return "7"
            if (dr, dc) == (-1, 1):  return "9"
            if (dr, dc) == (1, -1):  return "1"
            if (dr, dc) == (1, 1):   return "3"
        grid[start_coord] = 3
        grid[target_coord] = 2
        
        return None
    
    def find_all_coordinates_of_target(self, target_id):
        """Scans the 3D grid and returns a list of (row, col) tuples 

        for every cell that contains the specified target_id.
        """
        # Reshape the raw observation to your 3D grid format
        myobs_raw = self.get_player_fov()
        myobs = np.array(myobs_raw).reshape((10, 20, 10))
        
        # Find all 3D indices where the value matches the target_id
        matching_indices = np.argwhere(myobs == target_id)
        
        # Extract just the unique (row, col) positions, dropping the 3rd axis index
        # We use a set to avoid duplicate coordinates if an ID appears twice in the same cell
        unique_coords = {tuple(idx[:2]) for idx in matching_indices}
        
        # Return as a list of tuples
        return list(unique_coords)
    
    def reset(self, new_seed=None):
        '''
        Reset the environment to start a brand new episode

        Returns the initial observation and an optional info dict
        '''
        self.Game.reset(new_seed=new_seed)
        self.current_step = 0
        return self.get_observation(), {}

    def step(self, action):
        '''
        Takes in an int action and applies it to the environment

        Returns the next observation, the reward associated with this action, if
        the episode is complete or not, if maxsteps is reached, and optional
        info.
        '''
        action = self.agent_action_to_game(action)
        
        if action is None:
            action = '<'
        self.current_step += 1
        reward = 0
        done = False
        truncated = self.current_step >= self.maxsteps

        self.Game.game_loop(action)

        # Reward the agent for getting to the next level
        reward =  (self.get_curr_z()[0] == 1)
        done = (self.get_curr_z()[0] == 10)

        return self.get_observation(), reward, done, truncated, {}

    def render(self):
        '''Renders the environment visually for evaluation purposes'''
        self.Game.render()

    def end(self):
        '''Close the game environment'''
        self.Game.end()

    def agent_action_to_game(self, action):
        # Player Coords
        player_coords = self.find_all_coordinates_of_target(target_id=1)[0]
        
        # Action 0: Move to Door
        if action == 0:
            door_coords = self.find_all_coordinates_of_target(target_id=4)[0]
            movement_to_door = self.get_next_action_astar(player_coords, door_coords,wall_id=2)
            return movement_to_door
        
        # Action 1: Move to Closest Dark Cell
        elif action == 1:
            darkest_cell_coords = self.find_nearest_dark_tile_coords(player_id=1, wall_id=2)
            movement_to_darkest = self.get_next_action_astar(player_coords, darkest_cell_coords, wall_id=2)
            return movement_to_darkest
        
        # Action 2: '<'
        elif action == 2:
            return '<'
        
        # Action 3: '>'
        elif action == 3:
            return '>'
        
    def action_mask(self):
        # Default mask
        mask = np.ones(self.action_size)

        # Player Coords
        player_coords = self.find_all_coordinates_of_target(target_id=1)[0]
        
        # Action 0: Move to Door
        door_coords = self.find_all_coordinates_of_target(target_id=4)
        
        if len(door_coords) > 0:
            movement_to_door = self.get_next_action_astar(player_coords, door_coords[0], wall_id=2)
            mask[0] = (movement_to_door is not None)
        else:
            mask[0] = 0
        
        # Action 1: Move to Closest Dark Cell
        darkest_cell_coords = self.find_nearest_dark_tile_coords(player_id=1, wall_id=2)
        if darkest_cell_coords is not None:
            movement_to_darkest = self.get_next_action_astar(player_coords, darkest_cell_coords, wall_id=2)
            mask[1] = (movement_to_darkest is not None)
        else:
            mask[1] = 0

        if len(door_coords) > 0 and player_coords == door_coords[0]:
            mask = np.zeros(self.action_size)
            mask[2] = 1

        return mask

    def get_player_fov(self):
        '''Flattens the player view of the level into a 1D array'''
        entity_layer = self.Game.LevelManager.Player.mentalmap
        obs = np.array([col[ix].typeid if ix < len(col) else 0 for row in entity_layer for col in row for ix in range(config.LEVELMAX_ENTITIES)])
        return obs

    def get_level_observation(self):
        '''Flattens the level entities into a 1D array'''
        currlevel = self.Game.LevelManager.get_curr_level()
        if not currlevel:
            return np.empty(config.LEVELROWS * config.LEVELCOLS * config.LEVELMAX_ENTITIES)
        entity_layer = currlevel.EntityLayer
        obs = [col[ix].typeid if ix < len(col) else 0 for row in entity_layer for col in row for ix in range(config.LEVELMAX_ENTITIES)]
        return obs

    def get_curr_z(self):
        '''Returns the current level z index as a 1D array'''
        return np.array([self.Game.LevelManager.currentz])

    def get_curr_health(self):
        '''Returns the current player health as a 1D array'''
        return np.array([self.Game.LevelManager.Player.Health.currenthealth])

    def get_curr_inventory(self):
        '''Returns the current player inventory as a 1D array'''
        inventory = self.Game.LevelManager.Player.Inventory.get_all_items()
        obs = [item.typeid for item in inventory if item]
        return np.array(obs)

    def get_curr_turn(self):
        '''Returns the current turn as a 1D array'''
        return np.array(self.Game.turn)




