from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QDateEdit, QComboBox, QSpinBox, QPushButton,
    QScrollArea, QFrame, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont


class CreatedExamProgramPage(QWidget):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        title = QLabel("Oluşturulmuş Sınav Programları")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.info_label = QLabel("Burada oluşturulmuş sınav programlarını görüntüleyebilirsiniz.")
        self.info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.info_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # Örnek veri - Gerçek veriler API'den çekilecek
        example_programs = [
            {"date": "2024-06-15", "time": "10:00", "course": "Matematik", "classroom": "A101"},
            {"date": "2024-06-16", "time": "14:00", "course": "Fizik", "classroom": "B202"},
            {"date": "2024-06-17", "time": "09:00", "course": "Kimya", "classroom": "C303"},
        ]

        for program in example_programs:
            program_frame = QFrame()
            program_layout = QHBoxLayout(program_frame)

            date_label = QLabel(f"Tarih: {program['date']}")
            time_label = QLabel(f"Saat: {program['time']}")
            course_label = QLabel(f"Ders: {program['course']}")
            classroom_label = QLabel(f"Sınıf: {program['classroom']}")

            program_layout.addWidget(date_label)
            program_layout.addWidget(time_label)
            program_layout.addWidget(course_label)
            program_layout.addWidget(classroom_label)

            self.scroll_layout.addWidget(program_frame)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)