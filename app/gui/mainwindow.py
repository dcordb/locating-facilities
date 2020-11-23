from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

from matplotlib.figure import Figure
from app.gui.mpl import FacilitiesCanvas, FacilitiesToolbar

from app.gui.resources import resources

import app.models.fastmodel as FastModel
import app.models.fussymodel as FussyModel
import app.controller.controller as Controller

from app.utils.utils import Load

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

    def __init__(self, parent=None) -> None:
        qtw.QDialog.__init__(self, parent)

        self.setUI()
        self.setConnections()

    def setUI(self):
        self.setWindowTitle('Load from')
        self.setWindowModality(qtc.Qt.WindowModality.ApplicationModal)

        self.comboAction = qtw.QComboBox()
        self.comboAction.addItem('Load from file', Load.fromFile)
        self.comboAction.addItem('Load random sample', Load.fromSample)
        self.comboAction.addItem('Load from sidebar modification panel', Load.fromSidebar)

        self.comboModels = qtw.QComboBox()
        self.comboModels.addItem(FastModel.__repr__, [FastModel])
        self.comboModels.addItem(FussyModel.__repr__, [FussyModel])
        self.comboModels.addItem(f'{FastModel.__repr__}, {FussyModel.__repr__}', [FastModel, FussyModel])

        self.form = qtw.QFormLayout()
        self.form.addRow('Action', self.comboAction)
        self.form.addRow('Model', self.comboModels)

        self.btnBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        self.form.addRow(self.btnBox)

        self.form.setSizeConstraint(qtw.QLayout.SetFixedSize)
        self.setLayout(self.form)

    def setConnections(self):
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
        self.canvas = canvas

        self.setUI()
        self.setLoadDialog()
        self.setSaveDialog()
        self.setHelpDialog()
        self.setConnections()

    def setUI(self):
        self.setLayout(qtw.QVBoxLayout())

        self.hboxCanvas = qtw.QHBoxLayout()
        self.hboxCanvas.addWidget(self.canvas)

        self.textEditor = TextEditor()
        self.hboxCanvas.addWidget(self.textEditor)

        self.layout().addLayout(self.hboxCanvas)

        self.setHBoxActions()
        self.layout().addLayout(self.hboxActions)

    def setLoadDialog(self):
        self.loadDialog = LoadDialog(self)

        self.loadDialog.choosedLoadFile.connect(Controller.loadFile)
        self.loadDialog.choosedLoadRandom.connect(Controller.loadRandomSample)
        self.loadDialog.choosedLoadSidebar.connect(Controller.loadText)

    def setSaveDialog(self):
        pass

    def setHelpDialog(self):
        pass

    def setHBoxActions(self):
        self.hboxActions = qtw.QHBoxLayout()

        self.btnLoad = qtw.QPushButton('&Load', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        self.btnSave = qtw.QPushButton('&Save', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        self.labInfo = qtw.QLabel()
        self.btnHelp = qtw.QPushButton('&Help', sizePolicy=qtw.QSizePolicy(qtw.QSizePolicy.Fixed, qtw.QSizePolicy.Fixed))
        self.separator = qtw.QFrame()
        self.separator.setFrameStyle(qtw.QFrame.VLine | qtw.QFrame.Raised)

        self.hboxActions.addWidget(self.btnLoad)
        self.hboxActions.addWidget(self.btnSave)
        self.hboxActions.addWidget(self.separator)
        self.hboxActions.addWidget(self.labInfo)
        self.hboxActions.addStretch()
        self.hboxActions.addWidget(self.btnHelp)

    def setConnections(self):
        self.btnLoad.clicked.connect(self.onBtnLoad)

    @qtc.Slot()
    def onBtnLoad(self):
        self.loadDialog.exec_()

class MainWindow(qtw.QMainWindow):
    '''
    Main Window
    '''

    def __init__(self) -> None:
        qtw.QMainWindow.__init__(self)

        self.loadCSS()
        self.setUI()

    def setUI(self):
        self.setWindowTitle('Locating Facilities')

        self.canvas = FacilitiesCanvas(Figure())
        self.canvas.updateCanvas()

        self.toolbar = FacilitiesToolbar(self.canvas)

        self.addToolBar(self.toolbar)
        self.setCentralWidget(CentralWidget(self.canvas))

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