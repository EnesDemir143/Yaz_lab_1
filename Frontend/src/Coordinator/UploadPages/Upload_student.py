from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QProgressBar, QMessageBox, QFileDialog, QComboBox, QStackedLayout
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.UploadPages.upload_worker import UploadWorker

class UploadStudentList(QWidget):
    done = pyqtSignal()
    
    def __init__(self, user_info, parent_dashboard=None, setup_mode=False):
        super().__init__()
        self.user_info = user_info
        self.parent_dashboard = parent_dashboard
        self.setup_mode = setup_mode
        self.file_path = None
        self.current_endpoint = "upload_students_list"
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        title = QLabel("📚 Öğrenci Listesi Yükle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("Yüklenecek Excel dosyasını seçiniz")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #aaa;")
        
        # --- Dosya seçimi ---
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Henüz dosya seçilmedi")
        self.file_label.setStyleSheet("color: #aaa;")
        self.select_btn = QPushButton("Dosya Seç")
        self.select_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_btn)
        
        # --- Upload butonu ---
        self.upload_btn = QPushButton("📤 Yüklemeyi Başlat")
        self.upload_btn.clicked.connect(self.upload_action)
        
        # --- Progress bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # --- Setup mode için Okey butonu ---
        if self.setup_mode:
            self.okey_btn = QPushButton("✅ Okey (Devam Et)")
            self.okey_btn.setMinimumHeight(50)
            self.okey_btn.setEnabled(False)  # Başlangıçta devre dışı
            self.okey_btn.clicked.connect(self.handle_done)
        
        # --- Layout birleştirme ---
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addLayout(file_layout)
        layout.addWidget(self.upload_btn)
        layout.addWidget(self.progress_bar)
        
        if self.setup_mode:
            layout.addStretch()
            layout.addWidget(self.okey_btn)
        else:
            layout.addStretch()
        
        self.setLayout(layout)
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_label.setText(file_path.split("/")[-1])
            self.file_path = file_path
    
    def upload_action(self):
        if not self.file_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir Excel dosyası seçin.")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Setup mode veya normal mode için endpoint
        if self.setup_mode:
            endpoint = self.current_endpoint
        else:
            if not self.parent_dashboard or not hasattr(self.parent_dashboard, "current_endpoint"):
                QMessageBox.warning(self, "Uyarı", "Geçerli bir işlem seçilmedi.")
                return
            endpoint = self.parent_dashboard.current_endpoint
        
        self.worker = UploadWorker(
            endpoint,
            self.file_path,
            self.user_info,
        )
        self.worker.finished.connect(self.on_upload_finished)
        self.worker.start()
    
    def on_upload_finished(self, result):
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        
        if "error" in result.get("status", ""):
            QMessageBox.critical(self, "Hata", result["detail"])
            if self.parent_dashboard and hasattr(self.parent_dashboard, 'text_output'):
                self.parent_dashboard.text_output.append(
                    f"❌ Hata: {result['detail']} {result.get('message', '')}\n"
                )
        else:
            msg = result.get("message", "İstek tamamlandı.")
            detail = result.get("detail", "")
            
            if self.parent_dashboard and hasattr(self.parent_dashboard, 'text_output'):
                self.parent_dashboard.text_output.append(f"✅ {detail}\n")
            
            QMessageBox.information(self, "Başarılı", f"message: {msg}\n\n{detail}")
            
            # Setup mode'da başarılı upload sonrası Okey butonunu aktif et
            if self.setup_mode:
                self.okey_btn.setEnabled(True)
                self.okey_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            
            if self.parent_dashboard and hasattr(self.parent_dashboard, 'menu'):
                self.parent_dashboard.menu.setCurrentRow(0)
    
    def handle_done(self):
        """Okey butonuna basıldığında"""
        self.done.emit()
        if self.setup_mode:
            self.close()