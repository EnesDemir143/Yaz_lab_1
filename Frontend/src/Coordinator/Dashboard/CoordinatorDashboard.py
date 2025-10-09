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
from Frontend.src.Coordinator.ClassList.class_list_page import ClassListPage

class CoordinatorDashboard(QWidget):
    def __init__(self, controller, user_info=None):
        super().__init__()
        self.controller = controller
        self.user_info = user_info or {}
        self.file_path = None
        self.classroom_completed = False  # Sınıf ekleme tamamlandı mı?
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
        
        # Menü sırası değiştirildi - "Sınıf Ekle" Genel'in hemen altında
        for item_text in [
            "🏠 Genel",
            "🏫 Sınıf Ekle",
            "📁 Ders Listesi Yükle",
            "📚 Öğrenci Listesi Yükle",
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
        
        # Stack sırası menü sırasına göre güncellendi
        self.insert_classroom_page = ClassroomPage(self.stack, self.user_info)
        self.upload_classes_page = UploadClassList(self.user_info, self)
        self.upload_students_page = UploadStudentList(self.user_info, self)
        self.student_list_page = StudentListPage(self.user_info, self)
        self.class_list_page = ClassListPage(self.user_info, self)
        
        self.stack.addWidget(self.general_page)  # 0
        self.stack.addWidget(self.insert_classroom_page)  # 1
        self.stack.addWidget(self.upload_classes_page)  # 2
        self.stack.addWidget(self.upload_students_page)  # 3
        self.stack.addWidget(self.student_list_page)  # 4
        self.stack.addWidget(self.class_list_page)  # 5
        
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        frame = QFrame()
        frame.setLayout(self.stack)
        content_layout.addWidget(frame)
        
        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)
        
        # Başlangıçta "Sınıf Ekle" sayfasını göster (index 1)
        self.menu.setCurrentRow(1)
        self.disable_other_menu_items()
    
    def disable_other_menu_items(self):
        """Sınıf Ekle dışındaki tüm menü öğelerini devre dışı bırak"""
        if not self.classroom_completed:
            for i in range(self.menu.count()):
                if i != 1:  # 1 = Sınıf Ekle index'i
                    item = self.menu.item(i)
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                    item.setForeground(Qt.gray)
    
    def enable_all_menu_items(self):
        """Tüm menü öğelerini aktif et"""
        self.classroom_completed = True
        for i in range(self.menu.count()):
            item = self.menu.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            item.setForeground(Qt.white)  # Veya varsayılan renginiz
    
    def create_placeholder_page(self, message):
        w = QWidget()
        l = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #ccc; font-size: 15px;")
        l.addWidget(label)
        w.setLayout(l)
        return w
    
    def switch_page(self, index):
        # Sınıf ekleme tamamlanmadıysa ve Sınıf Ekle dışında bir sayfa seçildiyse, engelle
        if not self.classroom_completed and index != 1:
            self.menu.setCurrentRow(1)  # Tekrar Sınıf Ekle'ye dön
            return
        
        # Güncellenmiş mapping - sıra değişti
        mapping = {
            0: ("general", "Genel"),
            1: ("insert_classroom", "Sınıf Ekle"),
            2: ("upload_classes_list", "Ders Listesi Yükle"),
            3: ("upload_students_list", "Öğrenci Listesi Yükle"),
            4: ("student_list", "Öğrenci Listesi"),
            5: ("class_list", "Ders Listesi"),
        }
        
        if index in mapping:
            self.current_endpoint, title = mapping[index]
            self.title_label.setText(title)
            self.stack.setCurrentIndex(index)
    
    def logout(self):
        self.controller.logout()