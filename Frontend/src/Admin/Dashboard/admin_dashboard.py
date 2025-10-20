from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton,
    QListWidgetItem, QTextEdit, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from Frontend.src.Admin.UploadPages.upload_class import UploadClassList
from Frontend.src.Admin.UploadPages.upload_student import uploadStudentList
from Frontend.src.Admin.InsertCoordinator.insert_coordinator import InsertCoordinator
from Frontend.src.Styles.load_qss import load_stylesheet
from Frontend.src.Admin.Classroom.clasroomPage import ClassroomPage
from Frontend.src.Admin.StudentListPage.studentList_page import StudentListPage
from Frontend.src.Admin.ClassListPage.class_list_page import ClassListPage
from Frontend.src.Admin.ExamProgramPages.exam_program_interface import ExamProgramPage
from Frontend.src.Admin.ExamProgramPages.created_exam_program_page import CreatedExamProgramPage

class AdminDashboard(QWidget):
    def __init__(self, controller, user_info=None):
        super().__init__()
        self.controller = controller
        self.user_info = user_info
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Dashboard | Yönetim Paneli")
        self.resize(1200, 750)
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/admin_dashboard_styles.qss"))

        main_layout = QHBoxLayout(self)
        sidebar = QVBoxLayout()
        content_layout = QVBoxLayout()

        sidebar_label = QLabel("🧭 Admin Menü")
        sidebar_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sidebar_label.setAlignment(Qt.AlignCenter)

        self.menu = QListWidget()
        for item_text in [
            "🏠 Genel",
            "📁 Ders Listesi Yükle",
            "📚 Öğrenci Listesi Yükle",
            "👩‍🏫 Koordinatör Ekle",
            "🏫 Sınıf Ekle",
            "👨‍🎓 Öğrenci Listesi",
            "📖 Ders Listesi",
            " Sınav Programı Oluştur",
            "🗓️ Oluşturulan Sınav Programları"
        ]:
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

        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.info_label = QLabel(f"{self.user_info['email']} | {self.user_info['department']}")
        self.info_label.setFont(QFont("Segoe UI", 10))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #aaa;")

        self.stack = QStackedLayout()

        self.general_page = QWidget()
        g_layout = QVBoxLayout()
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.append("🟢 Yönetim paneline hoş geldiniz.\n")
        g_layout.addWidget(self.text_output)
        self.general_page.setLayout(g_layout)

        self.upload_classes_page = UploadClassList(self.user_info, self)
        
        self.upload_students_page = uploadStudentList(self.user_info, self)
        
        self.inser_coordinator_page = InsertCoordinator(self.user_info, self)

        self.classroom_page = ClassroomPage(self.stack, self.user_info)
        
        self.student_list_page = StudentListPage(self.user_info, self)
        
        self.class_list_page = ClassListPage(self.user_info, self)
        
        self.exam_program_page = ExamProgramPage(self.user_info, self)
        
        self.created_exam_program_page = CreatedExamProgramPage(self.user_info, self)
        
        self.exam_program_page.program_created.connect(self.created_exam_program_page.add_exam_program)
        self.exam_program_page.program_created.connect(self.on_exam_program_created)

        self.empty_page = QWidget()
        e_layout = QVBoxLayout()
        e_label = QLabel("Bu bölüm henüz aktif değil.")
        e_label.setAlignment(Qt.AlignCenter)
        e_layout.addWidget(e_label)
        self.empty_page.setLayout(e_layout)

        # Stack’e ekleme
        self.stack.addWidget(self.general_page)
        self.stack.addWidget(self.upload_classes_page)
        self.stack.addWidget(self.upload_students_page)
        self.stack.addWidget(self.inser_coordinator_page)
        self.stack.addWidget(self.classroom_page)
        self.stack.addWidget(self.student_list_page)
        self.stack.addWidget(self.class_list_page)
        self.stack.addWidget(self.exam_program_page)
        self.stack.addWidget(self.created_exam_program_page)

        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.info_label)
        content_layout.addLayout(self.stack)

        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 3)

        self.menu.setCurrentRow(0)

    def switch_page(self, index):
        mapping = {
            0: ("general", "Genel"),
            1: ("upload_classes_list", "Ders Listesi Yükle"),
            2: ("upload_students_list", "Öğrenci Listesi Yükle"),
            3: ("insert_coordinator", "Koordinatör Ekle"),
            4: ("insert_classroom", "Sınıf Ekle"),
            5: ("student_list", "Öğrenci Listesi"),
            6: ("class_list", "Ders Listesi"),
            7: ("exam_program", "Sınav Programı Oluştur"),
            8: ("created_exam_program", "Oluşturulan Sınav Programları")
        }

        if index in mapping:
            self.current_endpoint, title = mapping[index]
            self.title_label.setText(title)
            self.stack.setCurrentIndex(index)

    def logout(self):
        self.controller.logout()
        
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
                
        general_item = self.menu.item(0)
        general_item.setFlags(general_item.flags() | Qt.ItemIsEnabled)
        general_item.setForeground(Qt.white)
                