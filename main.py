import curses
import argparse
import timing
import game
import training
import logging

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crestet Game Options')
    parser.add_argument('-a', '--agent', action='store_true', help='run the agent')
    parser.add_argument('-s', '--seed', type=int, help='provide the game seed')
    parser.add_argument('-t', '--timing', action='store_true',
                        help='turn on timing measurements'\
                             '(timing is on by default for profiling)')
    parser.add_argument('-d', '--display', action='store_true',
                        help='turns the display ON'\
                                '(display is ON by default when playing)'\
                                '(display is OFF by default for agents)')
    parser.add_argument('-p', '--profiling', action='store_true',
                        help='runs random games to get a timing analysis')
    parser.add_argument('-c', '--combat', action='store_true',
                        help='runs a combat analysis test')
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
        g = game.Game(seed=args.seed, timing=args.timing)
        g.start()
        g.main()
