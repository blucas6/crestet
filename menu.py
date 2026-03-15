import logger
import config

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
        '''Clears the text array before it gets generated'''
        self.text = [' '*self.cols for _ in range(self.rows)]

class DepthMenu(Menu):
    '''Displays the level depth information'''
    def __init__(self, origin, rows, cols):
        super().__init__(origin, rows, cols)
    
    def update(self, z):
        '''Updates the level index'''
        super().update()
        self.text[0] = f'Current Level: {z+1}'

class HealthMenu(Menu):
    '''Displays the health bar'''
    def __init__(self, origin, rows, cols):
        super().__init__(origin, rows, cols)

    def update(self, healthcomponent):
        super().update()
        currenthealth = healthcomponent.currenthealth
        maxhealth = healthcomponent.maxhealth
        amount = round(config.HEALTHMENU_LENGTH * currenthealth / maxhealth)
        self.text[0] = '[' + amount*'\u2588' + (config.HEALTHMENU_LENGTH-amount)*' ' + ']'

class StatusMenu(Menu):
    '''
    Display player status
    '''
    def __init__(self, origin, rows, cols, turn):
        super().__init__(origin, rows, cols)
        self.turn = turn
        self.text[0] = f'Player Turn:{self.turn}'

    def update(self, turn):
        '''Add the new turn'''
        super().update()
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
        super().update()
        if not self.msg:
            self.msg = self.Messager.pop_message(self.blocking)
            self.text[0] = self.msg
            if self.Messager.MsgQueue:
                self.text[0] += '--more--'

    def clear(self):
        self.msg = ''
        self.text[0] = ''

class InventoryMenu(Menu):
    '''Displays the player inventory'''
    def __init__(self, origin, rows, cols):
        super().__init__(origin, rows, cols)
        self.count = 96
    
    def update(self, inventory):
        '''Update the current inventory menu'''
        super().update()
        self.text[0] = '=Inventory='
        if inventory:
            self.text[1] = f'(Q)uiver:'
            if inventory.quiver:
                self.text[2] = self.display_item(' ', inventory.quiver)
            self.text[3] = f'(M)ain Hand: '
            if inventory.mainHand:
                self.text[4] = ' '+inventory.mainHand.name
            self.text[5] = f'(O)ff Hand: '
            if inventory.offHand:
                self.text[6] = ' '+inventory.offHand.name
            self.text[7] = f'(H)ead: '
            if inventory.head:
                self.text[8] = ' '+inventory.head.name
            self.text[9] = f'(B)ody: '
            if inventory.body:
                self.text[10] = ' '+inventory.body.name
            self.text[11] = f'(F)eet: '
            if inventory.feet:
                self.text[12] = ' '+inventory.feet.name
            self.text[13] = 'Bag:'
            if inventory.contents:
                for idx, entity in enumerate(inventory.contents):
                    i = 14+idx
                    if i < self.rows:
                        self.text[i] = self.display_item(f'({self.letter()}): ', entity)
        self.count = 96
    
    def display_item(self, preText, item):
        '''Display an item to the menu, pretext is usually the letter key'''
        if hasattr(item, 'Stack'):
            amount = item.Stack.amount
            return f'{preText}{item.name} ({amount})'
        else:
            return f'{preText}{item.name}'

    def letter(self):
        '''Return the correct character incremented from the previous'''
        self.count += 1
        return chr(self.count)

class MenuManager:
    '''
    Holds all menus
    '''

    def __init__(self):
        pass

    def init(self, messager, blocking, turn):
        self.StatusMenu = StatusMenu(config.STATUSMENU_ORIGIN, 1, 20, turn)
        self.MessageMenu = MessageMenu(messager, blocking, config.MESSAGEMENU_ORIGIN, 1, 30)
        self.HealthMenu = HealthMenu(config.HEALTHMENU_ORIGIN, 1, config.HEALTHMENU_LENGTH+2)
        self.DepthMenu = DepthMenu(config.DEPTHMENU_ORIGIN, 1, 20)
        self.InventoryMenu = InventoryMenu(config.INVENTORYMENU_ORIGIN, 20, 30)

    def get_menus(self):
        return [self.StatusMenu, self.MessageMenu, self.HealthMenu, self.DepthMenu, self.InventoryMenu]
