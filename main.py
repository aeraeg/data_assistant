
from PyQt6.QtWidgets import QApplication

import sys

from config_pyqt.ui.login import Login #for developing mode only

def main():
    app = QApplication(sys.argv)
    #ex = AppWindow()    
    ex = Login()
    ex.show()
    #sys.exit(app.exec_())
    sys.exit(app.exec()
)
if __name__ == '__main__':
    main()