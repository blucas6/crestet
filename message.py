
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

    def add_message(self, msg):
        '''
        Adds a msg to the msg queue
        '''
        self.MsgQueue.append(msg)
    
    def add_damage_message(self, attackentity, defendentity):
        if attackentity.name == 'Player':
            self.MsgQueue.append(f'You hit the {defendentity.name}')
        elif defendentity.name == 'Player':
            self.MsgQueue.append(f'The {attackentity.name} hits you')
        else:
            self.MsgQueue.append(f'The {attackentity.name} hits the {defendentity.name}')
    
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
            self.MsgQueue.append(f'The {attackentity.name} charges the {defendentity.name}')

    def add_eat_message(self, entitya, entityb):
        if entitya.name == 'Player':
            self.MsgQueue.append(f'You eat the {entityb.name}')
        elif entityb.name == 'Player':
            self.MsgQueue.append(f'The {entitya.name} eats you')
        else:
            self.MsgQueue.append(f'The {entitya.name} eats the {entityb.name}')

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
