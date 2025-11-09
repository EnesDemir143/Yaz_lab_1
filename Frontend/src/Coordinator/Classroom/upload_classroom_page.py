from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QHBoxLayout, QTextEdit, QFrame, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet


class UploadClassroomPage(QWidget):
    def __init__(self, parent_stack, user_info, classroom_id, dashboard=None):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.dashboard = dashboard
        self.classroom_id = classroom_id
        self.init_ui()

        # API'den mevcut bilgileri çek
        self.fetch_classroom_data()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)

        title = QLabel(f"🏫 Derslik Bilgilerini Güncelle ({self.classroom_id})")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # Form alanları
        self.classroom_name = QLineEdit()
        self.department_box = QComboBox()
        self.department_box.addItems(["", "Bilgisayar Mühendisliği", "Elektrik Mühendisliği", "Elektronik Mühendisliği", "İnşaat Mühendisliği"])
        self.capacity = QLineEdit()
        self.desks_row = QLineEdit()
        self.desks_col = QLineEdit()
        self.structure = QLineEdit()

        self.form_fields = [
            ("Derslik Adı:", self.classroom_name),
            ("Bölüm Adı:", self.department_box),
            ("Kapasite:", self.capacity),
            ("Sıra Satır Sayısı:", self.desks_row),
            ("Sıra Sütun Sayısı:", self.desks_col),
            ("Masa Yapısı:", self.structure)
        ]

        for label, widget in self.form_fields:
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 11))
            self.layout.addWidget(lbl)
            self.layout.addWidget(widget)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ Geri Dön")
        self.save_btn = QPushButton("💾 Kaydet")
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.save_btn)
        self.layout.addLayout(btn_layout)

        # Sonuç / log alanı
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.layout.addWidget(self.result)

        self.setLayout(self.layout)

        # Buton olayları
        self.back_btn.clicked.connect(self.go_back)
        self.save_btn.clicked.connect(self.update_classroom)

    def fetch_classroom_data(self):
        self.result.setText("⏳ Derslik bilgileri yükleniyor...")
        self.worker = ClassroomRequests("search_classroom", {"classroom_code": self.classroom_id}, self.user_info)
        self.worker.finished.connect(self.handle_fetch_response)
        self.worker.start()

    def handle_fetch_response(self, response):
        """Veri çekildikten sonra formu doldur."""
        if response.get("status") == "error":
            QMessageBox.critical(self, "Hata", response.get("detail", "Derslik bilgisi alınamadı."))
            return

        classroom = response.get("classroom", {})
        self.classroom_name.setText(classroom.get("classroom_name", ""))
        dept_name = classroom.get("department_name", "")
        index = self.department_box.findText(dept_name)
        if index != -1:
            self.department_box.setCurrentIndex(index)
        else:
            self.department_box.setCurrentIndex(0)
        self.capacity.setText(str(classroom.get("capacity", "")))
        self.desks_row.setText(str(classroom.get("desks_per_row", "")))
        self.desks_col.setText(str(classroom.get("desks_per_column", "")))
        self.structure.setText(str(classroom.get("desk_structure", "")))

        self.result.setText("✅ Derslik bilgileri yüklendi.")

    def update_classroom(self):
        """Kullanıcının düzenlediği bilgileri API'ye gönderir."""
        if not all([
            self.classroom_name.text().strip(),
            self.department_box.currentText().strip(),
            self.capacity.text().strip(),
            self.desks_row.text().strip(),
            self.desks_col.text().strip(),
            self.structure.text().strip()
        ]):
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        try:
            data = {
                "classroom_id": self.classroom_id,
                "classroom_name": self.classroom_name.text().strip(),
                "department_name": self.department_box.currentText().strip(),
                "capacity": int(self.capacity.text().strip()),
                "desks_per_row": int(self.desks_row.text().strip()),
                "desks_per_column": int(self.desks_col.text().strip()),
                "desk_structure": self.structure.text().strip()
            }
        except ValueError:
            QMessageBox.warning(self, "Hata", "Kapasite, satır ve sütun değerleri sayısal olmalıdır.")
            return

        self.result.setText("⏳ Güncelleme yapılıyor...")

        self.worker = ClassroomRequests("update_classroom", data, self.user_info)
        self.worker.finished.connect(self.handle_update_response)
        self.worker.start()

    def handle_update_response(self, response):
        if response.get("status") == "error":
            QMessageBox.critical(self, "Hata", response.get("detail", "Derslik güncellenemedi."))
        else:
            QMessageBox.information(self, "Başarılı", "Derslik başarıyla güncellendi!")
            self.result.setText("✅ Güncelleme başarılı!")

    def go_back(self):
        from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage
        classroom_page = ClassroomPage(self.parent_stack, self.user_info, self.dashboard)
        self.parent_stack.addWidget(classroom_page)
        self.parent_stack.setCurrentWidget(classroom_page)
