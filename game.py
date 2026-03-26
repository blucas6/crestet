import state
import engine
import timing as tt
import message
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
        self.playerFOV = True
        '''Use player FOV to generate map'''

        # Objects
        self.StateMachine = state.StateMachine()
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
        self.Messager = message.Messager()
        '''Connection to the message queue instance'''

        # Timing
        logger.Logger.debug = not timing
        tt.Timing.allowTiming = timing

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
        tt.Timing().start('Game Setup')
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
        self.MenuManager.init(self.Messager, self.messageblocking, self.turn)
        self.LevelManager.init(
                self.Messager,
                totallevels=config.TOTALLEVELS,
                currentz=0,
                levelrows=config.ROWS,
                levelcols=config.COLS,
                rng=self.RNG)
        self.LevelManager.level_setup_default((1,1))
        # update player FOV
        self.LevelManager.Player.update_mental_map(self.LevelManager.get_curr_level())
        # update menu health
        self.MenuManager.HealthMenu.update(self.LevelManager.Player.Health)
        # update menu z level
        self.MenuManager.DepthMenu.update(self.LevelManager.currentz)
        # update inventory
        self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)
        tt.Timing().end()

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
        if self.StateMachine.GameState != state.GameState.RUNNING:
            event = self.Engine.read_input()
            eventtype,event = self.event_type(event)
        else:
            # do not check for events if running
            eventtype = Event.EVENT
            event = ' '
            self.Engine.pause(config.CHARGE_FRAME_DELAY)
        return event,eventtype

    def clear_state(self):
        '''Clears the current message'''
        # clear the message queue
        self.MenuManager.MessageMenu.clear()
        # grab new message
        self.messages()
        # update inventory menu
        self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)

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
        self.MenuManager.MessageMenu.clear()

        logger.Logger.log(f'GAMESTATE: {self.StateMachine.GameState}')

        if self.StateMachine.GameState == state.GameState.INTERACTING:
            self.StateMachine.callback(self.StateMachine, self.MenuManager, event)
        else:
            # update all entities
            self.LevelManager.update_level(self.Animator, self.Messager, self.MenuManager, self.StateMachine, event)

            # end the player charge, get back into playing mode
            if (self.StateMachine.GameState == state.GameState.RUNNING and
                not self.LevelManager.Player.Charge.charging):
                self.StateMachine.new_state('endrun')

        # update player FOV
        self.LevelManager.Player.update_mental_map(self.LevelManager.get_curr_level())

        # update health menu
        self.MenuManager.HealthMenu.update(self.LevelManager.Player.Health)

        # update menu z level
        self.MenuManager.DepthMenu.update(self.LevelManager.currentz)

        # update inventory menu
        self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)

        if not self.StateMachine.GameState == state.GameState.END:
            if self.win():
                self.StateMachine.new_state('endgame')
                self.Messager.add_message('You won!')
            elif self.lose():
                self.StateMachine.new_state('endgame')
                self.Messager.add_message('You died!')

        # update and grab any messages in the queue
        self.messages()


    def render(self):
        '''Render the current game state to the screen'''
        # rewrite all the map buffers and menu buffers to the screen
        level = self.LevelManager.get_curr_level()
        if level:
            # do animations before the screen changes 
            self.animations(copy.deepcopy(self.Display.screenbuffer),
                            copy.deepcopy(self.Display.colorbuffer))
            screenbuffer,colorbuffer = self.Display.prepare_buffers(self.LevelManager,
                                                                    self.MenuManager,
                                                                    self.playerFOV)
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
        if self.LevelManager.Player.z == self.LevelManager.totallevels-1:
            return True
        return False

    def lose(self):
        '''Returns if the game is lost'''
        if not self.LevelManager.Player.Health.alive:
            return True
        return False 

    def end(self):
        '''Called when the game ends'''
        tt.Timing().show()

    def messages(self):
        '''Deal with messages in the queue'''
        self.MenuManager.MessageMenu.update()
        if self.Messager.MsgQueue:
            # still more messages to process, msg queue should never be full if
            # non blocking mode is on
            self.StateMachine.new_state('msgQFull')
        else:
            self.StateMachine.new_state('msgQEmpty')

    def animations(self, screenbuffer, colorbuffer):
        '''Display animations queued'''
        if not self.Animator.AnimationQueue:
            return
        # get copy buffers to reset to after each frame
        oldscreenbuffer = copy.deepcopy(screenbuffer)
        oldcolorbuffer = copy.deepcopy(colorbuffer)
        # go through each animation
        for anim in self.Animator.AnimationQueue:
            for num in anim.frames.keys():
                # reset buffers
                screenbuffer = copy.deepcopy(oldscreenbuffer)
                colorbuffer = copy.deepcopy(oldcolorbuffer)
                self.Display.add_animation_frame(screenbuffer, colorbuffer, anim, num)
                # display through engine
                if self.Engine.frame_ready():
                    # output
                    self.Engine.output(screenchars=screenbuffer,
                                        screencolors=colorbuffer)
                self.Engine.pause(anim.delay)
            if anim.finalframe:
                self.Display.add_animation_frame(oldscreenbuffer, oldcolorbuffer,
                                                 anim, list(anim.frames.keys())[-1])
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
        # GAME ACTIONS
        if event == 'q':
            # QUIT
            self.running = False
        elif event == 'r':
            # RESET
            self.StateMachine.new_state('reset')
            self.MenuManager.showinteract = False
            self.game_setup()
        elif event == 'f':
            # TOGGLE FOV
            self.playerFOV = not self.playerFOV
        elif event == ' ' or event == chr(curses.ascii.ESC):
            self.previousevent = ''
            self.StateMachine.new_state('donemotion')
            # DO NOTHING - clears msg queue and previous event
            return Event.CLEAR,event
        # MOTIONS 
        elif self.StateMachine.GameState == state.GameState.MOTION:
            self.StateMachine.new_state('donemotion')
            # Throwing/Charge Action
            if self.previousevent == 't' or self.previousevent == '5' or self.previousevent == 'F':
                # expects a direction
                if not event.isdigit() or event == '5':
                    self.Messager.add_message('Invalid direction!')
                    return Event.CLEAR,event
                # valid direction increment turn
                # return the combined event
                if self.previousevent == '5':
                    self.StateMachine.new_state('startrun')
                return Event.EVENT,self.previousevent+event
            # Inventory Action
            elif self.previousevent == 'e' or self.previousevent == 'u':
                return Event.EVENT,self.previousevent+event
        # PLAYER ACTIONS
        elif self.StateMachine.GameState == state.GameState.PLAYING:
            # Multi key action
            if event == 't' or event == '5' or event == 'e' or event == 'u' or event == 'F':
                if event == 'e':
                    self.Messager.add_message('Equip what?')
                elif event == 'u':
                    self.Messager.add_message('Unequip what?')
                else:
                    self.Messager.add_message('Direction?')
                self.StateMachine.new_state('motion')
                self.previousevent = event
                return Event.CLEAR,event
            else:
                # Player
                return Event.EVENT,event
        elif self.StateMachine.GameState == state.GameState.INTERACTING:
            return Event.EVENT,event

        # Defaults to returning NA for no action
        return Event.NA,event

