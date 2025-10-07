import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QFileDialog, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

API_BASE = "http://127.0.0.1:8000/admin"


# ---- Worker Threads ----
class UploadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, filepath: str, headers: dict = None):
        super().__init__()
        self.endpoint = endpoint
        self.filepath = filepath
        self.headers = headers or {}

    def run(self):
        try:
            with open(self.filepath, "rb") as f:
                files = {
                    "file": (
                        self.filepath.split("/")[-1],
                        f,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                }
                resp = requests.post(f"{API_BASE}/{self.endpoint}", files=files, headers=self.headers)
            self.finished.emit(resp.json())
        except Exception as e:
            self.finished.emit({"error": str(e)})


class PostWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, endpoint: str, payload=None, headers=None):
        super().__init__()
        self.endpoint = endpoint
        self.payload = payload or {}
        self.headers = headers or {}

    def run(self):
        try:
            resp = requests.post(f"{API_BASE}/{self.endpoint}", json=self.payload, headers=self.headers)
            self.finished.emit(resp.json())
        except Exception as e:
            self.finished.emit({"error": str(e)})


# ---- Admin Dashboard ----
class AdminDashboard(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"name": "Admin", "department": "Bilinmiyor"}
        self.headers = {"Authorization": f"Bearer {self.user_info.get('token', '')}"}
        self.current_endpoint = None
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
            QProgressBar {
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                text-align: center;
                background-color: rgba(255,255,255,0.05);
                color: #f0f0f0;
            }
            QProgressBar::chunk { background-color: #4CAF50; border-radius: 10px; }
        """)

        # ---- Layouts ----
        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content = QVBoxLayout()

        # ---- Sidebar ----
        sidebar_label = QLabel("🧭 Admin Menü")
        sidebar_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sidebar_label.setAlignment(Qt.AlignCenter)

        self.menu = QListWidget()
        for item_text in [
            "📁 Ders Listesi Yükle",
            "📚 Öğrenci Listesi Yükle",
            "👩‍🏫 Koordinatör Ekle",
            "🏫 Sınıf Ekle",
        ]:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(180, 40))
            self.menu.addItem(item)

        self.menu.currentRowChanged.connect(self.on_menu_selected)
        sidebar.addWidget(sidebar_label)
        sidebar.addWidget(self.menu)
        sidebar.addStretch()

        # ---- Content Area ----
        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(f"{self.user_info['name']} | {self.user_info['department']}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Yönetim paneline hoş geldiniz.\n")

        self.action_btn = QPushButton("Dosya Seç ve Yükle")
        self.action_btn.clicked.connect(self.handle_action)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        content.addWidget(self.title_label)
        content.addWidget(self.info_label)
        content.addWidget(self.text_output, 4)
        content.addWidget(self.action_btn)
        content.addWidget(self.progress_bar)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content, 3)

    # ---- Menü seçimi ----
    def on_menu_selected(self, index):
        mapping = {
            0: ("upload_classes_list", "Ders Listesi Yükle", True),
            1: ("upload_students_list", "Öğrenci Listesi Yükle", True),
            2: ("insert_coordinator", "Koordinatör Ekle", False),
            3: ("insert_classroom", "Sınıf Ekle", False),
        }

        if index in mapping:
            self.current_endpoint, title, needs_file = mapping[index]
            self.title_label.setText(title)
            self.action_btn.setText("Dosya Seç ve Yükle" if needs_file else "İşlemi Gerçekleştir")
            self.text_output.append(f"🔹 {title} seçildi...\n")

    # ---- İşlem ----
    def handle_action(self):
        if not self.current_endpoint:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir işlem seçin.")
            return

        # Dosya yüklenmesi gereken işlemler
        if self.current_endpoint in ["upload_classes_list", "upload_students_list"]:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
            )
            if not file_path:
                return

            self.text_output.append(f"📂 {file_path} seçildi. Yükleniyor...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)

            self.worker = UploadWorker(self.current_endpoint, file_path, self.headers)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.on_action_finished)
            self.worker.start()

        # Normal POST (örneğin koordinatör/sınıf ekleme)
        else:
            self.text_output.append(f"🚀 {self.current_endpoint} isteği gönderiliyor...\n")
            self.worker = PostWorker(self.current_endpoint, headers=self.headers)
            self.worker.finished.connect(self.on_action_finished)
            self.worker.start()

    # ---- Sonuç ----
    def on_action_finished(self, result):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)

        if "error" in result:
            self.text_output.append(f"❌ Hata: {result['error']}\n")
        else:
            msg = result.get("message", "")
            detail = result.get("detail", "")
            self.text_output.append(f"✅ {msg}\nℹ️ Detay: {detail}\n")
