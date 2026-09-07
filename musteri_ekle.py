import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt

class MusteriEkleEkrani(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 60, 80, 60)
        layout.setSpacing(25)
        
        t = QLabel("YENİ MÜŞTERİ TANIMLAMA")
        t.setStyleSheet("color: white; font-size: 18px; font-weight: 900; letter-spacing: 2px;")
        layout.addWidget(t)

        self.ad = QLineEdit(); self.ad.setPlaceholderText("Müşteri / Firma Adı")
        self.tel = QLineEdit(); self.tel.setPlaceholderText("İrtibat Numarası")
        self.adr = QTextEdit(); self.adr.setPlaceholderText("Adres Detayları"); self.adr.setFixedHeight(120)
        
        layout.addWidget(self.ad)
        layout.addWidget(self.tel)
        layout.addWidget(self.adr)

        self.btn_kaydet = QPushButton("VERİTABANINA İŞLE")
        self.btn_kaydet.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_kaydet.setStyleSheet("""
            QPushButton { background-color: #00F2FF; color: black; padding: 18px; font-weight: 900; border-radius: 15px; }
            QPushButton:hover { background-color: #00D1DB; }
        """)
        self.btn_kaydet.clicked.connect(self.kaydet)
        layout.addWidget(self.btn_kaydet)
        layout.addStretch()

    def kaydet(self):
        ad, tel, adr = self.ad.text(), self.tel.text(), self.adr.toPlainText()
        if not ad or not tel:
            QMessageBox.warning(self, "Eksik Veri", "Ad ve Telefon alanları zorunludur!")
            return

        try:
            conn = sqlite3.connect("data/musteri_takip.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO musteriler (ad_soyad, telefon, adres) VALUES (?, ?, ?)", (ad, tel, adr))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Sistem", f"{ad} başarıyla kaydedildi.")
            self.ad.clear(); self.tel.clear(); self.adr.clear()
        except Exception as e:
            QMessageBox.critical(self, "Veritabanı Hatası", str(e))