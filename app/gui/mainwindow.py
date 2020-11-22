from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

from matplotlib.figure import Figure
from app.gui.mpl import FacilitiesCanvas, FacilitiesToolbar

from app.gui.resources import resources

from app.models.simple_model import FastModel
from app.models.fussy_model import FussyModel

from app.utils.utils import Load

class ActionWidget(qtw.QWidget):
    '''
    Bottom widget holding action buttons
    '''

    def __init__(self) -> None:
        qtw.QWidget.__init__(self)

        self.setLayout(qtw.QHBoxLayout())

        btnLoad = qtw.QPushButton('&Load', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        btnSave = qtw.QPushButton('&Save', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        labInfo = qtw.QLabel()
        btnHelp = qtw.QPushButton('&Help', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        separator = qtw.QFrame()
        separator.setFrameStyle(qtw.QFrame.VLine | qtw.QFrame.Raised)

        self.layout().addWidget(btnLoad)
        self.layout().addWidget(btnSave)
        self.layout().addWidget(separator)
        self.layout().addWidget(labInfo)
        self.layout().addStretch()
        self.layout().addWidget(btnHelp)

        btnLoad.clicked.connect(self.onBtnLoad)

    def onBtnLoad(self):
        loadDialog = LoadDialog()
        r = loadDialog.exec_()

class TextEditor(qtw.QPlainTextEdit):
    '''
    Implements a simple text editor for displaying/editing the points
    '''

    def __init__(self) -> None:
        qtw.QPlainTextEdit.__init__(self)
        self.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.MinimumExpanding)

class LoadDialog(qtw.QDialog):
    def __init__(self) -> None:
        qtw.QDialog.__init__(self)

        self.setWindowTitle('Load from')
        self.setWindowModality(qtc.Qt.WindowModality.ApplicationModal)

        comboAction = qtw.QComboBox()
        comboAction.addItem('Load from file', Load.fromFile)
        comboAction.addItem('Load random sample', Load.fromSample)
        comboAction.addItem('Load from sidebar modification panel', Load.fromSidebar)

        comboModels = qtw.QComboBox()
        comboModels.addItem(FastModel.__name__, [FastModel])
        comboModels.addItem(FussyModel.__name__, [FussyModel])
        comboModels.addItem(f'{FastModel.__name__}, {FussyModel.__name__}', [FastModel, FussyModel])

        form = qtw.QFormLayout()
        form.addRow('Action', comboAction)
        form.addRow('Model', comboModels)

        btnBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)

        btnBox.accepted.connect(self.accept)
        btnBox.rejected.connect(self.reject)

        self.accepted.connect(self.onAccepted)

        form.addRow(btnBox)
        form.setSizeConstraint(qtw.QLayout.SetFixedSize)

        self.setLayout(form)

    def onAccepted(self): pass

class CentralWidget(qtw.QWidget):
    '''
    Central widget formed by a canvas and an action widget
    '''

    def __init__(self, canvas) -> None:
        qtw.QWidget.__init__(self)

        self.setLayout(qtw.QVBoxLayout())

        hlayout = qtw.QHBoxLayout()
        hlayout.addWidget(canvas)
        hlayout.addWidget(TextEditor())

        self.layout().addLayout(hlayout)

        actionWidget = ActionWidget()
        self.layout().addWidget(actionWidget)

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

if __name__ == '__main__':
    app = qtw.QApplication([])
    dialog = LoadDialog()
    dialog.show()
    app.exec_()