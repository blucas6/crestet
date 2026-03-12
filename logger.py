import os
import datetime

class Logger:
    '''Class to log all information to the same location'''
    logfile = 'log.log'

    @staticmethod
    def init(dire='', logfile=''):
        '''Clear and set the log file'''
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
        with open(Logger.logfile, 'a+') as l:
            l.write(f'{datetime.datetime.now()} - {msg}\n')
