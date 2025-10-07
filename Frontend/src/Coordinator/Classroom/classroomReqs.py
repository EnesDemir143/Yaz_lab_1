import requests
from PyQt5.QtCore import QThread, pyqtSignal

API_BASE = "http://127.0.0.1:8000/department_coordinator"

class ClassroomRequests(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, data: dict, user_info: dict):
        super().__init__()
        self.endpoint = endpoint
        self.user_info = user_info
        self.data = data

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.user_info['token']}"}
            url = f"{API_BASE}/{self.endpoint}"

            if self.endpoint in ["insert_classroom", "update_classroom"]:
                resp = requests.post(url, json=self.data, headers=headers, timeout=30)
            elif self.endpoint in ["search_classroom", "delete_classroom"]:
                resp = requests.post(url, params=self.data, headers=headers, timeout=30)
            else:
                print("Invalid endpoint")
                raise ValueError("Invalid endpoint")

            try:
                result = resp.json()
            except Exception:
                result = {"status": "error", "detail": resp.text}

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({"status": "error", "detail": str(e)})
