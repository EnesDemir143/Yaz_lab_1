from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QHBoxLayout, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet


class InsertClassroomPage(QWidget):
    inserted_classroom_count_with_users = {}
    done = pyqtSignal()
    
    def __init__(self, parent_stack, user_info, setup_mode=True):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.setup_mode = setup_mode
        
        if user_info.get("email") not in InsertClassroomPage.inserted_classroom_count_with_users:
            InsertClassroomPage.inserted_classroom_count_with_users[user_info.get("email")] = 0
        
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
        
        if not self.setup_mode or InsertClassroomPage.inserted_classroom_count_with_users[self.user_info.get('email')] > 0:
            self.back_btn = QPushButton("⬅️ Geri Dön")
            btn_layout.addWidget(self.back_btn)
            self.back_btn.clicked.connect(self.go_back)
            
        btn_layout.addWidget(self.insert_btn)
        layout.addLayout(btn_layout)

        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        self.setLayout(layout)

        self.insert_btn.clicked.connect(self.insert_classroom)

    def go_back(self):
        from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage

        if self.parent_stack is None:
            classroom_page = ClassroomPage(None, self.user_info, setup_mode=True)
            classroom_page.done.connect(classroom_page.close)
            classroom_page.showFullScreen()
            self.close()  
        else:
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
            "desks_per_column": int(self.desks_col.text()) if self.desks_col.text().isdigit() else 0,
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
            
            InsertClassroomPage.inserted_classroom_count_with_users[self.user_info.get('email')] += 1
            
            if self.setup_mode:
                self.handle_done()
                InsertClassroomPage.done
            
    def handle_done(self):
        self.done.emit()
