from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.ClassList.class_list_page_worker import Class_list_page_worker


class ClassListPage(QWidget):
    def __init__(self, user_info, parent_dashboard):
        super().__init__()
        self.user_info = user_info
        self.parent_dashboard = parent_dashboard

        self.department_name = self.user_info.get('department', 'Unknown Department')
        self.classes_data = {}

        self.init_ui()
        self.load_classes_for_department()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Başlık
        title = QLabel(f"📚 {self.department_name} Bölümü Ders Listesi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ders listesi
        self.class_frame = QFrame()
        self.class_layout = QVBoxLayout(self.class_frame)

        self.class_title = QLabel("Dersler:")
        self.class_title.setFont(QFont("Arial", 13, QFont.Bold))
        self.class_layout.addWidget(self.class_title)

        self.class_list = QListWidget()
        self.class_list.itemClicked.connect(self.show_students_for_class)
        self.class_layout.addWidget(self.class_list)

        layout.addWidget(self.class_frame)

        # Öğrenci listesi
        self.student_frame = QFrame()
        self.student_layout = QVBoxLayout(self.student_frame)

        self.student_title = QLabel("Bir ders seçiniz")
        self.student_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.student_layout.addWidget(self.student_title)

        self.student_list = QListWidget()
        self.student_layout.addWidget(self.student_list)

        layout.addWidget(self.student_frame)
        self.student_frame.setVisible(False)

    # ---- Verileri yükle ----
    def load_classes_for_department(self):
        self.class_list.clear()
        self.student_list.clear()
        self.student_frame.setVisible(False)

        self.worker = Class_list_page_worker(
            "all_classes",
            self.user_info
        )
        self.worker.finished.connect(self.handle_classes_response)
        self.worker.start()

    def handle_classes_response(self, result):
        if result.get('status') == 'success':
            classes = result.get('classes', {})
            self.classes_data = classes

            if not classes:
                self.class_list.addItem("Bu bölüme ait ders bulunamadı.")
                return

            for cls_id, cls in classes.items():
                item = QListWidgetItem(f"{cls['class_id']} - {cls['class_name']}")
                item.setData(Qt.UserRole, cls)
                self.class_list.addItem(item)
        else:
            self.class_list.addItem(f"Hata: {result.get('detail', 'Bilinmeyen hata')}")

    def show_students_for_class(self, item):
        cls = item.data(Qt.UserRole)
        students = cls.get('students', [])

        self.student_list.clear()
        self.student_title.setText(f"📖 {cls['class_id']} - {cls['class_name']} Dersi Alan Öğrenciler:")
        self.student_frame.setVisible(True)

        if not students:
            self.student_list.addItem("Bu derse kayıtlı öğrenci yok.")
        else:
            for s in students:
                self.student_list.addItem(f"{s['student_num']} - {s['name']} {s['surname']}")
