from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Coordinator.StudentListPage.student_list_worker import Student_list_search_worker

class StudentListPage(QWidget):
    def __init__(self, user_info, parent_dashboard):
        super().__init__()
        self.user_info = user_info
        self.parent_dashboard = parent_dashboard
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/student_list_page_styles.qss"))

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("🎓 Öğrenci Listesi Menüsü")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        info = QLabel(
            "Ekranda bir arama kutusu bulunur. Öğrenci numarasına göre arama yapılır.<br>"
            "Kullanıcı öğrenci numarasını yazıp <b>“Ara”</b> dediğinde:<br>"
            "• Öğrencinin adı-soyadı<br>"
            "• Aldığı tüm dersler<br>"
            "• Derslerin kodları listelenir."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Öğrenci numarasını giriniz...")
        self.search_button = QPushButton("Ara")
        self.search_button.clicked.connect(self.search_student_action)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout()
        self.result_frame.setLayout(self.result_layout)
        layout.addWidget(self.result_frame)

        self.class_list = QListWidget()
        layout.addWidget(self.class_list)

        self.setLayout(layout)

    def search_student_action(self):
        student_id = self.search_box.text().strip()

        if not student_id.isdigit() or not student_id:
            self.result_layout.addWidget(QLabel("❌ Geçersiz öğrenci numarası."))
            return

        self.worker = Student_list_search_worker('student_list_filter', {'student_num': student_id}, self.user_info)
        
        self.worker.finished.connect(self.on_add_finished)
        self.worker.start()

        self.search_box.clear()
        
    def on_add_finished(self, result):
        self.result_layout.takeAt(0)  
        self.class_list.clear()

        if "error" in result.get("status", ""):
            self.result_layout.addWidget(QLabel(f"❌ Hata: {result.get('message', '')}"))
            if self.parent_dashboard:
                self.parent_dashboard.text_output.append(
                    f"❌ Hata: {result.get('message', '')}\n"
                )
            return

        name = result.get("name", "Bilinmiyor")
        surname = result.get("surname", "Bilinmiyor")
        classes = result.get("classes", [])

        self.result_layout.addWidget(QLabel(f"✅ Sonuç: {name} {surname}"))

        if not classes:
            self.result_layout.addWidget(QLabel("❌ Bu öğrenciye ait ders bulunamadı."))
            return

        for class_name, class_code in classes:
            item = QListWidgetItem(f"{class_name} ({class_code})")
            item.setBackground(QColor("#f100f0f0"))
            item.setFont(QFont("Segoe UI", 10))
            self.class_list.addItem(item)

        if self.parent_dashboard:
            self.parent_dashboard.text_output.append(
                f"✅ Başarılı: {name} {surname} adlı öğrencinin dersleri listelendi.\n"
            )
         
