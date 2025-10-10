from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Styles.load_qss import load_stylesheet

class InsertClassroomPage(QWidget):
    classroom_added_with_user = {}
    
    def __init__(self, parent_stack, user_info, dashboard=None):
        super().__init__()
        self.user_info = user_info
        self.parent_stack = parent_stack
        self.dashboard = dashboard 
        
        # Kullanıcı ilk kez ekleniyor mu kontrol et
        user_email = self.user_info.get("email")
        if user_email not in InsertClassroomPage.classroom_added_with_user:
            InsertClassroomPage.classroom_added_with_user[user_email] = False
        
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(load_stylesheet("Frontend/src/Styles/classroom_page_styles.qss"))
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        user_email = self.user_info.get('email')
        has_added_classroom = InsertClassroomPage.classroom_added_with_user.get(user_email, False)
        
        if not has_added_classroom:
            title = QLabel("➕ İlk Dersliği Ekleyin")
            title.setFont(QFont("Arial", 18, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
        
            info_label = QLabel("⚠️ Devam etmek için en az bir derslik eklemeniz gerekmektedir.")
            info_label.setFont(QFont("Arial", 10))
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("color: #ff9800; margin-bottom: 10px;")
            layout.addWidget(info_label)
        else:
            # Derslik eklenmişse normal başlık göster
            title = QLabel("➕ Yeni Derslik Ekle")
            title.setFont(QFont("Arial", 18, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
        
        # Form alanları
        self.classroom_id = QLineEdit()
        self.classroom_name = QLineEdit()
        self.department = QLineEdit()
        self.capacity = QLineEdit()
        self.desks_row = QLineEdit()
        self.desks_col = QLineEdit()
        self.structure = QLineEdit()
        
        fields = [
            ("Derslik Kodu:", self.classroom_id),
            ("Derslik Adı:", self.classroom_name),
            ("Bölüm Adı:", self.department),
            ("Kapasite:", self.capacity),
            ("Sıra Satır Sayısı:", self.desks_row),
            ("Sıra Sütun Sayısı:", self.desks_col),
            ("Masa Yapısı:", self.structure)
        ]
        
        for label, widget in fields:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅️ Geri Dön")
        self.insert_btn = QPushButton("Kaydet")
        
        # Geri dön butonu - sadece derslik eklenmişse aktif
        if has_added_classroom:
            self.back_btn.setEnabled(True)
            self.back_btn.setStyleSheet("")  # Normal stil
        else:
            self.back_btn.setEnabled(False)
            self.back_btn.setStyleSheet("background-color: #555; color: #888;")
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.insert_btn)
        layout.addLayout(btn_layout)
        
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)
        
        self.setLayout(layout)
        
        self.insert_btn.clicked.connect(self.insert_classroom)
        self.back_btn.clicked.connect(self.go_back)
    
    def go_back(self):
        from Frontend.src.Coordinator.Classroom.clasroomPage import ClassroomPage
        classroom_page = ClassroomPage(self.parent_stack, self.user_info)
        self.parent_stack.addWidget(classroom_page)
        self.parent_stack.setCurrentWidget(classroom_page)
        
    def insert_classroom(self):
        # Validation
        if not all([
            self.classroom_id.text(),
            self.classroom_name.text(),
            self.department.text(),
            self.capacity.text(),
            self.desks_row.text(),
            self.desks_col.text(),
            self.structure.text()
        ]):
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        # Sayısal değerleri kontrol et
        try:
            capacity = int(self.capacity.text())
            desks_row = int(self.desks_row.text())
            desks_col = int(self.desks_col.text())
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Kapasite ve sıra sayıları sayısal olmalıdır!")
            return
        
        data = {
            "classroom_id": self.classroom_id.text(),
            "classroom_name": self.classroom_name.text(),
            "department_name": self.department.text(),
            "capacity": capacity,
            "desks_per_row": desks_row,
            "desks_per_column": desks_col,
            "desk_structure": self.structure.text()
        }
        
        self.request = ClassroomRequests("insert_classroom", data, self.user_info)
        self.request.finished.connect(self.handle_response)
        self.request.start()
    
    def handle_response(self, response):
        self.result.setText(str(response))
        
        if response.get("status") == "error":
            QMessageBox.critical(self, "Hata", response.get("detail", "Bilinmeyen hata"))
        else:
            QMessageBox.information(self, "Başarılı", "Derslik başarıyla eklendi!")
            
            user_email = self.user_info.get('email')
            
            # İlk derslik eklendiyse durumu güncelle
            if not InsertClassroomPage.classroom_added_with_user.get(user_email, False):
                InsertClassroomPage.classroom_added_with_user[user_email] = True
                
                # Dashboard'a bildir
                if self.dashboard:
                    self.dashboard.on_first_classroom_added()
                
                # UI'ı güncelle (geri dön butonunu aktif et)
                self.refresh_ui()
            
            # Formu temizle
            self.clear_form()
    
    def refresh_ui(self):
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                child = old_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            QWidget().setLayout(old_layout)
        
        self.init_ui()
    
    def clear_form(self):
        self.classroom_id.clear()
        self.classroom_name.clear()
        self.department.clear()
        self.capacity.clear()
        self.desks_row.clear()
        self.desks_col.clear()
        self.structure.clear()
        self.result.clear()