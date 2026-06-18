import state
import generator
import traceback
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
    def __init__(self, seed=None, msgblocking=True, usedisplay=True, timing=False):
        # Properties
        self.running = False
        '''If the game is running'''
        self.seed = seed 
        '''Random seed for random calls'''
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
        self.Generator = generator.Generator()
        '''Sets up all levels from the config'''

        # Timing
        tt.Timing.allowTiming = timing


    def start(self):
        '''
        Entry point for the game to start, will call the main loop after
        full initialization
        '''
        logger.Logger.init()

        self.display_setup()
        self.game_setup()

    def display_setup(self, timedelay: int=0):
        '''
        Sets up the display for outputting to the screen
        '''
        if self.usedisplay:
            # initialize engine
            self.Engine.init(timedelay)
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
        try:
            # timing measurement if using timing
            tt.Timing.reset()
            tt.Timing.start('Game Setup')

            # start running
            self.running = True
            # reset turn
            self.turn = 1
            # set up seed
            if self.seed is None:
                self.seed = secrets.randbits(64)
            self.RNG = random.Random(self.seed)
            # menus
            self.MenuManager.init(self.Messager, self.messageblocking, self.turn)
            # level manager
            self.LevelManager.init(self.Messager,
                                   rng=self.RNG,
                                   levelrows=config.LEVELROWS,
                                   levelcols=config.LEVELCOLS)
            # load generator and run the generation
            self.Generator.load_config(config.LEVELROWS, config.LEVELCOLS, self.RNG)
            self.Generator.generate_levels(self.LevelManager)
            # add player to the map
            self.LevelManager.place_player(config.PLAYERPOS, config.PLAYERZ)
            # update player FOV
            self.LevelManager.Player.update_mental_map(self.LevelManager.get_curr_level())
            # update menu health
            self.MenuManager.HealthMenu.update(self.LevelManager.Player.Health)
            # update menu z level
            self.MenuManager.DepthMenu.update(self.LevelManager.currentz)
            # update inventory
            self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)
            tt.Timing.end()

            logger.Logger.log(f'Game Settings:')
            logger.Logger.log(f'  Running: {self.running}')
            logger.Logger.log(f'  Seed: {self.seed}')
            logger.Logger.log(f'  Message Will Block: {self.messageblocking}')
            logger.Logger.log(f'  Display: {self.usedisplay}')
            logger.Logger.log(f'  Turn: {self.turn}')
            logger.Logger.log(f'  Player FOV: {self.playerFOV}')
            logger.Logger.log(f'  Timing: {tt.Timing.allowTiming}')
        except Exception as ex:
            self.end(error_ex=ex, stack=traceback.format_exc())

    def main(self):
        '''Main loop'''
        try:
            while self.running:
                event = self.Engine.read_input()
                self.game_loop(event)
                # output screen buffer to terminal
                self.render()
            self.end()
        except Exception as ex:
            self.end(error_ex=ex, stack=traceback.format_exc())

    def game_loop(self, event):
        '''
        Single game loop based on an event
        '''
        event,eventtype = self.process_events(event)
        if eventtype == Event.CLEAR:
            self.clear_state()
        elif eventtype == Event.EVENT:
            # update the game
            self.loop(event)

    def process_events(self, event):
        '''
        Gets an event and it's respective energy (continuously polling)
        '''
        if self.StateMachine.GameState != state.GameState.RUNNING:
            eventtype,event = self.event_type(event)
        else:
            # do not check for events if running
            eventtype = Event.EVENT
            event = ' '
            # do not call engine pause if the display is off
            if self.usedisplay:
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

        if self.StateMachine.GameState == state.GameState.INTERACTING and self.StateMachine.callback:
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

        # do animations before the screen changes 
        self.animations(copy.deepcopy(self.Display.screenbuffer),
                        copy.deepcopy(self.Display.colorbuffer))
        screenbuffer,colorbuffer = self.Display.prepare_buffers(self.LevelManager,
                                                                self.MenuManager,
                                                                self.playerFOV)
        # display through engine
        if self.usedisplay and self.Engine.frame_ready():
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

    def end(self, error_ex=None, stack=''):
        '''Called when the game ends'''
        self.running = False
        if self.usedisplay:
            self.Engine.end()
        tt.Timing.show()
        if error_ex:
            error_str = f'\n**Critical Failure**\n{type(error_ex).__name__}: {error_ex}\n\n{stack}' 
            logger.Logger.log(error_str)
            print(error_str)

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

