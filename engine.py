import curses
import color
import time

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

    def init(self, stdscr: curses.window, timedelay: int=0):
        '''
        Required to call at engine startup, returns size of terminal
        '''
        curses.start_color()
        self.Color = color.Color()
        self.stdscr = stdscr
        self.termrows, self.termcols = stdscr.getmaxyx()
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(self.inputtimeout)
        if timedelay > 0:
            self.framedelay = timedelay
        # clear log
        with open(self.eventlog, 'w+') as el:
            el.write('')
        self.initialized = True
        self.log_event(f'Engine initialized {(self.termrows,self.termcols)}')
        self.log_event(f'  Frame Delay: {self.framedelay}')
        self.log_event(f'  Baudrate:    {curses.baudrate()} (bit/sec)')
        self.log_event(f'  Long Name:   {curses.longname()}')

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
                        color = screencolors[r][c]
                    else:
                        color = self.Colors.white
                    self.stdscr.addch(r, c, chr, color)
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

    def cursor_position(self, pos):
        '''
        Moves the cursor to a position
        '''
        if not self.initialized:
            return
        if pos[0] < self.termrows and pos[1] < self.termcols:
            self.stdscr.move(pos[0], pos[1])
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
