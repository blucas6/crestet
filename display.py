import color as clr
import utility
import tower
import entity
import engine
import config
import logging

Logger = logging.getLogger(__name__)

class Display:
    '''Utility class to display screens with an engine class'''
    def __init__(self):
        self.screenbuffer: list[list[str]] = list
        '''2D buffer the size of the terminal for outputting to engine'''
        self.colorbuffer: list[list[clr.Color]] = list
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
        self.displayon = True
        self.Engine = engine.Engine()

    def init(self, usedisplay, levelorigin, timedelay: int=0):
        '''Setup the buffers'''
        self.displayon = usedisplay
        if self.displayon:
            self.Engine.init(timedelay)
            self.termrows = self.Engine.termrows
            self.termcols = self.Engine.termcols
        # create buffers
        self.clear_buffers()
        # colors must be accessed after engine has been initialized
        self.unknowncolor = clr.Color().white
        self.levelorigin = levelorigin

    def pause_engine(self, delay):
        # do not call engine pause if the display is off
        if self.displayon:
            self.Engine.pause(delay)

    def close_engine(self):
        if self.displayon:
            self.Engine.end()

    def clear_cursors(self):
        if self.cursor_on:
            if self.displayon:
                self.Engine.toggle_cursor(0)
            self.cursor_on = False

    def clear_buffers(self):
        '''Creates empty buffers'''
        self.screenbuffer = [[' ' for _ in range(self.termcols-1)] 
                                    for _ in range(self.termrows-1)]
        self.colorbuffer = [[clr.Color().white for _ in range(self.termcols-1)] 
                                    for _ in range(self.termrows-1)]

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

    def render_lightlayer(self, entitylayer, lightlayer):
        '''Add light highlighting to the screen'''
        color = clr.Color().bright_yellow
        for r,row in enumerate(lightlayer):
            for c,_ in enumerate(row):
                if lightlayer[r][c] and entitylayer[r][c]:
                    idx,ent = utility.get_max_entity(entitylayer[r][c])
                    rw, cl = self.level_to_screen_pos(r,c)
                    # only make non monsters glow
                    if ent.layer != entity.Layer.MONSTER_LAYER:
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

    def get_new_buffer(self, buffer):
        return [[item for item in row] for row in buffer]

    def output(self, screenbuffer, colorbuffer):
        if self.displayon and self.Engine.frame_ready():
            self.Engine.output(screenchars=screenbuffer,
                               screencolors=colorbuffer)

    def cursor_upkeep(self):
        if self.displayon and self.cursor_on:
            self.Engine.toggle_cursor(config.CURSOR_HIGHLIGHT)
            cursor_position = self.level_to_screen_pos(
                    *self.cursor_position)
            self.Engine.move_cursor(cursor_position)

    def render(self, entitylayer, lightlayer, menumanager):
        '''
        Render the current game state to the screen

        Tests depend on buffers being created even if displaying
        is turned off
        '''

        Logger.info('RENDER')

        self.clear_buffers()

        # go through entity layer
        self.render_entitylayer(entitylayer)

        # go through light layer
        self.render_lightlayer(entitylayer, lightlayer)
        
        # add menus
        self.render_menus(menumanager)

        # display through engine
        self.output(self.screenbuffer, self.colorbuffer)

        # update cursor
        self.cursor_upkeep()

    def add_animation_frame(self, screenbuffer, colorbuffer, frame, pos, color, fovpoints):
        '''Add the glyphs for the animation to the screen'''
        # add frame array to the screen
        for r,row in enumerate(frame):
            for c,col in enumerate(row):
                if not col:
                    continue
                elif (pos[0]+r,pos[1]+c) in fovpoints:
                    rw, cl = self.level_to_screen_pos(pos[0]+r, pos[1]+c)
                    screenbuffer[rw][cl] = col
                    colorbuffer[rw][cl] = color

    def get_animation_frames(self, animator, levelz, fovpoints):
        '''
        Takes in the animation queue to produce a list of modified frame 
        buffers to display
        '''
        loaded_frames = []
        loaded_colors = []
        time_delays = []

        # go through each animation
        for anim in animator.AnimationQueue:
            if anim.pos[2] != levelz:
                continue
            for num in anim.frames.keys():
                # reset buffers
                tmp_screenbuffer = self.get_new_buffer(self.screenbuffer)
                tmp_colorbuffer = self.get_new_buffer(self.colorbuffer) 
                self.add_animation_frame(tmp_screenbuffer,
                                         tmp_colorbuffer,
                                         anim.frames[num],
                                         anim.pos,
                                         anim.color,
                                         fovpoints)
                loaded_frames.append(tmp_screenbuffer)
                loaded_colors.append(tmp_colorbuffer)
                time_delays.append(anim.delay)
                
        return loaded_frames, loaded_colors, time_delays
    
    def display_animation_frames(self, frames, colors, delays):
        '''
        Frames: list of modified frame buffers (the animations)
        Colors: the modified color buffer
        Delays: pause time for each animation frame effect
        '''
        for frame,cframe,delay in zip(frames, colors, delays):
            # display through engine
            self.output(frame, cframe)
            self.pause_engine(delay)

    def play_animations(self, animator, levelz, fovpoints):
        '''Display animations queued'''

        # refreshing the screen unnecessarily every entity update will
        # cause massive slow downs
        if animator.AnimationQueue:
            lframes, lcolors, tdelays = self.get_animation_frames(animator,
                                                          levelz, fovpoints)
            self.display_animation_frames(lframes, lcolors, tdelays)

            # done with all animations
            animator.clearQueue()

            # output original screen
            self.output(self.screenbuffer, self.colorbuffer)


