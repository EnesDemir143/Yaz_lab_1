from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
    QPushButton, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Admin.ExamProgramPages.get_exam_schedule_worker import get_schedules as ExamScheduleWorker
from Backend.src.utils.exams.create_exam_program import float_to_time_str, download_exam_schedule

from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_NAME = '../../../../dejavu-sans.book.ttf'
FONT_NAME_BOLD = '../../../../DejaVuSans-Bold.ttf'

try:
    pdfmetrics.registerFont(TTFont(FONT_NAME, 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, 'DejaVuSans-Bold.ttf'))
except Exception as e:
    print(f"--- FONT YÜKLENEMEDİ UYARISI ---\n{e}")


class CreatedExamProgramPage(QWidget):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.exam_schedule = []
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        title = QLabel("📘 Oluşturulmuş Sınav Programları (Departman Bazlı)")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

        self.info_label = QLabel("Aşağıda her departmana ait sınav programları listelenmektedir.")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: #ccc; font-size: 13px;")
        self.main_layout.addWidget(self.info_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)
        
        self.load_exam_programs()

    # -------------------------- DATA LOAD --------------------------
    def load_exam_programs(self):
        loading_label = QLabel("⏳ Sınav programları yükleniyor...")
        loading_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(loading_label)

        self.worker = ExamScheduleWorker("get_exam_schedules", self.user_info)
        self.worker.finished.connect(self.on_exam_schedule_loaded)
        self.worker.start()

    def on_exam_schedule_loaded(self, result: dict):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if result.get("status") != "success":
            msg = result.get("message", "Veri alınamadı.")
            err_lbl = QLabel(f"❌ Hata: {msg}")
            err_lbl.setStyleSheet("color: red;")
            self.scroll_layout.addWidget(err_lbl)
            return

        # Tek departman ya da tüm departmanlar
        if "exam_schedule" in result:
            dep_name = result.get("department", "Bilinmiyor")
            self.display_department_program(dep_name, result["exam_schedule"])
        elif "departments" in result:
            for dep_name, dep_data in result["departments"].items():
                self.display_department_program(dep_name, dep_data)

        self.scroll_layout.addStretch()

    # -------------------------- DISPLAY --------------------------
    def display_department_program(self, department_name: str, dep_data: dict):
        dep_frame = QFrame()
        dep_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(40,40,40,0.3);
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        dep_layout = QVBoxLayout(dep_frame)

        dep_title = QLabel(f"🏛️ {department_name}")
        dep_title.setFont(QFont("Arial", 14, QFont.Bold))
        dep_title.setStyleSheet("color: #00c3ff;")
        dep_layout.addWidget(dep_title)

        for date, info in dep_data.items():
            day_label = QLabel(f"📅 {date} — {info.get('exam_type', 'Bilinmiyor')}")
            day_label.setStyleSheet("color: #4ee44e; font-weight: bold; margin-top: 5px;")
            dep_layout.addWidget(day_label)

            for exam in info.get("exams", []):
                for cls in exam.get("classes", []):
                    cname = cls.get("name", "-")
                    year = cls.get("year", "-")
                    start = str(cls.get("start_time", "-"))
                    end = str(cls.get("end_time", "-"))
                    count = cls.get("student_count", 0)
                    rooms = [r.get("classroom_id", "-") for r in cls.get("classrooms", [])]
                    seating_plan = cls.get("seating_plan", {})

                    exam_widget = QWidget()
                    exam_layout = QVBoxLayout(exam_widget)
                    exam_label = QLabel(
                        f"🧮 {cname} ({year}. Sınıf) | 👥 {count} öğrenci | 🏫 {', '.join(map(str, rooms))} | ⏰ {start} → {end}"
                    )
                    exam_label.setStyleSheet("color: white; font-size: 12px;")
                    exam_layout.addWidget(exam_label)

                    # Oturma planı butonu
                    toggle_button = QPushButton("▼ Oturma Planı Göster")
                    toggle_button.setCursor(Qt.PointingHandCursor)
                    toggle_button.setStyleSheet("""
                        QPushButton { background-color: #3e4b5f; border: none; border-radius: 4px; padding: 5px; font-size: 11px; color:white;}
                        QPushButton:hover { background-color: #4a5970; }
                    """)
                    exam_layout.addWidget(toggle_button)

                    plan_container = QWidget()
                    plan_container.setVisible(False)
                    exam_layout.addWidget(plan_container)

                    # PDF butonu
                    pdf_button = QPushButton("📄 PDF Olarak İndir")
                    pdf_button.setCursor(Qt.PointingHandCursor)
                    pdf_button.setStyleSheet("""
                        QPushButton { background-color: #2d71b8; border: none; border-radius: 4px; padding: 5px; font-size: 11px; color: white; }
                        QPushButton:hover { background-color: #3a82c9; }
                    """)
                    exam_layout.addWidget(pdf_button)

                    pdf_button.clicked.connect(
                        lambda checked, exam_name=cname, plan_data=seating_plan:
                            self.create_seating_plan_pdf(f"{exam_name}_oturma_plani.pdf", exam_name, plan_data)
                    )

                    toggle_button.clicked.connect(
                        lambda checked, btn=toggle_button, container=plan_container, data=seating_plan:
                            self.toggle_seating_plan_visibility(btn, container, data)
                    )

                    dep_layout.addWidget(exam_widget)

        self.scroll_layout.addWidget(dep_frame)

    # -------------------------- TOGGLE PLAN --------------------------
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
                    grid_layout = QGridLayout(grid_widget)
                    grid_layout.setSpacing(5)

                    # seating_plan dict -> {"3001": {"1,1": {"student_num":...}}}
                    parsed_grid = {}
                    for key, val in student_grid.items():
                        if isinstance(key, str) and "," in key:
                            r, c = map(int, key.split(","))
                            parsed_grid[(r, c)] = val

                    max_row = max((r for r, _ in parsed_grid.keys()), default=-1)
                    max_col = max((c for _, c in parsed_grid.keys()), default=-1)

                    for r in range(max_row + 1):
                        for c in range(max_col + 1):
                            cell = parsed_grid.get((r, c))
                            label = QLabel()
                            label.setAlignment(Qt.AlignCenter)
                            label.setFixedSize(45, 28)  
                            
                            if not cell:
                                label.setText("BOŞ")
                                label.setStyleSheet("""
                                    color: #777;
                                    font-size: 8px;
                                    background-color: #333;
                                    border: 1px solid #444;
                                    border-radius: 3px;
                                """)
                            else:
                                student_no = str(cell.get("student_num", "???"))
                                label.setText(student_no)
                                label.setStyleSheet("""
                                    color: white;
                                    font-size: 9px;
                                    font-weight: bold;
                                    background-color: #006a03;
                                    border: 1px solid #1b851f;
                                    border-radius: 3px;
                                """)
                            grid_layout.addWidget(label, r, c)


                    room_layout.addWidget(grid_widget)
                    container_layout.addWidget(room_frame)
            container.setVisible(True)
            button.setText("▲ Oturma Planı Gizle")

    # -------------------------- PDF EXPORT --------------------------
    def create_seating_plan_pdf(self, filename: str, exam_name: str, plan_data: dict):
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4),
                                leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                                topMargin=1.5 * cm, bottomMargin=1.5 * cm)

        story = []
        styles = {
            'MainTitle': ParagraphStyle(name='MainTitle', fontName=FONT_NAME_BOLD, fontSize=16, alignment=1, spaceAfter=10),
            'RoomTitle': ParagraphStyle(name='RoomTitle', fontName=FONT_NAME_BOLD, fontSize=12, spaceAfter=6, spaceBefore=10),
            'CellName': ParagraphStyle(name='CellName', fontName=FONT_NAME, fontSize=8, alignment=1, leading=10),
            'CellID': ParagraphStyle(name='CellID', fontName=FONT_NAME, fontSize=7, alignment=1, leading=8),
            'CellEmpty': ParagraphStyle(name='CellEmpty', fontName=FONT_NAME, fontSize=8, alignment=1, textColor=colors.grey, leading=10)
        }

        story.append(Paragraph(f"Sınav Oturma Planı: {exam_name}", styles['MainTitle']))
        story.append(Spacer(1, 0.5 * cm))

        first_room = True
        for room_name, student_grid in plan_data.items():
            if not first_room:
                story.append(PageBreak())
            first_room = False

            story.append(Paragraph(f"Derslik: {room_name}", styles['RoomTitle']))
            if not student_grid:
                story.append(Paragraph("Bu derslik için oturma planı verisi yok.", styles['CellEmpty']))
                continue

            parsed_grid = {}
            for key, val in student_grid.items():
                if isinstance(key, str) and "," in key:
                    r, c = map(int, key.split(","))
                    parsed_grid[(r, c)] = val

            max_row = max((r for r, _ in parsed_grid.keys()), default=-1)
            max_col = max((c for _, c in parsed_grid.keys()), default=-1)

            table_data = []
            for r in range(max_row + 1):
                row_data = []
                for c in range(max_col + 1):
                    cell = parsed_grid.get((r, c))
                    if cell:
                        name = cell.get('name', 'İsim Yok') + " " + cell.get('surname', '')
                        num = cell.get("student_num", "???")
                        cell_elem = [
                            Paragraph(name, styles['CellName']),
                            Paragraph(f"({num})", styles['CellID'])
                        ]
                    else:
                        cell_elem = Paragraph("(BOŞ)", styles['CellEmpty'])
                    row_data.append(cell_elem)
                table_data.append(row_data)

            page_width, _ = landscape(A4)
            usable_width = page_width - (doc.leftMargin + doc.rightMargin)
            num_cols = max_col + 1
            col_width = usable_width / num_cols
            col_widths = [col_width] * num_cols
            row_heights = [1.5 * cm] * (max_row + 1)

            t = Table(table_data, colWidths=col_widths, rowHeights=row_heights)
            t.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(t)

        try:
            doc.build(story)
            QMessageBox.information(self, "PDF Oluşturuldu", f"✅ PDF başarıyla oluşturuldu:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"❌ PDF oluşturulamadı:\n{e}")
