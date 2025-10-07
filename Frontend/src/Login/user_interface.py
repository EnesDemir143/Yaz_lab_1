import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from Frontend.src.Admin.admin_dashboard import AdminDashboard

LOGIN_API_URL = "http://127.0.0.1:8000/login"

# ---- Worker Thread ----
class LoginWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        try:
            resp = requests.post(LOGIN_API_URL, json={
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
        # ---- Genel pencere ayarları ----
        self.setWindowTitle("Kullanıcı Giriş Ekranı")
        self.setMinimumSize(800, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e2f, stop:1 #2a2a40
                );
            }
        """)

        # ---- Orta kısımda kart görünümü ----
        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setStyleSheet("""
            QFrame#card {
                background-color: rgba(255, 255, 255, 0.12);
                border-radius: 20px;
                padding: 40px;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 10px;
                padding: 10px;
                background: rgba(255,255,255,0.08);
                color: white;
                selection-background-color: #4CAF50;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
                background: rgba(255,255,255,0.15);
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(shadow)

        # Başlık
        title = QLabel("Kullanıcı Giriş Paneli")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Inputlar
        font = QFont("Segoe UI", 12)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-posta adresiniz")
        self.email_input.setFont(font)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(font)
        self.password_input.returnPressed.connect(self.handle_login)

        # Giriş butonu
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_button.clicked.connect(self.handle_login)

        # Bilgi etiketi (örnek hata mesajı için)
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

        # Ana layout — kartı ortala
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(self.card, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    # ---- Login işlemi ----
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
            self.dashboard = AdminDashboard(user_info=self.userinfo)
            self.dashboard.show()
            self.close()
        elif role == "coordinator":
            self.status_label.setText("✅ Koordinatör girişi başarılı!")
        else:
            self.status_label.setText("✅ Giriş başarılı!")

# ---- Main ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
