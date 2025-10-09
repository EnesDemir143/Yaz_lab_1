from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.UploadPages.upload_worker import UploadWorker


class UploadStudentList(QWidget):
    def __init__(self, user_info, parent_dashboard=None):
        super().__init__()
        self.user_info = user_info
        self.parent_dashboard = parent_dashboard
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📁 Öğrenci Listesi Yükle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        desc = QLabel("Yüklenecek Excel dosyasını seçiniz ")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #aaa;")

        file_layout = QHBoxLayout()
        self.file_label = QLabel("Henüz dosya seçilmedi")
        self.file_label.setStyleSheet("color: #aaa;")
        self.select_btn = QPushButton("Dosya Seç")
        self.select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_btn)

        self.upload_btn = QPushButton("📤 Yüklemeyi Başlat")
        self.upload_btn.clicked.connect(self.upload_action)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(file_layout)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

        self.setLayout(layout)

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

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)

        if not self.parent_dashboard or not hasattr(self.parent_dashboard, "current_endpoint"):
            QMessageBox.warning(self, "Uyarı", "Geçerli bir işlem seçilmedi.")
            return

        self.worker = UploadWorker(
            self.parent_dashboard.current_endpoint,
            self.file_path,
            self.user_info,
        )
        self.worker.finished.connect(self.on_upload_finished)
        self.worker.start()

    def on_upload_finished(self, result):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)

        if "error" in result.get("status", ""):
            QMessageBox.critical(self, "Hata", result["detail"])
            if self.parent_dashboard:
                self.parent_dashboard.text_output.append(
                    f"❌ Hata: {result['detail']} {result.get('message', '')}\n"
                )
        else:
            msg = result.get("message", "İstek tamamlandı.")
            detail = result.get("detail", "")
            if self.parent_dashboard:
                self.parent_dashboard.text_output.append(f"✅ {detail}\n")
            QMessageBox.information(self, "Başarılı", f"message: {msg}\n\n{detail}")

        if self.parent_dashboard:
            self.parent_dashboard.enable_next_step_after_student_upload()
