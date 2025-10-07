import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont


API_BASE = "http://127.0.0.1:8000/admin"


# ---- Worker Thread ----
class UploadWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, file_path: str, userinfo: dict, department, headers=None):
        super().__init__()
        self.file_path = file_path
        self.userinfo = userinfo
        self.department = department
        self.headers = headers or {}

    def run(self):
        try:
            headers = {"Authorization": f"Bearer {self.userinfo['token']}"}
            with open(self.file_path, "rb") as f:
                files = {
                    "file": (
                        self.file_path.split("/")[-1],
                        f,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                }
                data = {"uploaded_department": self.department}
                resp = requests.post(
                    f"{API_BASE}/upload_classes_list",
                    files=files,
                    data=data,
                    headers=headers, 
                    timeout=30
                )
            try:
                result = resp.json()
            except Exception:
                result = {"message": resp.text}
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"error": str(e)})


# ---- Ana GUI ----
class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info 
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
        titles = [
            "Genel", "Ders Listesi Yükle",
            "Öğrenci Listesi Yükle", "Koordinatör Ekle", "Sınıf Ekle"
        ]
        self.title_label.setText(titles[index])
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

        self.worker = UploadWorker(self.file_path, self.user_info, department=department)
        self.worker.finished.connect(self.on_upload_finished)
        self.worker.start()

    def on_upload_finished(self, result):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)

        if "error" in result:
            QMessageBox.critical(self, "Hata", result["error"])
            self.text_output.append(f"❌ Hata: {result['error']}\n")
        else:
            msg = result.get("message", "İstek tamamlandı.")
            self.text_output.append(f"✅ Ders listesi yüklendi.\nℹ️ {msg}\n")
            QMessageBox.information(self, "Başarılı", msg)
        self.menu.setCurrentRow(0)  # işlem bitince “Genel” sekmesine dön