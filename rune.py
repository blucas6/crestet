import entity
import config
import animation
import component
import color
import utility
import algo
import logger

class EmberRune(entity.Entity):
    def __init__(self):
        super().__init__(typeid=19,
                         name='Ember Rune',
                         glyph='?',
                         color=color.Color().red,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.ItemType = component.ItemType.NOEQUIP
        self.ApplyInfo = component.ApplyInfo.DIRECTION

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        messager.add_message('Flames shoot out!')
        direction = utility.ONE_LAYER_CIRCLE[int(cmd[0])-1]
        objr = row
        objc = col
        entitylayer = levelmanager.Levels[z].EntityLayer

        while True:
            r,c = objr + direction[0], objc + direction[1]
            if entitylayer:
                maxlayer = max([x.layer for x in entitylayer[r][c]])
                if maxlayer == entity.Layer.MONST_LAYER or maxlayer == entity.Layer.BARREL_LAYER:
                    objr, objc = r, c
                    break
                elif maxlayer == entity.Layer.WALL_LAYER:
                    break
            objr, objc = r, c

        # construct a grid of [0-1] (makes sure path to end point is valid)
        grid = [[1 if max([int(x.layer) for x in elist]) > entity.Layer.BARREL_LAYER else 0
                for elist in row]
                for row in entitylayer]
        returncode, pts = algo.astar(grid, (row,col), (objr,objc))
        if returncode != 1:
            logger.Logger.log(f'Error: rune failed -> {returncode}')
            return

        # create the animation
        pts = pts[1:]
        frames = {}
        for idx,pt in enumerate(pts):
            frames[str(idx)] = [['' for _ in row] for row in grid]
            for jdx,pt in enumerate(pts[:idx+1]):
                frames[str(idx)][pt[0]][pt[1]] = '*'
        origin = [0,0]
        delay = config.THROW_ANIM_DELAY
        anim = animation.Animation(origin, frames, color.Color().red, delay=delay)
        animator.queueUp(anim)

        # deal damage
        dmg = 3
        for ent in entitylayer[objr][objc]:
            parent.attack(levelmanager, animator, messager, ent, dmg)
