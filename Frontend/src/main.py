from PyQt5.QtWidgets import QApplication
import sys
from Frontend.src.Login.app_controller import AppController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    sys.exit(app.exec_())