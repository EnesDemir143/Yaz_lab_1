from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QDateEdit, QComboBox, QSpinBox, QPushButton,
    QScrollArea, QFrame, QMessageBox, QApplication,
    QDoubleSpinBox, QLineEdit
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from Frontend.src.Admin.ExamProgramPages.exam_program_worker import GetClasses
from Backend.src.utils.exams.ExanProgramClass import ExamProgram
from Backend.src.utils.exams.create_exam_program import create_exam_schedule
from Frontend.src.Admin.Classroom.classroomReqs import ClassroomRequests
from Frontend.src.Admin.ExamProgramPages.insert_exam_schedule_worker import InsertExamScheduleWorker

class ExamProgramPage(QWidget):
    program_created = pyqtSignal(dict)

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.dersler = []
        self.excluded_courses = set() 
        self.active_threads = []
        
        # --- DEĞİŞİKLİK 1: Adım 0'dan başlat ---
        self.current_step = 0 # 1 yerine 0'dan başlatıldı
        self.selected_department = None # Seçilen bölümü saklamak için
        # --- DEĞİŞİKLİK 1 BİTTİ ---
        
        self.saved_start_date = None
        self.saved_end_date = None
        self.saved_cumartesi = False
        self.saved_pazar = False
        self.saved_sinav_turu = "Vize"
        self.saved_varsayilan_sure = 75
        self.saved_istisna_ders = {}
        self.saved_istisna_sure = 60
        self.saved_bekleme = 15
        self.exam_conflict = False 
        self.start_time_value = 9.0
        self.end_time_value = 17.0
        
        self.classes_and_their_students = None
        self.classrooms_data = None
        self.exam_program = None
        
        self.init_ui()

    # -------------------------- UI SETUP --------------------------

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # Başlık
        header = QLabel("🎓 Sınav Programı Oluşturma")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # --- DEĞİŞİKLİK 2: Adım 0 metni ---
        self.progress_label = QLabel("Adım 0/6: Bölüm Seçimi")
        # --- DEĞİŞİKLİK 2 BİTTİ ---
        self.progress_label.setFont(QFont("Arial", 11))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        main_layout.addWidget(self.progress_label)
        
        # --- DEĞİŞİKLİK 1: Adım 0 widget'larını bir container'a al ---
        self.step_0_widget = QWidget() # Adım 0'ı (Bölüm Seçimi) tutan widget
        step_0_layout = QVBoxLayout(self.step_0_widget)
        step_0_layout.setContentsMargins(0, 0, 0, 0) # Ekstra boşluk olmasın
    
        department_options = QLabel("🏫 Bölüm Seçimi:")
        department_options.setFont(QFont("Arial", 11, QFont.Bold))
        # DÜZELTME: main_layout yerine step_0_layout'a eklendi
        step_0_layout.addWidget(department_options)
        
        dept_layout = QHBoxLayout()
        dept_label = QLabel("🏫 Bölüm Seçin:")
        self.department_box = QComboBox()
        self.department_box.addItems(["", "Bilgisayar Mühendisliği", "Elektrik Mühendisliği", "Elektronik Mühendisliği", "İnşaat Mühendisliği"])
        dept_layout.addWidget(dept_label)
        dept_layout.addWidget(self.department_box)

        # DÜZELTME: main_layout yerine step_0_layout'a eklendi
        step_0_layout.addLayout(dept_layout) 
        
        # step_0_widget (tüm Adım 0 içeriğiyle birlikte) ana layout'a ekleniyor
        main_layout.addWidget(self.step_0_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # --- DEĞİŞİKLİK 3: ScrollArea'yı başta gizle ---
        self.scroll_area.setVisible(False) 
        # --- DEĞİŞİKLİK 3 BİTTİ ---

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)

        main_layout.addWidget(self.scroll_area)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.back_btn = QPushButton("⬅ Geri")
        self.next_btn = QPushButton("İleri ➡")
        self.finish_btn = QPushButton("✓ Tamamla")

        for btn in [self.back_btn, self.next_btn, self.finish_btn]:
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)

        # --- DEĞİŞİKLİK 4: Buton bağlantı mantığını düzelt ---
        # Karmaşık if/else bloğu kaldırıldı. go_next fonksiyonu tüm mantığı yönetecek.
        self.back_btn.clicked.connect(self.go_back)
        self.next_btn.clicked.connect(self.go_next)
        # --- DEĞİŞİKLİK 4 BİTTİ ---
        
        self.finish_btn.clicked.connect(self.finish_program)

        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.finish_btn)
        main_layout.addLayout(button_layout)

        self.update_buttons()

    # -------------------------- ADIM YÖNETİMİ --------------------------

    def clear_content(self):
        """İçeriği temizle"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def clear_layout(self, layout):
        """Layout içindeki tüm widget'ları temizle"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
    
    def update_buttons(self):
        # --- DEĞİŞİKLİK 5: Geri butonu Adım 0'da gizli ---
        self.back_btn.setVisible(self.current_step > 0)
        # --- DEĞİŞİKLİK 5 BİTTİ ---
        self.next_btn.setVisible(self.current_step < 6)
        self.finish_btn.setVisible(self.current_step == 6)

    def update_progress(self):
        steps = {
            # --- DEĞİŞİKLİK 6: Adım 0 eklendi ---
            0: "Adım 0/6: Bölüm Seçimi",
            # --- DEĞİŞİKLİK 6 BİTTİ ---
            1: "Adım 1/6: Ders Seçimi",
            2: "Adım 2/6: Sınav Tarihleri",
            3: "Adım 3/6: Sınav Türü",
            4: "Adım 4/6: Sınav Süresi",
            5: "Adım 5/6: Bekleme Süresi",
            6: "Adım 6/6: Çakışma Kontrolü"
        }
        self.progress_label.setText(steps.get(self.current_step, ""))

    def go_next(self):
        # --- DEĞİŞİKLİK 7: Adım 0 -> 1 geçiş mantığı eklendi ---
        if self.current_step == 0:
            dept = self.department_box.currentText()
            if not dept:
                QMessageBox.warning(self, "Uyarı", "Lütfen devam etmek için bir bölüm seçiniz.")
                return
            
            self.selected_department = dept
            
            self.step_0_widget.setVisible(False) # Bölüm seçme alanını GİZLE
            self.scroll_area.setVisible(True)    # Ders listesi alanını GÖSTER  
            
            self.department_box.setEnabled(False) # Bölüm seçimini kilitle
            self.scroll_area.setVisible(True)    # İçerik alanını görünür yap
            
            self.current_step = 1
            self.load_step_1(self.selected_department) # Adım 1'i bölüm adıyla yükle
        # --- DEĞİŞİKLİK 7 BİTTİ ---
        else:
            self.save_current_step_data()
            
            if self.current_step < 6:
                self.current_step += 1
                self.load_current_step()
        
        self.update_buttons()
        self.update_progress()

    def save_current_step_data(self):
        try:
            if self.current_step == 2:
                if hasattr(self, 'start_date') and self.start_date:
                    self.saved_start_date = self.start_date.date()
                if hasattr(self, 'end_date') and self.end_date:
                    self.saved_end_date = self.end_date.date()
                self.start_time_value = self.parse_time_input(self.start_time_input.text())
                self.end_time_value = self.parse_time_input(self.end_time_input.text())
                if hasattr(self, 'check_cumartesi') and self.check_cumartesi:
                    self.saved_cumartesi = self.check_cumartesi.isChecked()
                if hasattr(self, 'check_pazar') and self.check_pazar:
                    self.saved_pazar = self.check_pazar.isChecked()
            
            elif self.current_step == 3:
                if hasattr(self, 'combo_sinav_turu') and self.combo_sinav_turu:
                    self.saved_sinav_turu = self.combo_sinav_turu.currentText()
            
            elif self.current_step == 4:
                if hasattr(self, 'spin_default') and self.spin_default:
                    self.saved_varsayilan_sure = self.spin_default.value()
            
            elif self.current_step == 5:
                if hasattr(self, 'spin_bekleme') and self.spin_bekleme:
                    self.saved_bekleme = self.spin_bekleme.value()
                    
            elif self.current_step == 6:
                if hasattr(self, 'check_conflict'):
                    self.exam_conflict = self.check_conflict.isChecked()
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"❌ Veriler kaydedilirken hata oluştu:\n{str(e)}")


    def go_back(self):
        # --- DEĞİŞİKLİK 8: Adım 1 -> 0 geri dönüş mantığı ---
        if self.current_step == 1:
            # Adım 1'den 0'a dönülüyor
            self.clear_content()
            
            self.scroll_area.setVisible(False)   # Ders listesi alanını GİZLE
            self.step_0_widget.setVisible(True)
                        
            self.scroll_area.setVisible(False)
            self.department_box.setEnabled(True) # Bölüm seçimini tekrar aç
            self.current_step = 0
        # --- DEĞİŞİKLİK 8 BİTTİ ---
        elif self.current_step > 1:
            self.current_step -= 1
            self.load_current_step()
            
        self.update_buttons()
        self.update_progress()

    def load_current_step(self):
        self.clear_content()
        QApplication.processEvents() 
        
        # --- DEĞİŞİKLİK 9: load_step_1 buradan kaldırıldı ---
        # load_step_1 artık sadece go_next tarafından özel olarak çağrılıyor.
        steps = {
            2: self.load_step_2,
            3: self.load_step_3,
            4: self.load_step_4,
            5: self.load_step_5,
            6: self.load_step_6
        }
        # --- DEĞİŞİKLİK 9 BİTTİ ---
        
        # Sadece 2 ve üzeri adımlar için çalışır
        if self.current_step in steps:
            steps[self.current_step]()
            
    def parse_time_input(self, text: str) -> float:
        try:
            if "." in text:
                hour_str, minute_str = text.split(".")
                hour = int(hour_str)
                minute = int(minute_str)
                return hour + (minute / 60.0)
            else:
                return float(text)
        except Exception:
            return None


    # -------------------------- ADIM 1 --------------------------

    def load_step_1(self, department: str):
        self.clear_content()
            
        title = QLabel("Programa dahil olmayacak dersleri işaretleyiniz:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        
        info = QLabel("İşaretlenen dersler sınav programına dahil edilmeyecektir.")
        info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(info)
        self.content_layout.addSpacing(10)

        if not self.dersler or self.selected_department != department:
            loading_label = QLabel(f"📚 {department} bölümü için dersler yükleniyor...")
            self.content_layout.addWidget(loading_label)
            
            # --- ÖNEMLİ ---
            self.get_classes_thread = GetClasses("just_classes", self.user_info, department=department)
            self.get_classes_thread.finished.connect(self.populate_classes)
            self.get_classes_thread.start()
        else:
            # Dersler zaten yüklü, sadece checkbox'ları tekrar oluştur
            self.populate_classes({"classes": [(None, d) for d in self.dersler]})

        self.content_layout.addStretch()

    def populate_classes(self, classes_data):
        # 'classes' anahtarını kontrol et
        response = classes_data.get("classes", [])
        if not response:
             QMessageBox.warning(self, "Veri Yok", "Bölüm için ders bulunamadı.")
        
        self.dersler = [ders[1] for ders in response]

        # "Yükleniyor" etiketini kaldır
        for i in range(self.content_layout.count()):
            w = self.content_layout.itemAt(i).widget()
            if isinstance(w, QLabel) and w.text() and "yükleniyor" in w.text().lower():
                w.deleteLater()
                break

        # Checkbox'ları oluştur
        for ders in self.dersler:
            cb = QCheckBox(ders)
            cb.setCursor(Qt.PointingHandCursor)
            cb.setChecked(ders in self.excluded_courses)
            cb.toggled.connect(lambda checked, name=ders: self._toggle_excluded(name, checked))
            self.content_layout.addWidget(cb)

        self.content_layout.addStretch()

    def _toggle_excluded(self, name: str, checked: bool):
        if checked:
            self.excluded_courses.add(name)
        else:
            self.excluded_courses.discard(name)

    # -------------------------- ADIM 2 --------------------------

    def load_step_2(self):
        self.clear_content()
        title = QLabel("Sınav tarih aralığını ve hariç tutulacak günleri seçiniz:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        self.content_layout.addSpacing(20)

        # Tarih seçimi
        date_label = QLabel("📅 Sınav Tarih Aralığı:")
        date_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(date_label)

        self.start_date = QDateEdit()
        if self.saved_start_date:
            self.start_date.setDate(self.saved_start_date)
        else:
            self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")

        self.end_date = QDateEdit()
        if self.saved_end_date:
            self.end_date.setDate(self.saved_end_date)
        else:
            self.end_date.setDate(QDate.currentDate().addDays(10))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        
        # Saat seçimi   
        saat_label = QLabel("⏰ Sınav Gün Başlangıç ve Bitiş Saatleri:")
        saat_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(saat_label)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Başlangıç:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("Bitiş:"))
        date_layout.addWidget(self.end_date)
        date_layout.addStretch()
        self.content_layout.addLayout(date_layout)
        self.content_layout.addSpacing(20)

        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("Örn: 09.15")
        self.start_time_input.setText("09.00")  # varsayılan değer
        self.start_time_input.setFixedWidth(90)
        self.start_time_input.setAlignment(Qt.AlignCenter)
        self.start_time_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                font-size: 10pt;
            }
        """)

        # 🕔 Bitiş saati giriş alanı
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("Örn: 17.30")
        self.end_time_input.setText("17.00")
        self.end_time_input.setFixedWidth(90)
        self.end_time_input.setAlignment(Qt.AlignCenter)
        self.end_time_input.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                font-size: 10pt;
            }
        """)

        # Layout’a ekleme
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Gün Başlangıç Saati:"))
        time_layout.addWidget(self.start_time_input)
        time_layout.addWidget(QLabel("Gün Bitiş Saati:"))
        time_layout.addWidget(self.end_time_input)
        time_layout.addStretch()
        self.content_layout.addLayout(time_layout)
        self.content_layout.addSpacing(20)

        # Hariç günler
        exclude_label = QLabel("🚫 Hariç Tutulacak Günler:")
        exclude_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(exclude_label)
        self.check_cumartesi = QCheckBox("Cumartesi")
        self.check_cumartesi.setChecked(self.saved_cumartesi)
        self.check_pazar = QCheckBox("Pazar")
        self.check_pazar.setChecked(self.saved_pazar)
        for cb in [self.check_cumartesi, self.check_pazar]:
            cb.setCursor(Qt.PointingHandCursor)
            self.content_layout.addWidget(cb)
        self.content_layout.addStretch()

    # -------------------------- ADIM 3 --------------------------

    def load_step_3(self):
        self.clear_content()
        title = QLabel("Sınav türünü seçiniz:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        self.content_layout.addSpacing(20)

        type_label = QLabel("📝 Sınav Türü:")
        type_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(type_label)
        self.combo_sinav_turu = QComboBox()
        self.combo_sinav_turu.addItems(["Vize", "Final", "Bütünleme"])
        self.combo_sinav_turu.setCurrentText(self.saved_sinav_turu)
        self.combo_sinav_turu.setCursor(Qt.PointingHandCursor)
        self.combo_sinav_turu.setMinimumHeight(35)
        self.content_layout.addWidget(self.combo_sinav_turu)
        self.content_layout.addStretch()

    def load_step_4(self):
        self.clear_content()
        title = QLabel("Varsayılan sınav süresini ve istisnaları belirleyiniz:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        self.content_layout.addSpacing(20)

        default_label = QLabel("⏱️ Varsayılan Sınav Süresi:")
        default_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(default_label)
        default_info = QLabel("Tüm dersler için varsayılan sınav süresi:")
        default_info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(default_info)

        self.spin_default = QSpinBox()
        self.spin_default.setRange(30, 180)
        self.spin_default.setValue(self.saved_varsayilan_sure)
        self.spin_default.setSuffix(" dakika")
        self.spin_default.setMinimumHeight(35)
        self.content_layout.addWidget(self.spin_default)
        self.content_layout.addSpacing(20)

        # İstisna dersi
        exception_label = QLabel("⚠️ İstisna Ders (Opsiyonel):")
        exception_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(exception_label)
        exception_info = QLabel("Farklı bir süreye ihtiyaç duyan dersi seçiniz:")
        exception_info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(exception_info)

        self.combo_istisna_ders = QComboBox()
        self.combo_istisna_ders.addItem("-- Seçiniz (Opsiyonel) --", None)
        kalan_dersler = [d for d in self.dersler if d not in self.excluded_courses]
        for ders in kalan_dersler:
            self.combo_istisna_ders.addItem(ders, ders)

        self.combo_istisna_ders.setCursor(Qt.PointingHandCursor)
        self.combo_istisna_ders.setMinimumHeight(35)
        self.content_layout.addWidget(self.combo_istisna_ders)

        duration_label = QLabel("İstisna Sınav Süresi:")
        duration_label.setStyleSheet("margin-top: 10px;")
        self.content_layout.addWidget(duration_label)
        self.spin_istisna = QSpinBox()
        self.spin_istisna.setRange(30, 180)
        self.spin_istisna.setValue(self.saved_istisna_sure)
        self.spin_istisna.setSuffix(" dakika")
        self.spin_istisna.setMinimumHeight(35)
        self.content_layout.addWidget(self.spin_istisna)
        self.content_layout.addStretch()
        
        self.combo_istisna_ders.currentIndexChanged.connect(self.guncelle_istisna_suresi_gorunumu)
        self.spin_istisna.valueChanged.connect(self.kaydet_istisna_suresi)
    
        self.guncelle_istisna_suresi_gorunumu(self.combo_istisna_ders.currentIndex())

    def guncelle_istisna_suresi_gorunumu(self, index):
        secili_ders = self.combo_istisna_ders.currentData()
        
        if secili_ders in self.saved_istisna_ders:
            self.spin_istisna.blockSignals(True)
            self.spin_istisna.setValue(self.saved_istisna_ders[secili_ders])
            self.spin_istisna.blockSignals(False)
        else:
            self.spin_istisna.blockSignals(True)
            self.spin_istisna.setValue(self.spin_default.value())
            self.spin_istisna.blockSignals(False)

    def kaydet_istisna_suresi(self, yeni_sure):
        secili_ders = self.combo_istisna_ders.currentData()
        
        if secili_ders:
            if yeni_sure == self.spin_default.value():
                if secili_ders in self.saved_istisna_ders:
                    del self.saved_istisna_ders[secili_ders]
            else:
                self.saved_istisna_ders[secili_ders] = yeni_sure
            

    def load_step_5(self):
        self.clear_content()
        title = QLabel("Sınavlar arası bekleme süresini belirleyiniz:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        self.content_layout.addWidget(title)
        self.content_layout.addSpacing(20)

        wait_label = QLabel("⏳ Bekleme Süresi:")
        wait_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.content_layout.addWidget(wait_label)
        info = QLabel("Bir sınav bitiminden sonraki sınava kadar geçmesi gereken minimum süre.")
        info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(info)

        self.spin_bekleme = QSpinBox()
        self.spin_bekleme.setRange(5, 60)
        self.spin_bekleme.setValue(self.saved_bekleme)
        self.spin_bekleme.setSuffix(" dakika")
        self.spin_bekleme.setMinimumHeight(35)
        self.content_layout.addWidget(self.spin_bekleme)
        self.content_layout.addStretch()
        
        
    def load_step_6(self):
        self.clear_content()

        title = QLabel("🔍 Ders Çakışma Kontrolü")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(title)
        self.content_layout.addSpacing(20)

        self.check_conflict = QCheckBox(
            "Bu seçenek seçilirse, dersler aynı anda sınav olabilir."
        )
        self.check_conflict.setChecked(self.exam_conflict)
        self.check_conflict.setCursor(Qt.PointingHandCursor)
        self.check_conflict.setFont(QFont("Arial", 15))
        self.content_layout.addWidget(self.check_conflict)

        self.content_layout.addStretch()

    def finish_program(self):
        try:
            self.save_current_step_data()

            self.exam_program = ExamProgram()
            self.exam_program.set_dersler(self.dersler)
            self.exam_program.set_excluded_courses(list(self.excluded_courses))
            self.exam_program.set_exam_conflict(self.exam_conflict)

            if self.saved_start_date and self.saved_end_date:
                self.exam_program.set_tarih_araligi(
                    self.saved_start_date.toString(Qt.ISODate),
                    self.saved_end_date.toString(Qt.ISODate)
                )

            haris_gunler = []
            if self.saved_cumartesi:
                haris_gunler.append("Cumartesi")
            if self.saved_pazar:
                haris_gunler.append("Pazar")
            self.exam_program.set_haris_gunler(haris_gunler)

            self.exam_program.set_sinav_turu(self.saved_sinav_turu)

            self.exam_program.set_varsayilan_sure(self.saved_varsayilan_sure)

            if self.saved_istisna_ders:
                for ders, sure in self.saved_istisna_ders.items():
                    self.exam_program.set_istisna_ders(ders, sure)

            self.exam_program.set_start_end_time(self.start_time_value, self.end_time_value)

            self.exam_program.set_bekleme_suresi(self.saved_bekleme)

            self.get_class_and_student_worker = GetClasses("classes_with_years", self.user_info, department=self.selected_department)
            self.get_class_and_student_worker.finished.connect(self.handle_classes_and_students)
            self.get_class_and_student_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"❌ Program oluşturulurken hata oluştu:\n{str(e)}")


    def handle_classes_and_students(self, response):
            try:
                if response.get("status") != "success":
                    QMessageBox.critical(
                        self, "Hata",
                        f"❌ Sınıf ve öğrenci bilgileri alınamadı:\n{response.get('detail', 'Bilinmeyen hata')}"
                    )
                    return

                self.classes_and_their_students = response.get("classes", {})

                self.get_classroom_worker = ClassroomRequests("exam_classrooms", {'department': self.selected_department}, self.user_info)
                self.get_classroom_worker.finished.connect(self.handle_classroom_response)
                self.get_classroom_worker.start()

            finally:
                if hasattr(self, "get_class_and_student_worker"):
                    self.get_class_and_student_worker.quit()
                    self.get_class_and_student_worker.wait()

    def handle_classroom_response(self, response):
        try:
            if response.get("status") != "success":
                QMessageBox.warning(
                    self, "Uyarı",
                    f"⚠️ Sınıf bilgileri alınamadı:\n{response.get('detail', 'Bilinmeyen hata')}\n\n"
                    "Program varsayılan odalarla oluşturulacak."
                )
                raise Exception("Classroom verileri alınamadı")
            
            else:
                self.classrooms_data = response.get("classrooms", [])

            self.create_exam_program()

        finally:
            if hasattr(self, "get_classroom_worker"):
                self.get_classroom_worker.quit()
                self.get_classroom_worker.wait()
    
    def make_json_safe(self, data):
        if isinstance(data, dict):
            new_dict = {}
            for k, v in data.items():
                if isinstance(k, tuple):
                    k = f"{k[0]},{k[1]}"
                new_dict[str(k)] = self.make_json_safe(v)
            return new_dict
        elif isinstance(data, list):
            return [self.make_json_safe(i) for i in data]
        elif isinstance(data, (datetime,)):
            return data.isoformat()
        else:
            return data
    
        
    def create_exam_program(self):
        try:
            if not self.exam_program:
                raise ValueError("ExamProgram nesnesi oluşturulmamış")
            if not self.classes_and_their_students:
                raise ValueError("Sınıf ve öğrenci verileri alınamadı")
            if not self.classrooms_data:
                raise ValueError("Classroom verileri alınamadı")
            
            self.results = create_exam_schedule(
                exam_program=self.exam_program,
                class_dict=self.classes_and_their_students,
                classrooms=self.classrooms_data,
            )
            stats = self.results.get("statistics", {})
            failed_classes = stats.get("failed_classes", 0)
            QMessageBox.information(
                self, "Başarılı",
                f"✅ Sınav programı başarıyla oluşturuldu!\n\n"
                f"📚 Toplam ders: {stats.get('total_classes')}\n"
                f"✓ Yerleştirilen: {stats.get('successful_classes')}\n"
                f"✗ Yerleştirilemeyen: {stats.get('failed_classes')}\n"
                f"Yerleştirilmeyen ders adları: {', '.join(failed_classes) if (failed_classes) > 0 else 'Yok'}"
            )
            exam_schedule = self.make_json_safe(self.results['exam_schedule'])
            

            self.insert_exam_schedule_worker = InsertExamScheduleWorker("insert_exam_schedule_to_db", exam_schedule, self.user_info)
            self.insert_exam_schedule_worker.finished.connect(self.handle_insert_exam_schedule)
            self.active_threads.append(self.insert_exam_schedule_worker)  
            self.insert_exam_schedule_worker.start()
            
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"❌ Beklenmeyen hata:\n{str(e)}")

                
    def handle_insert_exam_schedule(self, response):
        try:
            if response.get("status") != "success":
                QMessageBox.warning(
                    self, "Uyarı",
                    f"⚠️ Exam schedule DB ye eklenemedi:\n{response.get('message', 'Bilinmeyen hata')}\n\n")
                raise Exception("Exam schedule DB ye eklenemedi")
          
            self.program_created.emit(self.results)  
            
        finally:
            if hasattr(self, "insert_exam_schedule_worker"):
                self.insert_exam_schedule_worker.quit()
                self.insert_exam_schedule_worker.wait()
                if self.insert_exam_schedule_worker in self.active_threads:
                    self.active_threads.remove(self.insert_exam_schedule_worker)
