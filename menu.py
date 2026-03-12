
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
        self.turn = turn
        self.text[0] = f'Player Turn:{self.turn}'


class MenuManager:

    def __init__(self):
        pass

    def init(self, turn):
        self.StatusMenu = StatusMenu((25,1), 1, 20, turn)

    def get_menus(self):
        return [self.StatusMenu]
