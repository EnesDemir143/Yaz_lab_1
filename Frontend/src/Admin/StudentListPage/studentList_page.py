from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from Frontend.src.Styles.load_qss import load_stylesheet

class StudentListPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/student_list_page_styles.qss"))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # --- Başlık ---
        title = QLabel("🎓 Öğrenci Listesi Menüsü")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        # --- Açıklama kısmı ---
        info = QLabel(
            "Ekranda bir arama kutusu bulunur. Öğrenci numarasına göre arama yapılır.<br>"
            "Kullanıcı öğrenci numarasını yazıp <b>“Ara”</b> dediğinde:<br>"
            "• Öğrencinin adı-soyadı<br>"
            "• Aldığı tüm dersler<br>"
            "• Derslerin kodları listelenir."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # --- Arama kutusu ve buton ---
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Öğrenci numarasını giriniz...")
        self.search_button = QPushButton("Ara")
        self.search_button.clicked.connect(self.search_student)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # --- Sonuç alanı ---
        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout()
        self.result_frame.setLayout(self.result_layout)
        layout.addWidget(self.result_frame)

        # --- Liste alanı ---
        self.class_list = QListWidget()
        layout.addWidget(self.class_list)

        self.setLayout(layout)

    def search_student(self):
        student_id = self.search_box.text().strip()

        # Basit örnek veri tabanı gibi:
        students = {
            "260201001": {
                "name": "Ayşe Yılmaz",
                "courses": [
                    ("Algoritmalar", "CSE301"),
                    ("Veri Yapıları", "CSE201")
                ]
            },
            "260201002": {
                "name": "Ahmet Demir",
                "courses": [
                    ("Veri Tabanı", "CSE303"),
                    ("Yapay Zeka", "CSE401")
                ]
            }
        }

        self.result_layout.takeAt(0)  # Önceki sonucu temizle
        self.class_list.clear()

        if student_id in students:
            student = students[student_id]
            name_label = QLabel(f"<b>Öğrenci:</b> {student['name']}")
            courses_label = QLabel("<b>Aldığı Dersler:</b>")
            name_label.setStyleSheet("color: #ff5555; font-size: 16px;")
            courses_label.setStyleSheet("color: #ff5555; font-size: 16px;")
            self.result_layout.addWidget(name_label)
            self.result_layout.addWidget(courses_label)

            for course, code in student["courses"]:
                item = QListWidgetItem(f"- {course} (Kodu: {code})")
                self.class_list.addItem(item)
        else:
            not_found = QLabel("❌ Öğrenci bulunamadı.")
            not_found.setStyleSheet("color: #ff4444; font-size: 15px;")
            self.result_layout.addWidget(not_found)
