from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

from matplotlib.figure import Figure
from app.gui.mpl import FacilitiesCanvas, FacilitiesToolbar

from app.gui.resources import resources

class ActionWidget(qtw.QWidget):
    '''
    Bottom widget holding action buttons
    '''

    def __init__(self) -> None:
        qtw.QWidget.__init__(self)

        self.setLayout(qtw.QHBoxLayout())

        btnLoad = qtw.QPushButton('&Load')
        btnSave = qtw.QPushButton('&Save')
        labInfo = qtw.QLabel('Information...')
        btnHelp = qtw.QPushButton('&Help')

        self.layout().addWidget(btnLoad)
        self.layout().addWidget(btnSave)
        self.layout().addWidget(labInfo)
        self.layout().addWidget(btnHelp)

class CentralWidget(qtw.QWidget):
    '''
    Central widget formed by a canvas and an action widget
    '''

    def __init__(self, canvas) -> None:
        qtw.QWidget.__init__(self)

        self.setLayout(qtw.QVBoxLayout())
        self.layout().addWidget(canvas)

        actionWidget = ActionWidget()
        self.layout().addWidget(actionWidget)

        self.layout().setContentsMargins(0, 0, 0, 0)

class MainWindow(qtw.QMainWindow):
    '''
    Main Window
    '''

    def __init__(self) -> None:
        qtw.QMainWindow.__init__(self)
        self.loadCSS()

        self.setWindowTitle('Locating Facilities')

        canvas = FacilitiesCanvas(Figure())
        canvas.updateCanvas()

        toolbar = FacilitiesToolbar(canvas)

        self.addToolBar(toolbar)
        self.setCentralWidget(CentralWidget(canvas))

        self.show()

    def loadCSS(self):
        f = qtc.QFile(':/style.css')                            
        f.open(qtc.QFile.ReadOnly | qtc.QFile.Text)

        ts = qtc.QTextStream(f)
        css = ts.readAll()
        self.setStyleSheet(css)

        f.close()