from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Admin.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet


class InsertClassroomPage(QWidget):
    def __init__(self, parent_stack, user_info):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("➕ Add New Classroom")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Form alanları
        self.classroom_id = QLineEdit()
        self.classroom_name = QLineEdit()
        self.department = QLineEdit()
        self.capacity = QLineEdit()
        self.desks_row = QLineEdit()
        self.desks_col = QLineEdit()
        self.structure = QLineEdit()

        fields = [
            ("Derslik Kodu:", self.classroom_id),
            ("Derslik Adı:", self.classroom_name),
            ("Bölüm Adı:", self.department),
            ("Kapasite:", self.capacity),
            ("Sıra Satır Sayısı:", self.desks_row),
            ("Sıra Sütun Sayısı:", self.desks_col),
            ("Masa Yapısı:", self.structure)
        ]

        for label, widget in fields:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.insert_btn = QPushButton("Kaydet")
        self.back_btn = QPushButton("⬅️ Geri Dön")
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.insert_btn)
        layout.addLayout(btn_layout)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)

        self.insert_btn.clicked.connect(self.insert_classroom)
        self.back_btn.clicked.connect(self.go_back)

    def go_back(self):
        # ClassroomPage’e dön
        from Frontend.src.Admin.Classroom.clasroomPage import ClassroomPage
        classroom_page = ClassroomPage(self.parent_stack, self.user_info)
        self.parent_stack.addWidget(classroom_page)
        self.parent_stack.setCurrentWidget(classroom_page)

    def insert_classroom(self):
        data = {
            "classroom_id": self.classroom_id.text(),
            "classroom_name": self.classroom_name.text(),
            "department_name": self.department.text(),
            "capacity": int(self.capacity.text()) if self.capacity.text().isdigit() else 0,
            "desks_per_row": int(self.desks_row.text()) if self.desks_row.text().isdigit() else 0,
            "desk_per_column": int(self.desks_col.text()) if self.desks_col.text().isdigit() else 0,
            "desk_structure": self.structure.text()
        }

        self.request = ClassroomRequests("insert_classroom", data, self.user_info)
        self.request.finished.connect(self.handle_response)
        self.request.start()

    def handle_response(self, response):
        self.result.setText(str(response))
        if response.get("status") == "error":
            QMessageBox.critical(self, "Insert Failed", response.get("detail", "Unknown error"))
        else:
            QMessageBox.information(self, "Success", "Classroom inserted successfully!")
