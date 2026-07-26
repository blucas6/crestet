### CONFIGURATION FILES
LEVEL_CONFIG_FILE = 'levels.json'
'''Contains the json for setting up the levels'''

### ANIMATIONS
THROW_ANIM_DELAY = 0.02
'''Delay travel time in throwing animation'''

CHARGE_FRAME_DELAY = 0.01
'''Delay between frames when running'''

EXPLOSION_ANIM_DELAY = 0.05
'''Jelly explosion animation'''


### LEVEL
LEVELORIGIN = (2,2)
'''Where the levels are displayed on the screen'''
LEVELROWS = 13
'''Amount of rows in the level grid'''
LEVELCOLS = 30
'''Amount of columns in the level grid'''
MAX_RETRIES = 1000
'''Amount of retries during generation for randomness'''
LEVELMAX_ENTITIES = 10
'''Maximum entities on a square'''

## PLAYER
PLAYERPOS = [1,1]
'''Starting player position'''
PLAYERZ = 0
'''Starting player z index'''
PLAYERFOV = 20
'''Player FOV range'''
PLAYERHEALTH = 8
'''Player health amount'''


MONS_IDLE = [0,4]
'''Likeliness of brain transition'''

## NEWT
NEWT_HEALTH = 5
NEWT_SIGHTRANGE = 5
NEWT_XP = 1

## JELLY
JELLY_HEALTH = 1
JELLY_SPLASHDMG = 5
JELLY_XP = 2

## GOBLIN
GOBLIN_HEALTH = 4
GOBLIN_SIGHTRANGE = 5
GOBLIN_XP = 1

### MENUS
STATUSMENU_ORIGIN = (18,20)
STATUSMENU_SZ = [1,25]
MESSAGEMENU_ORIGIN = (0,0)
MESSAGEMENU_SZ = [1,60]
HEALTHMENU_ORIGIN = (18,1)
HEALTHMENU_BAR = 10
DEPTHMENU_ORIGIN = (19,1)
DEPTHMENU_SZ = [1,20]
INVENTORYMENU_ORIGIN = (2, 43)
INVENTORYMENU_SZ = [20,30]
INTERACTMENU_ORIGIN = (5, 5)
INTERACTMENU_SZ = [3,20]

### ENGINE
CURSOR_HIGHLIGHT = 2
