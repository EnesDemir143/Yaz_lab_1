import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont


API_BASE = "http://127.0.0.1:8000/department_coordinator"

class UploadWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, file_path: str, user_info: dict, headers=None):
        super().__init__()
        self.endpoint = endpoint
        self.file_path = file_path
        self.user_info = user_info
        self.headers = headers or {}

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.user_info['token']}"}
            with open(self.file_path, "rb") as f:
                files = {
                    "file": (
                        self.file_path.split("/")[-1],
                        f,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                }
                resp = requests.post(
                    f"{API_BASE}/{self.endpoint}",
                    files=files,
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