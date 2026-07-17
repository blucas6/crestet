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
import utility

class Game:
    '''
    Game class controls the entire game execution from start to finish
    '''
    def __init__(self, seed=None, msgblocking=True, usedisplay=True,
                 timing=False, logging=True):
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
        self.viewing_level = -1

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

        # Logging
        if timing:
            logger.Logger.logging = False
        else:
            logger.Logger.logging = logging


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

            logger.Logger.log(f'Game Settings:')
            logger.Logger.log(f'  Running: {self.running}')
            logger.Logger.log(f'  Seed: {self.seed}')
            logger.Logger.log(f'  Messages Will Block: {self.messageblocking}')
            logger.Logger.log(f'  Display: {self.usedisplay}')
            logger.Logger.log(f'  Turn: {self.turn}')
            logger.Logger.log(f'  Player FOV: {self.playerFOV}')
            logger.Logger.log(f'  Timing: {tt.Timing.allowTiming}')
            logger.Logger.log(f'  Total Levels: {self.LevelManager.totallevels}')

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
            # menus
            leveling = self.LevelManager.Player.Leveling
            lvl = leveling.curr_level
            xp = leveling.xp
            nextlv = leveling.nextlv
            self.MenuManager.init(self.Messager, self.messageblocking, self.turn, lvl, xp, nextlv)
            # update menu health
            self.MenuManager.HealthMenu.update(self.LevelManager.Player.Health)
            # update menu z level
            self.MenuManager.DepthMenu.update(self.LevelManager.currentz)
            # update inventory
            self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)
            tt.Timing.end()

        except Exception as ex:
            self.end(errorex=ex, stack=traceback.format_exc())

    def main(self):
        '''Main loop'''
        if not self.running:
            return
        try:
            self.render()
            while self.running:
                event = self.Engine.read_input()
                self.game_loop(event)
            self.end()
        except Exception as ex:
            self.end(errorex=ex, stack=traceback.format_exc())

    def game_loop(self, event):
        '''
        Single game loop based on an event
        '''
        eventtype,event = self.process_events(event)
        if eventtype == state.Event.CLEAR:
            self.clear_state()
        elif eventtype == state.Event.BLANK:
            # clear the previous message
            self.MenuManager.MessageMenu.clear()
            self.messages()
        elif eventtype == state.Event.EVENT:
            # event was valid, save it
            self.previousevent = event

            # update the player before the rest of the game
            energy = self.LevelManager.update_player(self.Animator,
                    self.Messager, self.MenuManager, self.StateMachine, event)

            # render player move
            self.render()

            # update the game
            self.loop(energy)
        # output screen buffer to terminal
        if eventtype != state.Event.NA:
            logger.Logger.log(f'RENDER')
            self.render()

    def process_events(self, event):
        '''
        Gets an event and it's respective energy (continuously polling)
        '''
        if self.StateMachine.GameState != state.GameState.RUNNING:
            eventtype,event = self.event_type(event)
        else:
            # do not check for events if running
            eventtype = state.Event.EVENT
            event = ' '
            # do not call engine pause if the display is off
            if self.usedisplay:
                self.Engine.pause(config.CHARGE_FRAME_DELAY)
        return eventtype,event

    def clear_state(self):
        '''Clears all active states'''
        # clear the message queue
        self.MenuManager.MessageMenu.clear()
        # grab new message
        self.messages()
        # update inventory menu
        self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)
        # clear any engine cursors
        if self.Display.cursor_on:
            self.Engine.toggle_cursor(0)
            self.Display.cursor_on = False
        # clear viewing level 
        self.viewing_level = -1

    def loop(self, energy):
        '''
        Execute one loop in the game loop
        '''

        logger.Logger.log(f'GAMESTATE: {self.StateMachine.GameState}')

        # increment the turn
        self.turn += 1

        # clear current message
        self.MenuManager.MessageMenu.clear()

        if self.StateMachine.GameState == state.GameState.INTERACTING and self.StateMachine.callback:
            self.StateMachine.callback(self.StateMachine, self.MenuManager, event)
        else:
            # update all entities
            self.LevelManager.update_all(self.Animator, self.Messager, self.MenuManager, self.StateMachine, energy)

            # end the player charge, get back into playing mode
            if (self.StateMachine.GameState == state.GameState.RUNNING and
                not self.LevelManager.Player.Charge.charging):
                self.StateMachine.new_state('endrun')

        # update player FOV
        self.LevelManager.Player.update_mental_map(self.LevelManager.get_curr_level())

        # check for ending the game
        if not self.StateMachine.GameState == state.GameState.END:
            if self.win():
                self.StateMachine.new_state('endgame')
                self.Messager.add_message('You won!')
            elif self.lose():
                self.StateMachine.new_state('endgame')
                self.Messager.add_message('You died!')

        # update and grab any messages in the queue
        self.messages()

        ## MENUS
        # update status menu
        player = self.LevelManager.Player
        lvl = player.Leveling.curr_level
        currxp = player.Leveling.xp
        nextlv = player.Leveling.nextlv
        self.MenuManager.StatusMenu.update(self.turn, lvl, currxp, nextlv)

        # update health menu
        self.MenuManager.HealthMenu.update(self.LevelManager.Player.Health)

        # update menu z level
        self.MenuManager.DepthMenu.update(self.LevelManager.currentz)

        # update inventory menu
        self.MenuManager.InventoryMenu.update(self.LevelManager.Player.Inventory)


    def render(self):
        '''Render the current game state to the screen'''
        if not self.usedisplay:
            return

        # do animations before the screen changes 
        self.animations(self.Display.screenbuffer, self.Display.colorbuffer)

        if self.StateMachine.GameState == state.GameState.VIEWING:
            currlevel = self.LevelManager.Levels[self.viewing_level]
        else:
            currlevel = self.LevelManager.get_curr_level()

        # get the either the entire level or the FOV
        if (self.StateMachine.GameState != state.GameState.VIEWING and
            self.playerFOV):
            entitylayer = self.LevelManager.Player.mentalmap
        elif currlevel:
            entitylayer = currlevel.EntityLayer
        else:
            entitylayer = []

        # make sure there is a level to grab from
        if currlevel:
            lightlayer = currlevel.LightLayer
        else:
            lightlayer = []

        screenbuffer,colorbuffer = self.Display.prepare_buffers(entitylayer,
                                                                lightlayer,
                                                                self.MenuManager)
        # display through engine
        if self.usedisplay and self.Engine.frame_ready():
            # output
            self.Engine.output(screenchars=screenbuffer,screencolors=colorbuffer)

        if self.Display.cursor_on:
            self.Engine.toggle_cursor(config.CURSOR_HIGHLIGHT)
            cursor_position = self.Display.level_to_screen_pos(*self.Display.cursor_position)
            self.Engine.move_cursor(cursor_position)

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

    def end(self, errorex=None, stack=''):
        '''Called when the game ends'''
        self.running = False
        if self.usedisplay:
            self.Engine.end()
        tt.Timing.show()
        if errorex:
            error_str = f'\n**Critical Failure**\n{type(errorex).__name__}: {errorex}\n\n{stack}' 
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

    def animations(self, original_screenbuffer, original_colorbuffer):
        '''Display animations queued'''
        if not self.Animator.AnimationQueue:
            return

        # go through each animation
        for anim in self.Animator.AnimationQueue:
            for num in anim.frames.keys():
                # reset buffers
                screenbuffer = self.Display.get_new_buffer(original_screenbuffer)
                colorbuffer = self.Display.get_new_buffer(original_colorbuffer) 
                self.Display.add_animation_frame(screenbuffer, colorbuffer, anim, num)
                # display through engine
                if self.Engine.frame_ready():
                    # output
                    self.Engine.output(screenchars=screenbuffer,
                                        screencolors=colorbuffer)
                self.Engine.pause(anim.delay)
            if anim.finalframe:
                # get copy buffers to reset to after each frame
                screenbuffer = self.Display.get_new_buffer(original_screenbuffer)
                colorbuffer = self.Display.get_new_buffer(original_colorbuffer) 
                self.Display.add_animation_frame(screenbuffer, colorbuffer,
                                                 anim, list(anim.frames.keys())[-1])
        # done with all animations
        self.Animator.clearQueue()

    def observation_event(self, event):
        if not event.isdigit():
            return state.Event.NA, event
        key = int(event)
        row,col = utility.get_new_pos(self.Display.cursor_position, key)
        self.Display.cursor_position = [row,col]
        if self.LevelManager.within_level((row,col), self.LevelManager.currentz):
            msg = ''
            map = []
            if self.playerFOV:
                map = self.LevelManager.Player.mentalmap[row][col]
            else:
                level = self.LevelManager.get_curr_level()
                if level:
                    map = level.EntityLayer[row][col]
            for ix,ent in enumerate(map):
                msg += ent.name
                if ix != len(map)-1:
                    msg += ','
            self.Messager.add_message(msg)
        return state.Event.BLANK, event

    def view_event(self, event):
        if self.viewing_level == -1:
            self.viewing_level = self.LevelManager.Player.z
        if event == '<':
            if self.viewing_level + 1 < len(self.LevelManager.Levels):
                self.viewing_level += 1
        elif event == '>':
            if self.viewing_level - 1 >= 0:
                self.viewing_level -= 1
        self.Messager.add_message(f'Viewing Level: {self.viewing_level}')
        return state.Event.BLANK, event
    
    def motion_event(self, event):
        '''Handles events that are part of a motion'''
        self.StateMachine.new_state('done')
        # Throwing/Charge Action
        if self.previousevent == 't' or self.previousevent == '5' or self.previousevent == 'F':
            # expects a direction
            if not event.isdigit() or event == '5':
                self.Messager.add_message('Invalid direction!')
                return state.Event.CLEAR,event
            # valid direction increment turn
            # return the combined event
            if self.previousevent == '5':
                self.StateMachine.new_state('startrun')
            return state.Event.EVENT,self.previousevent+event
        # Inventory Action
        elif self.previousevent == 'e' or self.previousevent == 'u':
            return state.Event.EVENT,self.previousevent+event
        return state.Event.CLEAR,event

    def player_event(self, event):
        '''Process all events that are player actions'''
        # Multi key action
        if event == 't' or event == '5' or event == 'e' or event == 'u' or event == 'F':
            # throw
            if event == 't':
                if not self.LevelManager.Player.Inventory.has_ammo():
                    self.Messager.add_message('No ammo')
                    return state.Event.CLEAR,event
                else:
                    self.Messager.add_message('Direction?')
            # equip
            elif event == 'e':
                self.Messager.add_message('Equip what?')
            # unequip
            elif event == 'u':
                self.Messager.add_message('Unequip what?')
            else:
                self.Messager.add_message('Direction?')
            self.StateMachine.new_state('motion')
            self.previousevent = event
            return state.Event.CLEAR,event
        else:
            # Player
            return state.Event.EVENT,event

    def reset(self, new_seed=False):
        '''Restarts the game, new seed will generate a new game'''
        if new_seed:
            self.seed = None
        self.StateMachine.new_state('reset')
        self.MenuManager.showinteract = False
        self.game_setup()

    def event_type(self, event):
        '''
        Process key press event from engine
            NA:    does not count as an action
            CLEAR: will not cause an update because turn counter does not increase, updates menus
            EVENT: counts as a energy for updating entities
        '''
        # Disregard empty events
        if not event:
            return state.Event.NA,event
        # GAME ACTIONS
        if event == 'q':
            # QUIT
            self.running = False
        elif event == 'r':
            # RESET
            self.reset()
            return state.Event.BLANK,event
        elif event == 'R':
            # RESET with new SEED
            self.reset(new_seed=True)
            return state.Event.BLANK,event
        elif event == 'f':
            # TOGGLE FOV
            self.playerFOV = not self.playerFOV
            return state.Event.BLANK,event
        elif event == 'o':
            # START OBSERVATION TOOL
            self.StateMachine.new_state('looking')
            if self.StateMachine.GameState == state.GameState.LOOKING:
                self.Display.cursor_on = True
                prow, pcol = (self.LevelManager.Player.row, self.LevelManager.Player.col)
                self.Display.cursor_position = [prow,pcol]
                self.Messager.add_message('-- Observation Tool --')
            return state.Event.BLANK,event
        elif event == 'v':
            # START VIEW MODE
            self.StateMachine.new_state('viewing')
            if self.StateMachine.GameState == state.GameState.VIEWING:
                self.Messager.add_message('-- View Mode --')
                self.viewing_level = self.LevelManager.Player.z
            return state.Event.BLANK,event
        elif event == ' ' or event == chr(curses.ascii.ESC):
            # DO NOTHING - clears msg queue and previous event
            self.previousevent = ''
            self.StateMachine.new_state('done')
            return state.Event.CLEAR,event
        elif self.StateMachine.GameState == state.GameState.MOTION:
            # MOTION
            return self.motion_event(event)
        elif self.StateMachine.GameState == state.GameState.PLAYING:
            # PLAYER ACTIONS
            return self.player_event(event)
        elif self.StateMachine.GameState == state.GameState.INTERACTING:
            # INTERACTING
            return state.Event.EVENT,event
        elif self.StateMachine.GameState == state.GameState.LOOKING:
            # OBSERVATION TOOL
            return self.observation_event(event)
        elif self.StateMachine.GameState == state.GameState.VIEWING:
            # VIEW MODE
            return self.view_event(event)

        # Defaults to returning NA for no action
        return state.Event.NA,event

