import sys
import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal

LOGIN_API_URL = "http://127.0.0.1:8000/login"

# ---- Worker Thread ----
class LoginWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        try:
            resp = requests.post(LOGIN_API_URL, json={
                "email": self.email,
                "password": self.password
            })
            if resp.status_code == 200:
                self.finished.emit(resp.json())
            else:
                self.finished.emit({"error": resp.text})
        except Exception as e:
            self.finished.emit({"error": str(e)})