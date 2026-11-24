import entity
import typeid
import color
import utility
import wall
import logging
import tower
import component
import item

Logger = logging.getLogger(__name__)

class Key(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.KEY,
                         name='Key',
                         glyph='{',
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL,
                         fg=color.COLOR.YELLOW)
        self.ItemTraits = component.ItemTraits(
                itemtype=component.ItemType.NOEQUIP)

class Chest(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BED,
                         name='Chest',
                         glyph='±',
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.MEDIUM,
                         fg=color.COLOR.YELLOW)
        self.bag = []
        '''Bag is a list of items the chest contains'''

    def update_state(self, levelmanager, rng):
        '''Update the chest color'''
        if self.bag:
            self.fg = color.COLOR.YELLOW
        else:
            self.fg = color.COLOR.GREY

    def on_init(self, rng, levelmanager, generator):
        '''Fill chest with items'''
        self.bag = generator.get_chest_items(rng, self.z+1)
        self.update_state(levelmanager, rng)

    def on_top(self, entity, levelmanager, rng, generator):
        '''Spill items if the entity carries a key'''
        if not hasattr(entity, 'Inventory'):
            return
        Logger.info(f'Chest on top trigger')
        if self.bag:
            if entity.Inventory.has_key():
                key = entity.Inventory.get_key()
                currlevel = levelmanager.Levels[self.z]
                for pt in utility.generate_surrounding_pts(rng):
                    if not self.bag:
                        Logger.info(f'chest empty')
                        break
                    chest_item = self.bag[-1]
                    r = pt[0] + self.row
                    c = pt[1] + self.col
                    if not levelmanager.is_entity_pos_valid(currlevel, chest_item, (r,c)):
                        continue
                    maxlayer = utility.get_max_layer(currlevel.EntityLayer[r][c])
                    if maxlayer < entity.layer.STAIR_LAYER:
                        if levelmanager.add_to_level(chest_item, (r,c), currlevel.z, generator, rng):
                            Logger.info(f'chest placed {chest_item}')
                            self.bag.pop()
            self.update_state(levelmanager, rng)

class Bed(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.BED,
                         name='Bed',
                         glyph='¬',
                         layer=entity.Layer.BARREL_LAYER,
                         size=entity.Size.MEDIUM,
                         fg=color.COLOR.CYAN)
        self.Breakable = component.Breakable(max_dmg=1, smashed_item=item.Wood())

class Dresser(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.DRESSER,
                         name='Dresser',
                         glyph='ʭ',
                         layer=entity.Layer.BARREL_LAYER,
                         size=entity.Size.MEDIUM,
                         fg=color.COLOR.YELLOW)
        self.Breakable = component.Breakable(max_dmg=1, smashed_item=item.Wood())

class Room:
    def __init__(self, origin, row_size, col_size):
        self.origin = origin
        '''Top left point of the room'''
        self.row_size = row_size
        '''Room height'''
        self.col_size = col_size
        '''Room width'''
        self.pts = set()
        '''All the points in the room'''
        self.furniture_pts = []
        '''Available points for furniture'''
        self.door_pos = None
        '''Record of where the door was placed'''

        self.get_room_pts()

    def get_room_pts(self):
        '''Set up the room points'''
        self.pts = set()
        for rw in range(self.row_size+1):
            for cl in range(self.col_size+1):
                self.pts.add((self.origin[0]+rw, self.origin[1]+cl))
                if (rw == 1 or rw == self.row_size-1) and (cl > 0 and cl < self.col_size-1):
                    self.furniture_pts.append((self.origin[0]+rw, self.origin[1]+cl))

    def inroom(self, pt):
        '''Check point list if a point is in a room'''
        if tuple(pt) in self.pts:
            return True
        return False

    def place_room(self, levelmanager, currlevel, rng, generator):
        '''Put the room onto the level'''
        Logger.info(f'Placing room: {self.origin} r:{self.row_size} c:{self.col_size}')
        outer_walls = []
        for rw in range(self.row_size+1):
            if rw == 0 or rw == self.row_size:
                for cl in range(self.col_size+1):
                    pos = [self.origin[0] + rw, self.origin[1] + cl]
                    if not levelmanager.is_entity_pos_valid(currlevel, wall.Limestone(), pos):
                        continue
                    if levelmanager.add_to_level(wall.Limestone(), pos, currlevel.z, generator, rng):
                        if cl > 0 and cl < self.col_size:
                            outer_walls.append(pos)
            else:
                for cl in range(self.col_size+1):
                    pos = [self.origin[0] + rw, self.origin[1] + cl]
                    if cl == 0 or cl == self.col_size:
                        if not levelmanager.is_entity_pos_valid(currlevel, wall.Limestone(), pos):
                            continue
                        if levelmanager.add_to_level(wall.Limestone(), pos, currlevel.z, generator, rng):
                            outer_walls.append(pos)
                    else:
                        levelmanager.add_to_level(tower.StoneFloor(), pos, currlevel.z, generator, rng, overwrite=True)

        self.door_pos = outer_walls[rng.randint(0, len(outer_walls)-1)]
        levelmanager.add_to_level(tower.StoneFloor(), self.door_pos, currlevel.z, generator, rng, overwrite=True)
        levelmanager.add_to_level(tower.Door(), self.door_pos, currlevel.z, generator, rng)

        idx = rng.randint(0, len(self.furniture_pts)-1)
        bed_pos = self.furniture_pts[idx]
        levelmanager.add_to_level(Bed(), bed_pos, currlevel.z, generator, rng)
        self.furniture_pts.pop(idx)

        idx = rng.randint(0, len(self.furniture_pts)-1)
        dresser_pos = self.furniture_pts[idx]
        levelmanager.add_to_level(Dresser(), dresser_pos, currlevel.z, generator, rng)
        self.furniture_pts.pop(idx)

        idx = rng.randint(0, len(self.furniture_pts)-1)
        chest_pos = self.furniture_pts[idx]
        levelmanager.add_to_level(Chest(), chest_pos, currlevel.z, generator, rng)
        self.furniture_pts.pop(idx)


