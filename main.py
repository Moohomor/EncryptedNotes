import sys

from PyQt5.QtWidgets import QApplication

from window_hello import WindowHello

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WindowHello()
    ex.show()
    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)
    sys.exit(app.exec_())