from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QPushButton, QMessageBox, QGridLayout, QFileDialog
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QColor, QPen
from Backend.src.utils.exams.create_exam_program import float_to_time_str, download_exam_schedule
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPainter
import datetime

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
        self.pdf_button = None

    def add_exam_program(self, result_data: dict):
        self.exam_schedule = result_data.get("exam_schedule", [])
        failed_classes = result_data.get("failed_classes", [])
        stats = result_data.get("statistics", {})

        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame { background-color: rgba(0, 255, 100, 0.08); border: 1px solid rgba(0,255,100,0.3); border-radius: 10px; padding: 10px; }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        stats_label = QLabel(
            f"📊 Toplam Ders: {stats.get('total_classes', 0)} | ✅ Başarılı: {stats.get('successful_classes', 0)} | ❌ Yerleşemeyen: {stats.get('failed_classes', 0)}"
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
            return

        for day in self.exam_schedule:
            day_frame = QFrame()
            day_frame.setStyleSheet("QFrame { background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; }")
            day_layout = QVBoxLayout(day_frame)

            day_label = QLabel(f"📅 Tarih: {day.get('date', '-')}")
            day_label.setFont(QFont("Arial", 13, QFont.Bold))
            day_label.setStyleSheet("color: #4ee44e;")
            day_layout.addWidget(day_label)

            exams = day.get("exams", [])
            if not exams:
                empty_lbl = QLabel("— Bu gün için sınav bulunmuyor —")
                empty_lbl.setStyleSheet("color: #888; font-style: italic;")
                day_layout.addWidget(empty_lbl)
            else:
                for exam in exams:
                    for cls in exam.get("classes", []):
                        exam_info_container = QWidget()
                        exam_info_layout = QVBoxLayout(exam_info_container)
                        exam_info_layout.setContentsMargins(0, 5, 0, 5)

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
                        exam_label.setStyleSheet("color: white; font-size: 12px; padding-bottom: 5px;")
                        exam_info_layout.addWidget(exam_label)

                        toggle_button = QPushButton("▼ Oturma Planı Göster")
                        toggle_button.setCursor(Qt.PointingHandCursor)
                        toggle_button.setStyleSheet("QPushButton { background-color: #3e4b5f; border: none; border-radius: 4px; padding: 5px; font-size: 11px; } QPushButton:hover { background-color: #4a5970; }")
                        exam_info_layout.addWidget(toggle_button)
                        
                        plan_container = QWidget()
                        plan_container.setVisible(False)
                        exam_info_layout.addWidget(plan_container)

                        seating_plan_data = cls.get('seating_plan', {})
                        toggle_button.clicked.connect(
                            lambda checked, btn=toggle_button, container=plan_container, data=seating_plan_data: 
                            self.toggle_seating_plan_visibility(btn, container, data)
                        )

                        day_layout.addWidget(exam_info_container)

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
            
        if not self.pdf_button:
            self.pdf_button = QPushButton("📄 Oturma Planını PDF Olarak Dışa Aktar")
            self.pdf_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0b7dda;
                }
            """)
            self.pdf_button.clicked.connect(self.handle_export_pdf)
            self.main_layout.addWidget(self.pdf_button, alignment=Qt.AlignCenter)
    
    def toggle_seating_plan_visibility(self, button: QPushButton, container: QWidget, plan_data: dict):
        if container.isVisible():
            container.setVisible(False)
            button.setText("▼ Oturma Planı Göster")
        else:
            if not container.layout():
                container_layout = QVBoxLayout(container)
                container_layout.setSpacing(15)

                for room_name, student_grid in plan_data.items():
                    if not student_grid: 
                        continue

                    room_frame = QFrame()
                    room_frame.setStyleSheet("QFrame { border: 1px solid #444; border-radius: 5px; }")
                    room_layout = QVBoxLayout(room_frame)

                    room_label = QLabel(f"🏫 {room_name}")
                    room_label.setFont(QFont("Arial", 11, QFont.Bold))
                    room_label.setStyleSheet("border: none; padding: 5px; color: #aaa;")
                    room_layout.addWidget(room_label)

                    grid_widget = QWidget()
                    student_grid_layout = QGridLayout(grid_widget)
                    student_grid_layout.setSpacing(5)

                    max_row = max((key[0] for key in student_grid.keys()), default=-1)
                    max_col = max((key[1] for key in student_grid.keys()), default=-1)

                    for r in range(max_row + 1):
                        for c in range(max_col + 1):
                            cell_content = student_grid.get((r, c))
                            cell_label = QLabel()
                            cell_label.setAlignment(Qt.AlignCenter)
                            cell_label.setFixedSize(60, 40)
                            
                            if cell_content == 'AISLE':
                                cell_label.setText("Koridor")
                                cell_label.setStyleSheet("color: #666; font-size: 9px; background-color: #282828; border-radius: 3px;")
                            elif cell_content is None:
                                cell_label.setText("BOŞ")
                                cell_label.setStyleSheet("color: #777; font-size: 10px; background-color: #333; border: 1px solid #444; border-radius: 4px;")
                            else:
                                student_no = str(cell_content.get('student_num', '???'))
                                cell_label.setText(student_no)
                                cell_label.setStyleSheet("color: white; font-weight: bold; background-color: #005a03; border: 1px solid #1b851f; border-radius: 4px;")
                            
                            student_grid_layout.addWidget(cell_label, r, c)
                    
                    room_layout.addWidget(grid_widget)
                    container_layout.addWidget(room_frame)

            container.setVisible(True)
            button.setText("▲ Oturma Planı Gizle")


    def download_excel(self):
        if not self.exam_schedule:
            QMessageBox.warning(self, "Uyarı", "İndirilecek bir sınav programı bulunmuyor.")
            return
        filename = "sinav_programi.xlsx"
        try:
            download_exam_schedule(exam_schedule=self.exam_schedule, filename=filename)
            QMessageBox.information(self, "Başarılı", f"Sınav programı '{filename}' olarak başarıyla kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya kaydedilirken bir hata oluştu:\n{e}")
            
    def handle_export_pdf(self):
            if not self.exam_schedule:
                QMessageBox.warning(self, "Uyarı", "PDF'e aktarılacak bir oturma planı bulunmuyor.")
                return

            options = QFileDialog.Options()
            filename, _ = QFileDialog.getSaveFileName(self, "Oturma Planını PDF Olarak Kaydet", "oturma_planlari.pdf", "PDF Dosyaları (*.pdf);;Tüm Dosyalar (*)", options=options)

            if filename:
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                
                success = self.export_all_seating_plans_to_pdf(self.exam_schedule, filename)
                if success:
                    QMessageBox.information(self, "Başarılı", f"Tüm oturma planları başarıyla\n'{filename}'\ndosyasına kaydedildi.")
                else:
                    QMessageBox.critical(self, "Hata", "PDF oluşturulurken bir hata meydana geldi.")