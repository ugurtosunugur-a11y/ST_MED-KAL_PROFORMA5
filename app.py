import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
import io

st.set_page_config(page_title="ST Medikal Otomasyon", layout="centered")

# --- GİRİŞ KONTROLÜ ---
if "giris" not in st.session_state: st.session_state["giris"] = False
if not st.session_state["giris"]:
    sifre = st.text_input("Şifre:", type="password")
    if st.button("Giriş"):
        if sifre == "ST2025": # Şifre
            st.session_state["giris"] = True
            st.rerun()
    st.stop()

st.title("Proforma Oluşturucu")
st.info("Sistem 'sablon.docx' dosyasındaki değişkenleri doldurur.")

# --- 1. SOL/SAĞ MENÜ BİLGİLERİ ---
col1, col2 = st.columns(2)
with col1:
    k_adi = st.text_input("Kurum Adı")
    k_adres = st.text_input("Adres")
    k_ulke = st.text_input("Ülke", value="TÜRKİYE")
    k_tel = st.text_input("Telefon")
    
with col2:
    tarih = st.date_input("Tarih", datetime.now())
    para = st.selectbox("Para Birimi", ["EURO", "USD", "TRY", "GBP"])
    
    # Notlar kısmındaki değişkenler
    gecerlilik = st.number_input("Geçerlilik Süresi (Gün)", value=15)
    kdv_oran = st.number_input("KDV Oranı (%)", value=20)
    vade = st.text_input("Ödeme Vadesi", value="PEŞİN")

st.markdown("---")

# --- 2. ÜRÜN GİRİŞ TABLOSU ---
if "urunler" not in st.session_state:
    st.session_state.urunler = [{"adet": 1, "tanim": "", "fiyat": 0.0}]

def satir_ekle(): st.session_state.urunler.append({"adet": 1, "tanim": "", "fiyat": 0.0})
def satir_sil(): 
    if len(st.session_state.urunler) > 1: st.session_state.urunler.pop()

c1, c2 = st.columns([1,1])
c1.button("➕ Satır Ekle", on_click=satir_ekle)
c2.button("➖ Satır Sil", on_click=satir_sil)

# Para birimi simgesi belirleme (Görsel güzellik için)
simge = "€" if para == "EURO" else "$" if para == "USD" else "₺" if para == "TRY" else para

toplam_tutar = 0
word_tablo_listesi = []

for i, urun in enumerate(st.session_state.urunler):
    c_a, c_b, c_c = st.columns([1, 3, 2])
    adet = c_a.number_input(f"Adet", min_value=1, key=f"a{i}")
    tanim = c_b.text_input(f"Tanım", value=urun["tanim"], key=f"t{i}")
    fiyat = c_c.number_input(f"Fiyat", value=urun["fiyat"], key=f"f{i}")
    
    satir_toplam = adet * fiyat
    toplam_tutar += satir_toplam
    
    # Word'e gidecek veriyi hazırla
    word_tablo_listesi.append({
        'adet': adet,
        'tanim': tanim,
        'fiyat': f"{fiyat:,.2f} {simge}",
        'toplam': f"{satir_toplam:,.2f} {simge}"
    })
    
    # Ekran yenilenince veriler kaybolmasın
    urun["adet"] = adet
    urun["tanim"] = tanim
    urun["fiyat"] = fiyat

# --- 3. HESAPLAMALAR ---
kdv_tutar = toplam_tutar * (kdv_oran / 100)
genel_toplam = toplam_tutar + kdv_tutar

# --- 4. WORD OLUŞTURMA ---
st.markdown("---")
if st.button("Dökümanı Oluştur"):
    try:
        doc = DocxTemplate("sablon.docx")
        
        # Word içindeki {{...}} yerlerine gidecek veriler
        context = {
            'kurum_adi': k_adi,
            'adres': k_adres,
            'ulke': k_ulke,
            'telefon': k_tel,
            'tarih': tarih.strftime('%d.%m.%Y'),
            
            # Tablo verisi
            'urunler': word_tablo_listesi,
            
            # Hesaplamalar
            'ara_toplam': f"{toplam_tutar:,.2f} {simge}",
            'kdv_orani': kdv_oran,
            'kdv_tutari': f"{kdv_tutar:,.2f} {simge}",
            'genel_toplam': f"{genel_toplam:,.2f} {simge}",
            
            # Notlar kısmı
            'gecerlilik_gun': gecerlilik,
            'para_birimi': para,
            'vade': vade
        }
        
        doc.render(context)
        
        # İndirme işlemi
        bio = io.BytesIO()
        doc.save(bio)
        
        st.success("Dosya Hazırlandı!")
        dosya_adi = f"Proforma_{k_adi}_{datetime.now().strftime('%Y%m%d')}.docx"
        
        st.download_button(
            label="⬇️ Word Dosyasını İndir",
            data=bio.getvalue(),
            file_name=dosya_adi,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error(f"Hata: 'sablon.docx' dosyası bulunamadı veya içindeki kodlarda hata var.\nDetay: {e}")