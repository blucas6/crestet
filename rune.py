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

        entitylayer = levelmanager.Levels[z].EntityLayer
        objr,objc = utility.find_last_position(cmd[0], row, col, entitylayer)

        grid,pts = utility.get_path_pts(entitylayer, row, col, objr, objc)

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
