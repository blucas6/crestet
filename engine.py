import curses
import sys
import time
import os
import logging

Logger = logging.getLogger(__name__)

class Engine:
    '''
    Engine class provides a curses interface displayer
    Pass any 2D character buffer and display it with colors
    '''
    def __init__(self):
        self.inputtimeout = 0
        '''Optional ms between engine display'''
        self.stdscr: curses.window = None
        '''Curses.window'''
        self.framedelay = 0
        '''Optional delay between frames'''
        self.frames = 0
        '''Current frame counter'''
        self.initialized = False
        '''Keeps track of object initialization of the curses module'''
        self.color_pairs = {}
        self._next_color = 1

    def gc(self, fg, bg=-1, rw=-1, cl=-1):
        if not self.initialized:
            Logger.error('Engine gc() called before initialization!')
            return None
        if not bg:
            bg = -1
        key = (fg, bg)
        if not key in self.color_pairs:
            try:
                if fg >= curses.COLORS:
                    fg -= 8
                if bg >= curses.COLORS:
                    bg -= 8
                curses.init_pair(self._next_color, fg, bg)
                self.color_pairs[key] = curses.color_pair(self._next_color)
                self._next_color += 1
            except:
                Logger.error(f'Engine invalid color pair! -> {fg} {bg} {rw} {cl}')
                return None
        return self.color_pairs[key]

    def frame_ready(self):
        '''
        Decrement frame counter and return if engine is ready to display
        '''
        self.frames -= 1
        if self.frames <= 0:
            self.frames = self.framedelay
            return True
        return False

    def init(self, timedelay: int=0):
        '''
        Required to call at engine startup, returns size of terminal
        '''
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.start_color()
        curses.use_default_colors()
        self.termrows, self.termcols = self.stdscr.getmaxyx()
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.timeout(self.inputtimeout)
        if timedelay > 0:
            self.framedelay = timedelay
        if sys.platform == 'win32':
            os.environ['ESCDELAY'] = '25'
        else:
            curses.set_escdelay(25)
        self.initialized = True
        Logger.info(f'Engine initialized {(self.termrows,self.termcols)}')
        Logger.info(f'  Frame Delay: {self.framedelay}')
        Logger.info(f'  Baudrate:    {curses.baudrate()} (bit/sec)')
        Logger.info(f'  Long Name:   {curses.longname()}')

    def end(self):
        '''End the curses module correctly'''
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        Logger.info('--Engine Shutdown--')

    def output(self, screenchars: list=[], screencolors: list=[]):
        '''
        Call to output a 2D character buffer and an optional 2D curses
        color pair buffer to the terminal
        '''
        if not self.initialized:
            Logger.error('Engine output() called before initialization!')
            return
        try:
            self.stdscr.erase()
            for r,row in enumerate(screenchars):
                for c,chr in enumerate(row):
                    thecolor = -1
                    if r < len(screencolors) and c < len(screencolors[r]):
                        thecolor = screencolors[r][c]
                    if not thecolor:
                        thecolor = self.gc(curses.COLOR_MAGENTA)
                    self.stdscr.addch(r, c, chr, thecolor)
            self.stdscr.refresh()
        except Exception as e:
            Logger.error(f'Display ERROR: [{c},{r}]: {e}')

    def read_input(self):
        '''
        Call to grab input and return a valid event in string form
        '''
        if not self.initialized:
            return
        try:
            event = self.stdscr.getch()
            if event != curses.ERR:
                return chr(event)
        except Exception as e:
            Logger.error(f'Read input ERROR: {event}')

    def get_cursor(self):
        '''Returns the current position of the cursor on screen'''
        if not self.initialized:
            return
        return self.stdscr.getyx()

    def toggle_cursor(self, mode):
        '''
        Changes the cursor state

        0 : OFF
        1 : ON
        2 : ON HIGHLIGHTED
        '''
        if not self.initialized:
            return
        if mode < 0 or mode > 2:
            return
        curses.curs_set(mode)

    def move_cursor(self, pos):
        '''
        Moves the cursor to a position
        '''
        if not self.initialized:
            return
        if pos[0] < self.termrows and pos[1] < self.termcols:
            try:
                self.stdscr.move(pos[0], pos[1])
            except Exception as e:
                Logger.error(f'Failed to move cursor: {e}')
        else:
            Logger.error(f'Invalid cursor position {pos}')

    def pause(self, t: float=1):
        '''
        Sleeps the engine for t amount of seconds
        
        Discards any key presses during that time
        '''
        if t <= 0:
            return
        time.sleep(t)
        while self.stdscr.getch() != -1:
            pass

