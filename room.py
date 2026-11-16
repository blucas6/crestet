import entity
import typeid
import color
import wall
import logging
import tower

Logger = logging.getLogger(__name__)

class Room:
    def __init__(self, origin, row_size, col_size):
        self.origin = origin
        self.row_size = row_size
        self.col_size = col_size
        self.pts = self.get_room_pts()
        self.door_pos = None

    def get_room_pts(self):
        pts = set()
        for rw in range(self.row_size+1):
            for cl in range(self.col_size+1):
                pts.add((self.origin[0]+rw, self.origin[1]+cl))
        return pts

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
                    if levelmanager.add_to_level(wall.Limestone(), pos, currlevel.z, self):
                        if cl > 0 and cl < self.col_size:
                            outer_walls.append(pos)
            else:
                for cl in range(self.col_size+1):
                    pos = [self.origin[0] + rw, self.origin[1] + cl]
                    if cl == 0 or cl == self.col_size:
                        if levelmanager.add_to_level(wall.Limestone(), pos, currlevel.z, self):
                            outer_walls.append(pos)
                    else:
                        levelmanager.add_to_level(tower.WoodFloor(), pos, currlevel.z, self, overwrite=True)

        self.door_pos = outer_walls[rng.randint(0, len(outer_walls)-1)]
        levelmanager.add_to_level(tower.Door(), self.door_pos, currlevel.z, self, overwrite=True)

