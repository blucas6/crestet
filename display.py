import color as clr
import tower
import logger

class Display:
    '''Utility class to display screens with an engine class'''
    def __init__(self):
        self.screenbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.colorbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.unknownglyph = ' '
        '''Glyph to show unexplored area'''
        self.unknowncolor = None
        '''Color of unknown area'''
        self.levelorigin = (-1,-1)
        '''Where the levels are placed on the screen'''
        self.termrows = 0
        '''Total terminal rows'''
        self.termcols = 0
        '''Total terminal columns'''
        self.cursor_on = False
        '''Controls whether the engine cursor is on or not'''
        self.cursor_position = [0,0]
        '''Current position of the cursor on the level (not the screen position)'''

    def init(self, termrows, termcols, levelorigin):
        '''Setup the buffers'''
        # create buffers
        self.termrows = termrows
        self.termcols = termcols
        self.clear_buffers()
        # colors must be accessed after engine has been initialized
        self.unknowncolor = clr.Color().white
        self.levelorigin = levelorigin

    def clear_buffers(self):
        '''Creates empty buffers'''
        self.screenbuffer = [[' ' for _ in range(self.termcols-1)] 
                                    for _ in range(self.termrows-1)]
        self.colorbuffer = [[clr.Color().white for _ in range(self.termcols-1)] 
                                    for _ in range(self.termrows-1)]

    def prepare_buffers(self, levelmanager, menumanager, useplayerFOV):
        '''Build the buffers to send to the engine'''

        self.clear_buffers()

        level = levelmanager.get_curr_level()

        # get the either the entire level or the FOV
        if useplayerFOV:
            entitylayer = levelmanager.Player.mentalmap
        elif level:
            entitylayer = level.EntityLayer
        else:
            entitylayer = []

        # make sure there is a level to grab from
        if level:
            lightlayer = level.LightLayer
        else:
            lightlayer = []

        # go through entity layer
        self.render_entitylayer(entitylayer)

        # go through light layer
        self.render_lightlayer(lightlayer)
        
        # add menus
        self.render_menus(menumanager)

        return self.screenbuffer, self.colorbuffer

    def render_menus(self, menumanager):
        '''Go through all menus and add their text buffers to the screen'''
        for menu in menumanager.get_menus():
            for r,row in enumerate(menu.text):
                for c,ch in enumerate(row):
                    rw = r+menu.origin[0]
                    cl = c+menu.origin[1]
                    if rw < len(self.screenbuffer) and cl < len(self.screenbuffer[rw]):
                        self.screenbuffer[rw][cl] = ch
                        self.colorbuffer[rw][cl] = clr.Color().white

    def render_lightlayer(self, lightlayer):
        '''Add light highlighting to the screen'''
        color = clr.Color().bright_yellow
        for r,row in enumerate(lightlayer):
            for c,_ in enumerate(row):
                rw, cl = self.level_to_screen_pos(r,c)
                if lightlayer[r][c]:
                    self.colorbuffer[rw][cl] = color

    def render_entitylayer(self, entitylayer):
        '''Go through the entity layer and add it to the screen'''
        for r,row in enumerate(entitylayer):
            for c,col in enumerate(row):
                rw, cl = self.level_to_screen_pos(r,c)
                # find top most entity
                if not entitylayer[r][c]:
                    glyph = self.unknownglyph
                    color = self.unknowncolor
                elif len(entitylayer[r][c]) == 1:
                    glyph = entitylayer[r][c][0].glyph
                    color = entitylayer[r][c][0].color
                else:
                    idx = max(range(len(entitylayer[r][c])),
                            key=lambda i:entitylayer[r][c][i].layer)
                    glyph = entitylayer[r][c][idx].glyph
                    color = entitylayer[r][c][idx].color
                if not self.bounds_check(self.screenbuffer, rw, cl):
                    continue
                # add glyph
                self.screenbuffer[rw][cl] = glyph
                if not self.bounds_check(self.colorbuffer, rw, cl):
                    continue
                # add color
                self.colorbuffer[rw][cl] = color

    def bounds_check(self, buffer, r, c):
        '''
        Checks if a position is valid within the screen buffer
        '''
        if (r > len(buffer)-1 or c > len(buffer[r])-1):
            return False
        return True

    def level_to_screen_pos(self, r, c):
        '''Helper function to convert an entity position to a screen position'''
        return r+self.levelorigin[0], c+self.levelorigin[1]

    def add_animation_frame(self, screenbuffer, colorbuffer, anim, key):
        '''Add the glyphs for the animation to the screen'''
        ar, ac = anim.origin[0], anim.origin[1]
        # add frame array to the screen
        for r,row in enumerate(anim.frames[key]):
            for c,col in enumerate(row):
                if not col:
                    continue
                rw, cl = self.level_to_screen_pos(ar+r,ac+c)
                screenbuffer[rw][cl] = col
                colorbuffer[rw][cl] = anim.color

