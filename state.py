import enum
import logger

class Event(enum.Enum):
    '''
    Event types from user

    NA    : not an event - nothing happens
    CLEAR : clearing event - reset menus and message window, render screen
    BLANK : empty event - check message loop and render the screen, no clearing or game loop
    EVENT : normal event - full game loop
    '''
    NA = -1
    CLEAR = 0
    BLANK = 1
    EVENT = 2

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
    INTERACTING = 6
    LOOKING = 7
    VIEWING = 8

class StateMachine:
    def __init__(self):
        self.GameState = GameState.PLAYING
        '''Current state of the game'''
        self.callback = None

    def new_state(self, newstate):
        '''
        Change the game state
        '''
        if newstate == 'msgQFull':
            # too many messages to display, block user input until resolved
            self.GameState = GameState.PAUSEONMSG
        elif newstate == 'msgQEmpty' and self.GameState == GameState.PAUSEONMSG:
            # if paused and msg queue is cleared, go back to normal
            self.GameState = GameState.PLAYING
        elif newstate == 'endgame':
            self.GameState = GameState.END
        elif newstate == 'reset':
            self.GameState = GameState.PLAYING
        elif newstate == 'motion' and self.GameState == GameState.PLAYING:
            # start the key motion
            self.GameState = GameState.MOTION
        elif newstate == 'done' and (self.GameState == GameState.MOTION or
                                     self.GameState == GameState.INTERACTING or
                                     self.GameState == GameState.LOOKING):
            # end the key motion
            self.GameState = GameState.PLAYING
        elif newstate == 'startrun' and self.GameState == GameState.PLAYING:
            # start the charge
            self.GameState = GameState.RUNNING
        elif newstate == 'endrun' and self.GameState == GameState.RUNNING:
            # end the charge
            self.GameState = GameState.PLAYING
        elif (newstate == 'interact' and
             (self.GameState == GameState.PLAYING or self.GameState == self.GameState.RUNNING)):
            self.GameState = GameState.INTERACTING
        elif newstate == 'looking' and self.GameState == GameState.PLAYING:
            self.GameState = GameState.LOOKING
        elif newstate == 'viewing' and self.GameState == GameState.PLAYING:
            self.GameState = GameState.VIEWING

        logger.Logger.log(f'NEW STATE: {newstate} RESULT: {self.GameState}')


