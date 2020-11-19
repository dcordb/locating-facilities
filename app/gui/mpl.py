from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backend_bases import NavigationToolbar2
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from app.models.utils import Point, PointW
from typing import List

class FacilitiesCanvas(FigureCanvas):
    '''
    Represents a canvas to plot facilities into.
    '''

    def __init__(self, fig: Figure) -> None:
        FigureCanvas.__init__(self, fig)
        self.setSizePolicy(qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding)

    def updateCanvas(self, near: List[PointW] = [], far: List[PointW] = [], *sols) -> None:
        x = [0, 1, 2, 3, 2, 2]
        y = [0, 2, 4, 1, 3, 3]

        self.ax = self.figure.subplots()
        self.ax.scatter(x, y)
        self.draw()

    def mplMouseMove(self, event):
        pass

class FacilitiesToolbar(NavigationToolbar2, qtw.QToolBar):
    '''
    Represents the toolbar to work with facilities canvas plot.
    '''

    def __init__(self, canvas) -> None:
        qtw.QToolBar.__init__(self)
        NavigationToolbar2.__init__(self, canvas)

    # functions required by MPL to be implemented

    # def set_cursor(self, cursor):
    #     pass

    # def draw_rubberband(self):
    #     pass

    # def set_message(self):
    #     pass

    # def set_history_buttons(self):
    #     pass