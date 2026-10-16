import entity

class Notif:
    def __init__(self, msg, pos):
        self.msg = msg
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
    
    def add_text(self, msg):
        self.MsgQueue.append(Notif(msg, []))

    def add_notif(self, msg, pos):
        '''
        Adds a msg to the msg queue
        '''
        self.MsgQueue.append(Notif(msg, pos))
    
    def add_damage_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            msg = f'You hit the {defendentity.name}.'
            pos = attackentity.pos()
        elif defendentity.name == 'Player':
            msg = f'The {attackentity.name} hits you.'
            pos = defendentity.pos()
        else:
            msg = f'The {attackentity.name} hits the {defendentity.name}.'
            pos = attackentity.pos()
        self.add_notif(msg, pos)
    
    def add_kill_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            msg = f'You kill the {defendentity.name}!'
            pos = attackentity.pos()
        elif defendentity.name == 'Player':
            msg = f'The {attackentity.name} kills you!'
            pos = defendentity.pos()
        else:
            msg = f'The {attackentity.name} kills the {defendentity.name}!'
            pos = attackentity.pos()
        self.add_notif(msg, pos)

    def add_charge_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            msg = f'You charge the {defendentity.name}'
            pos = attackentity.pos()
        elif defendentity.name == 'Player':
            msg = f'The {attackentity.name} charges you!'
            pos = defendentity.pos()
        else:
            msg = f'The {attackentity.name} charges the {defendentity.name}.'
            pos = attackentity.pos()
        self.add_notif(msg, pos)

    def add_eat_message(self, entity_eats, entity_eaten):
        if entity_eats.name == 'Player':
            msg = f'You eat the {entity_eaten.name}.'
            pos = entity_eats.pos()
        elif entity_eaten.name == 'Player':
            msg = f'The {entity_eats.name} eats you.'
            pos = entity_eaten.pos()
        else:
            msg = f'The {entity_eats.name} eats the {entity_eaten.name}.'
            pos = entity_eats.pos()
        self.add_notif(msg, pos)

    def add_level_up_message(self, ent):
        if ent.name == 'Player':
            msg = f'You level up!'
        else:
            msg = f'The {ent.name} levels up!'
        self.add_notif(msg, ent.pos())

    def add_status_message(self, ent, status):
        if status == entity.StatusEffect.FROZEN:
            if ent.name == 'Player':
                msg = f'You freeze!'
            else:
                msg = f'The {ent.name} freezes!'
        elif status == entity.StatusEffect.BLIND:
            if ent.name == 'Player':
                msg = f'You are blinded!'
            else:
                msg = f'The {ent.name} is blinded!'
        self.add_notif(msg, ent.pos())
    
    def add_break_message(self, entity_attack, entity_defend):
        if entity_attack.name == 'Player':
            msg = f'You break the {entity_defend.name}.'
            pos = entity_attack.pos()
        elif entity_defend.name == 'Player':
            msg = f'The {entity_defend.name} breaks you!'
            pos = entity_defend.pos()
        else:
            msg = f'The {entity_attack.name} breaks the {entity_defend.name}.'
            pos = entity_defend.pos()
        self.add_notif(msg, pos)

    def add_miss_message(self, entity_attack, entity_defend):
        if entity_attack.name == 'Player':
            msg = f'You miss the {entity_defend.name}.'
            pos = entity_attack.pos()
        elif entity_defend.name == 'Player':
            msg = f'The {entity_attack.name} misses you.'
            pos = entity_defend.pos()
        else:
            msg = f'The {entity_attack.name} misses the {entity_defend.name}.'
            pos = entity_attack.pos()
        self.add_notif(msg, pos)



