import requests
from PyQt5.QtCore import QThread, pyqtSignal

API_BASE = "http://127.0.0.1:8000/department_coordinator"

class Class_list_page_worker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, data: dict, user_info: dict):
        super().__init__()
        self.endpoint = endpoint
        self.user_info = user_info

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.user_info['token']}"}
            url = f"{API_BASE}/{self.endpoint}"
            resp = requests.get(url, headers=headers, timeout=30)

            try:
                result = resp.json()
            except Exception:
                result = {"status": "error", "detail": resp.text}

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({"status": "error", "detail": str(e)})
