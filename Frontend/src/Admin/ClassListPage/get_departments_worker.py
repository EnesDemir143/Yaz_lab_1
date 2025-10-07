import requests
from PyQt5.QtCore import QThread, pyqtSignal

API_BASE = "http://127.0.0.1:8000/admin"

class departments_list_worker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, userinfo: dict):
        super().__init__()
        self.endpoint = endpoint
        self.userinfo = userinfo

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.userinfo['token']}"}
            url = f"{API_BASE}/{self.endpoint}"
            resp = requests.get(url, headers=headers, timeout=30)

            try:
                result = resp.json()
            except Exception:
                result = {"status": "error", "detail": resp.text}

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({"status": "error", "detail": str(e)})
