import requests

class DersSecimi:
    def __init__(self, api_base_url, token):
        
        self.api_base_url = api_base_url
        self.token = token
        self.dersler = self._fetch_courses_from_api()

    def _fetch_courses_from_api(self):
       
        endpoint = f"{self.api_base_url}/all_courses"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            response = requests.post(endpoint, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return [d["class_name"] for d in data["courses"]]
                else:
                    print("⚠️ API hata mesajı:", data.get("message"))
            else:
                print(f"⚠️ HTTP Hatası: {response.status_code}")
        except Exception as e:
            print("❌ API bağlantı hatası:", str(e))

        
        return []

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
