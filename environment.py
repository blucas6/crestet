import numpy as np
import logger
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
        self.obs_size = 6
        self.action_size = 5
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
        # Human: 7
        # Newt: 8
        # Jelly: 9
        self.current_action_mask = []
        self.movement_to_door = None
        self.movement_to_dark = None
        self.movement_to_monster = None
        self.movement_away_monster = None
        self.door_distance = np.inf

        self.opposite_action = {
            "8": "2",  # Up -> Down
            "2": "8",  # Down -> Up
            "4": "6",  # Left -> Right
            "6": "4",  # Right -> Left
            "7": "3",  # Up-Left -> Down-Right
            "3": "7",  # Down-Right -> Up-Left
            "9": "1",  # Up-Right -> Down-Left
            "1": "9"   # Down-Left -> Up-Right
        }

        # notation mapping
        self.action_to_coords = {
            "8": (-1, 0),
            "2": (1, 0),
            "4": (0, -1),
            "6": (0, 1),
            "7": (-1, -1),
            "9": (-1, 1),
            "1": (1, -1),
            "3": (1, 1)
        }

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

        # Health
        health = self.get_curr_health()[0] / config.PLAYERHEALTH
        
        # Compute Action Mask
        self.current_action_mask, player_coords, door_coords, self.movement_to_door, darkest_cell_coords, self.movement_to_dark, closest_monster_coords, closest_monster_id, self.movement_to_monster, self.movement_away_monster = self.graph_observation()

        # Door Dir + Distance
        door_vec = dark_vec = monster_vec = np.array([0,0])
        door_distance = dark_distance = monster_distance = -1
        
        # Monster ID
        if closest_monster_id is not None:
            if closest_monster_id == 8:
                monster_id = [1,0]
            else:
                monster_id = [0,1]
        else:
            monster_id = [0,0]
        
        if door_coords is not None:
            door_vec, door_distance = self.get_normalized_vector_and_distance(player_coords, door_coords)
        
        if darkest_cell_coords is not None:
            dark_vec, dark_distance = self.get_normalized_vector_and_distance(player_coords, darkest_cell_coords)

        if closest_monster_coords is not None:
            monster_vec, monster_distance = self.get_normalized_vector_and_distance(player_coords, closest_monster_coords)

        self.door_distance = door_distance

        obs = np.concatenate([[health], [door_distance], 
                              [dark_distance],
                              [monster_distance],
                              monster_id], )
        return obs
    
    def get_normalized_vector_and_distance(self, player_coords, target_coords):
        """
        Calculates the unit vector from player to target and the normalized distance
        based on a 20x10 grid size.
        
        player_coords: (row, col) or (y, x)
        target_coords: (row, col) or (y, x)
        """
        if player_coords is None or target_coords is None:
            # Return zeros if either coordinate is missing (e.g., no monster found)
            return np.array([0.0, 0.0]), 0.0
            
        # 1. Compute directional displacements
        # (target - player) points from player to the target
        dr = target_coords[0] - player_coords[0]
        dc = target_coords[1] - player_coords[1]
        
        displacement = np.array([dr, dc], dtype=np.float32)
        distance = np.linalg.norm(displacement)
        
        # 2. Compute the Unit Vector
        if distance > 0:
            unit_vector = displacement / distance
        else:
            unit_vector = np.array([0.0, 0.0]) # Player is standing exactly on the target
            
        # 3. Normalize distance by the maximum possible grid diagonal
        # Max diagonal for 20x10 grid = sqrt(20^2 + 10^2) = sqrt(500)
        max_diagonal = np.sqrt(20**2 + 10**2)
        normalized_distance = distance / max_diagonal
        
        return unit_vector, normalized_distance

    def find_nearest_dark_tile_coords(self, player_id=1, obstacle_ids=[2, 8, 9]):
        """Finds the closest dark cell (2) to the player whose path strictly 

        consists of only open floor (0) cells. Excludes map outer borders.
        """
        myobs_raw = self.get_player_fov()
        myobs = np.array(myobs_raw).reshape((10, 20, 10))
        
        # 1. Parse into a unified 2D structural grid
        # 0 = open floor, 1 = hard wall, 2 = dark cell
        grid = np.zeros((10, 20), dtype=int)
        
        is_wall_id = np.any(np.isin(myobs, obstacle_ids), axis=2)
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

    def get_next_action_astar(self, start_coord, target_coord, obstacle_ids=[2, 8, 9]):
        """Takes a start (row, col) and target (row, col), runs 8-way A*,
        treating known walls as obstacles while allowing movement through dark cells,
        and returns the next directional step action string.
        """
        if start_coord == target_coord:
            return None
        
        myobs_raw = self.get_player_fov()
        myobs = np.array(myobs_raw).reshape((10, 20, 10))
        
        # 1. True if the cell contains the wall_id
        is_wall_id = np.any(np.isin(myobs, obstacle_ids), axis=2)

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
        final = list(unique_coords)
        if final:
            return final
        else:
            return None
    
    def reset(self, new_seed=None):
        '''
        Reset the environment to start a brand new episode

        Returns the initial observation and an optional info dict
        '''
        if new_seed is None:
            new_seed = np.random.randint(0,1000)

        self.Game.reset(new_seed=new_seed)
        self.current_step = 0
        self.current_action_mask = []
        self.movement_to_door = None
        self.movement_to_dark = None
        self.movement_to_monster = None
        self.movement_away_monster = None
        self.door_distance = np.inf
        return self.get_observation(), {}

    def step(self, action):
        '''
        Takes in an int action and applies it to the environment

        Returns the next observation, the reward associated with this action, if
        the episode is complete or not, if maxsteps is reached, and optional
        info.
        '''
        game_action = self.agent_action_to_game(action)

        self.current_step += 1
        reward = 0
        done = False
        truncated = self.current_step >= self.maxsteps

        self.Game.game_loop(game_action)

        # Reward the agent for getting to the next level
        done = (np.abs(self.door_distance) < 0.01) or (self.get_curr_health()[0] <= 0)
        reward = 1 if (np.abs(self.door_distance) < 0.01) else 0 
        reward += 0.01 if action == 0 else 0

        return self.get_observation(), reward, done, truncated, {}

    def render(self):
        '''Renders the environment visually for evaluation purposes'''
        self.Game.render()

    def end(self):
        '''Close the game environment'''
        self.Game.end()

    def agent_action_to_game(self, action):
        if action == 0:
            return self.movement_to_door
        elif action == 1:
            return self.movement_to_dark
        elif action == 2:
            return '<'
        elif action == 3:
            return self.movement_to_monster
        elif action == 4:
            return self.movement_away_monster
    
    def get_action_mask(self):
        return self.current_action_mask
    
    def graph_observation(self):
        # Default mask
        mask = np.ones(self.action_size)

        # Player Coords
        player_coords = self.find_all_coordinates_of_target(target_id=1)
        if player_coords is not None:
            player_coords = player_coords[0]
        else:
            return mask, None, None, None, None, None, None, None, None, None
        
        # Action 0: Move to Door
        door_coords = self.find_all_coordinates_of_target(target_id=4)
        movement_to_door = None
        
        if door_coords is not None:
            door_coords = door_coords[0]
            movement_to_door = self.get_next_action_astar(player_coords, door_coords)
            mask[0] = (movement_to_door is not None)
        else:
            mask[0] = 0
        
        # Action 1: Move to Closest Dark Cell
        darkest_cell_coords = self.find_nearest_dark_tile_coords(player_id=1)
        movement_to_darkest = None
        if darkest_cell_coords is not None:
            movement_to_darkest = self.get_next_action_astar(player_coords, darkest_cell_coords)
            mask[1] = (movement_to_darkest is not None)
        else:
            mask[1] = 0

        # Action 2: Move Up Stair
        if door_coords is not None and np.all(player_coords == door_coords):
            mask = np.zeros(self.action_size)
            mask[2] = 1
        else:
            mask[2] = 0
        
        # Action 3: Move to Closest Monster
        newts = self.find_all_coordinates_of_target(target_id=8)
        jellys = self.find_all_coordinates_of_target(target_id=9)
        
        # Combine lists while keeping track of which ID belongs to which coordinate
        # Each element in all_monsters will be a tuple: (coords, monster_id)
        all_monsters = []
        movement_to_monster = None
        closest_monster_coords = None
        closest_monster_id = None
        if newts: 
            all_monsters.extend([(coords, 8) for coords in newts])
        if jellys: 
            all_monsters.extend([(coords, 9) for coords in jellys])
        
        if len(all_monsters) > 0:
            # Find the closest monster tuple based on Manhattan distance to the coords
            closest_monster_tuple = min(all_monsters, key=lambda item: abs(player_coords[0] - item[0][0]) + abs(player_coords[1] - item[0][1]))
            
            # Extract the coordinates and the specific ID
            closest_monster_coords = closest_monster_tuple[0]
            closest_monster_id = closest_monster_tuple[1]
            
            # Get path to the closest monster
            movement_to_monster = self.get_next_action_astar(player_coords, closest_monster_coords)
            mask[3] = (movement_to_monster is not None)
            
        else:
            mask[3] = 0
        
        # Action 4: Move Away from closest monster
        movement_away = None
        if movement_to_monster is not None:
            mask[4] = 1
            movement_away = self.opposite_action[movement_to_monster]
            myobs_raw = self.get_player_fov()
            myobs = np.array(myobs_raw).reshape((10, 20, 10))
            cell = tuple(np.array(player_coords) + np.array(self.action_to_coords[movement_away]))
            mask[4] = not np.any(myobs[cell] == 2)
        else:
            mask[4] = 0

        if not np.any(mask):
            mask[2] = 1

        return mask, player_coords, door_coords, movement_to_door, darkest_cell_coords, movement_to_darkest, closest_monster_coords, closest_monster_id, movement_to_monster, movement_away

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




