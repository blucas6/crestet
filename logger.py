import os
import datetime

class Logger:
    '''Class to log all information to the same location'''
    logfile = 'log.log'
    logging = True

    @staticmethod
    def init(dire='', logfile='', enabled=False): 
        '''Clear and set the log file'''
        if not Logger.logging:
            return
        if logfile:
            Logger.logfile = logfile
        if dire:
            Logger.logfile = os.path.join(dire, Logger.logfile)
        directory = os.path.dirname(Logger.logfile)
        if directory and not os.path.exists(directory):
            os.makedirs(os.path.dirname(Logger.logfile))
        with open(Logger.logfile, 'w+') as l:
            l.write(f'{datetime.datetime.now()} - Starting new logger session\n')

    @staticmethod
    def log(msg):
        '''Log a message'''
        if not Logger.logging:
            return
        with open(Logger.logfile, 'a+') as l:
            l.write(f'{datetime.datetime.now()} - {msg}\n')