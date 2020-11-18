from PySide2 import QtWidgets as qtw
from PySide2 import QtGui as qtg
from PySide2 import QtCore as qtc

class MainWindow(qtw.QMainWindow):
    def __init__(self) -> None:
        qtw.QMainWindow.__init__(self)
        self.setupGUI()
        self.show()

    def setupGUI(self):
        pass