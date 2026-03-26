import enum

import logger

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

class StateMachine:
    def __init__(self):
        self.GameState = GameState.PLAYING
        self.callback = None

    def new_state(self, newstate):
        '''
        Change the game state
        '''
        logger.Logger.log(f'NEW STATE: {newstate}')
        if newstate == 'msgQFull' and self.GameState == GameState.PLAYING:
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
        elif newstate == 'donemotion' and self.GameState == GameState.MOTION:
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
        elif newstate == 'doneinteract' and self.GameState == GameState.INTERACTING:
            self.GameState = GameState.PLAYING
