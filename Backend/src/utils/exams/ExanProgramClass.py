class ExamProgram:
    def __init__(self):
        self.dersler = []
        self.excluded_courses = []
        self.tarih_baslangic = None
        self.tarih_bitis = None
        self.haris_gunler = []
        self.sinav_turu = None
        self.varsayilan_sure = 75
        self.istisna_dersler = {}  
        self.bekleme_suresi = 15
        self.exam_conflict = False
        self.start_time = 9.0
        self.end_time = 17.0
        
    def get_exam_type(self):
        return self.sinav_turu

    def get_start_time(self):
        return self.start_time
    
    def get_end_time(self):
        return self.end_time
        
    def get_first_date_of_exam(self):
        return self.tarih_baslangic
        
    def get_last_date_of_exam(self):
        return self.tarih_bitis
    
    def get_exception_classes(self):
        return self.istisna_dersler
    
    def get_default_duration(self):
        return self.varsayilan_sure
    
    def set_exam_conflict(self, conflict: bool):
        self.exam_conflict = conflict
    
    def get_exam_conflict(self):
        return self.exam_conflict
    
    def set_dersler(self, dersler):
        self.dersler = dersler
    
    def set_excluded_courses(self, excluded_courses):
        self.excluded_courses = excluded_courses
    
    def get_kalan_dersler(self):
        return [d for d in self.dersler if d not in self.excluded_courses]
    
    def set_tarih_araligi(self, baslangic, bitis):
        self.tarih_baslangic = baslangic
        self.tarih_bitis = bitis
    
    def set_haris_gunler(self, gunler):
        self.haris_gunler = gunler
    
    def set_sinav_turu(self, tur):
        self.sinav_turu = tur
    
    def set_varsayilan_sure(self, sure):
        self.varsayilan_sure = sure
    
    def set_istisna_ders(self, ders_adi, sure):
        if ders_adi:
            self.istisna_dersler[ders_adi] = sure
    
    def set_bekleme_suresi(self, sure):
        self.bekleme_suresi = sure
        
    def get_bekleme_suresi(self):
        return self.bekleme_suresi
    
    def get_ders_suresi(self, ders_adi):
        return self.istisna_dersler.get(ders_adi, self.varsayilan_sure)
    
    def to_dict(self):
        return {
            "kalan_dersler": self.get_kalan_dersler(),
            "tarih_baslangic": self.tarih_baslangic,
            "tarih_bitis": self.tarih_bitis,
            "haris_gunler": self.haris_gunler,
            "sinav_turu": self.sinav_turu,
            "varsayilan_sure": self.varsayilan_sure,
            "istisna_dersler": self.istisna_dersler,
            "bekleme_suresi": self.bekleme_suresi
        }