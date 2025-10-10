from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QDateEdit, QComboBox, QSpinBox, QLineEdit, QPushButton,
    QScrollArea, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from Backend.src.utils.exams.algoritmalar import (
    DersSecimi, SinavTarihleri, SinavTuru, SinavSuresi, BeklemeSuresi
)
from Frontend.src.Coordinator.ExamProgramPage.exam_program_worker import GetClasses


class ExamProgramPage(QWidget):
    program_created = pyqtSignal(dict)  # Sınav programı oluşturulunca emit edilecek
    
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.dersler = []
        self.checkboxes = []
        self.current_step = 1
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Başlık
        header = QLabel("🎓 Sınav Programı Oluşturma")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Progress göstergesi
        self.progress_label = QLabel("Adım 1/5: Ders Seçimi")
        self.progress_label.setFont(QFont("Segoe UI", 11))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        main_layout.addWidget(self.progress_label)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅ Geri")
        self.next_btn = QPushButton("İleri ➡")
        self.finish_btn = QPushButton("✓ Tamamla")
        
        for btn in [self.back_btn, self.next_btn, self.finish_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
        
        self.back_btn.clicked.connect(self.go_back)
        self.next_btn.clicked.connect(self.go_next)
        self.finish_btn.clicked.connect(self.finish_program)
        
        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.finish_btn)
        
        main_layout.addLayout(button_layout)
        
        # İlk adımı yükle
        self.load_step_1()
        self.update_buttons()
        
    def clear_content(self):
        """İçeriği temizle"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def update_buttons(self):
        """Buton görünürlüğünü güncelle"""
        self.back_btn.setVisible(self.current_step > 1)
        self.next_btn.setVisible(self.current_step < 5)
        self.finish_btn.setVisible(self.current_step == 5)
    
    def update_progress(self):
        """Progress label'ı güncelle"""
        steps = {
            1: "Adım 1/5: Ders Seçimi",
            2: "Adım 2/5: Sınav Tarihleri",
            3: "Adım 3/5: Sınav Türü",
            4: "Adım 4/5: Sınav Süresi",
            5: "Adım 5/5: Bekleme Süresi"
        }
        self.progress_label.setText(steps.get(self.current_step, ""))
    
    def load_step_1(self):
        """1. Adım: Ders Seçimi"""
        self.clear_content()
        
        title = QLabel("Programa dahil olmayacak dersleri işaretleyiniz:")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        
        info = QLabel("İşaretlenen dersler sınav programına dahil edilmeyecektir.")
        info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(info)
        
        self.content_layout.addSpacing(10)
        
        # Dersleri yükle
        if not self.dersler:
            loading_label = QLabel("📚 Dersler yükleniyor...")
            self.content_layout.addWidget(loading_label)
            
            self.get_classes_thread = GetClasses("just_classes", self.user_info)
            self.get_classes_thread.finished.connect(self.populate_classes)
            self.get_classes_thread.start()
        else:
            self.populate_classes(self.dersler)
        
        self.content_layout.addStretch()
    
    def populate_classes(self, classes):
        response = classes.get("classes", [])
        self.dersler = [ders[1] for ders in response] 
        
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget and "yükleniyor" in widget.text().lower():
                widget.deleteLater()
                break
        
        self.checkboxes.clear()
        for ders in self.dersler:
            cb = QCheckBox(ders)
            cb.setCursor(Qt.PointingHandCursor)
            self.checkboxes.append(cb)
            self.content_layout.addWidget(cb)
        
        self.content_layout.addStretch()
    
    def load_step_2(self):
        """2. Adım: Sınav Tarihleri"""
        self.clear_content()
        
        title = QLabel("Sınav tarih aralığını ve hariç tutulacak günleri seçiniz:")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        
        self.content_layout.addSpacing(20)
        
        # Tarih seçimi
        date_label = QLabel("📅 Sınav Tarih Aralığı:")
        date_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.content_layout.addWidget(date_label)
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(10))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Başlangıç:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("Bitiş:"))
        date_layout.addWidget(self.end_date)
        date_layout.addStretch()
        self.content_layout.addLayout(date_layout)
        
        self.content_layout.addSpacing(20)
        
        # Hariç tutulacak günler
        exclude_label = QLabel("🚫 Hariç Tutulacak Günler:")
        exclude_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.content_layout.addWidget(exclude_label)
        
        self.check_cumartesi = QCheckBox("Cumartesi")
        self.check_pazar = QCheckBox("Pazar")
        
        for cb in [self.check_cumartesi, self.check_pazar]:
            cb.setCursor(Qt.PointingHandCursor)
            self.content_layout.addWidget(cb)
        
        self.content_layout.addStretch()
    
    def load_step_3(self):
        """3. Adım: Sınav Türü"""
        self.clear_content()
        
        title = QLabel("Sınav türünü seçiniz:")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        
        self.content_layout.addSpacing(20)
        
        type_label = QLabel("📝 Sınav Türü:")
        type_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.content_layout.addWidget(type_label)
        
        self.combo_sinav_turu = QComboBox()
        self.combo_sinav_turu.addItems(["Vize", "Final", "Bütünleme"])
        self.combo_sinav_turu.setCursor(Qt.PointingHandCursor)
        self.combo_sinav_turu.setMinimumHeight(35)
        self.content_layout.addWidget(self.combo_sinav_turu)
        
        self.content_layout.addStretch()
    
    def load_step_4(self):
        """4. Adım: Sınav Süresi"""
        self.clear_content()
        
        title = QLabel("Varsayılan sınav süresini ve istisnaları belirleyiniz:")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        
        self.content_layout.addSpacing(20)
        
        # Varsayılan süre
        default_label = QLabel("⏱️ Varsayılan Sınav Süresi:")
        default_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.content_layout.addWidget(default_label)
        
        self.spin_default = QSpinBox()
        self.spin_default.setRange(30, 180)
        self.spin_default.setValue(75)
        self.spin_default.setSuffix(" dakika")
        self.spin_default.setMinimumHeight(35)
        self.content_layout.addWidget(self.spin_default)
        
        self.content_layout.addSpacing(20)
        
        # İstisna
        exception_label = QLabel("⚠️ İstisna Ders (Opsiyonel):")
        exception_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.content_layout.addWidget(exception_label)
        
        self.input_ders = QLineEdit()
        self.input_ders.setPlaceholderText("Ders adını giriniz...")
        self.input_ders.setMinimumHeight(35)
        self.content_layout.addWidget(self.input_ders)
        
        self.spin_istisna = QSpinBox()
        self.spin_istisna.setRange(30, 180)
        self.spin_istisna.setValue(60)
        self.spin_istisna.setSuffix(" dakika")
        self.spin_istisna.setMinimumHeight(35)
        self.content_layout.addWidget(self.spin_istisna)
        
        self.content_layout.addStretch()
    
    def load_step_5(self):
        """5. Adım: Bekleme Süresi"""
        self.clear_content()
        
        title = QLabel("Sınavlar arası bekleme süresini belirleyiniz:")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        
        self.content_layout.addSpacing(20)
        
        wait_label = QLabel("⏳ Bekleme Süresi:")
        wait_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.content_layout.addWidget(wait_label)
        
        info = QLabel("Bir sınav bitiminden sonraki sınava kadar geçmesi gereken minimum süre.")
        info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(info)
        
        self.spin_bekleme = QSpinBox()
        self.spin_bekleme.setRange(5, 60)
        self.spin_bekleme.setValue(15)
        self.spin_bekleme.setSuffix(" dakika")
        self.spin_bekleme.setMinimumHeight(35)
        self.content_layout.addWidget(self.spin_bekleme)
        
        self.content_layout.addStretch()
    
    def go_next(self):
        """Sonraki adıma geç"""
        if self.current_step < 5:
            self.current_step += 1
            self.load_current_step()
            self.update_buttons()
            self.update_progress()
    
    def go_back(self):
        """Önceki adıma dön"""
        if self.current_step > 1:
            self.current_step -= 1
            self.load_current_step()
            self.update_buttons()
            self.update_progress()
    
    def load_current_step(self):
        """Mevcut adımı yükle"""
        steps = {
            1: self.load_step_1,
            2: self.load_step_2,
            3: self.load_step_3,
            4: self.load_step_4,
            5: self.load_step_5
        }
        steps[self.current_step]()
    
    def finish_program(self):
        """Programı tamamla ve sonuçları topla"""
        try:
            # Ders seçimi
            cikarilacaklar = [cb.text() for cb in self.checkboxes if cb.isChecked()]
            secim = DersSecimi(self.dersler)
            kalan_dersler = secim.filtrele(cikarilacaklar)
            
            # Tarih bilgisi
            tarih = SinavTarihleri()
            tarih.set_tarih_araligi(
                self.start_date.date().toString(Qt.ISODate),
                self.end_date.date().toString(Qt.ISODate)
            )
            haris_gunler = []
            if self.check_cumartesi.isChecked():
                haris_gunler.append("Cumartesi")
            if self.check_pazar.isChecked():
                haris_gunler.append("Pazar")
            tarih.set_haris_gunler(haris_gunler)
            
            # Sınav türü
            tur = SinavTuru()
            tur.set_tur(self.combo_sinav_turu.currentText())
            
            # Sınav süresi
            sure = SinavSuresi()
            sure.set_varsayilan(self.spin_default.value())
            if self.input_ders.text():
                sure.set_istisna(self.input_ders.text(), self.spin_istisna.value())
            
            # Bekleme süresi
            bekleme = BeklemeSuresi()
            bekleme.set_sure(self.spin_bekleme.value())
            
            results = {
                "kalan_dersler": kalan_dersler,
                "tarih_bilgisi": tarih,
                "sinav_turu": tur,
                "sinav_suresi": sure,
                "bekleme_suresi": bekleme
            }
            
            print("---- SINAV PROGRAMI SONUÇLARI ----")
            print("Kalan Dersler:", results["kalan_dersler"])
            print("Tarih Bilgisi:", results["tarih_bilgisi"])
            print("Sınav Türü:", results["sinav_turu"])
            print("Sınav Süresi:", results["sinav_suresi"])
            print("Bekleme Süresi:", results["bekleme_suresi"])
            
            self.program_created.emit(results)
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ Sınav programı başarıyla oluşturuldu!\n\n"
                f"📚 Ders sayısı: {len(kalan_dersler)}\n"
                f"📝 Sınav türü: {self.combo_sinav_turu.currentText()}\n"
                f"⏱️ Varsayılan süre: {self.spin_default.value()} dk"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"❌ Program oluşturulurken hata oluştu:\n{str(e)}"
            )