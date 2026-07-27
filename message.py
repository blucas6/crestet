import entity

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

    def pop_message(self, blocking=True):
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

    def add_message(self, msg):
        '''
        Adds a msg to the msg queue
        '''
        self.MsgQueue.append(msg)
    
    def add_damage_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            self.MsgQueue.append(f'You hit the {defendentity.name}.')
        elif defendentity.name == 'Player':
            self.MsgQueue.append(f'The {attackentity.name} hits you.')
        else:
            self.MsgQueue.append(f'The {attackentity.name} hits the {defendentity.name}.')
    
    def add_kill_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            self.MsgQueue.append(f'You kill the {defendentity.name}!')
        elif defendentity.name == 'Player':
            self.MsgQueue.append(f'The {attackentity.name} kills you!')
        else:
            self.MsgQueue.append(f'The {attackentity.name} kills the {defendentity.name}!')

    def add_charge_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            self.MsgQueue.append(f'You charge the {defendentity.name}')
        elif defendentity.name == 'Player':
            self.MsgQueue.append(f'The {attackentity.name} charges you!')
        else:
            self.MsgQueue.append(f'The {attackentity.name} charges the {defendentity.name}.')

    def add_eat_message(self, entitya, entityb):
        if entitya.name == 'Player':
            self.MsgQueue.append(f'You eat the {entityb.name}.')
        elif entityb.name == 'Player':
            self.MsgQueue.append(f'The {entitya.name} eats you.')
        else:
            self.MsgQueue.append(f'The {entitya.name} eats the {entityb.name}.')

    def add_level_up_message(self, entitya):
        if entitya.name == 'Player':
            self.MsgQueue.append(f'You level up!')
        else:
            self.MsgQueue.append(f'The {entitya.name} levels up!')

    def add_status_message(self, entitya, status):
        if status == entity.StatusEffect.FROZEN:
            if entitya.name == 'Player':
                self.MsgQueue.append(f'You freeze!')
            else:
                self.MsgQueue.append(f'The {entitya.name} freezes!')
        elif status == entity.StatusEffect.BLIND:
            if entitya.name == 'Player':
                self.MsgQueue.append(f'You are blinded!')
            else:
                self.MsgQueue.append(f'The {entitya.name} is blinded!')
    
    def add_break_message(self, entitya, entityb):
        if entitya.name == 'Player':
            self.MsgQueue.append(f'You break the {entityb.name}.')
        elif entityb.name == 'Player':
            self.MsgQueue.append(f'The {entitya.name} breaks you!')
        else:
            self.MsgQueue.append(f'The {entitya.name} breaks the {entityb.name}.')

    def add_miss_message(self, entitya, entityb):
        if entitya.name == 'Player':
            self.MsgQueue.append(f'You miss the {entityb.name}.')
        elif entityb.name == 'Player':
            self.MsgQueue.append(f'The {entitya.name} misses you.')
        else:
            self.MsgQueue.append(f'The {entitya.name} misses the {entityb.name}.')



