from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CreatedExamProgramPage(QWidget):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.programs = []
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        # --- Başlık ---
        title = QLabel("📘 Oluşturulmuş Sınav Programları")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        self.info_label = QLabel("Aşağıda oluşturulan sınav programları listelenmektedir.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #ccc; font-size: 13px;")
        self.main_layout.addWidget(self.info_label)

        # --- Scroll alanı ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def add_exam_program(self, result_data: dict):
        """Yeni oluşturulan programı ekrana ekler."""

        exam_schedule = result_data.get("exam_schedule", [])
        failed_classes = result_data.get("failed_classes", [])
        stats = result_data.get("statistics", {})

        # --- Önce varsa eski içerikleri temizle ---
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # --- Genel istatistikler kutusu ---
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

        # --- Program detayları ---
        if not exam_schedule:
            msg = QLabel("⚠️ Henüz sınav programı oluşturulmamış.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #888; font-style: italic;")
            self.scroll_layout.addWidget(msg)
        else:
            for day in exam_schedule:
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

                # Gün başlığı
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
                        start = self._float_to_time_str(exam.get("start_time", "-"))
                        end = self._float_to_time_str(exam.get("end_time", "-"))
                        classes = exam.get("classes", [])

                        for cls in classes:
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

        # --- Başarısız dersler kısmı ---
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

    def _float_to_time_str(self, hour_float: float) -> str:
        hour = int(hour_float)
        minute = int(round((hour_float - hour) * 60))
        return f"{hour:02d}:{minute:02d}"
