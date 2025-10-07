from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Admin.UploadPages.upload_class import UploadClassList
from Frontend.src.Admin.UploadPages.upload_student import uploadStudentList
from Frontend.src.Admin.InsertCoordinator.insert_coordinator import InsertCoordinator
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Admin.Classroom.clasroomPage import ClassroomPage

class AdminDashboard(QWidget):
    def __init__(self, parent, user_info=None):
        super().__init__()
        self.parent = parent
        self.user_info = user_info
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Dashboard | Yönetim Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/admin_dashboard_styles.qss"))

        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content_layout = QVBoxLayout()

        # ---- Menü ----
        sidebar_label = QLabel("🧭 Admin Menü")
        sidebar_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sidebar_label.setAlignment(Qt.AlignCenter)

        self.menu = QListWidget()
        for item_text in [
            "🏠 Genel",
            "📁 Ders Listesi Yükle",
            "📚 Öğrenci Listesi Yükle",
            "👩‍🏫 Koordinatör Ekle",
            "🏫 Sınıf Ekle",
        ]:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(180, 40))
            self.menu.addItem(item)
        self.menu.currentRowChanged.connect(self.switch_page)

        sidebar.addWidget(sidebar_label)
        sidebar.addWidget(self.menu)
        sidebar.addStretch()

        # ---- Başlık ve bilgi ----
        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(f"{self.user_info['email']} | {self.user_info['department']}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        # ---- Stack sayfaları ----
        self.stack = QStackedLayout()

        # Genel sayfa
        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Yönetim paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)

        # Ders listesi yükleme sayfası (yeni sınıftan)
        self.upload_classes_page = UploadClassList(self.user_info, self)
        
        self.upload_students_page = uploadStudentList(self.user_info, self)
        
        self.inser_coordinator_page = InsertCoordinator(self.user_info, self)

        self.classroom_page = ClassroomPage(self.stack, self.user_info)

        self.empty_page = QWidget()
        e_layout = QVBoxLayout()
        e_label = QLabel("Bu bölüm henüz aktif değil.")
        e_label.setAlignment(Qt.AlignCenter)
        e_layout.addWidget(e_label)
        self.empty_page.setLayout(e_layout)

        # Stack’e ekleme
        self.stack.addWidget(self.general_page)
        self.stack.addWidget(self.upload_classes_page)
        self.stack.addWidget(self.upload_students_page)
        self.stack.addWidget(self.inser_coordinator_page)
        self.stack.addWidget(self.classroom_page)
        self.stack.addWidget(self.empty_page)
        self.stack.addWidget(self.empty_page)
        self.stack.addWidget(self.empty_page)

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        content_layout.addLayout(self.stack)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)

        self.menu.setCurrentRow(0)

    def switch_page(self, index):
        mapping = {
            0: ("general", "Genel"),
            1: ("upload_classes_list", "Ders Listesi Yükle"),
            2: ("upload_students_list", "Öğrenci Listesi Yükle"),
            3: ("insert_coordinator", "Koordinatör Ekle"),
            4: ("insert_classroom", "Sınıf Ekle"),
        }

        if index in mapping:
            self.current_endpoint, title = mapping[index]
            self.title_label.setText(title)
            self.stack.setCurrentIndex(index)

    def closeEvent(self, event):
        if self.parent:
            self.parent.show()
            self.parent.status_label.setText("")
        event.accept()
