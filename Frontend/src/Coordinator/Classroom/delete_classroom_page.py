from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet


class DeleteClassroomPage(QWidget):
    def __init__(self, parent_stack, user_info):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("🗑️ Delete Classroom")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.classroom_code_input = QLineEdit()
        layout.addWidget(QLabel("Derslik Kodu:"))
        layout.addWidget(self.classroom_code_input)

        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ Geri Dön")
        self.delete_btn = QPushButton("Sil")
        self.delete_btn.setStyleSheet("background-color: #d9534f;")
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.delete_btn.clicked.connect(self.delete_classroom)
        self.back_btn.clicked.connect(self.go_back)

    def go_back(self):
        from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage
        classroom_page = ClassroomPage(self.parent_stack, self.user_info)
        self.parent_stack.addWidget(classroom_page)
        self.parent_stack.setCurrentWidget(classroom_page)

    def delete_classroom(self):
        code = self.classroom_code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Warning", "Please enter classroom code.")
            return

        confirm = QMessageBox.question(
            self, "Confirm", f"Delete classroom '{code}'?", QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        self.request = ClassroomRequests("delete_classroom", {"classroom_code": code}, self.user_info)
        self.request.finished.connect(self.handle_response)
        self.request.start()

    def handle_response(self, response):
        if response.get("status") == "error":
            QMessageBox.critical(self, "Error", response.get("detail", "Unknown error"))
        else:
            QMessageBox.information(self, "Deleted", "Classroom deleted successfully!")
            self.go_back()
