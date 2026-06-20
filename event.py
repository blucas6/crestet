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



class EventHandler:
    def __init__(self):
        pass

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
        elif event == 'R':
            # RESET with new SEED
            self.seed = None
            self.StateMachine.new_state('reset')
            self.MenuManager.showinteract = False
            self.game_setup()
        elif event == 'f':
            # TOGGLE FOV
            self.playerFOV = not self.playerFOV
        elif event == 'o':
            # START OBSERVATION TOOL
            self.StateMachine.new_state('looking')
        elif event == ' ' or event == chr(curses.ascii.ESC):
            self.previousevent = ''
            self.StateMachine.new_state('donemotion')
            # DO NOTHING - clears msg queue and previous event
            return Event.CLEAR,event
        elif event == 'u':
            self.LevelManager.Player.Leveling.gain_xp(1, self.LevelManager.Player, self.Messager)
            return Event.EVENT, 'u'
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

