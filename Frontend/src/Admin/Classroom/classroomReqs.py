import requests
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal

API_BASE = "http://127.0.0.1:8000/admin"

class ClassroomRequests(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, data: dict, userinfo: dict):
        super().__init__()
        self.endpoint = endpoint
        self.userinfo = userinfo
        self.data = data

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.userinfo['token']}"}
            resp = requests.post(
                f"{API_BASE}/{self.endpoint}",
                json=self.data,
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