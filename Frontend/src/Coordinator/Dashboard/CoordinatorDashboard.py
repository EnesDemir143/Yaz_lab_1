from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QStackedLayout, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet

class CoordinatorDashboard(QWidget):
    def __init__(self, controller, user_info=None):
        super().__init__()
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

        # ---- Sol Menü ----
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

        # ---- Çıkış butonu ----
        logout_btn = QPushButton("🚪 Çıkış Yap")
        logout_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)

        sidebar.addWidget(sidebar_label)
        sidebar.addWidget(self.menu)
        sidebar.addStretch()
        sidebar.addWidget(logout_btn)

        # ---- Üst bilgi ----
        self.title_label = QLabel("Coordinator Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        email = self.user_info.get("email", "unknown@domain")
        dept = self.user_info.get("department", "Bilinmiyor")
        self.info_label = QLabel(f"{email} | {dept}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        # ---- İçerik sayfaları ----
        self.stack = QStackedLayout()

        # 0️⃣ Genel sayfa
        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Koordinatör paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)

        # Diğer sayfalar placeholder
        self.upload_classes_page = self.create_placeholder_page("📁 Ders listesi yükleme alanı yakında aktif.")
        self.upload_students_page = self.create_placeholder_page("📚 Öğrenci listesi yükleme alanı yakında aktif.")
        self.insert_classroom_page = self.create_placeholder_page("🏫 Sınıf ekleme alanı yakında aktif.")
        self.student_list_page = self.create_placeholder_page("👨‍🎓 Öğrenci listesi yakında aktif.")
        self.class_list_page = self.create_placeholder_page("📖 Ders listesi yakında aktif.")

        # Stack’e sayfaları ekle (index sırasıyla eşleşsin)
        self.stack.addWidget(self.general_page)
        self.stack.addWidget(self.upload_classes_page)
        self.stack.addWidget(self.upload_students_page)
        self.stack.addWidget(self.insert_classroom_page)
        self.stack.addWidget(self.student_list_page)
        self.stack.addWidget(self.class_list_page)

        # ---- İçerik alanı ----
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        frame = QFrame()
        frame.setLayout(self.stack)
        content_layout.addWidget(frame)

        # ---- Genel yerleşim ----
        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)

        self.menu.setCurrentRow(0)

    # Basit placeholder sayfa oluşturucu
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
        titles = [
            "Genel",
            "Ders Listesi Yükle",
            "Öğrenci Listesi Yükle",
            "Sınıf Ekle",
            "Öğrenci Listesi",
            "Ders Listesi",
        ]

        if 0 <= index < len(titles):
            self.title_label.setText(titles[index])
            self.stack.setCurrentIndex(index)

    def logout(self):
        """AppController üzerinden logout işlemini tetikler"""
        self.controller.logout()
