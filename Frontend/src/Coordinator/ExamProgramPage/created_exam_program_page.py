from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Backend.src.utils.exams.create_exam_program import float_to_time_str, download_exam_schedule


class CreatedExamProgramPage(QWidget):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.programs = []
        self.exam_schedule = []
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        title = QLabel("📘 Oluşturulmuş Sınav Programları")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        self.info_label = QLabel("Aşağıda oluşturulan sınav programları listelenmektedir.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #ccc; font-size: 13px;")
        self.main_layout.addWidget(self.info_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        self.get_excel_btn = None

    def add_exam_program(self, result_data: dict):
        """Yeni oluşturulan programı ekrana ekler."""

        self.exam_schedule = result_data.get("exam_schedule", [])
        failed_classes = result_data.get("failed_classes", [])
        stats = result_data.get("statistics", {})

        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 255, 100, 0.08);
                border: 1px solid rgba(0,255,100,0.3);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_label = QLabel(
            f"📊 Toplam Ders: {stats.get('total_classes', 0)} | "
            f"✅ Başarılı: {stats.get('successful_classes', 0)} | "
            f"❌ Yerleşemeyen: {stats.get('failed_classes', 0)}"
        )
        stats_label.setAlignment(Qt.AlignCenter)
        stats_label.setFont(QFont("Arial", 12))
        stats_layout.addWidget(stats_label)
        self.scroll_layout.addWidget(stats_frame)

        if not self.exam_schedule:
            msg = QLabel("⚠️ Henüz sınav programı oluşturulmamış.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #888; font-style: italic;")
            self.scroll_layout.addWidget(msg)
        else:
            for day in self.exam_schedule:
                date = day.get("date", "-")
                exams = day.get("exams", [])

                day_frame = QFrame()
                day_frame.setStyleSheet("""
                    QFrame {
                        background-color: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 10px;
                        padding: 10px;
                    }
                """)
                day_layout = QVBoxLayout(day_frame)

                day_label = QLabel(f"📅 Tarih: {date}")
                day_label.setFont(QFont("Arial", 13, QFont.Bold))
                day_label.setStyleSheet("color: #4ee44e;")
                day_layout.addWidget(day_label)

                if not exams:
                    empty_lbl = QLabel("— Bu gün için sınav bulunmuyor —")
                    empty_lbl.setStyleSheet("color: #888; font-style: italic;")
                    day_layout.addWidget(empty_lbl)
                else:
                    for exam in exams:
                        classes = exam.get("classes", [])

                        for cls in classes:
                            start = float_to_time_str(cls.get("start_time", 0))
                            end = float_to_time_str(cls.get("end_time", 0))
                            cname = cls.get("name", "-")
                            cyear = cls.get("year", "-")
                            count = cls.get("student_count", 0)
                            rooms = [r.get("classroom_name", "-") for r in cls.get("classrooms", [])]

                            exam_label = QLabel(
                                f"🧮 {cname} ({cyear}. Sınıf)  |  👥 {count} öğrenci  |  "
                                f"🏫 Sınıflar: {', '.join(rooms)}  |  ⏰ {start} → {end}"
                            )
                            exam_label.setWordWrap(True)
                            exam_label.setStyleSheet("color: white; font-size: 12px;")
                            day_layout.addWidget(exam_label)

                self.scroll_layout.addWidget(day_frame)

        if failed_classes:
            fail_frame = QFrame()
            fail_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255,0,0,0.08);
                    border: 1px solid rgba(255,0,0,0.3);
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            fail_layout = QVBoxLayout(fail_frame)
            fail_title = QLabel("⚠️ Programa Yerleştirilemeyen Dersler:")
            fail_title.setFont(QFont("Arial", 12, QFont.Bold))
            fail_title.setStyleSheet("color: #ff5555;")
            fail_layout.addWidget(fail_title)

            for cls in failed_classes:
                fail_lbl = QLabel(f"❌ {cls.get('name', '-')}")
                fail_lbl.setStyleSheet("color: #ff9999;")
                fail_layout.addWidget(fail_lbl)

            self.scroll_layout.addWidget(fail_frame)

        self.scroll_layout.addStretch()
        
        if not self.get_excel_btn:
            self.get_excel_btn = QPushButton("📥 Excel Olarak İndir")
            self.get_excel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.get_excel_btn.clicked.connect(self.download_excel)
            self.main_layout.addWidget(self.get_excel_btn, alignment=Qt.AlignCenter)
    
    def download_excel(self):
        download_exam_schedule(
            exam_schedule=self.exam_schedule,
            filename="exam_schedule.xlsx"
        )