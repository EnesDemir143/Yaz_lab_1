import requests
from PyQt5.QtCore import QThread, pyqtSignal

API_BASE = "http://127.0.0.1:8000/admin"
API_BASE_COORDINATOR = "http://127.0.0.1:8000/department_coordinator"

class get_schedules(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint, user_info: dict, department: str = None):
        super().__init__()
        self.endpoint = endpoint
        self.user_info = user_info
        self.department = department

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.user_info['token']}"}
            
            if self.department:
                url = f"{API_BASE_COORDINATOR}/{self.endpoint}"
            else:
                url = f"{API_BASE}/{self.endpoint}"

            resp = requests.get(url, headers=headers, timeout=30)
            print(f"GET {url} - Status Code: {resp.status_code}")
            try:
                result = resp.json()
            except Exception:
                result = {"status": "error", "detail": resp.text}

            self.finished.emit(result)

        except Exception as e:
            self.finished.emit({"status": "error", "detail": str(e)})
