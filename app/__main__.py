from app.gui.mainwindow import MainWindow
from PySide2.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())