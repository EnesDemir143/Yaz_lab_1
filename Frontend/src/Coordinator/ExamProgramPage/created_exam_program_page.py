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
        self.programs = []
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        title = QLabel("📘 Oluşturulmuş Sınav Programları")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        self.info_label = QLabel("Burada oluşturulmuş sınav programlarını görüntüleyebilirsiniz.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.info_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def add_exam_program(self, result_data: dict):
        """Yeni oluşturulan programı ekrana ekler."""
        schedule = result_data.get("schedule", [])
        if not schedule:
            msg = QLabel("⚠️ Henüz sınav programı bulunamadı.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #888; font-style: italic;")
            self.scroll_layout.addWidget(msg)
            return

        for item in schedule:
            program_frame = QFrame()
            program_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            layout = QHBoxLayout(program_frame)

            date = item.get("day", "-")
            slot = item.get("slot_in_day", "-")
            course = item.get("course_name", "-")
            room = item.get("room_name", "-")

            lbl = QLabel(f"📅 {date} | ⏰ Slot: {slot} | 🧮 {course} | 🏫 {room}")
            layout.addWidget(lbl)

            self.scroll_layout.addWidget(program_frame)

        self.scroll_layout.addStretch()
