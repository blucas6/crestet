import curses
import argparse
from game import Game

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Roguelike Training')
    parser.add_argument('-e', '--environment', action='store_true',
                                help='Run the training environment')
    parser.add_argument('-s', '--seed', type=int,
                                help='Provide the environment a seed')
    parser.add_argument('-d', '--display', action='store_true',
                                help='Turn the display on in the environment')
    parser.add_argument('-t', '--timing', action='store_true',
                                help='Turn on timing measurements')
    args = parser.parse_args()

    if args.environment:
        pass
    else:
        g = Game(specificseed=args.seed, timing=args.timing)
        curses.wrapper(g.start)
