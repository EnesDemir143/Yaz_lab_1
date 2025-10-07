from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import requests
from Frontend.src.Admin.ClassListPage.class_list_page_worker import Class_list_page_worker
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Admin.ClassListPage.get_departments_worker import departments_list_worker 


class ClassListPage(QWidget):
    def __init__(self, user_info, parent_dashboard):
        super().__init__()
        self.user_info = user_info
        self.parent_dashboard = parent_dashboard
        self.department_names = []  # boş başlat

        self.init_ui()
        self.load_departments()

    def load_departments(self):
        self.get_departments_worker = departments_list_worker("get_departments", self.user_info)
        self.get_departments_worker.finished.connect(self.handle_departments_response)
        self.get_departments_worker.start()

    def handle_departments_response(self, result):
        if result.get('status') == 'success':
            departments = result.get('departments', [])
            self.department_names = [d['department'] for d in departments]

            for dept in self.department_names:
                item = QListWidgetItem(dept)
                self.department_list.addItem(item)

        else:
            self.student_title.setText("Bölümler yüklenemedi!")

    def show_classes_for_department(self, item):
        department = item.text()
        self.class_list.clear()
        self.student_list.clear()

        worker = Class_list_page_worker("all_classes", {"department": department}, self.user_info)
        worker.finished.connect(self.handle_classes_response)
        worker.start()

    def handle_classes_response(self, result):
        if result.get('status') == 'success':
            self.class_list.clear()
            classes = result.get('classes', [])
            for cls in classes:
                item = QListWidgetItem(f"{cls['code']} - {cls['name']}")
                item.setData(Qt.UserRole, cls['code'])
                self.class_list.addItem(item)
        else:
            self.student_title.setText("Dersler yüklenemedi!")

    def show_students_for_class(self, item):
        class_code = item.data(Qt.UserRole)
        self.student_list.clear()

        worker = Class_list_page_worker("students_for_class", {"class_code": class_code}, self.user_info)
        worker.finished.connect(self.handle_students_response)
        worker.start()

    def handle_students_response(self, result):
        if result.get('status') == 'success':
            students = result.get('students', [])
            for s in students:
                self.student_list.addItem(f"{s['student_num']} - {s['name']} {s['surname']}")
        else:
            self.student_title.setText("Öğrenciler yüklenemedi!")

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Başlık
        title = QLabel("📚 Ders Listesi Menüsü")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Bölüm listesi
        self.department_list = QListWidget()
        self.department_list.itemClicked.connect(self.show_classes_for_department)
        layout.addWidget(QLabel("Bölümler:"))
        layout.addWidget(self.department_list)

        # Ders listesi
        self.class_list = QListWidget()
        self.class_list.itemClicked.connect(self.show_students_for_class)
        layout.addWidget(QLabel("Dersler:"))
        layout.addWidget(self.class_list)

        # Öğrenci listesi alanı
        self.student_frame = QFrame()
        self.student_layout = QVBoxLayout(self.student_frame)

        self.student_title = QLabel("Bir ders seçiniz")
        self.student_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.student_layout.addWidget(self.student_title)

        self.student_list = QListWidget()
        self.student_layout.addWidget(self.student_list)

        layout.addWidget(QLabel("Öğrenciler:"))
        layout.addWidget(self.student_frame)


    