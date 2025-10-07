from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Admin.upload_file import UploadWorker

def load_stylesheet(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info 
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Dashboard | Yönetim Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Admin/styles.qss"))

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

        # ---- Başlık ve Bilgi ----
        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(f"{self.user_info['email']} | {self.user_info['department']}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        # ---- Sayfa yönetimi (stack) ----
        self.stack = QStackedLayout()

        # 0️⃣ Genel sayfası
        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Yönetim paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)

        # 1️⃣ Ders listesi yükleme sayfası
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

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        u_layout.addWidget(title)
        u_layout.addWidget(desc)
        u_layout.addLayout(file_layout)
        u_layout.addLayout(dept_layout)
        u_layout.addWidget(self.upload_btn)
        u_layout.addWidget(self.progress_bar)
        u_layout.addStretch()

        self.upload_classes_page.setLayout(u_layout)

        # Placeholder diğer sayfalar
        placeholder = QLabel("Bu bölüm henüz aktif değil.")
        placeholder.setAlignment(Qt.AlignCenter)
        self.empty_page = QWidget()
        l = QVBoxLayout()
        l.addWidget(placeholder)
        self.empty_page.setLayout(l)

        # stack ekleme
        self.stack.addWidget(self.general_page)
        self.stack.addWidget(self.upload_classes_page)
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
            0: ("general", "Genel", False),
            1: ("upload_classes_list", "Ders Listesi Yükle", True),
            2: ("upload_students_list", "Öğrenci Listesi Yükle", True),
            3: ("insert_coordinator", "Koordinatör Ekle", False),
            4: ("insert_classroom", "Sınıf Ekle", False),
        }

        if index in mapping:
            self.current_endpoint, title, _ = mapping[index]
            self.title_label.setText(title)
            self.stack.setCurrentIndex(index)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_label.setText(file_path.split("/")[-1])
            self.file_path = file_path

    def upload_action(self):
        if not self.file_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir Excel dosyası seçin.")
            return
        department = self.department_box.currentText()

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        if not hasattr(self, "current_endpoint") or not self.current_endpoint:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir işlem seçin.")
            return
    
        self.worker = UploadWorker(self.current_endpoint, self.file_path, self.user_info, department=department)
        self.worker.finished.connect(self.on_upload_finished)
        self.worker.start()

    def on_upload_finished(self, result):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)

        if "error" in result.get("status", ""):
            QMessageBox.critical(self, "Hata", result["detail"])
            self.text_output.append(f"❌ Hata: {result['detail']} {result['message']}\n ")
        else:
            msg = result.get("message", "İstek tamamlandı.")
            detail = result.get("detail", "")
            self.text_output.append(f"✅ {detail}\n")
            QMessageBox.information(self, "Başarılı", f"message: {msg}\n\n{result['detail']}")
        self.menu.setCurrentRow(0) 