from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet

class CoordinatorDashboard(QWidget):
    def __init__(self, parent, user_info=None):
        super().__init__()
        self.parent = parent
        self.user_info = user_info
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Coordinator Dashboard | Koordinatör Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/admin_dashboard_styles.qss"))

        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content_layout = QVBoxLayout()

        # ---- Menü ----
        sidebar_label = QLabel("🧭 Coordinator Menü")
        sidebar_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sidebar_label.setAlignment(Qt.AlignCenter)

        self.menu = QListWidget()
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

        sidebar.addWidget(sidebar_label)
        sidebar.addWidget(self.menu)
        sidebar.addStretch()

        self.title_label = QLabel("Coordinator Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(f"{self.user_info['email']} | {self.user_info['department']}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        self.stack = QStackedLayout()

        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Coordinator paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)

        self.empty_page = QWidget()
        e_layout = QVBoxLayout()
        e_label = QLabel("Bu bölüm henüz aktif değil.")
        e_label.setAlignment(Qt.AlignCenter)
        e_layout.addWidget(e_label)
        self.empty_page.setLayout(e_layout)

        # Stack’e ekleme
        self.stack.addWidget(self.general_page)

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
            3: ("insert_classroom", "Sınıf Ekle"),
            4: ("student_list", "Öğrenci Listesi"),
            5: ("class_list", "Ders Listesi"),
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
