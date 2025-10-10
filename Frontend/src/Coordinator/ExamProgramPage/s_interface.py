from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QDateEdit, QComboBox, QSpinBox, QPushButton,
    QScrollArea, QFrame, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from Frontend.src.Coordinator.ExamProgramPage.exam_program_worker import GetClasses
from Backend.src.utils.exams.ExanProgramClass import ExamProgram
from Backend.src.utils.exams.create_exam_program import create_exam_schedule
from Frontend.src.Coordinator.Classroom.classroomReqs import ClassroomRequests


class ExamProgramPage(QWidget):
    program_created = pyqtSignal(dict)

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent)
        self.user_info = user_info
        self.dersler = []
        self.excluded_courses = set() 
        self.current_step = 1
        
        self.saved_start_date = None
        self.saved_end_date = None
        self.saved_cumartesi = False
        self.saved_pazar = False
        self.saved_sinav_turu = "Vize"
        self.saved_varsayilan_sure = 75
        self.saved_istisna_ders = None
        self.saved_istisna_sure = 60
        self.saved_bekleme = 15
        self.exam_conflict = True 
        
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

        self.progress_label = QLabel("Adım 1/6: Ders Seçimi")
        self.progress_label.setFont(QFont("Arial", 11))
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #4CAF50; padding: 10px;")
        main_layout.addWidget(self.progress_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

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

        self.back_btn.clicked.connect(self.go_back)
        self.next_btn.clicked.connect(self.go_next)
        self.finish_btn.clicked.connect(self.finish_program)

        button_layout.addWidget(self.back_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.next_btn)
        button_layout.addWidget(self.finish_btn)
        main_layout.addLayout(button_layout)

        # İlk adım
        self.load_step_1()
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
        self.back_btn.setVisible(self.current_step > 1)
        self.next_btn.setVisible(self.current_step < 6)
        self.finish_btn.setVisible(self.current_step == 6)

    def update_progress(self):
        steps = {
            1: "Adım 1/6: Ders Seçimi",
            2: "Adım 2/6: Sınav Tarihleri",
            3: "Adım 3/6: Sınav Türü",
            4: "Adım 4/6: Sınav Süresi",
            5: "Adım 5/6: Bekleme Süresi",
            6: "Adım 6/6: Çakışma Kontrolü"
        }
        self.progress_label.setText(steps.get(self.current_step, ""))

    def go_next(self):
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
                if hasattr(self, 'combo_istisna_ders') and self.combo_istisna_ders:
                    self.saved_istisna_ders = self.combo_istisna_ders.currentData()
                if hasattr(self, 'spin_istisna') and self.spin_istisna:
                    self.saved_istisna_sure = self.spin_istisna.value()
            
            elif self.current_step == 5:
                if hasattr(self, 'spin_bekleme') and self.spin_bekleme:
                    self.saved_bekleme = self.spin_bekleme.value()
                    
            elif self.current_step == 6:
                if hasattr(self, 'check_conflict'):
                    self.exam_conflict = not self.check_conflict.isChecked()
                    
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"❌ Veriler kaydedilirken hata oluştu:\n{str(e)}")


    def go_back(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.load_current_step()
            self.update_buttons()
            self.update_progress()

    def load_current_step(self):
        self.clear_content()
        QApplication.processEvents() 
        
        steps = {
            1: self.load_step_1,
            2: self.load_step_2,
            3: self.load_step_3,
            4: self.load_step_4,
            5: self.load_step_5,
            6: self.load_step_6
        }
        steps[self.current_step]()

    # -------------------------- ADIM 1 --------------------------

    def load_step_1(self):
        self.clear_content()
        title = QLabel("Programa dahil olmayacak dersleri işaretleyiniz:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        self.content_layout.addWidget(title)

        info = QLabel("İşaretlenen dersler sınav programına dahil edilmeyecektir.")
        info.setStyleSheet("color: #888; font-style: italic;")
        self.content_layout.addWidget(info)
        self.content_layout.addSpacing(10)

        if not self.dersler:
            loading_label = QLabel("📚 Dersler yükleniyor...")
            self.content_layout.addWidget(loading_label)
            self.get_classes_thread = GetClasses("just_classes", self.user_info)
            self.get_classes_thread.finished.connect(self.populate_classes)
            self.get_classes_thread.start()
        else:
            self.populate_classes({"classes": [(None, d) for d in self.dersler]})

        self.content_layout.addStretch()

    def populate_classes(self, classes):
        response = classes.get("classes", [])
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

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Başlangıç:"))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("Bitiş:"))
        date_layout.addWidget(self.end_date)
        date_layout.addStretch()
        self.content_layout.addLayout(date_layout)
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
        
        # Önceden seçili değeri geri yükle
        if self.saved_istisna_ders:
            index = self.combo_istisna_ders.findData(self.saved_istisna_ders)
            if index >= 0:
                self.combo_istisna_ders.setCurrentIndex(index)

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
            "Bu seçenek seçilirse, dersler aynı anda sınav olamaz."
        )
        self.check_conflict.setChecked(self.exam_conflict)
        self.check_conflict.setCursor(Qt.PointingHandCursor)
        self.check_conflict.setFont(QFont("Arial", 15))
        self.content_layout.addWidget(self.check_conflict)

        self.content_layout.addStretch()

    # -------------------------- TAMAMLAMA --------------------------
    def finish_program(self):
        try:
            # Son adımdaki verileri kaydet
            self.save_current_step_data()
            
            # ExamProgram objesi oluştur
            self.exam_program = ExamProgram()
            
            # Ders bilgilerini ayarla
            self.exam_program.set_dersler(self.dersler)
            self.exam_program.set_excluded_courses(list(self.excluded_courses))
            
            # Tarih bilgilerini kayıtlı değerlerden al
            if self.saved_start_date and self.saved_end_date:
                self.exam_program.set_tarih_araligi(
                    self.saved_start_date.toString(Qt.ISODate),
                    self.saved_end_date.toString(Qt.ISODate)
                )
            
            # Hariç günleri ayarla
            haris_gunler = []
            if self.saved_cumartesi:
                haris_gunler.append("Cumartesi")
            if self.saved_pazar:
                haris_gunler.append("Pazar")
            self.exam_program.set_haris_gunler(haris_gunler)
            
            # Sınav türünü ayarla
            self.exam_program.set_sinav_turu(self.saved_sinav_turu)
            
            # Sınav sürelerini ayarla
            self.exam_program.set_varsayilan_sure(self.saved_varsayilan_sure)
            if self.saved_istisna_ders:
                self.exam_program.set_istisna_ders(self.saved_istisna_ders, self.saved_istisna_sure)
            
            # Bekleme süresini ayarla
            self.exam_program.set_bekleme_suresi(self.saved_bekleme)
            
            # Önce sınıf ve öğrenci verilerini al
            get_class_and_student_worker = GetClasses("all_classes", self.user_info)
            get_class_and_student_worker.finished.connect(self.handle_classes_and_students)
            get_class_and_student_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"❌ Program oluşturulurken hata oluştu:\n{str(e)}")
            
    def handle_classes_and_students(self, response):
        """Sınıf ve öğrenci verilerini işler."""
        if response.get("status") != "success":
            QMessageBox.critical(
                self, "Hata", 
                f"❌ Sınıf ve öğrenci bilgileri alınamadı:\n{response.get('detail', 'Bilinmeyen hata')}"
            )
            return
        
        # Sınıf ve öğrenci verilerini sakla
        self.classes_and_their_students = response.get("classes", {})
        
        # Şimdi classroom verilerini al
        get_classroom_worker = ClassroomRequests("exam_classrooms", user_info=self.user_info)
        get_classroom_worker.finished.connect(self.handle_classroom_response)
        get_classroom_worker.start()
        
    def handle_classroom_response(self, response):
        """Classroom verilerini işler ve sınav programını oluşturur."""
        if response.get("status") != "success":
            QMessageBox.warning(
                self, "Uyarı", 
                f"⚠️ Sınıf bilgileri alınamadı:\n{response.get('detail', 'Bilinmeyen hata')}\n\n"
                "Program varsayılan odalarla oluşturulacak."
            )
            raise Exception("Classroom verileri alınamadı")
        else:
            classrooms_list = response.get("classrooms", [])
            self.classrooms_data = []
            
            for classroom in classrooms_list:
                self.classrooms_data.append({
                    'id': classroom.get('classroom_id', ''),
                    'name': classroom.get('classroom_name', ''),
                    'capacity': classroom.get('capacity', 0)
                })
        
        self.create_exam_program()
        
    def create_exam_program(self):
        """Tüm veriler toplandıktan sonra sınav programını oluşturur."""
        try:
            # Verilerin kontrolü
            if not self.exam_program:
                raise ValueError("ExamProgram nesnesi oluşturulmamış")
            if not self.classes_and_their_students:
                raise ValueError("Sınıf ve öğrenci verileri alınamadı")
            if not self.classrooms_data:
                raise ValueError("Classroom verileri alınamadı")
            
            # Sınav programını oluştur
            results = create_exam_schedule(
                exam_program=self.exam_program,
                class_dict=self.classes_and_their_students,
                rooms_data=self.classrooms_data,
                excel_output_path="sinav_programi.xlsx"
            )
            
            # Uyarıları göster
            warning_text = ""
            if results.get('warnings'):
                warning_text = "\n\n⚠️ Uyarılar:\n" + "\n".join(results['warnings'][:5])
                if len(results['warnings']) > 5:
                    warning_text += f"\n... ve {len(results['warnings']) - 5} uyarı daha"
            
            # Başarı mesajı
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ Sınav programı başarıyla oluşturuldu!\n\n"
                f"📚 Ders sayısı: {len(results.get('schedule', []))}\n"
                f"🏢 Kullanılan oda sayısı: {len(self.classrooms_data)}\n"
                f"📝 Sınav türü: {self.exam_program.sinav_turu}\n"
                f"⏱️ Varsayılan süre: {self.exam_program.varsayilan_sure} dk\n"
                f"⚠️ Uyarı sayısı: {len(results.get('warnings', []))}"
                f"{warning_text}"
            )
            
            # Debug bilgisi
            print("---- SINAV PROGRAMI SONUÇLARI ----")
            print("Kalan Dersler:", self.exam_program.get_kalan_dersler())
            print("Schedule:", results.get('schedule'))
            print("Excel Path:", results.get('excel'))
            
            # Sonuçları emit et
            self.program_created.emit(results)
            
        except Exception as e:
            QMessageBox.critical(
                self, "Hata", 
                f"❌ Program oluşturulurken hata oluştu:\n{str(e)}\n\n"
                f"Debug:\n"
                f"- ExamProgram: {'✓' if self.exam_program else '✗'}\n"
                f"- Classes: {'✓' if self.classes_and_their_students else '✗'}\n"
                f"- Classrooms: {'✓' if self.classrooms_data else '✗'}"
            )