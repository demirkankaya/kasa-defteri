import sys, sqlite3, os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, 
                             QStackedWidget, QGridLayout)
from PyQt6.QtCore import Qt
from datetime import datetime

# Kendi dosyalarımızdan sınıfları çağırıyoruz
from style import STIL_QUANTUM
from musteriler import MusteriListesi
from musteri_ekle import MusteriEkleEkrani
from auth import LoginEkrani 
from kasa import KasaDefteriEkrani 

class DemirCRM(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DEMİR CRM v4.0")
        self.showMaximized()
        self.setStyleSheet(STIL_QUANTUM)
        self.init_ui()

    def init_ui(self):
        merkezi = QWidget()
        self.setCentralWidget(merkezi)
        layout = QHBoxLayout(merkezi)
        layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

        # --- YAN MENÜ ---
        self.sidebar = QFrame(); self.sidebar.setObjectName("Sidebar"); self.sidebar.setFixedWidth(280)
        side_lay = QVBoxLayout(self.sidebar); side_lay.setContentsMargins(0, 40, 0, 40)
        
        logo = QLabel("DEMİR CRM"); logo.setStyleSheet("color: white; font-weight: 900; padding: 30px; border:none; letter-spacing: 4px; font-size: 20px;")
        side_lay.addWidget(logo)

        self.btn_grup = []
        menus = [("ANA SAYFA", 0), ("MÜŞTERİLER", 1), ("YENİ KAYIT", 2), ("KASA DEFTERİ", 3)]
        for text, idx in menus:
            btn = QPushButton(text); btn.setObjectName("MenuBtn"); btn.setCheckable(True); btn.setAutoExclusive(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.sayfa_degistir(i))
            side_lay.addWidget(btn); self.btn_grup.append(btn)
        
        self.btn_grup[0].setChecked(True); side_lay.addStretch()
        layout.addWidget(self.sidebar)

        # --- İÇERİK ALANI ---
        self.content = QStackedWidget(); self.content.setObjectName("ContentArea")
        
        self.sayfa_dash = QWidget(); self.setup_dash_layout(self.sayfa_dash)
        self.sayfa_liste = MusteriListesi()
        self.sayfa_ekle = MusteriEkleEkrani()
        self.sayfa_kasa = KasaDefteriEkrani()

        self.sayfa_liste.detay_sinyali.connect(self.detay_sayfasini_ac)

        self.content.addWidget(self.sayfa_dash)   # Index 0
        self.content.addWidget(self.sayfa_liste)  # Index 1
        self.content.addWidget(self.sayfa_ekle)   # Index 2
        self.content.addWidget(self.sayfa_kasa)   # Index 3
        
        layout.addWidget(self.content)
        self.kartlari_guncelle()

    def setup_dash_layout(self, w):
        w.setStyleSheet("background-color: #121212; border:none;")
        lay = QVBoxLayout(w); lay.setContentsMargins(60, 60, 60, 60)
        t = QLabel("SİSTEM ANALİZİ"); t.setStyleSheet("color: #00F2FF; font-weight: 900; letter-spacing: 2px;")
        lay.addWidget(t); lay.addSpacing(30)
        self.dash_grid = QGridLayout(); self.dash_grid.setSpacing(25)
        lay.addLayout(self.dash_grid); lay.addStretch()

    def kartlari_guncelle(self):
        """Dashboard üzerindeki sayaçları yeniler."""
        while self.dash_grid.count():
            item = self.dash_grid.takeAt(0); w = item.widget()
            if w: w.deleteLater()
            
        try:
            conn = sqlite3.connect("data/musteri_takip.db")
            cursor = conn.cursor()
            
            m_sayi = cursor.execute("SELECT COUNT(*) FROM musteriler").fetchone()[0]
            
            bugun = datetime.now().strftime("%d.%m.%Y")
            gunluk = cursor.execute("SELECT SUM(toplam_tutar) FROM satislar WHERE tarih LIKE ?", (f"{bugun}%",)).fetchone()[0]
            gunluk = gunluk if gunluk else 0.0
            
            bu_ay = datetime.now().strftime(".%m.%Y")
            aylik = cursor.execute("SELECT SUM(toplam_tutar) FROM satislar WHERE tarih LIKE ?", (f"%{bu_ay}%",)).fetchone()[0]
            aylik = aylik if aylik else 0.0
            
            conn.close()
        except: m_sayi, gunluk, aylik = 0, 0.0, 0.0
        
        k1 = self.create_stat_card("TOPLAM MÜŞTERİ", str(m_sayi))
        k2 = self.create_stat_card("GÜNLÜK CİRO", f"₺{gunluk:,.2f}")
        k3 = self.create_stat_card("AYLIK TOPLAM CİRO", f"₺{aylik:,.2f}")
        
        self.dash_grid.addWidget(k1, 0, 0)
        self.dash_grid.addWidget(k2, 0, 1)
        self.dash_grid.addWidget(k3, 0, 2)

    def create_stat_card(self, title, value):
        k = QFrame(); k.setObjectName("Kart"); k.setFixedHeight(180); k.setMinimumWidth(260)
        kl = QVBoxLayout(k); kl.setContentsMargins(30,30,30,30)
        t_color = "#00F2FF" if "AYLIK" in title else "#555"
        l1 = QLabel(title); l1.setStyleSheet(f"color:{t_color}; font-size:11px; font-weight:bold; border:none; letter-spacing:1px;")
        l2 = QLabel(value); l2.setStyleSheet("color:white; font-size:32px; font-weight:200; border:none;")
        kl.addWidget(l1); kl.addWidget(l2); kl.addStretch()
        return k

    def detay_sayfasini_ac(self, m_id):
        from kart import MusteriKartiEkrani
        if self.content.count() > 4:
            self.content.removeWidget(self.content.widget(4))
        detay = MusteriKartiEkrani(m_id, ana_pencere=self)
        self.content.addWidget(detay)
        self.content.setCurrentIndex(4)

    def sayfa_degistir(self, index):
        self.content.setCurrentIndex(index)
        if index == 0: self.kartlari_guncelle()
        elif index == 1: self.sayfa_liste.verileri_yukle()
        elif index == 3: self.sayfa_kasa.verileri_yukle()

class SistemYoneticisi:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login = LoginEkrani()
        self.login.giris_basarili.connect(self.baslat)
        self.login.show()
        sys.exit(self.app.exec())

    def baslat(self):
        self.login.close(); self.m = DemirCRM(); self.m.show()

if __name__ == "__main__":
    # Kodun veritabanına doğrudan müdahale etmesini engellemek için sadece klasör kontrolü yapıyoruz.
    # Tasarladığın 'musteri_takip.db' dosyasının bu klasör içinde olduğundan emin ol.
    if not os.path.exists("data"):
        os.makedirs("data")
        
    SistemYoneticisi()