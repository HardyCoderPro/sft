import requests
from datetime import datetime

API_BASE_URL = "https://api.ondex.uk/ondexapi"

def make_api_request(endpoint, params, user_id):
    # Parametreleri kontrol et
    if not params:
        return {"error": "Parametreler eksik"}
    
    # API isteği yap
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API hatası: {response.status_code}"}
    except Exception as e:
        return {"error": f"Bağlantı hatası: {str(e)}"}

# Tüm API fonksiyonları
def tc_sorgu(tc, user_id):
    return make_api_request("tcsorgu.php", {"tc": tc}, user_id)

def tc_pro_sorgu(tc, user_id):
    return make_api_request("tcprosorgu.php", {"tc": tc}, user_id)

def adres_sorgu(tc, user_id):
    return make_api_request("adressorgu.php", {"tc": tc}, user_id)

def hane_sorgu(tc, user_id):
    return make_api_request("hanesorgu.php", {"tc": tc}, user_id)

def ad_soyad_sorgu(ad, soyad, il=None, ilce=None, user_id=None):
    params = {"ad": ad, "soyad": soyad}
    if il: params["il"] = il
    if ilce: params["ilce"] = ilce
    return make_api_request("adsoyadsorgu.php", params, user_id)

def ad_soyad_pro_sorgu(ad, soyad, il=None, ilce=None, user_id=None):
    params = {"ad": ad, "soyad": soyad}
    if il: params["il"] = il
    if ilce: params["ilce"] = ilce
    return make_api_request("adsoyadprosorgu.php", params, user_id)

def aile_sorgu(tc, user_id):
    return make_api_request("ailesorgu.php", {"tc": tc}, user_id)

def aile_pro_sorgu(tc, user_id):
    return make_api_request("aileprosorgu.php", {"tc": tc}, user_id)

def gsm_tc_sorgu(gsm, user_id):
    return make_api_request("gsmtcsorgu.php", {"gsm": gsm}, user_id)

def gsm_tc_pro_sorgu(gsm, user_id):
    return make_api_request("gsmtcprosorgu.php", {"gsm": gsm}, user_id)

def tc_gsm_sorgu(tc, user_id):
    return make_api_request("tcgsmsorgu.php", {"tc": tc}, user_id)

def tc_gsm_pro_sorgu(tc, user_id):
    return make_api_request("tcgsmprosorgu.php", {"tc": tc}, user_id)

def sulale_sorgu(tc, user_id):
    return make_api_request("sulalesorgu.php", {"tc": tc}, user_id)

def sulale_pro_sorgu(tc, user_id):
    return make_api_request("sulaleprosorgu.php", {"tc": tc}, user_id)

def hayat_hikayesi_sorgu(tc, user_id):
    return make_api_request("hayathikayesisorgu.php", {"tc": tc}, user_id)

def isyeri_sorgu(tc, user_id):
    return make_api_request("isyerisorgu.php", {"tc": tc}, user_id)

def isyeri_arkadasi_sorgu(tc, user_id):
    return make_api_request("isyeriarkadasisorgu.php", {"tc": tc}, user_id)

def isyeri_yetkili_sorgu(tc, user_id):
    return make_api_request("isyeriyetkilisorgu.php", {"tc": tc}, user_id)

def operator_sorgu(gsm, user_id):
    return make_api_request("operator.php", {"gsm": gsm}, user_id)

# API fonksiyonlarını eşleme
API_FUNCTIONS = {
    "TC Sorgu": tc_sorgu,
    "TC Pro Sorgu": tc_pro_sorgu,
    "Adres Sorgu": adres_sorgu,
    "Hane Sorgu": hane_sorgu,
    "Ad Soyad Sorgu": ad_soyad_sorgu,
    "Ad Soyad Pro Sorgu": ad_soyad_pro_sorgu,
    "Aile Sorgu": aile_sorgu,
    "Aile Pro Sorgu": aile_pro_sorgu,
    "GSM TC Sorgu": gsm_tc_sorgu,
    "GSM TC Pro Sorgu": gsm_tc_pro_sorgu,
    "TC GSM Sorgu": tc_gsm_sorgu,
    "TC GSM Pro Sorgu": tc_gsm_pro_sorgu,
    "Sülale Sorgu": sulale_sorgu,
    "Sülale Pro Sorgu": sulale_pro_sorgu,
    "Hayat Hikayesi Sorgu": hayat_hikayesi_sorgu,
    "İşyeri Sorgu": isyeri_sorgu,
    "İşyeri Arkadaşı Sorgu": isyeri_arkadasi_sorgu,
    "İşyeri Yetkili Sorgu": isyeri_yetkili_sorgu,
    "Operatör Sorgu": operator_sorgu
}