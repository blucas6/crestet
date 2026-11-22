import config
import animation
import color
import dataclasses
import room
import biosphere
import wall
import inspect 
import rune
import item
import monster
import utility 
import copy
import entity
import algo
import tower
import json
import level
from dataclasses import dataclass
import logging

Logger = logging.getLogger(__name__)

@dataclass
class LevelLayout:
    '''Configuration data for each level'''
    floor: bool
    '''Generate the floor'''
    outer_walls: bool
    '''Generate the outer walls'''
    upstair: bool
    '''Generate an upstairs'''
    downstair: bool
    '''Generate a downstairs'''
    min_walls: int
    '''Minimum amount of walls to place inside'''
    min_barrels: int
    '''Minimum amount of barrels on the level'''
    lights: bool
    '''Generate lights'''
    items: int
    '''Minimum amount of items on the level'''
    runes: int
    '''Minimum amount of runes on the level'''
    mons: bool
    '''If there are monsters on the level'''
    plants: int
    rooms: int

    upstair_pos: tuple = ()
    '''Location of the upstairs on the level'''
    downstair_pos: tuple = ()
    '''Location of the downstairs on the level'''
    all_rooms: list[room.Room] = dataclasses.field(default_factory=list)

class Generator:
    '''Reads from a config file to build all level objects'''
    def __init__(self):
        self.levelrows = 0
        '''How many rows in a level'''
        self.levelcols = 0
        '''How many columns in a level'''
        self.total_levels = 0
        '''Total levels in the game'''
        self.level_layouts: list[LevelLayout] = []
        '''List of all LevelLayout objects'''
        self.light_amount = 0
        '''How many lights to generate in each level'''
        self.wall_shapes = {}
        '''Wall shapes for inner wall generation'''
        self.monster_classes = []
        '''Collection of monster classes'''
        self.wall_classes = []
        '''Collection of wall classes'''
        self.spawn_items = []
        '''Collection of item classes'''
        self.chest_items = []
        self.rune_classes = []
        '''Collection of rune classes'''
        self.all_pts = []
        '''All points in the level'''

    def load_classes(self):
        '''Gather all object classes from files'''
        self.monster_classes = [
            obj for name,obj in inspect.getmembers(monster, inspect.isclass)
            if obj.__module__ == monster.__name__ and hasattr(obj, 'difficulty')
        ]
        self.wall_classes = [
            obj for name,obj in inspect.getmembers(wall, inspect.isclass)
            if obj.__module__ == wall.__name__
        ]
        self.spawn_items = [
            obj for name,obj in inspect.getmembers(item, inspect.isclass)
            if obj.__module__ == item.__name__ and hasattr(obj, 'spawn')
        ]
        self.chest_items = [
            obj for name,obj in inspect.getmembers(item, inspect.isclass)
            if obj.__module__ == item.__name__ and hasattr(obj, 'chest_value')
        ]
        self.rune_classes = [
            obj for name,obj in inspect.getmembers(rune, inspect.isclass)
            if obj.__module__ == rune.__name__
        ]
        Logger.info(f'Classes Loaded: {self.monster_classes}')
        Logger.info(f'Classes Loaded: {self.wall_classes}')
        Logger.info(f'Classes Loaded: {self.spawn_items}')
        Logger.info(f'Classes Loaded: {self.chest_items}')
        Logger.info(f'Classes Loaded: {self.rune_classes}')

    def load_config(self, levelrows, levelcols):
        '''Read the config file and load the level layout objects'''
        self.level_layouts = []
        self.levelrows = levelrows
        self.levelcols = levelcols
        self.all_pts = utility.get_pts(self.levelrows, self.levelcols)
        try:
            data = None
            with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
                data = json.load(jfile)

            # set up the generator class members
            self.total_levels = data['total_levels']
            self.light_amount = data['light_amount']
            self.wall_shapes = data['wall_shapes']

            # load each level config
            levellayout = LevelLayout(**data['0'])
            self.level_layouts.append(levellayout)

            # if no level was specified, use the previous level config
            for ix in range(1,self.total_levels):
                if str(ix) in data:
                    levelgen = LevelLayout(**data[str(ix)])
                self.level_layouts.append(copy.deepcopy(levelgen))
            
        except Exception as ex:
            Logger.error(f'Generator parsing error: {ex}')
            raise

    def generate_levels(self, levelmanager: level.LevelManager, rng):
        '''Go through each level layout and set up the level'''

        levelmanager.totallevels = self.total_levels

        for z,level_layout in enumerate(self.level_layouts):
            # keep track of stair positions
            upstair_pos = []
            downstair_pos = []
            # add level to level manager list before building the level
            currlevel = level.Level(rows=self.levelrows, cols=self.levelcols, z=z)
            levelmanager.Levels.append(currlevel)

            if level_layout.floor:
                self.generate_floor(levelmanager, currlevel, rng)
            if level_layout.outer_walls:
                self.generate_outer_walls(levelmanager, currlevel, rng)
            if level_layout.rooms > 0:
                gen_rooms = self.generate_rooms(levelmanager, currlevel, level_layout.rooms, rng)
                level_layout.all_rooms = gen_rooms
            if level_layout.min_walls > 0:
                self.generate_walls(levelmanager, currlevel, level_layout.min_walls, level_layout.all_rooms, rng)
            if level_layout.min_barrels > 0:
                self.generate_barrels(levelmanager, currlevel, level_layout.min_barrels, level_layout.all_rooms, rng)
            if level_layout.mons:
                self.generate_mons(levelmanager, currlevel, 0, currlevel.LevelDifficulty.max, rng)
            if level_layout.items > 0:
                self.generate_items(levelmanager, currlevel, level_layout.items, rng)
            if level_layout.runes > 0:
                self.generate_runes(levelmanager, currlevel, level_layout.runes, rng)
            if level_layout.plants > 0:
                self.generate_plants(levelmanager, currlevel, level_layout.plants, rng)
            if level_layout.lights:
                self.generate_lights(levelmanager, currlevel, level_layout.all_rooms, rng)
            if level_layout.upstair:
                # save the upstairs position to the following level's downstairs position
                upstair_pos = self.generate_upstair(levelmanager, currlevel, level_layout.all_rooms, rng)
                if z+1 < len(self.level_layouts):
                    self.level_layouts[z+1].downstair_pos = upstair_pos
            if level_layout.downstair:
                downstair_pos = self.generate_downstair(levelmanager, currlevel, level_layout, rng)
            # clear path before any items are placed
            if z == config.PLAYERZ:
                if level_layout.upstair:
                    Logger.info(f'Clearing path for player')
                    # make path for player to upstair
                    self.generate_clear_path(levelmanager, currlevel, config.PLAYERPOS, upstair_pos, level_layout.all_rooms, rng)
            if upstair_pos and downstair_pos:
                self.generate_clear_path(levelmanager, currlevel, upstair_pos, downstair_pos, level_layout.all_rooms, rng)
            for theroom in level_layout.all_rooms:
                if theroom.door_pos:
                    if z == config.PLAYERZ:
                        self.generate_clear_path(levelmanager, currlevel, config.PLAYERPOS, theroom.door_pos, level_layout.all_rooms, rng)
                    else:
                        self.generate_clear_path(levelmanager, currlevel, downstair_pos, theroom.door_pos, level_layout.all_rooms, rng)
            # make sure player can be placed, even after placing all items down
            if z == config.PLAYERZ:
                levelmanager.add_to_level(tower.Floor(), config.PLAYERPOS, currlevel.z, self, rng, overwrite=True)
        Logger.info(f'----- FINISHED LEVEL GENERATION -----')

    def generate_floor(self, levelmanager: level.LevelManager, currlevel: level.Level, rng):
        '''Adds floors to the entity array'''
        for r in range(self.levelrows):
            for c in range(self.levelcols):
                levelmanager.add_to_level(tower.Floor(), [r,c], currlevel.z, self, rng, overwrite=True)

    def generate_outer_walls(self, levelmanager: level.LevelManager, currlevel: level.Level, rng):
        '''Adds surrounding walls to the entity array'''
        for r in range(self.levelrows):
            for c in range(self.levelcols):
                if r == 0 or c == 0 or r == self.levelrows-1 or c == self.levelcols-1:
                    wall_piece = self.get_wall_piece(rng)
                    levelmanager.add_to_level(wall_piece, [r,c], currlevel.z, self, rng, overwrite=True)

    def generate_upstair(self, levelmanager: level.LevelManager, currlevel: level.Level, all_rooms, rng):
        '''Places an upstairs in a random spot, returns the placement'''
        pts = copy.copy(self.all_pts)
        for room in all_rooms:
            for pt in room.pts:
                pts.remove(pt)
        r,c = utility.get_random_pt(rng, pts)
        levelmanager.add_to_level(tower.StairUp(), [r,c], currlevel.z, self, rng, overwrite=True)
        Logger.info(f'Placed UPSTAIR z:{currlevel.z}: {(r,c)}')
        return (r,c)
    
    def generate_downstair(self, levelmanager: level.LevelManager, currlevel: level.Level,
                           levellayout: LevelLayout, rng):
        '''Places the downstairs at the designated spot, returns the placement'''
        if not levellayout.downstair_pos:
            Logger.error(f'ERROR: downstair position is empty! z:{currlevel.z}')
            return ()
        levelmanager.add_to_level(tower.StairDown(),
                                  levellayout.downstair_pos,
                                  currlevel.z,
                                  self,
                                  rng,
                                  overwrite=True)
        return levellayout.downstair_pos

    def generate_clear_path(self, levelmanager:level.LevelManager, currlevel:level.Level, a, b, all_rooms, rng):
        '''Creates a floor path between points a -> b'''
        if not a or not b:
            Logger.error(f'Error: Clearing a path between {a}->{b} cannot be None!')
            return
        grid = [[max([ent.layer for ent in elist]) for elist in row]
                    for row in currlevel.EntityLayer]
        for theroom in all_rooms:
            for pt in theroom.pts:
                grid[pt[0]][pt[1]] = entity.Layer.WALL_LAYER + 10
        pts = algo.dijkstra(grid, tuple(a), tuple(b), diagonals=False)
        Logger.info(f'Clear Path ({currlevel.z}): {a} -> {b}\n{pts}')
        if pts:
            for pt in pts:
                maxlayer = max([x.layer for x in currlevel.EntityLayer[pt[0]][pt[1]]])
                if maxlayer >= entity.Layer.WALL_LAYER:
                    levelmanager.add_to_level(tower.Floor(), pt, currlevel.z, self, rng, overwrite=True)

    def generate_walls(self, levelmanager:level.LevelManager, currlevel:level.Level, minwalls, all_rooms, rng):
        '''
        Generates walls on the level using predetermined shapes
        Minimum walls counts how many wall spaces need to be covered in the level
        '''
        wallsplaced = 0
        attempt = 0
        # go through until minimum wall amount was reached or max tries
        pts = copy.copy(self.all_pts)
        while wallsplaced < minwalls and attempt < config.MAX_RETRIES and pts:
            attempt += 1
            idx = rng.randint(0,len(pts)-1)
            pt = pts.pop(idx)
            # grab a shape and rotate it
            shape = self.wall_shapes[rng.randint(0,len(self.wall_shapes)-1)]
            times = rng.randint(0,3)
            for _ in range(times):
                shape = [list(row) for row in zip(*shape[::-1])]
            for sr,srows in enumerate(shape):
                for sc,scols in enumerate(srows):
                    if not scols:
                        continue

                    place_at = [pt[0]+sr,pt[1]+sc]

                    if self.in_any_rooms(place_at, all_rooms):
                        continue

                    wall_piece = self.get_wall_piece(rng)

                    if not levelmanager.is_entity_pos_valid(currlevel, wall_piece, place_at):
                        continue

                    if levelmanager.add_to_level(wall_piece, place_at, currlevel.z, self, rng):
                        wallsplaced += 1
                        if wallsplaced >= minwalls:
                            return

        Logger.warning(f'WALL GEN MAX RETRIES')

    def generate_barrels(self, levelmanager, currlevel, min_barrels, all_rooms, rng):
        '''Add barrels to the level'''
        barrels_placed = 0
        attempt = 0
        pts = copy.copy(self.all_pts)
        while barrels_placed < min_barrels and attempt < config.MAX_RETRIES and pts:
            attempt += 1
            idx = rng.randint(0,len(pts)-1)
            pt = pts.pop(idx)
            shape = self.wall_shapes[rng.randint(0,len(self.wall_shapes)-1)]
            times = rng.randint(0,3)
            for _ in range(times):
                shape = [list(row) for row in zip(*shape[::-1])]
            for sr,srows in enumerate(shape):
                for sc,scols in enumerate(srows):
                    if not scols:
                        continue
                    place_at = [pt[0]+sr, pt[1]+sc]
                    if self.in_any_rooms(place_at, all_rooms):
                        continue
                    barrel = tower.Barrel()
                    if not levelmanager.is_entity_pos_valid(currlevel, barrel, place_at):
                        continue
                    if levelmanager.add_to_level(barrel, place_at, currlevel.z, rng, self):
                        barrels_placed += 1
            if barrels_placed >= min_barrels:
                return
        Logger.warning(f'BARREL GEN MAX RETRIES')

    def generate_lights(self, levelmanager:level.LevelManager, currlevel:level.Level, all_rooms, rng):
        '''Add lights to the level'''
        pts = copy.copy(self.all_pts)
        for theroom in all_rooms:
            for pt in theroom.pts:
                pts.remove(pt)
        for _ in range(self.light_amount):
            r,c = utility.get_random_pt(rng, pts)
            _,myentity  = utility.get_max_entity(currlevel.EntityLayer[r][c])
            valid = all([False if type(ent) == tower.Light else True for ent in currlevel.EntityLayer[r][c]])
            if myentity.layer < entity.Layer.WALL_LAYER and valid:
                light = tower.Light()
                levelmanager.add_to_level(light, (r,c), currlevel.z, rng, self)

    def generate_mons(self, levelmanager: level.LevelManager, currlevel: level.Level, starting_difficulty, level_difficulty, rng):
        '''Add monsters to the level'''

        '''
        for _ in range(1):
            r = rng.randint(1,self.levelrows-1)
            c = rng.randint(1,self.levelcols-1)
            levelmanager.place_entity(currlevel.z, monster.Human(), (r,c))
        '''
        all_mons = [m for m in self.monster_classes if m.difficulty <= level_difficulty]
        attempt = 0
        while starting_difficulty < level_difficulty and attempt < config.MAX_RETRIES:
            attempt += 1
            Logger.info(f'Attempt mons gen: {attempt} difficulty: {starting_difficulty} ({level_difficulty})')
            r,c = utility.get_random_pt(rng, self.all_pts)
            n = rng.randint(0, len(all_mons)-1)
            new_mon = all_mons[n]()
            if not levelmanager.is_entity_pos_valid(currlevel, new_mon, (r,c)):
                continue
            if levelmanager.add_to_level(new_mon, (r,c), currlevel.z, self, rng):
                starting_difficulty += new_mon.difficulty
                Logger.info(f'Adding new mon to level: {new_mon}')
                self.generate_pack_mons(levelmanager, currlevel, all_mons[n], (r,c), rng)
        if attempt >= config.MAX_RETRIES:
            Logger.warning('Generate mons max retries!')

    def generate_pack_mons(self, levelmanager, currlevel, mon, pos, rng):
        '''Generate pack monsters based on pack leader'''

        if not hasattr(mon, 'pack') or not hasattr(mon, 'packtype'):
            return

        packmons = [m for m in self.monster_classes if m.__name__ in mon.packtype]
        if not packmons:
            Logger.warning(f'Monster pack list empty!')
            return

        for ix in range(mon.pack):
            attempt = 0
            genpts = utility.generate_surrounding_pts(rng)
            while attempt < config.MAX_RETRIES:
                attempt += 1
                if len(packmons) == 1:
                    n = 0
                else:
                    n = rng.randint(0, len(packmons)-1)
                new_mon = packmons[n]()
                dx,dy = next(genpts, (None,None))
                if not dx or not dy:
                    break
                r = pos[0]+dx
                c = pos[1]+dy
                if not levelmanager.is_entity_pos_valid(currlevel, new_mon, (r,c)):
                    continue
                if levelmanager.add_to_level(new_mon, (r,c), currlevel.z, self, rng):
                    Logger.info(f'Adding pack mon to level: {new_mon}')
                    break
            if attempt >= config.MAX_RETRIES:
                Logger.warning('Generate pack mons max retries!')

    def generate_mon_amount(self, levelmanager, currlevel, starting_difficulty, level_difficulty, fixed_amount, fovpoints, rng):
        '''Add monsters to level by a certain amount'''
        generated_amount = 0
        all_mons = [m for m in self.monster_classes if m.difficulty <= level_difficulty]
        attempt = 0
        while (starting_difficulty < level_difficulty and
               attempt < config.MAX_RETRIES and
               generated_amount < fixed_amount):
            attempt += 1
            Logger.info(f'Attempt mons gen: {attempt} difficulty: {starting_difficulty} ({level_difficulty})')
            pt = utility.get_random_pt(rng, self.all_pts, invalidpts=fovpoints)
            r = pt[0]
            c = pt[1]
            n = rng.randint(0, len(all_mons)-1)
            new_mon = all_mons[n]()
            if not levelmanager.is_entity_pos_valid(currlevel, new_mon, (r,c)):
                continue
            if levelmanager.add_to_level(new_mon, (r,c), currlevel.z, self, rng):
                starting_difficulty += new_mon.difficulty
                generated_amount += 1
                Logger.info(f'Adding new mon to level: {new_mon}')
                self.generate_pack_mons(levelmanager, currlevel, all_mons[n], (r,c), rng)
        if attempt >= config.MAX_RETRIES:
            Logger.warning('Generate mons max retries!')

    def generate_items(self, levelmanager: level.LevelManager, currlevel: level.Level, item_amount, rng):
        '''Add items to the level'''
        attempt = 0
        while item_amount > 0 and attempt < config.MAX_RETRIES:
            r,c = utility.get_random_pt(rng, self.all_pts)
            new_item = None
            n = rng.randint(0, len(self.spawn_items)-1)
            new_item = self.spawn_items[n]()
            if not levelmanager.is_entity_pos_valid(currlevel, new_item, (r,c)):
                continue
            if levelmanager.add_to_level(new_item, (r,c), currlevel.z, self, rng):
                item_amount -= 1

    def generate_runes(self, levelmanager: level.LevelManager, currlevel: level.Level, rune_amount, rng):
        attempt = 0
        while rune_amount > 0 and attempt < config.MAX_RETRIES:
            r,c = utility.get_random_pt(rng, self.all_pts)
            n = rng.randint(0, len(self.rune_classes)-1)
            new_rune = self.rune_classes[n]()
            if not levelmanager.is_entity_pos_valid(currlevel, new_rune, (r,c)):
                continue
            if levelmanager.add_to_level(new_rune, (r,c), currlevel.z, self, rng):
                rune_amount -= 1

    def generate_key(self, levelmanager, currlevel, rng, animator, key_amount=1):
        pts = copy.copy(self.all_pts)
        attempt = 0
        while attempt < config.MAX_RETRIES and pts and key_amount > 0:
            attempt += 1
            idx = rng.randint(0,len(pts)-1)
            point = pts.pop(idx)
            r = point[0]
            c = point[1]
            key = room.Key()
            if not levelmanager.is_entity_pos_valid(currlevel, key, (r,c)):
                continue
            if levelmanager.add_to_level(key, (r,c), currlevel.z, self, rng):
                key_amount -= 1
                frames = []
                delays = []
                for row in range(r):
                    frame = [['' for _ in grow] for grow in currlevel.EntityLayer]
                    for rx in range(row):
                        frame[rx][c] = '▓'
                    frames.append(frame)
                    delays.append(config.DROP_ANIM_DELAY)
                frame = [['' for _ in grow] for grow in currlevel.EntityLayer]
                frame[r][c] = '*'
                if utility.inbounds(frame, r-1, c-1):
                    frame[r-1][c-1] = '\\'
                if utility.inbounds(frame, r-1, c+1):
                    frame[r-1][c+1] = '/'
                if utility.inbounds(frame, r+1, c-1):
                    frame[r+1][c-1] = '/'
                if utility.inbounds(frame, r+1, c+1):
                    frame[r+1][c+1] = '\\'
                frames.append(frame)
                delays.append(config.DROP_ANIM_DELAY)
                origin = [0, 0, currlevel.z, 0]
                anim = animation.Animation(pos=origin,
                                           frames=frames,
                                           delays=delays,
                                           fg=color.COLOR.BRIGHT_YELLOW,
                                           always_visible=True)
                animator.queueUp(levelmanager, anim)

    def generate_plants(self, levelmanager: level.LevelManager, currlevel: level.Level, plant_amount, rng):
        plants = 0
        attempt = 0
        pts = copy.copy(self.all_pts)
        while plants < plant_amount and attempt < config.MAX_RETRIES and pts:
            attempt += 1
            idx = rng.randint(0,len(pts)-1)
            pt = pts.pop(idx)
            first_pad = utility.get_one_layer_pts(pt, self.levelrows, self.levelcols, shape='cross')
            for pos in first_pad:
                second_pad = utility.get_one_layer_pts(pos, self.levelrows, self.levelcols, shape='cross')
                for pos2 in second_pad:
                    plant_present = False
                    for ent in currlevel.EntityLayer[pos2[0]][pos2[1]]:
                        if ent.layer == entity.Layer.PLANT_LAYER:
                            plant_present = True
                    if plant_present:
                        continue
                    if rng.randint(1,3) == 1:
                        plant = biosphere.Plant()
                        if not levelmanager.is_entity_pos_valid(currlevel, plant, pos2):
                            continue
                        if levelmanager.add_to_level(plant, pos2, currlevel.z, self, rng):
                            plants += 1
                        if plants >= plant_amount:
                            return
        Logger.warning(f'PLANT GEN MAX RETRIES')

    def generate_rooms(self, levelmanager, currlevel, room_chance, rng):
        if rng.randint(1,100) > room_chance:
            return []
        gen_rooms = []
        rooms = 0
        attempt = 0
        pts = [[self.levelrows-1,0], [0,self.levelcols-1], [self.levelrows-1,self.levelcols-1]]
        if currlevel.z != 0:
            pts.append([0,0])
        while rooms < 1 and attempt < config.MAX_RETRIES and pts:
            attempt += 1
            idx = rng.randint(0,len(pts)-1)
            origin = pts.pop(idx)
            min_size = 4
            max_size = 7

            row_size = rng.randint(min_size, max_size)
            col_size = rng.randint(min_size, max_size)

            if origin[0] > self.levelrows/2:
                origin[0] = origin[0] - row_size
            if origin[1] > self.levelcols/2:
                origin[1] = origin[1] - col_size
            
            theroom = room.Room(origin, row_size, col_size)
            theroom.place_room(levelmanager, currlevel, rng, self)
            gen_rooms.append(theroom)
            rooms += 1
        return gen_rooms

    def get_wall_piece(self, rng):
        '''Return a random wall'''
        return self.wall_classes[rng.randint(0, len(self.wall_classes)-1)]()

    def in_any_rooms(self, pt, all_rooms):
        for theroom in all_rooms:
            if theroom.inroom(pt):
                return True
        return False
    
    def get_chest_items(self, rng, max_value=1):
        all_items = [i for i in self.chest_items if i.chest_value <= max_value]
        for i in self.chest_items:
            Logger.info(f'{i}')
            Logger.info(f'{i.chest_value} <= {max_value}')
        attempt = 0
        value = 0
        chest_bag = []
        while value < max_value and attempt < config.MAX_RETRIES:
            n = rng.randint(0, len(all_items)-1)
            bag_item = all_items[n]()
            value += bag_item.chest_value
            chest_bag.append(bag_item)
            Logger.info(f'Chest generation adding: {bag_item}')
        return chest_bag

