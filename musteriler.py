import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QMenu, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal

class MusteriListesi(QWidget):
    detay_sinyali = pyqtSignal(int) # Müşteri kartını açmak için sinyal

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #121212; border: none;")
        self.tum_veriler = [] # Arama filtresi için verileri hafızada tutacağız
        self.init_ui()
        self.verileri_yukle()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Üst Başlık
        baslik = QLabel("KAYITLI MÜŞTERİ LİSTESİ")
        baslik.setStyleSheet("color: white; font-size: 24px; font-weight: 900; letter-spacing: 2px;")
        layout.addWidget(baslik)

        # 🔍 ANLIK ARAMA ÇUBUĞU (Baş Harfe ve Telefona Göre)
        self.arama_cubugu = QLineEdit()
        self.arama_cubugu.setPlaceholderText("🔍 Müşteri adı (baş harfiyle) veya telefon numarası yazın...")
        self.arama_cubugu.setStyleSheet("""
            QLineEdit {
                background-color: #1A1A1A;
                color: white;
                border: 1px solid #222;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 1px solid #00F2FF;
            }
        """)
        self.arama_cubugu.textChanged.connect(self.arama_yap)
        layout.addWidget(self.arama_cubugu)

        # Tablo Yapısı
        self.tablo = QTableWidget(0, 4)
        self.tablo.setHorizontalHeaderLabels(["SİSTEM ID", "MÜŞTERİ / FİRMA ADI", "İRTİBAT TELEFONU", "AÇIK ADRES"])
        self.tablo.setColumnHidden(0, True) 
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tablo.verticalHeader().setVisible(False)
        self.tablo.verticalHeader().setDefaultSectionSize(55)
        self.tablo.setStyleSheet("""
            QTableWidget { background: #0D0D0D; color: #BBB; border: 1px solid #1F1F1F; border-radius: 15px; }
            QHeaderView::section { background: #121212; color: #444; border: none; font-weight: 900; height: 40px; }
            QTableWidget::item { border-bottom: 1px solid #1A1A1A; padding-left: 15px; }
            QTableWidget::item:selected { background: #1A1A1A; color: #00F2FF; }
        """)
        
        self.tablo.itemDoubleClicked.connect(self.detay_tetikle)
        self.tablo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tablo.customContextMenuRequested.connect(self.musteri_menu_ac)
        
        layout.addWidget(self.tablo)

    def verileri_yukle(self):
        try:
            conn = sqlite3.connect("data/musteri_takip.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, ad_soyad, telefon, adres FROM musteriler ORDER BY ad_soyad ASC")
            self.tum_veriler = cursor.fetchall() 
            conn.close()
            self.tabloyu_doldur(self.tum_veriler)
        except Exception as e:
            print(f"Müşteri listesi yüklenemedi: {e}")

    def tabloyu_doldur(self, veri_listesi):
        self.tablo.setRowCount(0)
        for row_idx, row_data in enumerate(veri_listesi):
            self.tablo.insertRow(row_idx)
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value) if value else "")
                if col_idx != 3: 
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.tablo.setItem(row_idx, col_idx, item)

    def arama_yap(self, aranan_metin):
        """Metin girildikçe baş harfe veya telefon numarasına göre anlık filtreleme yapar"""
        aranan_metin = aranan_metin.lower().strip()
        
        if not aranan_metin:
            self.tabloyu_doldur(self.tum_veriler)
            return

        filtrelenmis_veriler = []
        for veri in self.tum_veriler:
            ad_soyad = str(veri[1]).lower()
            telefon = str(veri[2]).lower()
            
            # Değişen Kısım: İsim aramasında 'in' yerine 'startswith' (..ile başlayan) kullandık
            # Telefon numarasında ise pratiklik için içinde geçmesi yeterli kalmaya devam etti
            if ad_soyad.startswith(aranan_metin) or aranan_metin in telefon:
                filtrelenmis_veriler.append(veri)
                
        self.tabloyu_doldur(filtrelenmis_veriler)

    def detay_tetikle(self, item):
        row = item.row()
        m_id = int(self.tablo.item(row, 0).text())
        self.detay_sinyali.emit(m_id)

    def musteri_menu_ac(self, pos):
        row = self.tablo.currentRow()
        if row == -1: return
        
        m_id = self.tablo.item(row, 0).text()
        m_adi = self.tablo.item(row, 1).text()
        
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background:#1A1A1A; color:white; } QMenu::item:selected { background:#FF0040; color:white; font-weight:bold; }")
        sil_aksiyon = menu.addAction(f"❌ {m_adi} Sistemden Tamamen Sil")
        
        aksiyon = menu.exec(self.tablo.viewport().mapToGlobal(pos))
        
        if aksiyon == sil_aksiyon:
            emin_mi = QMessageBox.question(self, "KRİTİK UYARI", 
                                           f"'{m_adi}' isimli müşteriyi sildiğinizde ona ait TÜM GEÇMİŞ SATIŞLAR DA kalıcı olarak silinecektir!\n\nBu işlemi onaylıyor musunuz?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if emin_mi == QMessageBox.StandardButton.Yes:
                try:
                    conn = sqlite3.connect("data/musteri_takip.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM satislar WHERE musteri_id = ?", (m_id,))
                    cursor.execute("DELETE FROM musteriler WHERE id = ?", (m_id,))
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(self, "Başarılı", f"{m_adi} dükkan sicilinden başarıyla kaldırıldı.")
                    self.verileri_yukle()
                    self.arama_cubugu.clear()
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Müşteri silinirken hata çıktı: {e}")