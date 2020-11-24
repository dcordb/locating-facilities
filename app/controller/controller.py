from PySide2 import QtCore as qtc
import pickle
from app.utils.utils import PARAMS, PT, floatRE
from app.utils.errors import *
import random

class Controller(qtc.QObject):
    redrawCanvas = qtc.Signal(list, list, list)
    resetLabel = qtc.Signal(list, list)
    resetTextEditor = qtc.Signal(list, list, float, float, float, float)
    notifyError = qtc.Signal(str)

    def _update(self, near, far, xmin, xmax, ymin, ymax, models):
        for o in near:
            if not xmin <= o.x <= xmax or not ymin <= o.y <= ymax:
                self.notifyError.emit(ErrorNotWithinBox)
                return False

        for o in far:
            if not xmin <= o.x <= xmax or not ymin <= o.y <= ymax:
                self.notifyError.emit(ErrorNotWithinBox)
                return False

        sols = []
        costs = []

        for model in models:
            pt, cost = model.optimize(near, far, xmin, xmax, ymin, ymax)
            sols.append(pt)
            costs.append(round(cost, 2))

        self.redrawCanvas.emit(near, far, sols)
        self.resetLabel.emit(sols, costs)

        return True

    def loadFile(self, file: str, models):
        with open(file, 'rb') as f:
            near, far, xmin, xmax, ymin, ymax = pickle.load(f)

        self._update(near, far, xmin, xmax, ymin, ymax, models)
        self.resetTextEditor.emit(near, far, xmin, xmax, ymin, ymax)

    def loadRandomSample(self, models):
        n = random.randint(1, 100)
        m = random.randint(1, 100)

        round2 = lambda x: round(x, 2)

        xmin = random.uniform(-100, 0)
        ymin = random.uniform(-100, 0)

        xmax = random.uniform(0, 100)
        ymax = random.uniform(0, 100)

        xmin = round2(xmin)
        ymin = round2(ymin)

        xmax = round2(xmax)
        ymax = round2(ymax)

        near = []
        for _ in range(n):
            x = random.uniform(xmin, xmax)
            y = random.uniform(ymin, ymax)
            w = random.uniform(1, 30)

            near.append(PT(round2(x), round2(y), round2(w), kind='Near'))

        far = []
        for _ in range(m):
            x = random.uniform(xmin, xmax)
            y = random.uniform(ymin, ymax)
            w = random.uniform(1, 30)

            far.append(PT(round2(x), round2(y), round2(w), kind='Far'))

        if not self._update(near, far, xmin, xmax, ymin, ymax, models):
            return

        self.resetTextEditor.emit(near, far, xmin, xmax, ymin, ymax)

    def loadText(self, text: str, models, internal=False):
        lines = text.splitlines()

        parts = []
        lstok = False
        
        for line in lines:
            if not line or line.isspace():
                continue

            if '*' in line:
                lstok = False

            else:
                if not lstok:
                    parts.append([])

                parts[-1].append(line)
                lstok = True

        if len(parts) != PARAMS:
            self.notifyError.emit(ErrorWholeFormat)
            return

        bl, near = self._readPoints(parts[0], 'Near')

        if not bl:
            self.notifyError.emit(ErrorPointFormat)
            return

        bl, far = self._readPoints(parts[1], 'Far')

        if not bl:
            self.notifyError.emit(ErrorPointFormat)
            return

        if len(parts[2]) != 1:  
            self.notifyError.emit(ErrorXYFormat)
            return

        line = parts[2][0].split()

        if not all(map(self._isfloat, line)):
            self.notifyError.emit(ErrorXYFormat)
            return

        xmin, xmax, ymin, ymax = map(float, line)

        if internal:
            return near, far, xmin, xmax, ymin, ymax

        self._update(near, far, xmin, xmax, ymin, ymax, models)

    def _readPoints(self, lines, kind):
        pts = []

        for line in lines:
            line = line.split()

            if len(line) != 3:
                return (False, [])

            if not all(map(self._isfloat, line)):
                return (False, [])

            x, y, w = map(float, line)
            pts.append(PT(x, y, w, kind=kind))

        return (True, pts)

    def _isfloat(self, x):
        obj = floatRE.fullmatch(x)
        return False if obj is None else True

    def saveFile(self, file, text):
        obj = self.loadText(text, models=None, internal=True)

        with open(file, 'wb') as f:
            pickle.dump(obj, f)

if __name__ == '__main__':
    text = (
    '''
    132 3 3
    213 32 123
    *
    213 32 45
    *
    1 2 3 4
    *
    '''
    )

    text1 = '****'

    c = Controller()
    c.loadText(text, 'asd')
    c.loadText(text1, 'asd')

    print(c._isfloat('.0'))