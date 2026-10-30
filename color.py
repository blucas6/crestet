import curses
from enum import IntEnum, unique

@unique
class COLOR(IntEnum):
    BLACK = curses.COLOR_BLACK
    RED = curses.COLOR_RED
    GREEN = curses.COLOR_GREEN
    YELLOW = curses.COLOR_YELLOW
    BLUE = curses.COLOR_BLUE
    MAGENTA = curses.COLOR_MAGENTA
    CYAN = curses.COLOR_CYAN
    WHITE = curses.COLOR_WHITE
    GREY = curses.COLOR_BLACK+8
    BRIGHT_RED = curses.COLOR_RED+8
    BRIGHT_GREEN = curses.COLOR_GREEN+8
    BRIGHT_YELLOW = curses.COLOR_YELLOW+8
    BRIGHT_BLUE = curses.COLOR_BLUE+8
    PINK = curses.COLOR_MAGENTA+8
    BRIGHT_CYAN = curses.COLOR_CYAN+8
    BRIGHT_WHITE = curses.COLOR_WHITE+8

def show_colors(stdscr):
    curses.start_color()
    curses.use_default_colors()
    numcolors = curses.COLORS
    stdscr.addstr(0, 0, f'Terminal supports {numcolors} colors.')
    for i in range(1, numcolors):
        curses.init_pair(i, i-1, 0)
    rows,cols = stdscr.getmaxyx()
    currrow = 3
    currcol = 0
    width = 8
    for i in range(1, numcolors):
        stdscr.attron(curses.color_pair(i))
        stdscr.addstr(currrow, currcol, f' {i-1} ')
        currcol += width
        if currcol + width > cols:
            currcol = 0
            currrow += 1
            if currrow >= rows - 1:
                break
    stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(show_colors)

