import entity
import config
import animation
import component
import color
import utility
import algo
import logging
import typeid

Logger = logging.getLogger(__name__)

class SnowRune(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.SNOW,
                         name='Snow Rune',
                         glyph='?',
                         color=color.Color().blue,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.ItemType = component.ItemType.NOEQUIP
        self.ApplyInfo = component.ApplyInfo.DIRECTION
        self.damage = 1

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        messager.add_notif(levelmanager.currentz, 'Ice freezes the air!', parent.pos())

        entitylayer = levelmanager.Levels[z].EntityLayer
        objr,objc = utility.find_last_position(cmd[0], row, col, entitylayer)

        grid,pts = utility.get_path_pts(entitylayer, row, col, objr, objc)

        # create the animation
        pts = pts[1:]
        frames = []
        delays = []
        for idx,pt in enumerate(pts):
            frame = [['' for _ in row] for row in grid]
            for jdx,pt in enumerate(pts[:idx+1]):
                frame[pt[0]][pt[1]] = '*'
            frames.append(frame)
            delays.append(config.THROW_ANIM_DELAY)
        origin = [0, 0, parent.z, parent.idx]
        anim = animation.Animation(pos=origin,
                                   frames=frames,
                                   color=color.Color().blue,
                                   delays=delays)
        animator.queueUp(levelmanager, anim)

        # deal damage
        for ent in entitylayer[objr][objc]:
            if hasattr(parent, 'Combat'):
                parent.Combat.deal_damage(parent, levelmanager, animator,
                                        messager, ent, True, self.damage, 'ice')
            ent.apply_status(messager, entity.StatusEffect.FROZEN, levelmanager)
        return True

class EmberRune(entity.Entity):
    def __init__(self):
        super().__init__(typeid=typeid.TID.EMBER,
                         name='Ember Rune',
                         glyph='?',
                         color=color.Color().red,
                         layer=entity.Layer.OBJECT_LAYER,
                         size=entity.Size.VERY_SMALL)
        self.ItemType = component.ItemType.NOEQUIP
        self.ApplyInfo = component.ApplyInfo.DIRECTION
        self.damage = 2

    def on_apply(self, cmd, parent, levelmanager, messager, animator, row, col, z):
        messager.add_notif(levelmanager.currentz, 'Flames shoot out!', parent.pos())

        entitylayer = levelmanager.Levels[z].EntityLayer
        objr,objc = utility.find_last_position(cmd[0], row, col, entitylayer)

        grid,pts = utility.get_path_pts(entitylayer, row, col, objr, objc)

        # create the animation
        pts = pts[1:]
        frames = []
        delays = []
        for idx,pt in enumerate(pts):
            frame = [['' for _ in row] for row in grid]
            for jdx,pt in enumerate(pts[:idx+1]):
                frame[pt[0]][pt[1]] = '*'
            frames.append(frame)
            delays.append(config.THROW_ANIM_DELAY)
        origin = [0, 0, parent.z, parent.idx]
        anim = animation.Animation(pos=origin,
                                   frames=frames,
                                   color=color.Color().red,
                                   delays=delays)
        animator.queueUp(levelmanager, anim)

        # deal damage
        for ent in entitylayer[objr][objc]:
            if hasattr(parent, 'Combat'):
                parent.Combat.deal_damage(parent, levelmanager, animator,
                                    messager, ent, True, self.damage, 'fire')
        return True


