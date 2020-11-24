from PySide2 import QtWidgets as qtw
from PySide2 import QtCore as qtc

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from app.gui.mpl import FacilitiesCanvas

from app.gui.resources import resources
from app.gui.codeeditor import CodeEditor

import app.models.fastmodel as FastModel
import app.models.fussymodel as FussyModel
from app.controller.controller import Controller

from app.utils.utils import Load, HELP_TEXT, SidebarPlaceholderSample

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
        self.comboAction.addItem('Load from sidebar text field', Load.fromSidebar)

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

class HelpDialog(qtw.QDialog):
    def __init__(self, parent=None) -> None:
        qtw.QDialog.__init__(self, parent)
        self.setUI()

    def setUI(self):
        self.setWindowTitle('Help')
        self.setLayout(qtw.QHBoxLayout())

        self.label = qtw.QLabel(HELP_TEXT)
        self.label.setTextFormat(qtc.Qt.TextFormat.MarkdownText)

        self.layout().addWidget(self.label)
        self.layout().setSizeConstraint(qtw.QLayout.SetFixedSize)

class CentralWidget(qtw.QWidget):
    '''
    Central widget formed by a canvas and an action widget
    '''

    saveDialogExecuted = qtc.Signal(str, str)

    def __init__(self, canvas) -> None:
        qtw.QWidget.__init__(self)
        self.canvas = canvas
        self.controller = Controller()

        self.setUI()
        self.setLoadDialog()
        self.setSaveDialog()
        self.setHelpDialog()
        self.setConnections()

    def setUI(self):
        self.setLayout(qtw.QVBoxLayout())

        self.hboxCanvas = qtw.QHBoxLayout()
        self.hboxCanvas.addWidget(self.canvas, stretch=2)

        self.textEditor = CodeEditor()
        self.textEditor.setFocusPolicy(qtc.Qt.StrongFocus)
        self.textEditor.setFocus()

        self.hboxCanvas.addWidget(self.textEditor, stretch=1)

        self.layout().addLayout(self.hboxCanvas)

        self.setHBoxActions()
        self.layout().addLayout(self.hboxActions)

    def setLoadDialog(self):
        self.loadDialog = LoadDialog(self)

        self.loadDialog.choosedLoadFile.connect(self.controller.loadFile)
        self.loadDialog.choosedLoadRandom.connect(self.controller.loadRandomSample)
        self.loadDialog.choosedLoadSidebar.connect(self.controller.loadText)

    def setSaveDialog(self):
        self.saveDialogExecuted.connect(self.controller.saveFile)

    def setHelpDialog(self):
        self.helpDialog = HelpDialog(self)

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
        self.btnSave.clicked.connect(self.onBtnSave)
        self.btnHelp.clicked.connect(self.onBtnHelp)

        self.textEditor.shortcut.activated.connect(self.pressedTextShortcut)
        self.controller.redrawCanvas.connect(self.canvas.updateCanvas)
        self.controller.resetLabel.connect(self.resetLabelInfo)
        self.controller.resetTextEditor.connect(self.resetTextEditorInfo)
        self.controller.notifyError.connect(self.displayErrorMsg)

    def resetLabelInfo(self, sols, costs):
        text = []

        for s, c in zip(sols, costs):
            text.append(f'point=({s.x}, {s.y}), cost={c} using {s.kind}')

        text = 'Found: ' + ', '.join(text) + '.'
        self.labInfo.setText(text)

    def resetTextEditorInfo(self, near, far, xmin, xmax, ymin, ymax):
        doFormat = lambda o: f'{o.x} {o.y} {o.w}'

        text = '\n'.join(map(doFormat, near))
        text += '\n*\n'
        text += '\n'.join(map(doFormat, far))
        text += '\n*\n'
        text += f'{xmin} {xmax} {ymin} {ymax}'

        self.textEditor.setPlainText(text)

    def displayErrorMsg(self, errorText):
        qtw.QMessageBox.critical(self, 'Error', errorText)

    @qtc.Slot()
    def onBtnLoad(self):
        self.loadDialog.open()

    @qtc.Slot()
    def onBtnSave(self):
        filepath, _ = qtw.QFileDialog.getSaveFileName(self)

        if not filepath:
            return

        self.saveDialogExecuted.emit(filepath, self.textEditor.toPlainText())

    @qtc.Slot()
    def onBtnHelp(self):
        self.helpDialog.open()
    
    @qtc.Slot()
    def pressedTextShortcut(self):
        ptext = self.textEditor.toPlainText()
        ctext = ptext or SidebarPlaceholderSample

        self.controller.loadText(ctext, [FastModel, FussyModel])

        if not ptext:
            self.textEditor.setPlainText(ctext)

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

        self.toolbar = NavigationToolbar(self.canvas, self)

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