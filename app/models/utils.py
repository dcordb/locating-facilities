from collections import namedtuple
import logging

PT = namedtuple('PT', ['x', 'y', 'w', 'kind'], defaults=[0, None])

def init_logger(logger_name):
    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # create console handler and set level to debug
        ch = logging.FileHandler(f'{logger_name}.log', mode='w')
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

    return logger