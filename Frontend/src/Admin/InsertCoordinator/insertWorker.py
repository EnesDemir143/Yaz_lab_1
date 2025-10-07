import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont


API_BASE = "http://127.0.0.1:8000/admin"

class InsertWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, coordinator_email: str, coordinator_password: str, coordinator_department: str, userinfo: dict):
        super().__init__()
        self.endpoint = endpoint
        self.userinfo = userinfo
        self.coordinator_email = coordinator_email
        self.coordinator_password = coordinator_password
        self.coordinator_department = coordinator_department

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.userinfo['token']}"}
            data = {"email": self.coordinator_email, "password": self.coordinator_password, "department": self.coordinator_department}
            resp = requests.post(
                f"{API_BASE}/{self.endpoint}",
                json=data,
                headers=headers, 
                timeout=30
            )
            try:
                result = resp.json()
            except Exception:
                result = {"message": resp.text}
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"error": str(e)})