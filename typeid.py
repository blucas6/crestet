from enum import IntEnum, unique

@unique
class TID(IntEnum):
    NOTHING         = 0
    PLAYER          = 1

    UNKNOWN         = 2
    UNKNOWNSTRUCT   = 3

    SANDSTONE       = 11
    LIMESTONE       = 12
    QUARRYSTONE     = 13
    RUBBLE          = 14

    BARREL          = 21
    FLOOR           = 22
    STAIRUP         = 23
    STAIRDOWN       = 24
    LIGHT           = 25

    BITE            = 31
    FIST            = 32
    PECK            = 33
    CLAW            = 34
    LICK            = 35

    PLANT           = 41

    ARROW           = 51
    FRUIT           = 52
    WOOD            = 53
    SWORD           = 54
    DART            = 55
    GAMBESON        = 56
    TURTLE_SHELL    = 57
    PRECIOUS_STONE  = 58
    CORPSE          = 59

    RAVEN           = 101
    GOBLIN          = 102
    NEWT            = 103
    JELLY           = 104
    HUMAN           = 105
    LYNX            = 106
    SNAIL           = 107

    EMBER           = 1001
    SNOW            = 1002
