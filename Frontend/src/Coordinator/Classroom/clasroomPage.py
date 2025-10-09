from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Coordinator.Classroom.insert_classroom_page import InsertClassroomPage
from Frontend.src.Coordinator.Classroom.search_classroom_page import SearchClassroomPage
from Frontend.src.Coordinator.Classroom.delete_classroom_page import DeleteClassroomPage


class ClassroomPage(QWidget):
    done = pyqtSignal()
    
    def __init__(self, parent_stack, user_info, setup_mode=False):

        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.setup_mode = setup_mode
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Classroom Management")
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))

        layout = QVBoxLayout()
        layout.setSpacing(20)
    
        if self.setup_mode:        
            self.okey_btn = QPushButton("Okey")
            layout.addWidget(self.okey_btn)    
    
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
        
        if self.setup_mode:
            self.okey_btn.setMinimumHeight(40)
            layout.addWidget(self.okey_btn)
            self.okey_btn.clicked.connect(self.handle_done)

        self.setLayout(layout)

        self.insert_btn.clicked.connect(lambda: self.open_page("insert"))
        self.search_btn.clicked.connect(lambda: self.open_page("search"))
        self.delete_btn.clicked.connect(lambda: self.open_page("delete"))

    def open_page(self, action_type: str):
        if action_type == "insert":
            self.page = InsertClassroomPage(self.parent_stack, self.user_info)
        elif action_type == "search":
            self.page = SearchClassroomPage(self.parent_stack, self.user_info)
        else:
            self.page = DeleteClassroomPage(self.parent_stack, self.user_info)

        self.page.done.connect(lambda: self.page.close())

        if self.setup_mode:
            self.page.showFullScreen()
        else:
            if self.parent_stack:
                self.parent_stack.addWidget(self.page)
                self.parent_stack.setCurrentWidget(self.page)


    def handle_done(self):
        if self.setup_mode:
            self.done.emit() 
            self.close()     
        else:
            self.done.emit()