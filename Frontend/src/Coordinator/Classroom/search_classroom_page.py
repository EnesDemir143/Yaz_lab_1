from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox,
    QHBoxLayout, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet
from PyQt5.QtWidgets import QDialog, QScrollArea

class SearchClassroomPage(QWidget):
    def __init__(self, parent_stack, user_info, dashboard=None):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.dashboard = dashboard
        self.visual_layout = None  # Görsel alanı saklayacağız
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("🔍 Search Classroom")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.classroom_code_input = QLineEdit()
        layout.addWidget(QLabel("Derslik Kodu:"))
        layout.addWidget(self.classroom_code_input)

        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("Ara")
        self.back_btn = QPushButton("⬅️ Geri Dön")
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.search_btn)
        self.set_classroom_btn = QPushButton("Derslik Bilgilerini Ayarla")
        self.set_classroom_btn.clicked.connect(
            lambda: self.set_classroon_fields({
                "classroom_code": self.classroom_code_input.text().strip()
            })
        )
        btn_layout.addWidget(self.set_classroom_btn)
        layout.addLayout(btn_layout)
        
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)

        # --- Görselleştirme Alanı ---
        self.visual_frame = QFrame()
        self.visual_frame.setStyleSheet("background-color: rgba(255,255,255,0.05); border-radius: 10px;")
        layout.addWidget(QLabel("🪑 Oturma Düzeni:"))
        layout.addWidget(self.visual_frame)

        self.setLayout(layout)

        self.search_btn.clicked.connect(self.search_classroom)
        self.back_btn.clicked.connect(self.go_back)

    def go_back(self):
        from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage
        classroom_page = ClassroomPage(self.parent_stack, self.user_info, self.dashboard)
        self.parent_stack.addWidget(classroom_page)
        self.parent_stack.setCurrentWidget(classroom_page)

    def search_classroom(self):
        code = self.classroom_code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Warning", "Please enter classroom code.")
            return

        self.request = ClassroomRequests("search_classroom", {"classroom_code": code}, self.user_info)
        self.request.finished.connect(self.handle_response)
        self.request.start()

    def handle_response(self, response):
        if response.get("status") == "error":
            QMessageBox.critical(self, "Search Failed", response.get("detail", "Not found"))
            return

        classroom = response.get("classroom", {})
        info_text = "\n".join([
            f"Derslik Adı: {classroom.get('classroom_name', '')}",
            f"Bölüm: {classroom.get('department_name', '')}",
            f"Kapasite: {classroom.get('capacity', '')}",
            f"Satır: {classroom.get('desks_per_row', '')}",
            f"Sütun: {classroom.get('desks_per_column', '')}",
            f"Masa Yapısı: {classroom.get('desk_structure', '')}"
        ])
        self.result.setText(info_text)

        # 🔹 Görselleştirmeyi çiz
        try:
            dialog = ClassroomLayoutDialog(
                self,
                classroom.get("classroom_name", "Derslik"),
                rows=int(classroom.get("desks_per_column", 0)),  # SATIR
                cols=int(classroom.get("desks_per_row", 0)),     # SÜTUN
                structure=int(classroom.get("desk_structure", 0))
            )
            dialog.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Visualization Error", f"Cannot visualize: {e}")
            
    def set_classroon_fields(self, classroom_data: dict):
        from Frontend.src.Coordinator.Classroom.upload_classroom_page import UploadClassroomPage
        classroom_id = classroom_data.get("classroom_code", "").strip()
        if not classroom_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir derslik kodu girin.")
            return

        upload_page = UploadClassroomPage(self.parent_stack, self.user_info, classroom_id, self.dashboard)
        self.parent_stack.addWidget(upload_page)
        self.parent_stack.setCurrentWidget(upload_page)



from PyQt5.QtWidgets import QDialog, QScrollArea, QWidget, QLabel, QVBoxLayout, QGridLayout, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ClassroomLayoutDialog(QDialog):
    def __init__(self, parent, room_name, rows, cols, structure):
        super().__init__(parent)
        self.setWindowTitle(f"🪑 {room_name} — Oturma Düzeni")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #f1f1f1;
                font-family: Arial;
            }
        """)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        # Grid layout
        self.layout_grid = QGridLayout(scroll_content)
        self.layout_grid.setSpacing(8)
        self.layout_grid.setAlignment(Qt.AlignCenter)

        # Başlık
        title = QLabel(f"{room_name} Oturma Düzeni ({rows}x{cols}, Yapı={structure})")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Bold))

        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(title)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        # Çizim fonksiyonu
        self.draw_layout(rows, cols, structure)

    def draw_layout(self, rows, cols, structure):
        self.setStyleSheet("""
            QDialog {
                background-color: #15171a;
                color: #f8f9fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-family: 'Segoe UI';
            }
        """)
        
        for r in range(rows):
            grid_col_index = 0
            aisle_counter = 0
            for block in range(cols):
                # Masa yapısı tanımı (örnek: 4 → Ö S S Ö)
                if structure == 1:
                    pattern = ['D']
                elif structure == 2:
                    pattern = ['D', 'S']
                elif structure == 3:
                    pattern = ['D', 'S', 'D']
                else:
                    pattern = ['D'] + ['S'] * (structure - 2) + ['D']

                for symbol in pattern:
                    frame = QFrame()
                    frame.setFixedSize(70, 70)
                    frame_layout = QVBoxLayout(frame)
                    frame_layout.setAlignment(Qt.AlignCenter)
                    frame_layout.setContentsMargins(0, 0, 0, 0)

                    label = QLabel()
                    label.setAlignment(Qt.AlignCenter)
                    label.setFont(QFont("Segoe UI", 9, QFont.Bold))

                    label.setText(f"R{r+1}\nC{grid_col_index+1- aisle_counter}")
                    label.setStyleSheet("""
                        QLabel {
                            background-color: qlineargradient(
                                spread:pad, x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3CB371, stop:1 #2E8B57);
                            color: #f5f5f5;
                            border-radius: 10px;
                            border: 1px solid #2f503d;
                            padding: 5px;
                            box-shadow: 0px 3px 8px rgba(0,0,0,0.4);
                        }
                        QLabel:hover {
                            background-color: qlineargradient(
                                spread:pad, x1:0, y1:0, x2:0, y2:1,
                                stop:0 #45d181, stop:1 #338d60);
                        }
                    """)


                    frame_layout.addWidget(label)
                    frame.setLayout(frame_layout)
                    self.layout_grid.addWidget(frame, r, grid_col_index)
                    grid_col_index += 1

                # Her masa bloğundan sonra koridor ekle
                if block < cols - 1:
                    corridor = QLabel("KORİDOR")
                    corridor.setAlignment(Qt.AlignCenter)
                    corridor.setFont(QFont("Segoe UI", 8, QFont.Bold))
                    corridor.setFixedSize(80, 70)
                    corridor.setStyleSheet("""
                        QLabel {
                            background-color: #2c2f34;
                            color: #bcbec2;
                            border-radius: 10px;
                            border: 1px solid #3e4147;
                            letter-spacing: 1px;
                        }
                    """)
                    self.layout_grid.addWidget(corridor, r, grid_col_index)
                    aisle_counter += 1
                    grid_col_index += 1
