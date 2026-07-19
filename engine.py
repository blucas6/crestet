import curses
import sys
import color
import time
import os

class Engine:
    '''
    Engine class provides a curses interface displayer
    Pass any 2D character buffer and display it with colors
    '''
    def __init__(self, debug=False):
        self.inputtimeout = 1
        '''Optional ms between engine display'''
        self.stdscr: curses.window = None
        '''Curses.window'''
        self.eventlog = 'EventLog.log'
        '''Where to dump events'''
        self.framedelay = 0
        '''Optional delay between frames'''
        self.frames = 0
        '''Current frame counter'''
        self.initialized = False
        '''Keeps track of object initialization of the curses module'''
        self.debug = debug
        '''Logs more messages if true'''

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
        #curses.use_default_colors()
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
        # clear log
        with open(self.eventlog, 'w+') as el:
            el.write('')
        self.initialized = True
        self.log_event(f'Engine initialized {(self.termrows,self.termcols)}')
        self.log_event(f'  Frame Delay: {self.framedelay}')
        self.log_event(f'  Baudrate:    {curses.baudrate()} (bit/sec)')
        self.log_event(f'  Long Name:   {curses.longname()}')

    def end(self):
        '''End the curses module correctly'''
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        self.log_event('--Engine Shutdown--')

    def output(self, screenchars: list=[], screencolors: list=[]):
        '''
        Call to output a 2D character buffer and an optional 2D curses
        color pair buffer to the terminal
        '''
        if not self.initialized:
            self.log_event('Engine output() called before initialization!')
            return
        try:
            self.stdscr.erase()
            for r,row in enumerate(screenchars):
                for c,chr in enumerate(row):
                    if r < len(screencolors) and c < len(screencolors[r]):
                        thecolor = screencolors[r][c]
                    else:
                        thecolor = color.Color().magenta
                    self.stdscr.addch(r, c, chr, thecolor)
            self.stdscr.refresh()
        except Exception as e:
            self.log_event(f'Display ERROR: [{c},{r}]: {e}')

    def read_input(self):
        '''
        Call to grab input and return a valid event in string form
        '''
        if not self.initialized:
            return
        try:
            event = self.stdscr.getch()
            if event != curses.ERR:
                if self.debug:
                    self.log_event(f'"{chr(event)}" ({event})')
                return chr(event)
        except Exception as e:
            self.log_event(f'Read input ERROR: {event}')

    def log_event(self, msg):
        '''
        Logs an event to the event log
        '''
        with open(self.eventlog, 'a+') as lf:
            lf.write(f'{msg}\n')
    
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
                self.log_event(f'Moving cursor {pos}')
                self.stdscr.move(pos[0], pos[1])
            except Exception as e:
                self.log_event(f'Failed to move cursor: {e}')
        else:
            self.log_event(f'Invalid cursor position {pos}')

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

