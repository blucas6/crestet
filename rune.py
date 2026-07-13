import entity
import component
import color

class EmberRune(entity.Entity):
    def __init__(self):
        super().__init__(typeid=19,
                         name='Ember Rune',
                         glyph='?',
                         color=color.Color().red,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.ItemType = component.ItemType.RUNE
        self.ApplyInfo = component.ApplyInfo.DIRECTION

    def on_apply(self, cmd, levelmanager, messager, z):
        messager.add_message('Flames shoot out!')
        direction = utility.ONE_LAYER_CIRCLE[int(cmd[1])-1]
        objr = self.row
        objc = self.col
        entitylayer = levelmanager.Levels[self.z].EntityLayer

        while True:
            r,c = objr + direction[0], objc + direction[1]
            if entitylayer:
                maxlayer = max([x.layer for x in entitylayer[r][c]])
                if maxlayer == Layer.MONST_LAYER or maxlayer == Layer.BARREL_LAYER:
                    objr, objc = r, c
                    break
                elif maxlayer == Layer.WALL_LAYER:
                    break
            objr, objc = r, c

        # construct a grid of [0-1] (makes sure path to end point is valid)
        grid = [[1 if max([int(x.layer) for x in elist]) > Layer.BARREL_LAYER else 0
                for elist in row]
                for row in entitylayer]
        returncode, pts = algo.astar(grid, (self.row,self.col), (objr,objc))
        if returncode != 1:
            logger.Logger.log(f'Error: rune failed -> {returncode}')
            return

        # create the animation
        frames = {}
        for idx,pt in enumerate(pts):
            frames[str(idx)] = [['' for _ in row] for row in grid]
            frames[str(idx)][pt[0]][pt[1]] = '*'
        origin = [0,0]
        delay = config.THROW_ANIM_DELAY
        anim = animation.Animation(origin, frames, entity.color, delay=delay)
        animator.queueUp(anim)

        # deal damage
        dmg = 3
        for ent in entitylayer[objr][objc]:
            self.attack(levelmanager, animator, messager, ent, dmg)




