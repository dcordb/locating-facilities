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

        self.btnLoad = qtw.QPushButton('&Load', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        self.btnSave = qtw.QPushButton('&Save', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        self.labInfo = qtw.QLabel()
        self.btnHelp = qtw.QPushButton('&Help', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        self.separator = qtw.QFrame()
        self.separator.setFrameStyle(qtw.QFrame.VLine | qtw.QFrame.Raised)

        self.layout().addWidget(self.btnLoad)
        self.layout().addWidget(self.btnSave)
        self.layout().addWidget(self.separator)
        self.layout().addWidget(self.labInfo)
        self.layout().addStretch()
        self.layout().addWidget(self.btnHelp)

        self.btnLoad.clicked.connect(self.onBtnLoad)

    @qtc.Slot()
    def onBtnLoad(self):
        LoadDialog.getInstance(self.parent()).exec_()

class TextEditor(qtw.QPlainTextEdit):
    '''
    Implements a simple text editor for displaying/editing the points
    '''

    def __init__(self) -> None:
        qtw.QPlainTextEdit.__init__(self)
        self.setSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.MinimumExpanding)

class LoadDialog(qtw.QDialog):
    '''Implements the load dialog'''

    choosedLoadFile = qtc.Signal(str, list)
    choosedLoadRandom = qtc.Signal(list)
    choosedLoadSidebar = qtc.Signal(str, list)

    _instance = None

    @classmethod
    def getInstance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)

        return cls._instance

    def __init__(self, parent=None) -> None:
        qtw.QDialog.__init__(self, parent)

        self.setWindowTitle('Load from')
        self.setWindowModality(qtc.Qt.WindowModality.ApplicationModal)

        self.comboAction = qtw.QComboBox()
        self.comboAction.addItem('Load from file', Load.fromFile)
        self.comboAction.addItem('Load random sample', Load.fromSample)
        self.comboAction.addItem('Load from sidebar modification panel', Load.fromSidebar)

        self.comboModels = qtw.QComboBox()
        self.comboModels.addItem(FastModel.__name__, [FastModel])
        self.comboModels.addItem(FussyModel.__name__, [FussyModel])
        self.comboModels.addItem(f'{FastModel.__name__}, {FussyModel.__name__}', [FastModel, FussyModel])

        self.form = qtw.QFormLayout()
        self.form.addRow('Action', self.comboAction)
        self.form.addRow('Model', self.comboModels)

        self.btnBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        self.form.addRow(self.btnBox)

        self.form.setSizeConstraint(qtw.QLayout.SetFixedSize)
        self.setLayout(self.form)

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.accepted.connect(self.onAccepted)

    @qtc.Slot()
    def onAccepted(self):
        action = self.comboAction.currentData()
        models = self.comboModels.currentData()

        if action is Load.fromFile:
            filePath, _ = qtw.QFileDialog.getOpenFileName(self.parent())

            if not filePath:
                return

            self.choosedLoadFile.emit(filePath, models)
        
        elif action is Load.fromSample:
            self.choosedLoadRandom.emit(models)

        else:
            text = self.parent().textEditor.toPlainText()
            self.choosedLoadSidebar.emit(text, models)

class CentralWidget(qtw.QWidget):
    '''
    Central widget formed by a canvas and an action widget
    '''

    def __init__(self, canvas) -> None:
        qtw.QWidget.__init__(self)

        self.setLayout(qtw.QVBoxLayout())

        self.hlayout = qtw.QHBoxLayout()
        self.hlayout.addWidget(canvas)

        self.textEditor = TextEditor()
        self.hlayout.addWidget(self.textEditor)

        self.layout().addLayout(self.hlayout)

        self.actionWidget = ActionWidget()
        self.layout().addWidget(self.actionWidget)

class MainWindow(qtw.QMainWindow):
    '''
    Main Window
    '''

    def __init__(self) -> None:
        qtw.QMainWindow.__init__(self)
        self.loadCSS()

        self.setWindowTitle('Locating Facilities')

        self.canvas = FacilitiesCanvas(Figure())
        self.canvas.updateCanvas()

        self.toolbar = FacilitiesToolbar(self.canvas)

        self.addToolBar(self.toolbar)
        self.setCentralWidget(CentralWidget(self.canvas))

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