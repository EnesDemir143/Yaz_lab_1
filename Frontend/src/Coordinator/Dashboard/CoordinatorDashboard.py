from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QStackedLayout, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Coordinator.UploadPages.Upload_class import UploadClassList
from Frontend.src.Coordinator.UploadPages.Upload_student import UploadStudentList
from Frontend.src.Coordinator.StudentListPage.student_list_page import StudentListPage
from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage
from Frontend.src.Coordinator.Classroom.insert_classroom_page import InsertClassroomPage
from Frontend.src.Coordinator.ClassList.class_list_page import ClassListPage


class CoordinatorDashboard(QWidget):
    def __init__(self, controller, user_info=None):
        super().__init__()
        self.setup_mode = True 
        self.controller = controller
        self.user_info = user_info or {}
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Coordinator Dashboard | Koordinatör Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/admin_dashboard_styles.qss"))

        # ---- Ana layout ----
        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content_layout = QVBoxLayout()

        sidebar_label = QLabel("🧭 Koordinatör Menü")
        sidebar_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sidebar_label.setAlignment(Qt.AlignCenter)

        self.menu = QListWidget()
        self.menu.setObjectName("menuList")
        for item_text in [
            "🏠 Genel",
            "📁 Ders Listesi Yükle",
            "📚 Öğrenci Listesi Yükle",
            "🏫 Sınıf Ekle",
            "👨‍🎓 Öğrenci Listesi",
            "📖 Ders Listesi",
        ]:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(180, 40))
            self.menu.addItem(item)
        self.menu.currentRowChanged.connect(self.switch_page)

        logout_btn = QPushButton("🚪 Çıkış Yap")
        logout_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)

        sidebar.addWidget(sidebar_label)
        sidebar.addWidget(self.menu)
        sidebar.addStretch()
        sidebar.addWidget(logout_btn)

        self.title_label = QLabel("Coordinator Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        email = self.user_info.get("email", "unknown@domain")
        dept = self.user_info.get("department", "Bilinmiyor")
        self.info_label = QLabel(f"{email} | {dept}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        self.stack = QStackedLayout()

        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Koordinatör paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)
        
        self.insert_classroom_page = ClassroomPage(self.stack, self.user_info)
        self.insert_classroom_page.done.connect(self.on_classroom_done)

        self.upload_classes_page = UploadClassList(self.user_info, self)
        self.upload_students_page = UploadStudentList(self.user_info, self)
        self.student_list_page = StudentListPage(self.user_info, self)
        self.class_list_page = ClassListPage(self.user_info, self)

        self.stack.addWidget(self.general_page)
        self.stack.addWidget(self.upload_classes_page)
        self.stack.addWidget(self.upload_students_page)
        self.stack.addWidget(self.insert_classroom_page)
        self.stack.addWidget(self.student_list_page)
        self.stack.addWidget(self.class_list_page)

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        frame = QFrame()
        frame.setLayout(self.stack)
        content_layout.addWidget(frame)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)

        self.menu.setCurrentRow(0)

        if self.setup_mode:
            self.hide_dashboard_ui()
            self.start_setup_only()
        else:
            self.menu.setCurrentRow(0)
            
    def hide_dashboard_ui(self):
        for widget in [self.menu, self.title_label, self.info_label]:
            widget.hide()

        old_layout = self.layout()
        if old_layout:
            self.clear_layout(old_layout)



    def create_placeholder_page(self, message):
        w = QWidget()
        l = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #ccc; font-size: 15px;")
        l.addWidget(label)
        w.setLayout(l)
        return w
    
    def on_classroom_done(self):
        self.stack.setCurrentWidget(self.general_page)
        self.title_label.setText("Genel")
        self.menu.setCurrentRow(0)


    def switch_page(self, index):
        mapping = {
            0: ("general", "Genel"),
            1: ("upload_classes_list", "Ders Listesi Yükle"),
            2: ("upload_students_list", "Öğrenci Listesi Yükle"),
            3: ("insert_classroom", "Sınıf Ekle"),
            4: ("student_list", "Öğrenci Listesi"),
            5: ("class_list", "Ders Listesi"),
        }

        if index in mapping:
            self.current_endpoint, title = mapping[index]
            self.title_label.setText(title)
            self.stack.setCurrentIndex(index)
                
    def start_setup_only(self):
        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        self.hide()

        self.insert_classroom_page = InsertClassroomPage(self, self.user_info, setup_mode=self.setup_mode)
        self.insert_classroom_page.done.connect(self.goto_classroom_management)
        
        self.insert_classroom_page.showFullScreen()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self.clear_layout(item.layout())

    def goto_classroom_management(self):
        self.hide()

        if hasattr(self, "insert_classroom_page"):
            self.insert_classroom_page.close()

        self.classroom_management_page = ClassroomPage(None, self.user_info, setup_mode=True)
        self.classroom_management_page.done.connect(self.finish_setup)
        self.classroom_management_page.showFullScreen()
    
    def finish_setup(self):
        if hasattr(self, "classroom_management_page"):
            self.classroom_management_page.close()

        self.showNormal()
        self.show()
        self.setup_mode = False

    
    def logout(self):
        self.controller.logout()
