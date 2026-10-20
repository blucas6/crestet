import entity
import logging

Logger = logging.getLogger(__name__)

class Notif:
    def __init__(self, msg, pos, unseen=''):
        self.msg = msg
        self.unseen = unseen
        self.pos = pos

class Messager:
    '''
    Message queue to hold messages generated in game
    '''

    def __init__(self):
        self.MsgQueue = []
    
    def clear(self):
        '''
        Clears the msg queue
        '''
        self.MsgQueue = []

    def pop_notif(self, blocking=True):
        '''
        If messages are in the queue, get the messages by FIFO
        '''
        if self.MsgQueue:
            msg = self.MsgQueue[0]
            # if blocking, delete only the message popped
            if blocking:
                del self.MsgQueue[0]
            # otherwise dump the remaining queue
            else:
                self.MsgQueue = []
            return msg
        return ''

    def show_notif(self, notif, fovpoints, levelz, status):
        '''
        Decide whether or not to show the message
        Messages without positions get shown automatically
        Messages with positions are subject to transformations
        '''
        if not notif.pos:
            return notif.msg
        if notif.pos[2] == levelz:
            if (notif.pos[0],notif.pos[1]) in fovpoints:
                return notif.msg
            elif notif.unseen:
                if notif.unseen == '_':
                    return None
                else:
                    return notif.unseen
            else:
                return notif.msg
        return None
    
    def add_text(self, msg):
        self.MsgQueue.append(Notif(msg, ()))

    def add_notif(self, levelz, msg, pos, unseen=''):
        '''
        Adds a message to the queue, filtering out out of position messages
        '''
        notif = Notif(msg, pos, unseen)
        # no position means it is alert text, always shown
        # or it's on the current level
        if not notif.pos or notif.pos[2] == levelz:
            self.MsgQueue.append(notif)
    
    def add_damage_message(self, levelz, attackentity, defendentity):
        if attackentity.name == 'Player':
            msg = f'You hit the {defendentity.name}.'
            unseen = 'You hit it.'
            pos = attackentity.pos()
        elif defendentity.name == 'Player':
            msg = f'The {attackentity.name} hits you.'
            unseen = 'It hits you.'
            pos = defendentity.pos()
        else:
            msg = f'The {attackentity.name} hits the {defendentity.name}.'
            unseen = 'You hear fighting.'
            pos = attackentity.pos()
        self.add_notif(levelz, msg, pos, unseen)
    
    def add_kill_message(self, levelz, attackentity, defendentity):
        if attackentity.name == 'Player':
            msg = f'You kill the {defendentity.name}!'
            unseen = 'You kill it!'
            pos = attackentity.pos()
        elif defendentity.name == 'Player':
            msg = f'The {attackentity.name} kills you!'
            unseen = 'You get killed!'
            pos = defendentity.pos()
        else:
            msg = f'The {attackentity.name} kills the {defendentity.name}!'
            unseen = 'Something gets killed!'
            pos = attackentity.pos()
        self.add_notif(levelz, msg, pos, unseen)

    def add_charge_message(self, levelz, attackentity, defendentity):
        if attackentity.name == 'Player':
            msg = f'You charge the {defendentity.name}.'
            unseen = 'You charge it.'
            pos = attackentity.pos()
        elif defendentity.name == 'Player':
            msg = f'The {attackentity.name} charges you!'
            unseen = 'It charges you!'
            pos = defendentity.pos()
        else:
            msg = f'The {attackentity.name} charges the {defendentity.name}.'
            unseen = 'You hear charging.'
            pos = attackentity.pos()
        self.add_notif(levelz, msg, pos, unseen)

    def add_eat_message(self, levelz, entity_eats, entity_eaten):
        if entity_eats.name == 'Player':
            msg = f'You eat the {entity_eaten.name}.'
            unseen = 'You eat it.'
            pos = entity_eats.pos()
        elif entity_eaten.name == 'Player':
            msg = f'The {entity_eats.name} eats you.'
            unseen = 'It eats you.'
            pos = entity_eaten.pos()
        else:
            msg = f'The {entity_eats.name} eats the {entity_eaten.name}.'
            unseen = 'You hear eating.'
            pos = entity_eats.pos()
        self.add_notif(levelz, msg, pos, unseen)

    def add_level_up_message(self, levelz, ent):
        if ent.name == 'Player':
            msg = f'You level up!'
            unseen = ''
        else:
            msg = f'The {ent.name} levels up!'
            unseen = 'It levels up!'
        self.add_notif(levelz, msg, ent.pos(), unseen)

    def add_status_message(self, levelz, ent, status):
        if status == entity.StatusEffect.FROZEN:
            if ent.name == 'Player':
                msg = f'You freeze!'
                unseen = 'You freeze!'
            else:
                msg = f'The {ent.name} freezes!'
                unseen = 'It freezes!'
        elif status == entity.StatusEffect.BLIND:
            if ent.name == 'Player':
                msg = f'You are blinded!'
                unseen = 'You are blinded!'
            else:
                msg = f'The {ent.name} is blinded!'
                unseen = 'It gets blinded!'
        self.add_notif(levelz, msg, ent.pos(), unseen)
    
    def add_break_message(self, levelz, entity_attack, entity_defend):
        if entity_attack.name == 'Player':
            msg = f'You break the {entity_defend.name}.'
            unseen = 'You break it.'
            pos = entity_attack.pos()
        elif entity_defend.name == 'Player':
            msg = f'The {entity_defend.name} breaks you!'
            unseen = 'It breaks you!'
            pos = entity_defend.pos()
        else:
            msg = f'The {entity_attack.name} breaks the {entity_defend.name}.'
            unseen = 'You hear breaking.'
            pos = entity_defend.pos()
        self.add_notif(levelz, msg, pos, unseen)

    def add_miss_message(self, levelz, entity_attack, entity_defend):
        if entity_attack.name == 'Player':
            msg = f'You miss the {entity_defend.name}.'
            unseen = 'You miss it.'
            pos = entity_attack.pos()
        elif entity_defend.name == 'Player':
            msg = f'The {entity_attack.name} misses you.'
            unseen = 'It misses you.'
            pos = entity_defend.pos()
        else:
            msg = f'The {entity_attack.name} misses the {entity_defend.name}.'
            unseen = '_'
            pos = entity_attack.pos()
        self.add_notif(levelz, msg, pos, unseen)

    def add_stair_message(self, levelz, ent, incrementz):
        if ent.name == 'Player':
            if incrementz > 0:
                msg = 'You walk up the stairs.'
            else:
                msg = 'You walk down the stairs.'
            self.add_text(msg)

    def add_stair_fail_message(self, levelz, ent, incrementz):
        if ent.name == 'Player':
            if incrementz > 0:
                msg = "Can't go up here."
            else:
                msg = "Can't go down here."
            self.add_text(msg)

    def add_level_fail_message(self, levelz, ent, newz):
        if ent.name == 'Player':
            if newz > 0:
                msg = 'There is nothing above you.'
            else:
                msg = 'There is nothing below you.'
            self.add_text(msg)

    def add_burst_message(self, levelz, ent):
        if ent.name == 'Player':
            msg = 'You explode!'
            unseen = ''
            pos = ent.pos()
        else:
            msg = f'The {ent.name} explodes!'
            unseen = 'You hear a burst!'
            pos = ent.pos()
        self.add_notif(levelz, msg, pos, unseen)





