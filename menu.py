import logger

class Menu:
    '''
    Basic menu class to display an updating menu
    '''
    def __init__(self, origin, rows, cols):
        self.origin = origin
        '''Top left corner in screen buffer'''
        self.rows = rows
        '''Max rows for the menu'''
        self.cols = cols
        '''Max cols for the menu'''
        self.text = [' '*self.cols for _ in range(self.rows)]
        '''Text array to be displayed'''

    def update(self, *_):
        '''Base class update method'''
        pass


class StatusMenu(Menu):
    '''
    Display player status
    '''
    def __init__(self, origin, rows, cols, turn):
        self.turn = turn
        super().__init__(origin, rows, cols)
        self.text[0] = f'Player Turn:{self.turn}'

    def update(self, turn):
        '''Add the new turn'''
        self.turn = turn
        self.text[0] = f'Player Turn:{self.turn}'

class MessageMenu(Menu):
    '''
    Display message queue
    '''
    def __init__(self, messager, blocking, origin, rows, cols):
        super().__init__(origin, rows, cols)
        self.Messager = messager
        self.msg = ''
        self.blocking = blocking

    def update(self):
        '''Get the latest message'''
        if not self.msg:
            self.msg = self.Messager.pop_message(self.blocking)
            self.text[0] = self.msg
            if self.Messager.MsgQueue:
                self.text[0] += '--more--'

    def clear(self):
        self.msg = ''
        self.text[0] = ' something '

class MenuManager:
    '''
    Holds all menus
    '''

    def __init__(self):
        pass

    def init(self, messager, blocking, turn):
        self.StatusMenu = StatusMenu((25,1), 1, 20, turn)
        self.MessageMenu = MessageMenu(messager, blocking, (0,0), 1, 30)

    def get_menus(self):
        return [self.StatusMenu, self.MessageMenu]
