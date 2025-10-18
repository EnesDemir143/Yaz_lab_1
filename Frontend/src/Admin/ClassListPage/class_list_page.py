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

        # Verileri cache için
        self.departments_data = {}
        self.classes_data = {}

        self.init_ui()
        self.load_all_data()

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

        # Ders listesi (başta gizli)
        self.class_frame = QFrame()
        self.class_layout = QVBoxLayout(self.class_frame)

        self.class_list = QListWidget()
        self.class_list.itemClicked.connect(self.show_students_for_class)

        self.class_layout.addWidget(QLabel("Dersler:"))
        self.class_layout.addWidget(self.class_list)
        layout.addWidget(self.class_frame)
        self.class_frame.setVisible(False)

        # Öğrenci listesi (başta gizli)
        self.student_frame = QFrame()
        self.student_layout = QVBoxLayout(self.student_frame)

        self.student_title = QLabel("Bir ders seçiniz")
        self.student_title.setFont(QFont("Arial", 12, QFont.Bold))
        self.student_layout.addWidget(self.student_title)

        self.student_list = QListWidget()
        self.student_layout.addWidget(self.student_list)

        layout.addWidget(self.student_frame)
        self.student_frame.setVisible(False)

    def load_all_data(self):
        self.get_departments_worker = departments_list_worker("get_departments", self.user_info)
        self.get_departments_worker.finished.connect(self.handle_departments_response)
        self.get_departments_worker.start()
        self.class_workers = []  # ✅ thread’leri burada tut

    def handle_departments_response(self, result):
        if result.get('status') == 'success':
            print("Departments fetched successfully.")
            departments = result.get('departments', [])
            for dept_name in departments:
                self.departments_data[dept_name] = {}
                item = QListWidgetItem(dept_name)
                self.department_list.addItem(item)

                worker = Class_list_page_worker("all_classes", {"department": dept_name}, self.user_info)
                worker.finished.connect(lambda result, dept=dept_name: self.handle_classes_response(result, dept))
                worker.start()
                self.class_workers.append(worker)  # ✅ listeye ekle
        else:
            self.student_title.setText("Bölümler yüklenemedi!")


    def handle_classes_response(self, result, department):
        if result.get('status') == 'success':
            classes = result.get('classes', {})
            for cls_id, cls in classes.items():
                if department not in self.departments_data:
                    self.departments_data[department] = {}
                self.departments_data[department][cls_id] = cls
        else:
            self.student_title.setText(f"{department} bölümü için dersler yüklenemedi!")


    def show_classes_for_department(self, item):
        department = item.text()
        self.class_list.clear()
        self.student_list.clear()
        self.class_frame.setVisible(True)
        self.student_frame.setVisible(False)

        classes = self.departments_data.get(department, {})
        for cls_id, cls in classes.items():
            item = QListWidgetItem(f"{cls['class_id']} - {cls['class_name']}")
            item.setData(Qt.UserRole, cls)
            self.class_list.addItem(item)

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
