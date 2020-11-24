from collections import namedtuple
from enum import Enum
import logging
import re

PARAMS = 3
floatRE = re.compile(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')

class Load(Enum):
    fromFile = 1
    fromSample = 2
    fromSidebar = 3

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

HELP_TEXT ='''### Tips:

- Add points on the text field on the right.

- Load them clicking `Load` button, selecting the action _Load from sidebar text field_ and corresponding model(s) to run.

- You can interact with the graph using the toolbar.

- You may save current sets of points by clicking `Save` button.

- Use quick editing feature: when you are done editing points, press `Ctrl+Shift+X` and it will load them into the graph.
'''

SidebarPlaceholderText ='''
Format:

- The i-th point has parameters x_i, y_i, w_i.

- The first n lines consists of n points representing a Near set.

- The following m lines consists of m points representing a Far set.

- The last line consists of 4 integers: xmin, xmax, ymin, ymax (the bounding box of solutions).

- Separate sets Near, Far and bounding box by a line consisting of an asterisk (*).

A valid input is shown (press Ctrl+Shift+X shorcut to add it directly, it will analyze it with both models):

'''

SidebarPlaceholderSample ='''5 3 2.111
4 1 2.654
1 -2.48 5
*
1 3 7
0 0.1 1
-2.35 5.4 1
1 2 3
*
-5.123 5 -10 10
'''

SidebarPlaceholderText += SidebarPlaceholderSample