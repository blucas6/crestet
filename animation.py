import color

class Animation:
    '''
    Holds all data for a single animation
    '''
    def __init__(self, origin, frames: dict, color: color.Color, delay=0.01):
        self.origin = origin 
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

    def queueUp(self, animation: Animation):
        '''
        Queue an animation object to be displayed
        '''
        self.AnimationQueue.append(animation)
    
    def clearQueue(self):
        '''
        Clears the animation queue
        '''
        self.AnimationQueue = []
