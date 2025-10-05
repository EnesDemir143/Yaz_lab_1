# main.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, QCheckBox,
    QDateEdit, QComboBox, QSpinBox, QLineEdit
)
from PyQt5.QtCore import QDate, Qt
from Backend.src.utils.exams.algoritmalar import DersSecimi, SinavTarihleri, SinavTuru, SinavSuresi, BeklemeSuresi


# ---------- 1. DERS SEÇİMİ SAYFASI ----------
class DersSecimiPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("1. Ders Seçimi")
        self.layout = QVBoxLayout()

        self.dersler = [
            "Bilgisayar Mühendisliğine Giriş",
            "Algoritmalar ve Programlama",
            "Veri Yapıları",
            "İşletim Sistemleri",
            "Veri Tabanı Yönetimi"
        ]
        self.checkboxes = []

        title_label = QLabel("Programa dahil olmayacak dersleri işaretleyiniz:")
        title_label.setObjectName("sectionTitle")
        self.layout.addWidget(title_label)

        for ders in self.dersler:
            cb = QCheckBox(ders)
            cb.setCursor(Qt.PointingHandCursor)
            self.layout.addWidget(cb)
            self.checkboxes.append(cb)

        self.setLayout(self.layout)

    def get_kalan_dersler(self):
        cikarilacaklar = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        secim = DersSecimi(self.dersler)
        return secim.filtrele(cikarilacaklar)


# ---------- 2. SINAV TARİHLERİ SAYFASI ----------
class SinavTarihleriPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("2. Sınav Tarihleri ve Günleri")
        self.layout = QVBoxLayout()

        lbl1 = QLabel("Sınav tarih aralığını seçiniz:")
        lbl1.setObjectName("sectionTitle")
        self.layout.addWidget(lbl1)

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addDays(10))
        self.end_date.setCalendarPopup(True)

        self.layout.addWidget(QLabel("Başlangıç tarihi:"))
        self.layout.addWidget(self.start_date)
        self.layout.addWidget(QLabel("Bitiş tarihi:"))
        self.layout.addWidget(self.end_date)

        lbl2 = QLabel("Hariç tutulacak günleri seçiniz:")
        lbl2.setObjectName("sectionTitle")
        self.layout.addWidget(lbl2)

        self.check_cumartesi = QCheckBox("Cumartesi")
        self.check_pazar = QCheckBox("Pazar")
        for cb in [self.check_cumartesi, self.check_pazar]:
            cb.setCursor(Qt.PointingHandCursor)
            self.layout.addWidget(cb)

        self.setLayout(self.layout)

    def get_tarih_bilgisi(self):
        tarih = SinavTarihleri()
        tarih.set_tarih_araligi(self.start_date.date().toString(Qt.ISODate),
                                self.end_date.date().toString(Qt.ISODate))
        haris_gunler = []
        if self.check_cumartesi.isChecked():
            haris_gunler.append("Cumartesi")
        if self.check_pazar.isChecked():
            haris_gunler.append("Pazar")
        tarih.set_haris_gunler(haris_gunler)
        return tarih


# ---------- 3. SINAV TÜRÜ SAYFASI ----------
class SinavTuruPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("3. Sınav Türü")
        self.layout = QVBoxLayout()

        lbl = QLabel("Sınav türünü seçiniz:")
        lbl.setObjectName("sectionTitle")
        self.layout.addWidget(lbl)

        self.combo = QComboBox()
        self.combo.addItems(["Vize", "Final", "Bütünleme"])
        self.combo.setCursor(Qt.PointingHandCursor)
        self.layout.addWidget(self.combo)

        self.setLayout(self.layout)

    def get_tur(self):
        tur = SinavTuru()
        tur.set_tur(self.combo.currentText())
        return tur


# ---------- 4. SINAV SÜRESİ SAYFASI ----------
class SinavSuresiPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("4. Sınav Süresi (Varsayılan & İstisna)")
        self.layout = QVBoxLayout()

        lbl = QLabel("Varsayılan sınav süresi (dk):")
        lbl.setObjectName("sectionTitle")
        self.layout.addWidget(lbl)

        self.spin_default = QSpinBox()
        self.spin_default.setRange(30, 180)
        self.spin_default.setValue(75)
        self.layout.addWidget(self.spin_default)

        lbl2 = QLabel("İstisna ders adı:")
        lbl2.setObjectName("sectionTitle")
        self.layout.addWidget(lbl2)

        self.input_ders = QLineEdit()
        self.layout.addWidget(self.input_ders)

        lbl3 = QLabel("İstisna sınav süresi (dk):")
        lbl3.setObjectName("sectionTitle")
        self.layout.addWidget(lbl3)

        self.spin_istisna = QSpinBox()
        self.spin_istisna.setRange(30, 180)
        self.layout.addWidget(self.spin_istisna)

        self.setLayout(self.layout)

    def get_sure(self):
        sure = SinavSuresi()
        sure.set_varsayilan(self.spin_default.value())
        if self.input_ders.text():
            sure.set_istisna(self.input_ders.text(), self.spin_istisna.value())
        return sure


# ---------- 5. BEKLEME SÜRESİ SAYFASI ----------
class BeklemeSuresiPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("5. Bekleme Süresi")
        self.layout = QVBoxLayout()

        lbl = QLabel("Varsayılan bekleme süresi (dk):")
        lbl.setObjectName("sectionTitle")
        self.layout.addWidget(lbl)

        self.spin = QSpinBox()
        self.spin.setRange(5, 60)
        self.spin.setValue(15)
        self.layout.addWidget(self.spin)

        self.setLayout(self.layout)

    def get_bekleme(self):
        bekleme = BeklemeSuresi()
        bekleme.set_sure(self.spin.value())
        return bekleme


# ---------- ANA WIZARD ----------
class SinavWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 Sınav Planlama Sihirbazı")
        self.resize(900, 600)  # ekranı büyüttük

        self.page1 = DersSecimiPage()
        self.page2 = SinavTarihleriPage()
        self.page3 = SinavTuruPage()
        self.page4 = SinavSuresiPage()
        self.page5 = BeklemeSuresiPage()

        self.addPage(self.page1)
        self.addPage(self.page2)
        self.addPage(self.page3)
        self.addPage(self.page4)
        self.addPage(self.page5)

        self.setStyleSheet(self.load_dark_style())

    def load_dark_style(self):
        return """
        QWizard {
            background-color: #121212;
            color: #EAEAEA;
            font-family: 'Segoe UI';
            font-size: 13px;
        }

        QWizardPage {
            background-color: #121212;
        }

        QLabel {
            color: #EAEAEA;
            font-size: 12px;
        }

        QLabel#sectionTitle {
            color: #4FC3F7;
            font-weight: bold;
            margin-top: 10px;
            font-size: 13px;
        }

        QLineEdit, QSpinBox, QComboBox, QDateEdit {
            background-color: #1E1E1E;
            color: #FFFFFF;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 4px;
        }

        QCheckBox {
            color: #EAEAEA;
        }

        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #4FC3F7;
            background: transparent;
        }

        QCheckBox::indicator:checked {
            background-color: #4FC3F7;
        }

        QWizard QPushButton {
            background-color: #4FC3F7;
            color: white;
            border-radius: 8px;
            padding: 8px 14px;
        }

        QWizard QPushButton:hover {
            background-color: #039BE5;
        }
        """

    def accept(self):
        # Butona basıldığında seçimleri yazdır
        print("---- SONUÇLAR ----")
        print("Kalan Dersler:", self.page1.get_kalan_dersler())
        print("Tarih Bilgisi:", self.page2.get_tarih_bilgisi())
        print("Sınav Türü:", self.page3.get_tur())
        print("Sınav Süresi:", self.page4.get_sure())
        print("Bekleme Süresi:", self.page5.get_bekleme())
        super().accept()


# ---------- UYGULAMA ÇALIŞTIRMA ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = SinavWizard()
    wizard.show()
    sys.exit(app.exec_())
