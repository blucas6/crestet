import curses
import color
import argparse
import timing
import simulator
import game
import training
import logging
import ascii

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
    parser.add_argument('-z', '--color', action='store_true',
                        help='Show all colors available in your terminal')
    parser.add_argument('-x', '--ascii', action='store_true',
                help='Show all ascii characters available in your terminal')
    args = parser.parse_args()

    logging.basicConfig(
        level = logging.INFO,
        filename = 'app.log',
        filemode = 'w',
        format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # AGENT
    if args.agent:
        training = training.Training(seed=args.seed, display=args.display, timing=args.timing) 
        training.start()
        training.run()

    # PROFILING SIMULATOR
    elif args.profiling:
        profiling = simulator.Profiling(seed=args.seed, display=args.display, timing=True)
        profiling.start()
        profiling.run()

    # COMBAT SIMULATOR
    elif args.combat:
        combat = simulator.CombatTest(seed=args.seed, display=args.display, timing=False)
        combat.start()
        combat.run()

    # COLORS
    elif args.color:
        curses.wrapper(color.show_colors)

    # ASCII
    elif args.ascii:
        ascii.show_ascii()

    # MAIN
    else:
        g = game.Game(seed=args.seed, timing=args.timing)
        g.start()
        g.main()
