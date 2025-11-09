from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Coordinator.Classroom.insert_classroom_page import InsertClassroomPage
from Frontend.src.Coordinator.Classroom.search_classroom_page import SearchClassroomPage
from Frontend.src.Coordinator.Classroom.delete_classroom_page import DeleteClassroomPage



class ClassroomPage(QWidget):
    def __init__(self, parent_stack, user_info, dashboard=None):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.dashboard = dashboard 
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
        
        self.okey_btn = QPushButton("✔️ Confirm Classroom Addition")
        layout.addWidget(self.okey_btn)
        self.okey_btn.setVisible(True)  

        for btn in [self.insert_btn, self.search_btn, self.delete_btn]:
            btn.setMinimumHeight(50)
            layout.addWidget(btn)

        self.setLayout(layout)

        self.insert_btn.clicked.connect(lambda: self.open_page("insert"))
        self.search_btn.clicked.connect(lambda: self.open_page("search"))
        self.delete_btn.clicked.connect(lambda: self.open_page("delete"))
        self.okey_btn.clicked.connect(self.next_step_after_insertion)
        

    def open_page(self, action_type: str):
        if action_type == "insert":
            page = InsertClassroomPage(self.parent_stack, self.user_info, self.dashboard)
        elif action_type == "search":
            page = SearchClassroomPage(self.parent_stack, self.user_info, self.dashboard)
        else:
            page = DeleteClassroomPage(self.parent_stack, self.user_info, self.dashboard)

        self.parent_stack.addWidget(page)
        self.parent_stack.setCurrentWidget(page)

    def next_step_after_insertion(self):
        if self.dashboard and not self.dashboard.has_schedules:
            self.dashboard.enable_next_step_after_classroom()  
            self.okey_btn.setVisible(True) 