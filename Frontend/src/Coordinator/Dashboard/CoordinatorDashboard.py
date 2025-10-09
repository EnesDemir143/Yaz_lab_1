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
        self.dashboard_built = False  # Dashboard'un oluşturulup oluşturulmadığını takip et
        
        if self.setup_mode:
            self.start_setup_only()
        else:
            self.build_dashboard()
            self.show()
    
    def build_dashboard(self):
        """Dashboard UI'ını oluştur"""
        if self.dashboard_built:
            return
            
        self.setWindowTitle("Coordinator Dashboard | Koordinatör Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/admin_dashboard_styles.qss"))
        
        # Ana layout
        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content_layout = QVBoxLayout()
        
        # Sidebar
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
        
        # Content area
        self.title_label = QLabel("Coordinator Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        
        email = self.user_info.get("email", "unknown@domain")
        dept = self.user_info.get("department", "Bilinmiyor")
        self.info_label = QLabel(f"{email} | {dept}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")
        
        # Stack layout
        self.stack = QStackedLayout()
        
        # General page
        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Koordinatör paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)
        
        # Other pages
        self.upload_classes_page = UploadClassList(self.user_info, self)
        self.upload_students_page = UploadStudentList(self.user_info, self)
        self.insert_classroom_page = ClassroomPage(self.stack, self.user_info, setup_mode=False)
        self.insert_classroom_page.done.connect(self.on_classroom_done)
        self.student_list_page = StudentListPage(self.user_info, self)
        self.class_list_page = ClassListPage(self.user_info, self)
        
        # Add pages to stack
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
        self.dashboard_built = True
    
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
        """Setup modunu başlat"""
        self.hide()
        self.insert_classroom_page_setup = InsertClassroomPage(None, self.user_info, setup_mode=True)
        self.insert_classroom_page_setup.done.connect(self.goto_classroom_management)
        self.insert_classroom_page_setup.showFullScreen()
    
    def goto_classroom_management(self):
        """InsertClassroom'dan ClassroomPage'e geç"""
        if hasattr(self, "insert_classroom_page_setup"):
            self.insert_classroom_page_setup.close()
        
        self.classroom_management_page = ClassroomPage(None, self.user_info, setup_mode=True)
        self.classroom_management_page.done.connect(self.goto_upload_classes_list)
        self.classroom_management_page.showFullScreen()
    
    def goto_upload_classes_list(self):
        if hasattr(self, "classroom_management_page"):
            self.classroom_management_page.close()
            
        self.upload_classes_list =  UploadClassList(self.user_info, None, setup_mode=True)
        self.upload_classes_list.done.connect(self.goto_upload_students_list)
        self.upload_classes_list.showFullScreen()
        
    def goto_upload_students_list(self):
        if hasattr(self, "upload_classes_list"):
            self.upload_classes_list.close()
        
        self.upload_students_list = UploadStudentList(self.user_info, None, setup_mode=True)
        self.upload_students_list.done.connect(self.finish_setup)
        self.upload_students_list.showFullScreen()
        
    def finish_setup(self):
        if hasattr(self, "classroom_management_page"):
            self.classroom_management_page.close()
        
        self.setup_mode = False
        
        if not self.dashboard_built:
            self.build_dashboard()
        
        if self.layout():
            self.layout().update()
            self.layout().activate()
        
        self.update()
        self.repaint()
        
        self.show()
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
    
    def logout(self):
        self.controller.logout()