import color

class AnimationFrame:
    def __init__(self, frame, delay=0.01):
        self.frame = frame
        self.delay = delay

class Animation:
    '''
    Holds all data for a single animation
    '''
    def __init__(self, pos, frames: dict, color, delay=0.01):
        self.pos = pos
        '''Position of the animation relative to the map'''
        self.frames = frames
        '''Dictionary of an array of frames to display'''
        self.color = color
        '''Color of the animation'''
        self.delay = delay
        '''Delay between frames (engine will sleep)'''

class Animator:
    '''
    Holds the animation queue
    '''
    def __init__(self):
        self.AnimationQueue = []
        '''Queue of animation objects'''

    def queueUp(self, levelmanager, animation: Animation):
        '''
        Queue an animation object to be displayed
        Only queue current level animations
        '''
        if levelmanager.currentz == animation.pos[2]:
            self.AnimationQueue.append(animation)
    
    def clearQueue(self):
        '''
        Clears the animation queue
        '''
        self.AnimationQueue = []
