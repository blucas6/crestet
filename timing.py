import time
import item
import inspect
import monster
import copy
import config
import json
import random
import datetime
import environment
import tqdm
import component
import matplotlib.pyplot as plt
import logging
import numpy as np

Logger = logging.getLogger(__name__)

class CombatTest:
    def __init__(self, seed, display, timing):
        self.display = display
        self.environment = environment.Environment(seed, display, timing)
        self.turn_delay_secs = 0.1
        self.weapons = []
        self.armor = []
        self.equipment = []
        self.monsters = []
        self.config_save = None
        self.results = {}
        self.mons_spawn_distance = 3
        self.rounds = 10

    def start(self):
        self.set_configuration()
        self.environment.start()
        self.get_equipment()
        self.get_monsters()

    def end(self):
        self.environment.end()
        with open(config.LEVEL_CONFIG_FILE, 'w+') as jfile:
            json.dump(self.config_save, jfile, indent=4)

    def get_equipment(self):
        self.weapons = [item.Sword]
        for w in self.weapons:
            if self.armor:
                for a in self.armor:
                    self.equipment.append([w(), a()])
            else:
                self.equipment.append([w()])

    def get_monsters(self):
        self.monsters = [
            obj for name,obj in inspect.getmembers(monster, inspect.isclass)
            if obj.__module__ == monster.__name__ and hasattr(obj, 'difficulty')
        ]

    def set_configuration(self):
        with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
            self.config_save = json.load(jfile)

        data = None
        with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
            data = json.load(jfile)

        data['total_levels'] = 2
        data['0']['floor'] = True
        data['0']['outer_walls'] = True
        data['0']['upstair'] = False
        data['0']['downstair'] = False
        data['0']['min_walls'] = 0
        data['0']['min_barrels'] = 0
        data['0']['lights'] = False
        data['0']['items'] = 0
        data['0']['runes'] = 0
        data['0']['mons'] = False
        data['1']['floor'] = True
        data['1']['outer_walls'] = True
        data['1']['upstair'] = False
        data['1']['downstair'] = False
        data['1']['min_walls'] = 0
        data['1']['min_barrels'] = 0
        data['1']['lights'] = False
        data['1']['items'] = 0
        data['1']['runes'] = 0
        data['1']['mons'] = False

        with open(config.LEVEL_CONFIG_FILE, 'w+') as jfile:
            json.dump(data, jfile, indent=4)

    def set_arena(self, mon, equipment):
        # generate a new game
        self.environment.reset(new_seed=True)
        levelmanager = self.environment.Game.LevelManager
        # turn off fov
        self.environment.Game.playerFOV = False
        # clear inventory
        player = self.environment.Game.LevelManager.Player
        player.Inventory = component.Inventory()
        # move player to half
        row = config.LEVELROWS // 2
        col = config.LEVELCOLS // 2
        levelmanager.move_entity(player, (row, col-self.mons_spawn_distance))
        # set up equipment
        for equip in equipment:
            player.Inventory.equip(equip)
        # place monster
        new_mon = mon()
        levelmanager.place_entity(0, new_mon, (row,col+self.mons_spawn_distance))
        return new_mon

    def run(self):
        '''Run the profiling and gather results'''

        try:

            if not self.environment.Game.running:
                return
            
            trials = [[mon,equip] for equip in self.equipment for mon in self.monsters]
            Logger.info(trials)
            num_trials = range(len(trials))
            iteratable = num_trials if self.display else tqdm.tqdm(num_trials)
            
            for stage in iteratable:
                player_average_turns = []
                monster_average_turns = []
                for round in range(self.rounds):
                    # update the configuration
                    monster = self.set_arena(trials[stage][0], trials[stage][1])

                    if self.display:
                        self.environment.render()
                        time.sleep(self.turn_delay_secs)

                    player = self.environment.Game.LevelManager.Player

                    Logger.info(f'SET ARENA')
                    Logger.info(f'{player} {monster}')
                    Logger.info(f'{player.Health} {monster.Health}')
                    Logger.info(f'{player.Inventory.show()}')

                    while (player.Health.currenthealth > 0 and
                        monster.Health.currenthealth > 0):
                        if not self.environment.Game.running:
                            break
                        
                        self.environment.Game.game_loop(str(6))

                        Logger.info(f'{player.Health} {monster.Health}')

                        if self.display:
                            time.sleep(self.turn_delay_secs)

                    turns = self.environment.Game.turn
                    if player.Health.currenthealth > 0:
                        player_average_turns.append(turns)
                        monster_average_turns.append(0)
                    else:
                        player_average_turns.append(0)
                        monster_average_turns.append(turns)

                if monster.name not in self.results:
                    self.results[monster.name] = {}
                    self.results[monster.name]['player'] = []
                    self.results[monster.name]['monster'] = []
                pavg = sum(player_average_turns) / len(player_average_turns)
                mavg = sum(monster_average_turns) / len(monster_average_turns)
                self.results[monster.name]['player'].append(pavg)
                self.results[monster.name]['monster'].append(mavg)

            self.end()
            self.plot()
        except Exception as e:
            self.end()
            print(f'ERROR: {e}')

    def plot(self):

        nplots = len(self.results.keys())
        num_cols = 2
        num_rows = (nplots + num_cols -1) // num_cols
        fig,axs = plt.subplots(num_rows, num_cols, figsize=(8,6))
        Logger.info(f'PLOTS: {nplots} {num_rows} {num_cols}')

        row = 0
        col = 0
        for monname in self.results.keys():

            categories = []
            for equipment in self.equipment:
                name = ''
                for equip in equipment:
                    name += equip.name
                categories.append(name)

            values1 = self.results[monname]['player']
            values2 = self.results[monname]['monster']
            
            x = np.arange(len(categories))
            width = 0.35
            axs[row,col].bar(x-width/2, values1, width, label='player')
            axs[row,col].bar(x+width/2, values2, width, label='monster')
            axs[row,col].set_ylabel('Turns (avg)')
            axs[row,col].set_title(f'{monname}')
            axs[row,col].set_xticks(x)
            axs[row,col].set_xticklabels(categories)
            axs[row,col].legend()
            
            col += 1
            if col >= num_cols:
                col = 0
                row += 1
            if row >= num_rows:
                break

        plt.tight_layout()
        plt.show()


class Profiling:
    '''Launch a bunch of randomized games to test FPS'''
    def __init__(self, seed, display, timing=True):
        self.display = display
        '''Boolean if the display is on'''
        self.environment = environment.Environment(seed, display, timing)
        '''Environment to run the games'''
        self.turn_delay_secs = 0.0001
        '''If using the display this will slow the speed between actions'''
        self.actions_per_game = 50
        '''Number of actions during each game'''
        self.levels_per_stage = [10, 15, 20, 30, 40, 50, 80, 100]
        '''Array of the amount of levels for each game'''
        self.fps_per_stage = []
        '''Resulting FPS on average for each game'''

    def start(self):
        '''Launch the environment'''
        Timing.clear_file()
        self.environment.start()

    def update_level_amount(self, total_levels):
        '''Update the config with a new amount of levels'''
        data = None
        with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
            data = json.load(jfile)

        data['total_levels'] = total_levels

        with open(config.LEVEL_CONFIG_FILE, 'w+') as jfile:
            json.dump(data, jfile, indent=4)

    def run(self):
        '''Run the profiling and gather results'''

        if not self.environment.Game.running:
            return
        
        num_levels = range(len(self.levels_per_stage))
        iteratable = num_levels if self.display else tqdm.tqdm(num_levels)
        
        for stage in iteratable:
            # update the configuration
            self.update_level_amount(self.levels_per_stage[stage])
            # generate a new game
            self.environment.reset(new_seed=True)

            if self.display:
                self.environment.render()
                time.sleep(self.turn_delay_secs)

            for _ in range(self.actions_per_game):
                if not self.environment.Game.running:
                    break
                
                # random moves
                actions = [1, 2, 3, 4, 6, 7, 8, 9]
                self.environment.Game.game_loop(str(actions[random.randint(0,len(actions)-1)]))

                if self.display:
                    time.sleep(self.turn_delay_secs)

            # get timing data
            Timing.show()
            if 'Game Loop' in Timing.final_measurements:
                self.fps_per_stage.append(Timing.final_measurements['Game Loop'])
            else:
                self.fps_per_stage.append(0)

        self.environment.end()
        self.plot()

    def plot(self):
        '''Plot the FPS per game'''
        plt.figure(figsize=(8, 6))
        plt.plot(self.levels_per_stage, self.fps_per_stage, marker='o', linestyle='-', linewidth=2)
        plt.title('FPS per Game', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Levels', fontsize=12)
        plt.ylabel('FPS', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.show()


class Timing:
    '''Timing object'''

    measurements = {}
    '''Holds all measurements <measurement_name> : [<values>, ...]'''
    logfile = 'time.log'
    '''Log file'''
    current_name = ''
    '''Current measurement name being taken'''
    current_meas = []
    '''Holds [start, end] times'''
    gap = []
    '''Holds start and end time of the pause'''
    subtract = 0
    '''Holds an amount of time to subtract at the end'''
    allowTiming = True
    '''Calling the timing functions will exit if this is False'''
    final_measurements = {}
    '''Store all the results as a key value pair'''

    @staticmethod
    def clear_file():
        '''Clears the log file'''
        with open(Timing.logfile, 'w+') as l:
            l.write('')

    @staticmethod
    def reset():
        '''Clear all saved measurements'''
        Timing.measurements = {}
        Timing.current_name = ''
        Timing.current_meas = []
        Timing.gap = []
        Timing.subtract = 0
        Timing.final_measurements = {}

    @staticmethod
    def start(name):
        '''Start the measurement'''
        if Timing.allowTiming:
            Timing.current_name = name
            Timing.current_meas = [time.perf_counter()]
    
    @staticmethod
    def pause():
        '''Pause the measurement'''
        if Timing.allowTiming:
            Timing.gap = [time.perf_counter()]
    
    @staticmethod
    def resume():
        '''Resume timing of the measurement'''
        if Timing.allowTiming:
            Timing.gap.append(time.perf_counter())
            Timing.subtract += Timing.gap[1] - Timing.gap[0]
    
    @staticmethod
    def end():
        '''End the measurement and save it'''
        if Timing.allowTiming:
            Timing.current_meas.append(time.perf_counter())
            total = Timing.current_meas[1] - Timing.current_meas[0] - Timing.subtract
            if not Timing.current_name in Timing.measurements:
                Timing.measurements[Timing.current_name] = [total]
            else:
                Timing.measurements[Timing.current_name].append(total)
            Timing.subtract = 0
            with open(Timing.logfile, 'a+') as l:
                l.write(f'\n{Timing.current_name} {Timing.current_meas}\n')
    
    @staticmethod
    def show():
        '''Prints out all measurements taken'''
        if Timing.allowTiming:
            with open(Timing.logfile, 'a+') as l:
                l.write(f'Timing Analysis {datetime.datetime.now()}\n\n')
                for measurement, times in Timing.measurements.items():
                    if len(times) > 1:
                        avg = sum([x for x in times]) / len(times)
                        Timing.final_measurements[measurement] = 1/avg
                        l.write(f'{measurement}\n')
                        l.write(f'  Averg: {avg} (sec)\n')
                        l.write(f'  Loops: {len(times)}\n')
                        l.write(f'  FPS:   {1/avg}\n')
                    elif len(times) > 0:
                        Timing.final_measurements[measurement] = 1/times[0]
                        l.write(f'{measurement}\n')
                        l.write(f'  Time: {times[0]} (sec)\n')
                        l.write(f'  FPS:  {1/times[0]}\n')
                    else:
                        l.write(f'{measurement}\n')
                        l.write(f'  Time: (sec)\n')
                        l.write(f'  FPS:  \n')
                l.write('\n\n')
