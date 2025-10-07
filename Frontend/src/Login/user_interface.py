import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from Frontend.src.Admin.Dashboard.admin_dashboard import AdminDashboard
from Frontend.src.Login.loginWorker import LoginWorker
from Frontend.src.Styles.load_qss import load_stylesheet

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kullanıcı Giriş Ekranı")
        self.setMinimumSize(800, 500)
        self.card = QFrame()
        self.card.setObjectName("card")
        
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/login.qss"))

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(shadow)

        title = QLabel("Kullanıcı Giriş Paneli")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        font = QFont("Segoe UI", 12)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-posta adresiniz")
        self.email_input.setFont(font)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(font)
        self.password_input.returnPressed.connect(self.handle_login)

        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.clicked.connect(self.handle_login)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FF5C5C;")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(25)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addWidget(self.login_button)
        layout.addSpacing(15)
        layout.addWidget(self.status_label)
        self.card.setLayout(layout)

        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    def handle_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.status_label.setText("Lütfen e-posta ve şifre giriniz.")
            return

        self.status_label.setText("Giriş yapılıyor...")

        self.worker = LoginWorker(email, password)
        self.worker.finished.connect(self.on_login_result)
        self.worker.start()

    def on_login_result(self, result):
        if "error" in result:
            self.status_label.setText("❌ " + result["error"])
            return

        token = result.get("token")
        role = result.get("role")

        if not token:
            self.status_label.setText("⚠️ Sunucudan token alınamadı.")
            return

        self.status_label.setStyleSheet("color: #4CAF50;")

        self.userinfo = {
            "email": result.get("email"),
            "department": result.get("department"),
            "role": role,
            "token": token
        }

        if role == "admin":
            self.status_label.setText("✅ Admin girişi başarılı!")
            self.dashboard = AdminDashboard(user_info=self.userinfo, parent=self)
            self.dashboard.show()
            self.hide()
        elif role == "coordinator":
            self.status_label.setText("✅ Koordinatör girişi başarılı!")
        else:
            self.status_label.setText("✅ Giriş başarılı!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
