import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QCalendarWidget, QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

class KasaDefteriEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #121212; border: none;")
        self.init_ui()
        self.verileri_yukle()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # --- ÜST PANEL: BAŞLIK ---
        ust_header = QVBoxLayout()
        baslik = QLabel("KASA DEFTERİ & ARŞİV")
        baslik.setStyleSheet("color: white; font-size: 28px; font-weight: 900; letter-spacing: 3px;")
        alt_bilgi = QLabel("Geçmişe dönük mali kayıtları, günlük/aylık ciroyu ve ödeme yöntemlerini buradan yönetin.")
        alt_bilgi.setStyleSheet("color: #555; font-size: 13px; font-weight: bold;")
        ust_header.addWidget(baslik)
        ust_header.addWidget(alt_bilgi)
        main_layout.addLayout(ust_header)

        # --- ORTA PANEL: TAKVİM VE ÖZET KARTLARI ---
        orta_panel = QHBoxLayout()
        orta_panel.setSpacing(30)

        # 1. PROFESYONEL VE TAM KARANLIK TAKVİM
        self.takvim = QCalendarWidget()
        self.takvim.setGridVisible(False)
        self.takvim.setNavigationBarVisible(True)
        self.takvim.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.takvim.setFixedWidth(400)

        self.takvim.setStyleSheet("""
            QCalendarWidget { border: 1px solid #1F1F1F; border-radius: 15px; background-color: #0D0D0D; }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #121212; border-bottom: 1px solid #1F1F1F; border-radius: 15px 15px 0 0; }
            QCalendarWidget QToolButton { color: white; background-color: transparent; font-weight: bold; icon-size: 30px; border: none; }
            QCalendarWidget QToolButton:hover { background-color: #1A1A1A; color: #00F2FF; }
            QCalendarWidget QMenu { background-color: #1A1A1A; color: white; border: 1px solid #333; }
            QCalendarWidget QMenu::item:selected { background-color: #00F2FF; color: black; }
            QCalendarWidget QSpinBox { color: white; background-color: #1A1A1A; selection-background-color: #00F2FF; selection-color: black; font-size: 14px; font-weight: bold; border: none; }
            QCalendarWidget QLabel { color: white; font-weight: bold; font-size: 14px; background-color: transparent; }
            QCalendarWidget QHeaderView::section { background-color: #0D0D0D; color: #444; border: none; font-weight: 900; text-transform: uppercase; font-size: 11px; }
            QCalendarWidget QAbstractItemView { background-color: #0D0D0D; color: #BBBBBB; selection-background-color: #00F2FF; selection-color: black; border: none; font-weight: bold; }
            QCalendarWidget QAbstractItemView:enabled:selected { background-color: #00F2FF; color: black; border-radius: 5px; }
            QCalendarWidget QAbstractItemView:disabled { color: #252525; }
        """)

        self.takvim.selectionChanged.connect(self.verileri_yukle)
        orta_panel.addWidget(self.takvim)

        # 2. ÖZET CİRO KARTI
        self.kart_ozet = QFrame()
        self.kart_ozet.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A1A1A, stop:1 #0D0D0D);
                border: 1px solid #1F1F1F; border-radius: 25px; 
            }
        """)
        ozet_lay = QVBoxLayout(self.kart_ozet)
        ozet_lay.setContentsMargins(40, 30, 40, 30)
        
        self.lbl_tarih_baslik = QLabel("BUGÜN")
        self.lbl_tarih_baslik.setStyleSheet("color: white; font-size: 14px; font-weight: 900; border:none;")
        
        self.lbl_ciro_rakam = QLabel("₺0.00")
        self.lbl_ciro_rakam.setStyleSheet("color: white; font-size: 50px; font-weight: 100; border:none; margin: 5px 0;")
        
        self.lbl_aylik_ciro = QLabel("Bu Ay Toplam: ₺0.00")
        self.lbl_aylik_ciro.setStyleSheet("color: #00F2FF; font-size: 14px; font-weight: bold; border:none; margin-bottom: 5px;")
        
        self.lbl_satis_adet = QLabel("0 İşlem Kaydedildi")
        self.lbl_satis_adet.setStyleSheet("color: #555; font-size: 13px; font-weight: bold; border:none;")
        
        ozet_lay.addWidget(self.lbl_tarih_baslik)
        ozet_lay.addWidget(self.lbl_ciro_rakam)
        ozet_lay.addWidget(self.lbl_aylik_ciro)
        ozet_lay.addWidget(self.lbl_satis_adet)
        ozet_lay.addStretch()
        
        orta_panel.addWidget(self.kart_ozet)
        main_layout.addLayout(orta_panel)

        # --- ALT PANEL: SATIŞ LİSTESİ TABLOSU ---
        self.tablo = QTableWidget(0, 5)
        self.tablo.setHorizontalHeaderLabels(["MÜŞTERİ ADI", "ÜRÜN DETAYI", "SAAT", "ÖDEME TÜRÜ", "TUTAR"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.verticalHeader().setDefaultSectionSize(60)
        self.tablo.setStyleSheet("""
            QTableWidget { background: transparent; color: #BBB; border: none; gridline-color: transparent; }
            QHeaderView::section { background: #121212; color: #444; border: none; font-weight: 900; height: 40px; text-transform: uppercase; font-size: 11px; }
            QTableWidget::item { border-bottom: 1px solid #1A1A1A; padding-left: 20px; }
            QTableWidget::item:selected { background: #1A1A1A; color: #00F2FF; }
        """)
        
        # SAĞ TIK MENÜSÜ AKTİF EDİLDİ
        self.tablo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tablo.customContextMenuRequested.connect(self.kasa_menu_ac)
        
        main_layout.addWidget(self.tablo)

    def verileri_yukle(self):
        try:
            conn = sqlite3.connect("data/musteri_takip.db")
            cursor = conn.cursor()
            
            secilen_qdate = self.takvim.selectedDate()
            secilen_str = secilen_qdate.toString("dd.MM.yyyy")
            secilen_ay_yil = secilen_qdate.toString(".MM.yyyy")
            
            if secilen_qdate == QDate.currentDate():
                self.lbl_tarih_baslik.setText("BUGÜNÜN ÖZETİ")
            else:
                self.lbl_tarih_baslik.setText(f"{secilen_str} ÖZETİ")

            sorgu = """
            SELECT musteriler.ad_soyad, satislar.urunler, satislar.tarih, satislar.odeme_yontemi, satislar.topham_tutar 
            FROM satislar 
            JOIN musteriler ON satislar.musteri_id = musteriler.id 
            WHERE satislar.tarih LIKE ? 
            ORDER BY satislar.id DESC
            """
            # Not: DB Browser'da kolon adını 'toplam_tutar' yaptıysanız buradaki typosuz sürümü (toplam_tutar) kullanın.
            sorgu = sorgu.replace("satislar.topham_tutar", "satislar.toplam_tutar")
            
            cursor.execute(sorgu, (f"{secilen_str}%",))
            veriler = cursor.fetchall()
            
            cursor.execute("SELECT SUM(toplam_tutar) FROM satislar WHERE tarih LIKE ?", (f"%{secilen_ay_yil}%",))
            aylik_toplam = cursor.fetchone()[0]
            aylik_toplam = aylik_toplam if aylik_toplam else 0.0

            self.tablo.setRowCount(0)
            gunluk_ciro = 0.0
            
            for row_idx, row_data in enumerate(veriler):
                self.tablo.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    if col_idx == 2:
                        val = str(value).split(" ")[1] if " " in str(value) else str(value)
                    elif col_idx == 3:
                        val = str(value) if value else "Belirtilmedi"
                    elif col_idx == 4:
                        val = f"₺{value:,.2f}"
                        gunluk_ciro += float(row_data[4])
                    else:
                        val = str(value)
                        
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    
                    if col_idx == 3:
                        if val == "Nakit": item.setForeground(Qt.GlobalColor.green)
                        elif val == "Havale": item.setForeground(Qt.GlobalColor.cyan)
                        elif val == "Kredi Kartı": item.setForeground(Qt.GlobalColor.yellow)

                    self.tablo.setItem(row_idx, col_idx, item)
            
            self.lbl_ciro_rakam.setText(f"₺{gunluk_ciro:,.2f}")
            ay_ismi = secilen_qdate.toString("MMMM")
            self.lbl_aylik_ciro.setText(f"{ay_ismi} Toplamı: ₺{aylik_toplam:,.2f}")
            self.lbl_satis_adet.setText(f"{len(veriler)} İşlem Gerçekleşti")
            
            conn.close()
        except Exception as e:
            print(f"Kasa Veri Yükleme Hatası: {e}")

    def kasa_menu_ac(self, pos):
        row = self.tablo.currentRow()
        if row == -1: return
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background:#1A1A1A; color:white; } QMenu::item:selected { background:#00F2FF; color:black; }")
        sil_aksiyon = menu.addAction("❌ Bu Satışı İptal Et / Sil")
        
        aksiyon = menu.exec(self.tablo.viewport().mapToGlobal(pos))
        
        if aksiyon == sil_aksiyon:
            secilen_tarih = self.takvim.selectedDate().toString("dd.MM.yyyy")
            musteri_adi = self.tablo.item(row, 0).text()
            urun_detayi = self.tablo.item(row, 1).text()
            saat = self.tablo.item(row, 2).text()
            tam_tarih = f"{secilen_tarih} {saat}"
            
            emin_mi = QMessageBox.question(self, "Satış İptali", 
                                           f"{musteri_adi} dökümündeki '{urun_detayi}' satışını iptal etmek istiyor musunuz?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if emin_mi == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("data/musteri_takip.db")
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT id FROM musteriler WHERE ad_soyad = ?", (musteri_adi,))
                    m_id_row = cursor.fetchone()
                    
                    if m_id_row:
                        m_id = m_id_row[0]
                        cursor.execute("""
                            DELETE FROM satislar 
                            WHERE musteri_id = ? AND urunler = ? AND tarih = ?
                        """, (m_id, urun_detayi, tam_tarih))
                        conn.commit()
                    
                    conn.close()
                    self.verileri_yukle() 
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Satış silinemedi: {e}")