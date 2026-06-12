import curses
import argparse
import game
import training

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crestet Game Options')
    parser.add_argument('-a', '--agent', action='store_true', help='Run the agent')
    parser.add_argument('-s', '--seed', type=int, help='Provide the game seed')
    parser.add_argument('-t', '--timing', action='store_true', help='Turn on timing measurements')
    parser.add_argument('-d', '--display', action='store_true', help='Turns the display on\n'\
                                                        'Display is on by default when playing\n'\
                                                        'Display is off by default for agents')
    args = parser.parse_args()

    if args.agent:
        training = training.Training(seed=args.seed, display=args.display) 
        training.run()
    else:
        g = game.Game(seed=args.seed, timing=args.timing)
        g.start()
        g.main()
