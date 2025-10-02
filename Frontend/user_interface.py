import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QRadioButton, QVBoxLayout, QButtonGroup, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kullanıcı Giriş Ekranı")
        self.resize(700, 450)  # Daha geniş ekran

        # Genel yazı tipi
        font = QFont("Segoe UI", 12)

        # Başlık
        title = QLabel("Kullanıcı Giriş Paneli")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # E-posta alanı
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-posta")
        self.email_input.setFont(font)
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)

        # Şifre alanı
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(font)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)

        # Kullanıcı rolleri (tek seçimlik radio button) - yan yana
        self.admin_radio = QRadioButton("Admin")
        self.coordinator_radio = QRadioButton("Bölüm Koordinatörü")
        self.student_radio = QRadioButton("Öğrenci")

        for rb in [self.admin_radio, self.coordinator_radio, self.student_radio]:
            rb.setFont(QFont("Segoe UI", 12, QFont.Bold))
            rb.setStyleSheet("""
                QRadioButton {
                    padding: 8px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 6px;
                }
                QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)

        # Radio butonları gruplandır
        self.user_group = QButtonGroup(self)
        self.user_group.addButton(self.admin_radio)
        self.user_group.addButton(self.coordinator_radio)
        self.user_group.addButton(self.student_radio)

        # Radio butonları yatay düzenle
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.admin_radio)
        radio_layout.addWidget(self.coordinator_radio)
        radio_layout.addWidget(self.student_radio)
        radio_layout.setAlignment(Qt.AlignCenter)
        radio_layout.setSpacing(30)

        # Giriş butonu (yeşil)
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

        # Düzen
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(25)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addLayout(radio_layout)
        layout.addSpacing(30)
        layout.addWidget(self.login_button)

        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
