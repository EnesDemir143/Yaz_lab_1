from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Admin.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet


class SearchClassroomPage(QWidget):
    def __init__(self, parent_stack, user_info):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("🔍 Search Classroom")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.classroom_code_input = QLineEdit()
        layout.addWidget(QLabel("Derslik Kodu:"))
        layout.addWidget(self.classroom_code_input)

        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("Ara")
        self.back_btn = QPushButton("⬅️ Geri Dön")
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.search_btn)
        layout.addLayout(btn_layout)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)

        self.search_btn.clicked.connect(self.search_classroom)
        self.back_btn.clicked.connect(self.go_back)

    def go_back(self):
        from Frontend.src.Admin.Classroom.clasroomPage import ClassroomPage
        classroom_page = ClassroomPage(self.parent_stack, self.user_info)
        self.parent_stack.addWidget(classroom_page)
        self.parent_stack.setCurrentWidget(classroom_page)

    def search_classroom(self):
        code = self.classroom_code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Warning", "Please enter classroom code.")
            return

        self.request = ClassroomRequests("search_classroom", {"classroom_code": code}, self.user_info)
        self.request.finished.connect(self.handle_response)
        self.request.start()

    def handle_response(self, response):
        if response.get("status") == "error":
            QMessageBox.critical(self, "Search Failed", response.get("detail", "Not found"))
        else:
            classroom = response.get("classroom", {})
            info_text = "\n".join([
                f"Derslik Adı: {classroom.get('classroom_name', '')}",
                f"Bölüm: {classroom.get('department_name', '')}",
                f"Kapasite: {classroom.get('capacity', '')}",
                f"Satır: {classroom.get('desks_per_row', '')}",
                f"Sütun: {classroom.get('desk_per_column', '')}",
                f"Masa Yapısı: {classroom.get('desk_structure', '')}"
            ])
            self.result.setText(info_text)
