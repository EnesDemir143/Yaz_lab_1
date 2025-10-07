import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont


class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Admin", "department": "Bilinmiyor"}
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Dashboard | Yönetim Paneli")
        self.resize(1200, 750)
        self.setStyleSheet("""
            QWidget { background-color: #181a28; color: #f0f0f0; }
            QListWidget {
                background-color: rgba(255,255,255,0.05);
                border: none;
                border-radius: 12px;
                padding: 10px;
                color: #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 12px 15px;
            }
            QPushButton:hover { background-color: #45a049; }
            QTextEdit {
                background-color: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 10px;
                color: #ddd;
                font-family: Consolas, monospace;
            }
            QComboBox {
                background-color: #2a2c3a;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                padding: 6px;
                color: #f0f0f0;
            }
            QLabel { font-size: 14px; }
        """)

        # ---- Ana Layout ----
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

        # ---- Ortadaki kısım (başlık ve içerik) ----
        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(f"{self.user_info['name']} | {self.user_info['department']}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        # Stack yapısı: sayfalar arasında geçiş
        self.stack = QStackedLayout()

        # Sayfa 0 - Genel
        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Yönetim paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)

        # Sayfa 1 - Ders Listesi Yükle
        self.upload_classes_page = QWidget()
        u_layout = QVBoxLayout()
        title = QLabel("📁 Ders Listesi Yükle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        desc = QLabel("Yüklenecek Excel dosyasını ve bölümünüzü seçin:")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #aaa;")

        file_layout = QHBoxLayout()
        self.file_label = QLabel("Henüz dosya seçilmedi")
        self.file_label.setStyleSheet("color: #aaa;")
        self.select_btn = QPushButton("Dosya Seç")
        self.select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_btn)

        dept_layout = QHBoxLayout()
        dept_label = QLabel("🏫 Bölüm Seçin:")
        self.department_box = QComboBox()
        self.department_box.addItems(["A Bölümü", "B Bölümü", "C Bölümü"])
        dept_layout.addWidget(dept_label)
        dept_layout.addWidget(self.department_box)

        self.upload_btn = QPushButton("📤 Yüklemeyi Başlat")
        self.upload_btn.clicked.connect(self.upload_action)

        u_layout.addWidget(title)
        u_layout.addWidget(desc)
        u_layout.addLayout(file_layout)
        u_layout.addLayout(dept_layout)
        u_layout.addWidget(self.upload_btn)
        u_layout.addStretch()
        self.upload_classes_page.setLayout(u_layout)

        # Diğer sayfalar için placeholder
        self.empty_page = QWidget()
        empty_layout = QVBoxLayout()
        placeholder = QLabel("Bu bölüm henüz aktif değil.")
        placeholder.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(placeholder)
        self.empty_page.setLayout(empty_layout)

        # Stack’e sayfaları ekle
        self.stack.addWidget(self.general_page)       # 0
        self.stack.addWidget(self.upload_classes_page) # 1
        self.stack.addWidget(self.empty_page)         # 2 - öğrenci
        self.stack.addWidget(self.empty_page)         # 3 - koordinatör
        self.stack.addWidget(self.empty_page)         # 4 - sınıf

        # ---- İçeriği birleştir ----
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        content_layout.addLayout(self.stack)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)

        # Varsayılan olarak “Genel” açık
        self.menu.setCurrentRow(0)

    # ---- Menü değiştiğinde ----
    def switch_page(self, index):
        titles = [
            "Genel", "Ders Listesi Yükle",
            "Öğrenci Listesi Yükle", "Koordinatör Ekle", "Sınıf Ekle"
        ]
        self.title_label.setText(titles[index])
        self.stack.setCurrentIndex(index)

    # ---- Dosya seçimi ----
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_label.setText(file_path.split("/")[-1])
            self.file_path = file_path
        else:
            self.file_path = None

    # ---- Yükleme işlemi ----
    def upload_action(self):
        if not self.file_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir Excel dosyası seçin.")
            return
        department = self.department_box.currentText()
        QMessageBox.information(
            self, "Bilgi",
            f"Dosya: {self.file_path}\nBölüm: {department}\n\n(Burada API isteği yapılacak)"
        )
        # İşlem geçmişine yaz
        self.text_output.append(f"📤 {self.file_path.split('/')[-1]} ({department}) yüklendi.\n")