# insert_exam_schedule_worker.py

from PyQt5.QtCore import QThread, pyqtSignal
import requests

API_BASE = "http://127.0.0.1:8000/admin"
API_BASE_COR = "http://127.0.0.1:8000/department_coordinator"

class InsertExamScheduleWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint, data, userinfo, role = None):
        super().__init__()
        self.endpoint = endpoint 
        self.data = data
        self.userinfo = userinfo
        self.role = role


    def run(self):
        headers = {
            "Authorization": f"Bearer {self.userinfo['token']}"
        }
        if self.role:
            url = f"{API_BASE_COR}/{self.endpoint}"
        else:
            url = f"{API_BASE}/{self.endpoint}"
        try:
            resp = requests.post(url, json=self.data, headers=headers, timeout=30)
            result = resp.json()
            print("result: ", result)
            self.finished.emit({"status": "success", "response": result})
        except Exception as e:
            self.finished.emit({"status": "error", "detail": str(e)})
