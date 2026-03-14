import engine
import copy
import config
import level
import display
import logger 
import curses.ascii
import random
import secrets
import color
import curses
import enum
import menu
import animation

class Event(enum.Enum):
    '''
    Event types from user

    NA    : not an event - continue without looking at user input
    CLEAR : clearing event - reset menus and message window
    EVENT : normal event - look at user input
    '''
    NA = -1
    CLEAR = 0
    EVENT = 1

class GameState(enum.Enum):
    '''
    Game States:
        1: User inputting actions to the player
        2: Game is over (winning/losing)
        3: Pausing will block player actions
        4: Motion will block player actions until the second event arrives
        5: Running will update the game without user interactions
    '''
    PLAYING = 1
    END = 2
    PAUSEONMSG = 3
    MOTION = 4
    RUNNING = 5

class Game:
    '''
    Game class controls the entire game execution from start to finish
    '''
    def __init__(self, specificseed=None, msgblocking=True, usedisplay=True, timing=False):
        # Properties
        self.running = False
        '''If the game is running'''
        self.seed = None
        '''Random seed for random calls'''
        self.specificseed = specificseed
        '''Set when recreating a seed'''
        self.messageblocking = msgblocking
        '''Set to true to pause on multiple messages being displayed'''
        self.usedisplay = usedisplay
        '''Decides if to set up the game for displaying'''
        self.previousevent = ''
        '''Used for key motions of multiple characters'''
        self.turn = 0
        '''Keeps track of game turn'''

        # Objects
        self.GameState = GameState.PLAYING
        '''Controls the state of the game'''
        self.Display = display.Display()
        '''Utility class to organize displaying to the engine'''
        self.Engine = engine.Engine(debug=True)
        '''Connection to for displaying and events'''
        self.LevelManager = level.LevelManager()
        '''Handles the levels'''
        self.MenuManager = menu.MenuManager()
        '''Holds all information for displaying menus'''
        self.Animator = animation.Animator()
        '''Holds the animation queue'''
        #self.Messager: Messager = None
        '''Connection to the message queue instance'''
        self.playerFOV = True
        '''Use player FOV to generate map'''
        #self.Timing = Timing(Timing)
        '''Timing for measurements'''
        #self.Logger.debugOn = not timing
        #self.Timing.allowTiming = timing

    def start(self, stdscr: curses.window | None = None):
        '''
        Entry point for the game to start, will call the main loop after
        full initialization
        '''
        logger.Logger.init()
        self.display_setup(stdscr)
        self.game_setup()
        self.main()

    def display_setup(self, stdscr: curses.window | None, timedelay: int=0):
        '''
        Sets up the display for outputting to the screen
        '''
        if stdscr and self.usedisplay:
            # initialize engine
            self.Engine.init(stdscr, timedelay)
            # setup display
            self.Display.init(self.Engine.termrows, self.Engine.termcols,
                              levelorigin=config.LEVELORIGIN)
        else:
            # need to initialize colors without curses module
            color.Color(display=False)

    def game_setup(self):
        '''
        Sets up the game from a fresh start
        '''
        #self.Timing.start('Game Setup')
        # start running
        self.running = True
        # reset turn
        self.turn = 1
        # set up objects
        if self.specificseed is None:
            self.seed = secrets.randbits(64)
        else:
            self.seed = self.specificseed
        self.RNG = random.Random(self.seed)
        logger.Logger.log(f'SEED: {self.seed}')
        self.MenuManager.init(self.turn)
        self.LevelManager.init(
                totallevels=config.TOTALLEVELS,
                currentz=0,
                levelrows=config.ROWS,
                levelcols=config.COLS,
                rng=self.RNG)
        self.LevelManager.level_setup_default()
        # update player FOV
        self.LevelManager.Player.update_mental_map(self.LevelManager.get_curr_level())

    def main(self):
        '''
        Main process
        '''
        while self.running:
            # check for events
            event,eventtype = self.process_events()
            # update the game
            if eventtype == Event.CLEAR:
                self.clear_state()
            elif eventtype == Event.EVENT :
                self.loop(event)
            # output screen buffer to terminal
            self.render()
        self.end()

    def process_events(self):
        '''
        Gets an event and it's respective energy (continuously polling)
        '''
        if self.GameState != GameState.RUNNING:
            event = self.Engine.read_input()
            eventtype,event = self.event_type(event)
        else:
            # do not check for events if running
            eventtype = Event.EVENT
            event = ' '
            #self.Engine.pause(CHARGE_FRAME_DELAY)
        return event,eventtype

    def clear_state(self):
        '''Clears the current message'''
        # clear the message queue
        #self.MenuManager.MessageMenu.clear()
        # grab new message
        self.messages()
        # update inventory menu
        #self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)

    def loop(self, event):
        '''
        Execute one loop in the game loop
        '''

        self.turn += 1

        # event was valid, save it
        self.previousevent = event

        # update the turn
        self.MenuManager.StatusMenu.update(self.turn)

        # clear current message
        #self.MenuManager.MessageMenu.clear()

        # update all entities
        self.LevelManager.update_level(self.Animator, event)

        # update player FOV
        self.LevelManager.Player.update_mental_map(self.LevelManager.get_curr_level())

        # update health menu

        # update inventory menu

        if not self.GameState == GameState.END:
            if self.win():
                self.state_machine('endgame')
                #self.Messager.addMessage('You won!')
            elif self.lose():
                self.state_machine('endgame')
                #self.Messager.addMessage('You died!')

        # update and grab any messages in the queue
        self.messages()

    def render(self):
        '''Render the current game state to the screen'''
        # rewrite all the map buffers and menu buffers to the screen
        level = self.LevelManager.get_curr_level()
        if level:
            screenbuffer,colorbuffer = self.Display.prepare_buffers(self.LevelManager,
                                                                    self.MenuManager,
                                                                    self.playerFOV)
            # animations
            self.animations(copy.deepcopy(screenbuffer), copy.deepcopy(colorbuffer))
        else:
            screenbuffer = []
            colorbuffer = []
        # display through engine
        if self.Engine.frame_ready():
            # output
            self.Engine.output(screenchars=screenbuffer,
                                screencolors=colorbuffer)

    def win(self):
        '''Returns true if the game has been won'''
        #if self.LevelManager.Player.z == self.LevelManager.TotalLevels-1:
        #    return True
        return False

    def lose(self):
        '''Returns if the game is lost'''
        if not self.LevelManager.Player.Health.alive:
            return True
        return False 

    def end(self):
        '''Called when the game ends'''
        pass

    def messages(self):
        '''Deal with messages in the queue'''
        '''
        self.MenuManager.MessageMenu.update(blocking=self.MessageBlocking)
        if self.Messager.MsgQueue:
            # still more messages to process, msg queue should never be full if
            # non blocking mode is on
            self.stateMachine('msgQFull')
        else:
            self.stateMachine('msgQEmpty')
            '''
        pass

    def animations(self, screenbuffer, colorbuffer):
        '''Display animations queued'''
        if not self.Animator.AnimationQueue:
            return
        # get longest animation
        maxframes = max([len(list(x.frames.keys()))
                         for x in self.Animator.AnimationQueue])
        for framecounter in range(maxframes):
            # go through each animation
            for anim in self.Animator.AnimationQueue:
                if framecounter >= len(list(anim.frames.keys())):
                    continue
                ar, ac = anim.origin[0], anim.origin[1]
                # add frame array to the screen
                for r,row in enumerate(anim.frames[str(framecounter)]):
                    for c,col in enumerate(row):
                        if not col:
                            continue
                        rw, cl = self.Display.level_to_screen_pos(ar+r,ac+c)
                        screenbuffer[rw][cl] = col
                        colorbuffer[rw][cl] = anim.color
            # display through engine
            if self.Engine.frame_ready():
                # output
                self.Engine.output(screenchars=screenbuffer,
                                    screencolors=colorbuffer)
            self.Engine.pause(anim.delay)
        # done with all animations
        self.Animator.clearQueue()

    def event_type(self, event):
        '''
        Process key press event from engine
            NA:    does not count as an action
            CLEAR: will not cause an update because turn counter does not increase, updates menus
            EVENT: counts as a energy for updating entities
        '''
        # Disregard empty events
        if not event:
            return Event.NA,event
        # Motions
        if self.GameState == GameState.MOTION:
            self.state_machine('donemotion')
            if self.previousevent == 't' or self.previousevent == '5':
                # Throwing/Charge Action
                # expects a direction
                if not event.isdigit() or event == '5':
                    #self.Messager.addMessage('Invalid direction!')
                    return Event.CLEAR,event
                # valid direction increment turn
                # return the combined event
                if self.previousevent == '5':
                    self.state_machine('startrun')
                return Event.EVENT,self.previousevent+event
            elif self.previousevent == 'e' or self.previousevent == 'u':
                # Inventory Action
                return Event.EVENT,self.previousevent+event
        if event == chr(curses.ascii.ESC) or event == 'q':
            # QUIT
            self.running = False
        elif event == 'r':
            # RESET
            self.state_machine('reset')
            self.game_setup()
        elif event == 'f':
            # TOGGLE FOV
            self.playerFOV = not self.playerFOV
        elif event == ' ':
            # DO NOTHING - clears msg queue
            return Event.CLEAR,event
        elif ((event == 't' or event == '5') and
              self.GameState == GameState.PLAYING):
            # Multi key action
            #self.Messager.addMessage('Direction?')
            self.state_machine('motion')
            self.previousevent = event
            return Event.CLEAR,event
        elif ((event == 'e' or event == 'u') and
              self.GameState == GameState.PLAYING):
            # Multi key action
            if event == 'e':
                #self.Messager.addMessage('Equip what?')
                pass
            elif event == 'u':
                #self.Messager.addMessage('Unequip what?')
                pass
            self.state_machine('motion')
            self.previousevent = event
            return Event.CLEAR,event
        elif self.GameState == GameState.PLAYING:
            # PLAYER ACTION
            return Event.EVENT,event
        # Defaults to returning NA for no action
        return Event.NA,event

    def state_machine(self, event):
        '''
        Change the game state
        '''
        if event == 'msgQFull' and self.GameState == GameState.PLAYING:
            # too many messages to display, block user input until resolved
            self.GameState = GameState.PAUSEONMSG
        elif event == 'msgQEmpty' and self.GameState == GameState.PAUSEONMSG:
            # if paused and msg queue is cleared, go back to normal
            self.GameState = GameState.PLAYING
        elif event == 'endgame':
            self.GameState = GameState.END
        elif event == 'reset':
            self.GameState = GameState.PLAYING
        elif event == 'motion' and self.GameState == GameState.PLAYING:
            # start the key motion
            self.GameState = GameState.MOTION
        elif event == 'donemotion' and self.GameState == GameState.MOTION:
            # end the key motion
            self.GameState = GameState.PLAYING
        elif event == 'startrun' and self.GameState == GameState.PLAYING:
            # start the charge
            self.GameState = GameState.RUNNING
        elif event == 'endrun' and self.GameState == GameState.RUNNING:
            # end the charge
            self.GameState = GameState.PLAYING
