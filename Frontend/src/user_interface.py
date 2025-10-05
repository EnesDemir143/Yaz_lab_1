import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# ---- Worker Thread ----
class LoginWorker(QThread):
    finished = pyqtSignal(dict)   # sonucu GUI'ye gönderecek

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        try:
            resp = requests.post("http://127.0.0.1:8000/login", json={
                "email": self.email,
                "password": self.password
            })
            if resp.status_code == 200:
                self.finished.emit(resp.json())
            else:
                self.finished.emit({"error": resp.text})
        except Exception as e:
            self.finished.emit({"error": str(e)})


# ---- Login Window ----
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kullanıcı Giriş Ekranı")
        self.resize(700, 450)

        font = QFont("Segoe UI", 12)

        # Başlık
        title = QLabel("Kullanıcı Giriş Paneli")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-posta")
        self.email_input.setFont(font)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(font)

        # Login butonu
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 14px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(25)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(30)
        layout.addWidget(self.login_button)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        # Worker başlat
        self.worker = LoginWorker(email, password)
        self.worker.finished.connect(self.on_login_result)
        self.worker.start()

    def on_login_result(self, result):
        if "error" in result:
            print("Login failed:", result["error"])
        else:
            role = result.get("role")
            if role == "admin":
                print("✅ Admin dashboard açılacak")
            elif role == "coordinator":
                print("✅ Coordinator dashboard açılacak")
            else:
                print("Login sonucu:", result)


# ---- Main ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
