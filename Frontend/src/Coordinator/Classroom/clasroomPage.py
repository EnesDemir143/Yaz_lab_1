from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Coordinator.Classroom.insert_classroom_page import InsertClassroomPage
from Frontend.src.Coordinator.Classroom.search_classroom_page import SearchClassroomPage
from Frontend.src.Coordinator.Classroom.delete_classroom_page import DeleteClassroomPage


class ClassroomPage(QWidget):
    done = pyqtSignal()
    
    def __init__(self, parent_stack, user_info):

        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Classroom Management")
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))

        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("🏫 Classroom Management Panel")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.insert_btn = QPushButton("➕ Insert Classroom")
        self.search_btn = QPushButton("🔍 Search Classroom")
        self.delete_btn = QPushButton("🗑️ Delete Classroom")

        for btn in [self.insert_btn, self.search_btn, self.delete_btn]:
            btn.setMinimumHeight(50)
            layout.addWidget(btn)

        self.setLayout(layout)

        self.insert_btn.clicked.connect(lambda: self.open_page("insert"))
        self.search_btn.clicked.connect(lambda: self.open_page("search"))
        self.delete_btn.clicked.connect(lambda: self.open_page("delete"))

    def open_page(self, action_type: str):
        if action_type == "insert":
            page = InsertClassroomPage(self.parent_stack, self.user_info)
        elif action_type == "search":
            page = SearchClassroomPage(self.parent_stack, self.user_info)
        else:
            page = DeleteClassroomPage(self.parent_stack, self.user_info)

        self.parent_stack.addWidget(page)
        self.parent_stack.setCurrentWidget(page)

    def handle_done(self):
        self.done.emit() 