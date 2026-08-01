import time
import datetime
import logging

Logger = logging.getLogger(__name__)

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
