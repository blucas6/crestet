import curses
import logger

class Color:
    '''
    Color class sets up the colors for the curses interface
    '''
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, display=True):
        '''
        Set up the color pairs for the curses interface
        '''
        if not self._initialized:
            self.black          = None
            self.red            = None 
            self.green          = None 
            self.yellow         = None 
            self.blue           = None 
            self.magenta        = None 
            self.cyan           = None 
            self.white          = None 
            self.grey           = None 
            self.bright_red     = None 
            self.bright_green   = None 
            self.bright_yellow  = None 
            self.bright_blue    = None 
            self.bright_pink    = None 
            self.bright_cyan    = None 
            self.bright_white   = None 

            self._initialized = True
            if display:
                self.curses_colors()

    def curses_colors(self):
        '''
        Create the color pairs for the curses module
        '''
        curses.init_pair(1, 0, curses.COLOR_BLACK)
        curses.init_pair(2, 1, curses.COLOR_BLACK)
        curses.init_pair(3, 2, curses.COLOR_BLACK)
        curses.init_pair(4, 3, curses.COLOR_BLACK)
        curses.init_pair(5, 4, curses.COLOR_BLACK)
        curses.init_pair(6, 5, curses.COLOR_BLACK)
        curses.init_pair(7, 6, curses.COLOR_BLACK)
        curses.init_pair(8, 7, curses.COLOR_BLACK)
        curses.init_pair(9, 8, curses.COLOR_BLACK)
        curses.init_pair(10, 9, curses.COLOR_BLACK)
        curses.init_pair(11, 10, curses.COLOR_BLACK)
        curses.init_pair(12, 11, curses.COLOR_BLACK)
        curses.init_pair(13, 12, curses.COLOR_BLACK)
        curses.init_pair(14, 13, curses.COLOR_BLACK)
        curses.init_pair(15, 14, curses.COLOR_BLACK)
        curses.init_pair(16, 15, curses.COLOR_BLACK)
        self.black = curses.color_pair(1)
        self.red = curses.color_pair(2)
        self.green = curses.color_pair(3)
        self.yellow = curses.color_pair(4)
        self.blue = curses.color_pair(5)
        self.magenta = curses.color_pair(6)
        self.cyan = curses.color_pair(7)
        self.white = curses.color_pair(8)
        self.grey = curses.color_pair(9)
        self.bright_red = curses.color_pair(10)
        self.bright_green = curses.color_pair(11)
        self.bright_yellow = curses.color_pair(12)
        self.bright_blue = curses.color_pair(13)
        self.bright_pink = curses.color_pair(14)
        self.bright_cyan = curses.color_pair(15)
        self.bright_white = curses.color_pair(16)

def show_colors(stdscr):
    curses.start_color()
    curses.use_default_colors()
    numcolors = curses.COLORS
    stdscr.addstr(0, 0, f'Terminal supports {numcolors} colors.')
    for i in range(1, numcolors):
        curses.init_pair(i, i-1, 0)
    rows,cols = stdscr.getmaxyx()
    currrow = 3
    currcol = 0
    width = 8
    for i in range(1, numcolors):
        stdscr.attron(curses.color_pair(i))
        stdscr.addstr(currrow, currcol, f' {i-1} ')
        currcol += width
        if currcol + width > cols:
            currcol = 0
            currrow += 1
            if currrow >= rows - 1:
                break
    stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(show_colors)

