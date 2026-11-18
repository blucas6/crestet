import entity
import typeid
import color
import wall
import logging
import tower
import component
import item

Logger = logging.getLogger(__name__)

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
        self.row_size = row_size
        self.col_size = col_size
        self.pts = set()
        self.furniture_pts = []
        self.door_pos = None
        self.bed_pos = None
        self.dresser_pos = None
        self.get_room_pts()

    def get_room_pts(self):
        self.pts = set()
        for rw in range(self.row_size+1):
            for cl in range(self.col_size+1):
                self.pts.add((self.origin[0]+rw, self.origin[1]+cl))
                if (rw == 1 or rw == self.row_size-1) and (cl > 0 and cl < self.col_size-1):
                    self.furniture_pts.append((self.origin[0]+rw, self.origin[1]+cl))

    def inroom(self, pt):
        if tuple(pt) in self.pts:
            return True
        return False

    def place_room(self, levelmanager, currlevel, rng):
        Logger.info(f'Placing room: {self.origin} r:{self.row_size} c:{self.col_size}')
        outer_walls = []
        for rw in range(self.row_size+1):
            if rw == 0 or rw == self.row_size:
                for cl in range(self.col_size+1):
                    pos = [self.origin[0] + rw, self.origin[1] + cl]
                    if not levelmanager.is_entity_pos_valid(currlevel, wall.Limestone(), pos):
                        continue
                    if levelmanager.add_to_level(wall.Limestone(), pos, currlevel.z, self):
                        if cl > 0 and cl < self.col_size:
                            outer_walls.append(pos)
            else:
                for cl in range(self.col_size+1):
                    pos = [self.origin[0] + rw, self.origin[1] + cl]
                    if cl == 0 or cl == self.col_size:
                        if not levelmanager.is_entity_pos_valid(currlevel, wall.Limestone(), pos):
                            continue
                        if levelmanager.add_to_level(wall.Limestone(), pos, currlevel.z, self):
                            outer_walls.append(pos)
                    else:
                        levelmanager.add_to_level(tower.WoodFloor(), pos, currlevel.z, self, overwrite=True)

        self.door_pos = outer_walls[rng.randint(0, len(outer_walls)-1)]
        levelmanager.add_to_level(tower.WoodFloor(), self.door_pos, currlevel.z, self, overwrite=True)
        levelmanager.add_to_level(tower.Door(), self.door_pos, currlevel.z, self)

        idx = rng.randint(0, len(self.furniture_pts)-1)
        self.bed_pos = self.furniture_pts[idx]
        levelmanager.add_to_level(Bed(), self.bed_pos, currlevel.z, self)
        self.furniture_pts.pop(idx)

        idx = rng.randint(0, len(self.furniture_pts)-1)
        self.dresser_pos = self.furniture_pts[idx]
        levelmanager.add_to_level(Dresser(), self.dresser_pos, currlevel.z, self)
        self.furniture_pts.pop(idx)



