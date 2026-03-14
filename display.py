import color as c
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

    def init(self, termrows, termcols, levelorigin):
        '''Setup the buffers'''
        # create buffers
        self.screenbuffer = [[' ' for _ in range(termcols-1)] 
                                    for _ in range(termrows-1)]
        self.colorbuffer = [[c.Color().white for _ in range(termcols-1)] 
                                    for _ in range(termrows-1)]
        # colors must be accessed after engine has been initialized
        self.unknowncolor = c.Color().white
        self.levelorigin = levelorigin

    def prepare_buffers(self, levelmanager, menumanager, useplayerFOV):
        '''Build the buffers to send to the engine'''

        if useplayerFOV:
            entitylayer = levelmanager.Player.mentalmap
        else:
            entitylayer = levelmanager.get_curr_level().EntityLayer
        lightlayer = levelmanager.get_curr_level().LightLayer

        # go through entity layer
        self.render_entitylayer(entitylayer)

        # go through light layer
        self.render_lightlayer(lightlayer)
        
        # add menus
        self.render_menus(menumanager)

        return self.screenbuffer, self.colorbuffer

    def render_menus(self, menumanager):
        for menu in menumanager.get_menus():
            for r,row in enumerate(menu.text):
                for c,ch in enumerate(row):
                    rw = r+menu.origin[0]
                    cl = c+menu.origin[1]
                    if rw < len(self.screenbuffer) and cl < len(self.screenbuffer[rw]):
                        self.screenbuffer[rw][cl] = ch

    def render_lightlayer(self, lightlayer):
        for r,row in enumerate(lightlayer):
            for c,_ in enumerate(row):
                rw, cl = self.level_to_screen_pos(r,c)
                if lightlayer[r][c]:
                    color = c.Color().yellow
                    self.colorbuffer[rw][cl] = color

    def render_entitylayer(self, entitylayer):
        # go through entity layer
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
        return r+self.levelorigin[0], c+self.levelorigin[1]

