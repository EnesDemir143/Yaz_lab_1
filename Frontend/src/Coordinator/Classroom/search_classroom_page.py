from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox,
    QHBoxLayout, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet


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
            rows = int(classroom.get("desks_per_row", 0))
            cols = int(classroom.get("desks_per_column", 0))
            struct = int(classroom.get("desk_structure", 0))
            cap = int(classroom.get("capacity", 0))
            self.draw_classroom_layout(rows, cols, struct, cap)
        except Exception as e:
            QMessageBox.warning(self, "Visualization Error", f"Cannot visualize: {e}")

    def draw_classroom_layout(self, rows: int, cols: int, structure: int, capacity: int = None):
        if self.visual_layout:
            while self.visual_layout.count():
                item = self.visual_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            self.visual_layout = QGridLayout(self.visual_frame)
            self.visual_layout.setSpacing(10)
            self.visual_layout.setAlignment(Qt.AlignCenter)

        total_capacity = capacity or (rows * cols * structure)

        desk_id = 1
        current_person = 1

        for r in range(rows):
            for c in range(cols):
                # Masa dış çerçevesi
                desk_frame = QFrame()
                desk_frame.setStyleSheet("""
                    QFrame {
                        background-color: #4CAF50;
                        border: 2px solid #2e7d32;
                        border-radius: 8px;
                    }
                """)
                desk_frame.setFixedSize(80 + (structure - 1) * 25, 55)

                inner_layout = QHBoxLayout()
                inner_layout.setContentsMargins(6, 6, 6, 6)
                inner_layout.setSpacing(6)

                # Her masada structure kadar küçük blok (kişi alanı)
                for i in range(structure):
                    block_frame = QFrame()
                    block_frame.setFixedSize(25, 35)
                    block_layout = QVBoxLayout()
                    block_layout.setContentsMargins(2, 2, 2, 2)
                    block_layout.setSpacing(0)

                    # Eğer hala kapasite dolmamışsa kişi yerleştir
                    if current_person <= total_capacity:
                        person_label = QLabel(str(current_person))
                        current_person += 1
                        person_label.setAlignment(Qt.AlignCenter)
                        person_label.setFont(QFont("Arial", 9, QFont.Bold))
                        person_label.setStyleSheet("""
                            QLabel {
                                background-color: #2e7d32;
                                color: white;
                                border-radius: 4px;
                                border: 1px solid #1b5e20;
                            }
                        """)
                    else:
                        # Kapasite dolduysa boş koltuk
                        person_label = QLabel("")
                        person_label.setStyleSheet("""
                            QLabel {
                                background-color: #777;
                                border-radius: 4px;
                                border: 1px solid #444;
                            }
                        """)

                    block_layout.addWidget(person_label)
                    block_frame.setLayout(block_layout)
                    inner_layout.addWidget(block_frame)

                desk_frame.setLayout(inner_layout)
                self.visual_layout.addWidget(desk_frame, r, c)

                desk_id += 1
                if current_person > total_capacity:
                    break
            if current_person > total_capacity:
                break
