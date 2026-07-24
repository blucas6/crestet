import curses
import argparse
import timing
import game
import training
import logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crestet Game Options')
    parser.add_argument('-a', '--agent', action='store_true', help='Run the agent')
    parser.add_argument('-s', '--seed', type=int, help='Provide the game seed')
    parser.add_argument('-t', '--timing', action='store_true',
                        help='Turn on timing measurements\n'\
                             'Timing is on by default for profiling')
    parser.add_argument('-d', '--display', action='store_true',
                        help='Turns the display on\n'\
                                'Display is on by default when playing\n'\
                                'Display is off by default for agents')
    parser.add_argument('-p', '--profiling', action='store_true',
                        help='Runs random games to get a timing analysis')
    parser.add_argument('-r', '--release', action='store_true',
                        help='Runs the game in Release mode (debug log off)')
    parser.add_argument('-c', '--combat', action='store_true',
                        help='Runs a combat analysis test')
    args = parser.parse_args()

    logging.basicConfig(
        level = logging.INFO,
        filename = 'app.log',
        filemode = 'w',
        format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.agent:
        training = training.Training(seed=args.seed, display=args.display, timing=args.timing) 
        training.start()
        training.run()
    elif args.profiling:
        profiling = timing.Profiling(seed=args.seed, display=args.display, timing=True)
        profiling.start()
        profiling.run()
    elif args.combat:
        combat = timing.CombatTest(seed=args.seed, display=args.display, timing=False)
        combat.start()
        combat.run()
    else:
        g = game.Game(seed=args.seed, timing=args.timing, logging=not args.release)
        g.start()
        g.main()
