from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Admin.InsertCoordinator.insertWorker import InsertWorker

class InsertCoordinator(QWidget):
    def __init__(self, user_info, parent_dashboard=None):
        super().__init__()
        self.user_info = user_info
        self.parent_dashboard = parent_dashboard  # AdminDashboard referansı
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("➕ Koordinatör Ekle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        desc = QLabel("Yeni koordinatör eklemek için bilgileri girin:")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #aaa;")

        # --- Email girişi ---
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        self.email_input = QTextEdit()
        self.email_input.setFixedHeight(30)
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)

        # --- Şifre girişi ---
        password_layout = QHBoxLayout()
        password_label = QLabel("Şifre:")
        self.password_input = QTextEdit()
        self.password_input.setFixedHeight(30)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # --- Bölüm seçimi ---
        dept_layout = QHBoxLayout()
        dept_label = QLabel("🏫 Bölüm Seçin:")
        self.department_box = QComboBox()
        self.department_box.addItems(["A Bölümü", "B Bölümü", "C Bölümü"])
        dept_layout.addWidget(dept_label)
        dept_layout.addWidget(self.department_box)

        # --- Ekle butonu ---
        self.add_btn = QPushButton("➕ Koordinatör Ekle")
        self.add_btn.clicked.connect(self.add_coordinator_action)

        # --- Layout birleştirme ---
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(dept_layout)
        layout.addLayout(email_layout)
        layout.addLayout(password_layout)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)
        
    def add_coordinator_action(self):
        email = self.email_input.toPlainText().strip()
        password = self.password_input.toPlainText().strip()
        department = self.department_box.currentText()

        if not email or not password or not department:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return
        
        if not self.parent_dashboard or not hasattr(self.parent_dashboard, "current_endpoint"):
            QMessageBox.warning(self, "Uyarı", "Geçerli bir işlem seçilmedi.")
            return
        
        self.worker = InsertWorker(
            endpoint=self.parent_dashboard.current_endpoint,
            coordinator_email=email,
            coordinator_password=password,
            coordinator_department=department,
            userinfo=self.user_info
        )

        self.worker.finished.connect(self.on_add_finished)
        self.worker.start()
        
        self.email_input.clear()
        self.password_input.clear()
        self.department_box.setCurrentIndex(0)
        
    def on_add_finished(self, result):
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
            self.parent_dashboard.menu.setCurrentRow(0)