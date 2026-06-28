import time
import config
import json
import random
import datetime
import environment
import tqdm
import matplotlib.pyplot as plt

class Profiling:
    def __init__(self, seed, display, timing=True):
        self.display = display
        self.environment = environment.Environment(seed, display, timing)
        self.turn_delay_secs = 0.002
        self.actions_per_game = 100
        self.levels_per_stage = [1, 5, 10, 20]
        self.fps_per_stage = []

    def start(self):
        Timing.clear_file()
        self.environment.start()

    def update_level_amount(self, total_levels):
        data = None
        with open(config.LEVEL_CONFIG_FILE, 'r') as jfile:
            data = json.load(jfile)

        data['total_levels'] = total_levels

        with open(config.LEVEL_CONFIG_FILE, 'w+') as jfile:
            json.dump(data, jfile, indent=4)

    def run(self):
        if not self.environment.Game.running:
            return
        
        num_levels = range(len(self.levels_per_stage))
        iteratable = num_levels if self.display else tqdm.tqdm(num_levels)
        
        for stage in iteratable:
            self.update_level_amount(self.levels_per_stage[stage])
            self.environment.reset(new_seed=True)

            if self.display:
                self.environment.render()
                time.sleep(self.turn_delay_secs)

            for actx in range(self.actions_per_game):
                if not self.environment.Game.running:
                    break
                
                actions = [1, 2, 3, 4, 6, 7, 8, 9]
                self.environment.step(actions[random.randint(0,len(actions)-1)])

                if self.display:
                    time.sleep(self.turn_delay_secs)

            Timing.show()
            # get timing data
            if 'Game Loop' in Timing.final_measurements:
                self.fps_per_stage.append(Timing.final_measurements['Game Loop'])
            else:
                self.fps_per_stage.append(0)

        self.environment.end()
        self.plot()

    def plot(self):
        plt.figure(figsize=(8, 6))
        plt.plot(self.levels_per_stage, self.fps_per_stage, marker='o', linestyle='-', linewidth=2)
        plt.title('FPS per Game', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('Games', fontsize=12)
        plt.ylabel('FPS', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.show()


class Timing:
    '''Timing object'''

    measurements = {}
    '''Holds all measurements'''
    logfile = 'time.log'
    '''Log file'''
    current_name = ''
    '''Current measurement name being taken'''
    current_meas = []
    '''Holds start and end time'''
    gap = []
    '''Holds start and end time of the pause'''
    subtract = 0
    '''Holds an amount of time to subtract at the end'''
    allowTiming = True
    final_measurements = {}

    @staticmethod
    def clear_file():
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
