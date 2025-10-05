class DersSecimi:
    def __init__(self, dersler):
        self.dersler = dersler

    def filtrele(self, cikarilacaklar):
        return [d for d in self.dersler if d not in cikarilacaklar]

    def __str__(self):
        return f"Dersler: {self.dersler}"


class SinavTarihleri:
    def __init__(self):
        self.baslangic = None
        self.bitis = None
        self.haris_gunler = []

    def set_tarih_araligi(self, bas, bit):
        self.baslangic = bas
        self.bitis = bit

    def set_haris_gunler(self, gunler):
        self.haris_gunler = gunler

    def __str__(self):
        return f"Tarih Aralığı: {self.baslangic} - {self.bitis}, Hariç Günler: {self.haris_gunler}"


class SinavTuru:
    def __init__(self):
        self.tur = None

    def set_tur(self, tur):
        self.tur = tur

    def __str__(self):
        return f"Sınav Türü: {self.tur}"


class SinavSuresi:
    def __init__(self):
        self.varsayilan = 75
        self.istisnalar = {}

    def set_varsayilan(self, sure):
        self.varsayilan = sure

    def set_istisna(self, ders, sure):
        self.istisnalar[ders] = sure

    def __str__(self):
        return f"Varsayılan: {self.varsayilan} dk, İstisnalar: {self.istisnalar}"


class BeklemeSuresi:
    def __init__(self):
        self.sure = 15

    def set_sure(self, sure):
        self.sure = sure

    def __str__(self):
        return f"Bekleme Süresi: {self.sure} dk"
