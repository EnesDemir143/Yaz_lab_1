from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QTextEdit, QStackedLayout, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Coordinator.UploadPages.Upload_class import UploadClassList
from Frontend.src.Coordinator.UploadPages.Upload_student import UploadStudentList
from Frontend.src.Coordinator.StudentListPage.student_list_page import StudentListPage
from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage
from Frontend.src.Coordinator.ClassList.class_list_page import ClassListPage
from Frontend.src.Coordinator.Classroom.insert_classroom_page import InsertClassroomPage
from Frontend.src.Coordinator.ExamProgramPage.s_interface import ExamProgramPage
from Frontend.src.Coordinator.ExamProgramPage.created_exam_program_page import CreatedExamProgramPage
from Frontend.src.Admin.ExamProgramPages.get_exam_schedule_worker import get_schedules


class CoordinatorDashboard(QWidget):
    def __init__(self, controller, user_info=None):
        super().__init__()
        self.controller = controller
        self.user_info = user_info or {}
        self.file_path = None
        self.classroom_completed = False
        self.has_schedules = False
        self.check_schedule()
        
    def check_schedule(self):
        
        self.get_schedule_worker = get_schedules("get_exam_schedule", self.user_info, True)
        self.get_schedule_worker.finished.connect(self.on_schedule_check_finished)
        self.get_schedule_worker.start()
        
    def on_schedule_check_finished(self, result):
        if result.get("status") == "success":
            self.has_schedules = True
            print("Exam schedules exist.")
            self.results = result
            self.class_list_page.load_classes_for_department()
        else:
            self.has_schedules = False
            print("No exam schedules found.")
        self.init_ui()
        
    
    def init_ui(self):
        self.setWindowTitle("Coordinator Dashboard | Koordinatör Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/admin_dashboard_styles.qss"))
        
        # ---- Ana layout ----
        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content_layout = QVBoxLayout()
        
        sidebar_label = QLabel("🧭 Koordinatör Menü")
        sidebar_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sidebar_label.setAlignment(Qt.AlignCenter)
        
        self.menu = QListWidget()
        self.menu.setObjectName("menuList")
        
        if not self.has_schedules:
            self.initial_menu_items = [
                "🏠 Genel",
                "🏫 Sınıf Yönetimi",
                "📁 Ders Listesi Yükle",
                "📚 Öğrenci Listesi Yükle",
            ]

            self.later_menu_items = [
                "👨‍🎓 Öğrenci Listesi",
                "📖 Ders Listesi",
                "🎓 Sınav Programı Oluştur",
            ]
            
            self.last_menu_items = [
                "🗂 Oluşturulmuş Sınav Programı"
            ]
        else:
            self.initial_menu_items = [
                "🏠 Genel",
                "🏫 Sınıf Yönetimi",
                "📁 Ders Listesi Yükle",
                "📚 Öğrenci Listesi Yükle",
                "👨‍🎓 Öğrenci Listesi",
                "📖 Ders Listesi",
                "🎓 Sınav Programı Oluştur",
                "🗂 Oluşturulmuş Sınav Programı"
            ]
            self.later_menu_items = []
            self.last_menu_items = []
            self.classroom_completed = True

        for item_text in self.initial_menu_items:
            item = QListWidgetItem(item_text)
            item.setSizeHint(QSize(180, 40))
            self.menu.addItem(item)

        self.menu.currentRowChanged.connect(self.switch_page)
        
        logout_btn = QPushButton("🚪 Çıkış Yap")
        logout_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        
        sidebar.addWidget(sidebar_label)
        sidebar.addWidget(self.menu)
        sidebar.addStretch()
        sidebar.addWidget(logout_btn)
        
        self.title_label = QLabel("Coordinator Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        
        email = self.user_info.get("email", "unknown@domain")
        dept = self.user_info.get("department", "Bilinmiyor")
        self.info_label = QLabel(f"{email} | {dept}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")
        
        self.stack = QStackedLayout()
        
        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Koordinatör paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)
        
        self.insert_classroom_page = InsertClassroomPage(self.stack, self.user_info, self)
        self.classroom_management_system = ClassroomPage(self.stack, self.user_info, self)
        self.upload_classes_page = UploadClassList(self.user_info, self)
        self.upload_students_page = UploadStudentList(self.user_info, self)
        self.student_list_page = StudentListPage(self.user_info, self)
        self.class_list_page = ClassListPage(self.user_info, self)
        self.exam_program_page = ExamProgramPage(self.user_info, self)
        self.created_exam_program_page = CreatedExamProgramPage(self.user_info, self)
        
        if not self.has_schedules:
            self.exam_program_page.program_created.connect(self.created_exam_program_page.add_exam_program)
            self.exam_program_page.program_created.connect(self.on_exam_program_created)
        else:
            self.created_exam_program_page.on_exam_schedule_loaded(self.results)
                
        self.stack.addWidget(self.general_page)  # 0
        if not self.has_schedules:
            self.stack.addWidget(self.insert_classroom_page)  # 1
        self.stack.addWidget(self.classroom_management_system)  # 2
        self.stack.addWidget(self.upload_classes_page)  # 3
        self.stack.addWidget(self.upload_students_page)  # 4
        self.stack.addWidget(self.student_list_page)  # 5
        self.stack.addWidget(self.class_list_page)  # 6
        self.stack.addWidget(self.exam_program_page)  # 7
        self.stack.addWidget(self.created_exam_program_page) # 8
        
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        frame = QFrame()
        frame.setLayout(self.stack)
        content_layout.addWidget(frame)
        
        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)
        
        # Başlangıçta InsertClassroomPage göster
        if not self.has_schedules:
            self.menu.setCurrentRow(1)
            self.disable_other_menu_items()
        else:
            self.menu.setCurrentRow(0)
            self.switch_page(0)
    
    def disable_other_menu_items(self):
        if not self.classroom_completed:
            for i in range(self.menu.count()):
                if i != 1:  # 1 = Sınıf Yönetimi index'i
                    item = self.menu.item(i)
                    item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                    item.setForeground(Qt.gray)
    
    def enable_next_step_after_classroom(self):
        self.classroom_completed = True

        for i in range(self.menu.count()):
            item = self.menu.item(i)
            if i in (1, 2):
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
                item.setForeground(Qt.white)
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                item.setForeground(Qt.gray)

        self.menu.setCurrentRow(2)
        self.switch_page(2)

    def enable_next_step_after_class_upload(self):
        for i in range(self.menu.count()):
            item = self.menu.item(i)
            if i in (1, 2, 3): 
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
                item.setForeground(Qt.white)
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
                item.setForeground(Qt.gray)
        self.menu.setCurrentRow(3)
        self.switch_page(3)
    
    def enable_next_step_after_student_upload(self):
        existing_texts = [self.menu.item(i).text() for i in range(self.menu.count())]
        for text in self.later_menu_items:
            if text not in existing_texts:
                item = QListWidgetItem(text)
                item.setSizeHint(QSize(180, 40))
                self.menu.addItem(item)
        
        self.class_list_page.load_classes_for_department()

        for i in range(1, self.menu.count()):
            item = self.menu.item(i)
            item.setFlags(item.flags() | Qt.ItemIsEnabled)
            item.setForeground(Qt.white)

        self.text_output.append("✅ Öğrenci yüklemesi tamamlandı, ek menüler eklendi.\n")
        
        self.menu.setCurrentRow(6)  
        self.switch_page(6)
    
    def on_exam_program_created(self, results):
        self.text_output.append("\n✅ Sınav programı başarıyla oluşturuldu!\n")
        exam_info = results.get('exam_program_info', {})
        kalan_dersler = exam_info.get('kalan_dersler', [])
        self.text_output.append(f"📝 Seçilen dersler: {len(kalan_dersler)} ders\n")

        
        self.text_output.append("📊 Şu ana kadar yapılan işlemler:\n")
        self.text_output.append(" - Sınıflar oluşturuldu ✅\n")
        self.text_output.append(" - Ders listesi yüklendi ✅\n")
        self.text_output.append(" - Öğrenci listesi yüklendi ✅\n")
        self.text_output.append(" - Sınav programı oluşturuldu ✅\n")
        
        existing_texts = [self.menu.item(i).text() for i in range(self.menu.count())]
        for text in self.last_menu_items:
            if text not in existing_texts:
                item = QListWidgetItem(text)
                item.setSizeHint(QSize(180, 40))
                self.menu.addItem(item)
                
        general_item = self.menu.item(0)
        general_item.setFlags(general_item.flags() | Qt.ItemIsEnabled)
        general_item.setForeground(Qt.white)
                
        self.menu.setCurrentRow(7)
        self.switch_page(7)
            
    def on_first_classroom_added(self):
        self.stack.setCurrentIndex(2)
        self.title_label.setText("Sınıf Yönetimi")
    
    def create_placeholder_page(self, message):
        w = QWidget()
        l = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #ccc; font-size: 15px;")
        l.addWidget(label)
        w.setLayout(l)
        return w
    
    def switch_page(self, index):
        if not self.classroom_completed and index != 1:
            self.menu.setCurrentRow(1)
            return

        mapping = {
            0: ("general", "Genel"),
            1: ("classroom_management", "Sınıf Yönetimi"),
            2: ("upload_classes_list", "Ders Listesi Yükle"),
            3: ("upload_students_list", "Öğrenci Listesi Yükle"),
            4: ("student_list", "Öğrenci Listesi"),
            5: ("class_list", "Ders Listesi"),
            6: ("exam_program", "Sınav Programı Oluştur"),
            7: ("created_exam_program", "Oluşturulmuş Sınav Programları"),
        }

        if index in mapping:
            self.current_endpoint, title = mapping[index]
            self.title_label.setText(title)
            if not self.has_schedules:
                if index == 0:
                    self.stack.setCurrentIndex(0)  # Genel sayfa
                elif index == 1 and not self.classroom_completed:
                    self.stack.setCurrentIndex(1)  # InsertClassroomPage
                elif index == 1 and self.classroom_completed:
                    self.stack.setCurrentIndex(2)  # ClassroomPage
                else:
                    # Menü indexi ile stack indexi aynı hizaya gelsin
                    self.stack.setCurrentIndex(index + 1)
            else:
                self.stack.setCurrentIndex(index)

    
    def logout(self):
        self.controller.logout()