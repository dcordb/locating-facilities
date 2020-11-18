from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backend_bases import NavigationToolbar2
import matplotlib.pyplot as plt
import numpy as np

from app.models.utils import PointW
from typing import List

class FacilitiesCanvas(FigureCanvas):
    '''
    Represents a canvas to plot facilities into.
    '''

    def __init__(self, near: List[PointW], far: List[PointW]) -> None:
        pass

    def mplMouseMove(self, event):
        pass

class FacilitiesToolbar(NavigationToolbar2, qtw.QToolBar):
    '''
    Represents the toolbar to work with facilities canvas plot.
    '''

    def __init__(self, canvas, parent) -> None:
        pass

    # functions required by MPL to be implemented

    def set_cursor(self):
        pass

    def draw_rubberband(self):
        pass

    def set_message(self):
        pass

    def set_history_buttons(self):
        pass