from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backend_bases import NavigationToolbar2
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from app.models.utils import PT
from typing import List

class FacilitiesCanvas(FigureCanvas):
    '''
    Represents a canvas to plot facilities into.
    '''

    def __init__(self, fig: Figure) -> None:
        self.fig = fig
        FigureCanvas.__init__(self, self.fig)
        self.setSizePolicy(qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding)

        self.pcs = []
        self.from_who = []

        self.mpl_connect('motion_notify_event', self.mplMouseMove)

    def updateCanvas(self, near: List[PT] = [], far: List[PT] = [], *sols) -> None:
        xnear = [ x for x, _, _, _ in near ]
        ynear = [ y for _, y, _, _ in near ]

        xfar = [ x for x, _, _, _ in far ]
        yfar = [ y for _, y, _, _ in far ]

        ax = self.fig.gca()
        ax.clear()

        if not near and not far and not sols:
            return

        self.pcs = []
        self.pcs.append(ax.scatter(xnear, ynear, label='Near'))
        self.pcs.append(ax.scatter(xfar, yfar, label='Far'))
        self.pcs.extend([ ax.scatter(x, y, label=f'Optimum {kind}') for x, y, _, kind in sols ])

        self.from_who = [ near, far ]
        self.from_who.extend([ [x] for x in sols ])

        ax.legend()
        ax.grid(True)

        xsols = [ x for x, _, _, _ in sols ]
        ysols = [ y for _, y, _, _ in sols ]

        xs = xnear + xfar + xsols
        ys = ynear + yfar + ysols

        for x, y in zip(xs, ys):
            ax.annotate(f'({x}, {y})', xy=(x + 0.1, y + 0.1))

    def mplMouseMove(self, event):
        for pathc, who in zip(self.pcs, self.from_who):
            ocurred, ids = pathc.contains(event)

            if ocurred:
                globalPos = event.guiEvent.globalPos()
                idx = ids['ind'][0]
                qtw.QToolTip.showText(globalPos, f'Point from {who[idx].kind}, index = {idx}, w = {who[idx].w}')
                break

        else:
            qtw.QToolTip.hideText()

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

if __name__ == '__main__':
    app = qtw.QApplication([])
    canvas = FacilitiesCanvas(Figure())
    canvas.show()

    near = [ PT(1, 1, 5, 'Near'), PT(2, 3, 7, 'Near'), PT(5, 2, 1, 'Near'), PT(3, 4, 7, 'Near') ]
    far = [ PT(7, 3, 2, 'Far'), PT(5, 5, 4, 'Far'), PT(1, 2, 3, 'Far') ]
    sols = [ PT(5, 7, 2, 'FastModel'), PT(9, 4, 1, 'FussyModel') ]

    canvas.updateCanvas(near, far, *sols)

    import sys
    sys.exit(app.exec_())