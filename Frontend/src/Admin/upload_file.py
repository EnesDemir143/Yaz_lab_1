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

class UploadWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, file_path: str, userinfo: dict, department, headers=None):
        super().__init__()
        self.endpoint = endpoint
        self.file_path = file_path
        self.userinfo = userinfo
        self.department = department
        self.headers = headers or {}

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.userinfo['token']}"}
            with open(self.file_path, "rb") as f:
                files = {
                    "file": (
                        self.file_path.split("/")[-1],
                        f,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                }
                data = {"uploaded_department": self.department}
                resp = requests.post(
                    f"{API_BASE}/{self.endpoint}",
                    files=files,
                    data=data,
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