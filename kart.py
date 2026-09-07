import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QPushButton, QLineEdit, QStackedWidget, QMessageBox, QMenu, QComboBox, QCalendarWidget, QSplitter)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

class MusteriKartiEkrani(QWidget):
    def __init__(self, m_id, ana_pencere=None):
        super().__init__()
        self.m_id = m_id
        self.ana_pencere = ana_pencere
        self.setStyleSheet("background-color: #121212; border: none;")
        
        self.tabloyu_hazirla()
        self.init_ui()
        self.yukle()

    def tabloyu_hazirla(self):
        pass

    def init_ui(self):
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(40, 40, 40, 40); self.lay.setSpacing(20)
        
        # --- ÜST BİLGİ PANELİ ---
        self.ust_panel = QFrame()
        self.ust_panel.setStyleSheet("background:#0D0D0D; border:1px solid #1F1F1F; border-radius:20px;")
        ul = QHBoxLayout(self.ust_panel)
        ul.setContentsMargins(25, 20, 25, 20)
        
        btn_geri = QPushButton("← GERİ")
        btn_geri.setFixedSize(80, 40)
        btn_geri.setStyleSheet("background:#1A1A1A; color:#888; font-weight:bold; border-radius:10px;")
        btn_geri.clicked.connect(self.geriye_don)
        ul.addWidget(btn_geri); ul.addSpacing(20)

        bilgi_lay = QVBoxLayout()
        self.name = QLabel("YÜKLENİYOR...")
        self.name.setStyleSheet("color:#00F2FF; font-size:22px; font-weight:900; border:none;")
        detay_lay = QHBoxLayout()
        self.lbl_tel = QLabel("📞 --"); self.lbl_tel.setStyleSheet("color:#555; font-size:12px; font-weight:bold; border:none;")
        self.lbl_adres = QLabel("📍 --"); self.lbl_adres.setStyleSheet("color:#555; font-size:12px; font-weight:bold; border:none; margin-left:15px;")
        detay_lay.addWidget(self.lbl_tel); detay_lay.addWidget(self.lbl_adres); detay_lay.addStretch()
        bilgi_lay.addWidget(self.name); bilgi_lay.addLayout(detay_lay)
        ul.addLayout(bilgi_lay); ul.addStretch()
        
        self.btn_yeni_satis = QPushButton("+ YENİ SATIŞ")
        self.btn_yeni_satis.setFixedSize(160, 50)
        self.btn_yeni_satis.setStyleSheet("background:#00F2FF; color:black; font-weight:900; border-radius:15px;")
        self.btn_yeni_satis.clicked.connect(lambda: self.sayfalar.setCurrentIndex(1))
        ul.addWidget(self.btn_yeni_satis)
        self.lay.addWidget(self.ust_panel)

        # --- SAYFALAR ---
        self.sayfalar = QStackedWidget()
        self.sayfalar.addWidget(self.setup_gecmis_view()) # Index 0
        self.sayfalar.addWidget(self.setup_satis_view())  # Index 1
        self.sayfalar.addWidget(self.setup_detay_view()) # Index 2
        self.lay.addWidget(self.sayfalar)

    def setup_gecmis_view(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0, 10, 0, 0)
        self.tablo_gecmis = QTableWidget(0, 5)
        self.tablo_gecmis.setHorizontalHeaderLabels(["ID", "İşlem Tarihi", "Satılan Ürünler", "İskonto", "Net Tutar"])
        self.tablo_gecmis.setColumnHidden(0, True)
        self.tablo_gecmis.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tablo_gecmis.verticalHeader().setVisible(False); self.tablo_gecmis.verticalHeader().setDefaultSectionSize(60)
        self.tablo_gecmis.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tablo_gecmis.customContextMenuRequested.connect(self.gecmis_menu_ac)
        self.tablo_gecmis.itemDoubleClicked.connect(self.gecmis_detay_goster)
        self.tablo_gecmis.setStyleSheet("QTableWidget { background:#0D0D0D; border:none; color:#BBB; } QHeaderView::section { background:#121212; color:#444; border:none; font-weight:900; } QTableWidget::item { border-bottom:1px solid #1A1A1A; padding-left:15px; }")
        lay.addWidget(self.tablo_gecmis)
        return w

    def setup_detay_view(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0, 10, 0, 0)
        ust_lay = QHBoxLayout()
        lbl = QLabel("SATIŞ DETAYLARI"); lbl.setStyleSheet("color:#00F2FF; font-weight:900; border:none;")
        btn_kapat = QPushButton("LİSTEYE DÖN"); btn_kapat.setFixedSize(120, 35)
        btn_kapat.setStyleSheet("background:#1A1A1A; color:#888; border-radius:8px; font-weight:bold;")
        btn_kapat.clicked.connect(lambda: self.sayfalar.setCurrentIndex(0))
        ust_lay.addWidget(lbl); ust_lay.addStretch(); ust_lay.addWidget(btn_kapat)
        lay.addLayout(ust_lay)

        self.detay_cerceve = QFrame(); self.detay_cerceve.setStyleSheet("background:#0D0D0D; border:1px solid #1F1F1F; border-radius:20px;")
        detay_lay = QVBoxLayout(self.detay_cerceve); detay_lay.setContentsMargins(40,40,40,40); detay_lay.setSpacing(15)
        self.lbl_detay_tarih = QLabel(); self.lbl_detay_tarih.setStyleSheet("color:#444; border:none;")
        self.lbl_detay_urunler = QLabel(); self.lbl_detay_urunler.setStyleSheet("color:white; font-size:18px; font-weight:bold; border:none;")
        self.lbl_detay_urunler.setWordWrap(True)
        self.lbl_detay_odeme = QLabel(); self.lbl_detay_odeme.setStyleSheet("color:#00F2FF; font-size:14px; border:none; font-weight:bold;")
        self.lbl_detay_iskonto = QLabel(); self.lbl_detay_iskonto.setStyleSheet("color:#FF0040; font-size:14px; border:none;")
        self.lbl_detay_tutar = QLabel(); self.lbl_detay_tutar.setStyleSheet("color:#00F2FF; font-size:30px; font-weight:900; border:none;")
        detay_lay.addWidget(self.lbl_detay_tarih); detay_lay.addWidget(self.lbl_detay_urunler); detay_lay.addWidget(self.lbl_detay_odeme); detay_lay.addWidget(self.lbl_detay_iskonto); detay_lay.addStretch(); detay_lay.addWidget(self.lbl_detay_tutar)
        lay.addWidget(self.detay_cerceve)
        return w

    def setup_satis_view(self):
        w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0, 10, 0, 0)
        
        # --- TABLO TANIMLAMASI ---
        self.ts = QTableWidget(10, 4)
        self.ts.setHorizontalHeaderLabels(["Ürün Cinsi", "Adet", "Birim Fiyat", "Tutar"])
        
        # Sütun Genişlik Modları ve Varsayılan Ayarlar
        self.ts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.ts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Tablo büyüdükçe ürün cinsi alanı esnesin
        self.ts.setColumnWidth(1, 65)   
        self.ts.setColumnWidth(2, 110)  
        self.ts.setColumnWidth(3, 110)  
        
        self.ts.verticalHeader().setVisible(False)
        self.ts.verticalHeader().setDefaultSectionSize(36) 
        
        self.ts.setStyleSheet("""
            QTableWidget { 
                background: #0D0D0D; 
                color: white; 
                border: 1px solid #1F1F1F; 
                border-radius: 15px;
                font-size: 13px;
            } 
            QHeaderView::section { 
                background: #121212; 
                color: #555; 
                border: none; 
                font-weight: 900;
                font-size: 11px;
                height: 30px;
            }
            QTableWidget::item {
                padding: 2px 8px;
            }
        """)
        self.ts.itemChanged.connect(self.hesapla)
        
        # --- KULLANICI ÖLÇEKLENDİRME PANELİ (QSplitter) ---
        # Yatayda sürüklenebilir bir ayırıcı panel oluşturuyoruz
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle { 
                background-color: #1F1F1F; 
                width: 6px; /* Tutma çubuğu kalınlığı */
                margin-left: 10px;
                margin-right: 10px;
                border-radius: 3px;
            }
            QSplitter::handle:hover {
                background-color: #00F2FF; /* Fare üzerine gelince dükkan renginde parlasın */
            }
        """)
        
        # Tabloyu splitter'a ekle
        splitter.addWidget(self.ts)
        
        # Sağ taraftaki boş alanı temsil edecek kukla bir widget ekliyoruz
        bos_sag_alan = QWidget()
        splitter.addWidget(bos_sag_alan)
        
        # Varsayılan Ölçeklendirme Ölçüleri: Tablo 550px ile başlasın, kalan yer boş alanın olsun
        splitter.setSizes([550, 400])
        splitter.setCollapsible(0, False) # Tablonun tamamen sıfıra kadar küçülüp kaybolmasını engeller
        
        lay.addWidget(splitter)
        
        # --- ALT PANEL DÜZENİ ---
        alt = QHBoxLayout(); sol = QVBoxLayout()
        
        # 🗓️ DOĞRUDAN AÇIK TAKVİM PANELİ
        lbl_tarih_title = QLabel("SATIŞ TARİHİ SEÇİN:")
        lbl_tarih_title.setStyleSheet("color: #555; font-size: 11px; font-weight: bold; border: none; margin-top: 5px;")
        
        self.calendar_satis = QCalendarWidget()
        self.calendar_satis.setSelectedDate(QDate.currentDate())
        self.calendar_satis.setGridVisible(False)
        self.calendar_satis.setFixedSize(260, 180)
        self.calendar_satis.setStyleSheet("""
            QCalendarWidget QWidget { background-color: #0D0D0D; color: #BBB; font-weight: bold; }
            QCalendarWidget QTableView { background-color: #0D0D0D; selection-background-color: #00F2FF; selection-color: black; border: 1px solid #1F1F1F; border-radius: 10px; }
            QCalendarWidget QMenu { background-color: #1A1A1A; color: white; }
            QCalendarWidget QAbstractItemView:enabled { color: white; selection-background-color: #00F2FF; selection-color: black; }
            QCalendarWidget QAbstractItemView:disabled { color: #333; }
        """)
        
        # Ödeme Yöntemi Alanı
        lbl_odeme_title = QLabel("ÖDEME YÖNTEMİ:")
        lbl_odeme_title.setStyleSheet("color: #555; font-size: 11px; font-weight: bold; border: none; margin-top: 5px;")
        self.cb_odeme = QComboBox()
        self.cb_odeme.addItems(["Nakit", "Havale", "Kredi Kartı"])
        self.cb_odeme.setFixedWidth(260)
        self.cb_odeme.setStyleSheet("""
            QComboBox { background:#0D0D0D; border: 1px solid #1F1F1F; color:white; padding:10px; border-radius:12px; font-weight: bold; }
            QComboBox QAbstractItemView { background-color: #0D0D0D; color: white; selection-background-color: #00F2FF; selection-color: black; }
        """)
        
        self.isk = QLineEdit(); self.isk.setPlaceholderText("İskonto (TL)"); self.isk.setFixedWidth(260)
        self.isk.setStyleSheet("background:#0D0D0D; border:1px solid #1F1F1F; color:white; padding:12px; border-radius:12px;")
        self.isk.textChanged.connect(self.toplam_al)
        
        self.net = QLabel("NET: ₺0.00"); self.net.setStyleSheet("color:#00F2FF; font-size:24px; font-weight:900; border:none;")
        
        sol.addWidget(lbl_tarih_title)
        sol.addWidget(self.calendar_satis)
        sol.addWidget(lbl_odeme_title)
        sol.addWidget(self.cb_odeme)
        sol.addWidget(self.isk)
        sol.addWidget(self.net)
        alt.addLayout(sol); alt.addStretch()
        
        btn_kaydet = QPushButton("İŞLEMİ KAYDET"); btn_kaydet.setFixedSize(280, 65); btn_kaydet.setStyleSheet("background-color:#00F2FF; color:black; font-weight:900; border-radius:18px;")
        btn_kaydet.clicked.connect(self.satis_kaydet); alt.addWidget(btn_kaydet); lay.addLayout(alt)
        return w

    def yukle(self):
        try:
            conn = sqlite3.connect("data/musteri_takip.db")
            r = conn.execute("SELECT ad_soyad, telefon, adres FROM musteriler WHERE id=?", (self.m_id,)).fetchone()
            if r: 
                self.name.setText(r[0].upper())
                self.lbl_tel.setText(f"📞 {r[1]}"); self.lbl_adres.setText(f"📍 {r[2]}")
            satislar = conn.execute("SELECT id, tarih, urunler, iskonto, toplam_tutar FROM satislar WHERE musteri_id=? ORDER BY id DESC", (self.m_id,)).fetchall()
            self.tablo_gecmis.setRowCount(0)
            for r_idx, row in enumerate(satislar):
                self.tablo_gecmis.insertRow(r_idx)
                for c_idx, val in enumerate(row):
                    display_val = f"₺{val}" if c_idx in [3, 4] else str(val)
                    it = QTableWidgetItem(display_val); it.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.tablo_gecmis.setItem(r_idx, c_idx, it)
            conn.close()
        except: pass

    def satis_kaydet(self):
        urunler_listesi = []
        for r in range(self.ts.rowCount()):
            u_item = self.ts.item(r, 0)
            a_item = self.ts.item(r, 1)
            if u_item and u_item.text().strip():
                adet = a_item.text() if a_item and a_item.text().strip() else "1"
                urunler_listesi.append(f"{u_item.text()} ({adet} Adet)")
        
        if not urunler_listesi: return
        
        u_metin = ", ".join(urunler_listesi)
        i_tutar = self.isk.text() if self.isk.text() else "0"
        n_fiyat = self.net.text().replace("NET: ₺", "")
        
        secilen_tarih = self.calendar_satis.selectedDate()
        su_an = datetime.now()
        
        if secilen_tarih == QDate.currentDate():
            tarih_metni = su_an.strftime("%d.%m.%Y %H:%M")
        else:
            tarih_metni = f"{secilen_tarih.toString('dd.MM.yyyy')} 10:00"
            
        odeme_turu = self.cb_odeme.currentText()
        
        conn = sqlite3.connect("data/musteri_takip.db")
        conn.execute("""
            INSERT INTO satislar (musteri_id, urunler, toplam_tutar, iskonto, tarih, odeme_yontemi) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.m_id, u_metin, n_fiyat, i_tutar, tarih_metni, odeme_turu))
        conn.commit(); conn.close()
        
        self.ts.clearContents()
        self.isk.clear()
        self.calendar_satis.setSelectedDate(QDate.currentDate())
        self.yukle()
        self.sayfalar.setCurrentIndex(0)

    def gecmis_detay_goster(self, item):
        row = item.row()
        s_id = self.tablo_gecmis.item(row, 0).text()
        
        try:
            conn = sqlite3.connect("data/musteri_takip.db")
            odeme_turu = conn.execute("SELECT odeme_yontemi FROM satislar WHERE id=?", (s_id,)).fetchone()[0]
            conn.close()
            odeme_turu = odeme_turu if odeme_turu else "Belirtilmedi"
        except:
            odeme_turu = "Belirtilmedi"

        self.lbl_detay_tarih.setText(f"İŞLEM TARİHİ: {self.tablo_gecmis.item(row, 1).text()}")
        urunler = self.tablo_gecmis.item(row, 2).text().replace(", ", "\n")
        self.lbl_detay_urunler.setText(urunler)
        self.lbl_detay_odeme.setText(f"💳 Ödeme Türü: {odeme_turu}")
        self.lbl_detay_iskonto.setText(f"Yapılan İskonto: {self.tablo_gecmis.item(row, 3).text()}")
        self.lbl_detay_tutar.setText(f"Net Tutar: {self.tablo_gecmis.item(row, 4).text()}")
        self.sayfalar.setCurrentIndex(2)

    def hesapla(self, item):
        if item.column() in [1, 2]:
            self.ts.blockSignals(True)
            try:
                a_txt = self.ts.item(item.row(), 1).text() if self.ts.item(item.row(), 1) else "0"
                f_txt = self.ts.item(item.row(), 2).text() if self.ts.item(item.row(), 2) else "0"
                a = float(a_txt); f = float(f_txt)
                self.ts.setItem(item.row(), 3, QTableWidgetItem(f"{a*f:.2f}"))
            except: pass
            self.ts.blockSignals(False); self.toplam_al()

    def toplam_al(self):
        t = 0.0
        for r in range(self.ts.rowCount()):
            it = self.ts.item(r, 3); t += float(it.text()) if it else 0
        try: i = float(self.isk.text()) if self.isk.text() else 0.0
        except: i = 0.0
        self.net.setText(f"NET: ₺{max(0, t-i):.2f}")

    def gecmis_menu_ac(self, pos):
        row = self.tablo_gecmis.currentRow()
        if row == -1: return
        menu = QMenu(self); menu.setStyleSheet("QMenu { background:#1A1A1A; color:white; }")
        sil = menu.addAction("❌ Bu Satışı Sil")
        if menu.exec(self.tablo_gecmis.viewport().mapToGlobal(pos)) == sil:
            s_id = self.tablo_gecmis.item(row, 0).text()
            conn = sqlite3.connect("data/musteri_takip.db")
            conn.execute("DELETE FROM satislar WHERE id=?", (s_id,)); conn.commit(); conn.close(); self.yukle()

    def geriye_don(self):
        if self.ana_pencere:
            self.ana_pencere.content.setCurrentIndex(1)
            self.ana_pencere.sayfa_liste.verileri_yukle()