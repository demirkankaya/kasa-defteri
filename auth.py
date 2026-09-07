import sqlite3
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QPushButton, 
                             QLabel, QFrame, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal

class LoginEkrani(QWidget):
    giris_basarili = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Girişi | Quantum CRM")
        self.showMaximized()
        self.setStyleSheet("background-color: #050505;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.kart = QFrame()
        self.kart.setFixedSize(450, 550)
        self.kart.setStyleSheet("background-color: #0D0D0D; border: 1px solid #1F1F1F; border-radius: 30px;")
        
        kart_layout = QVBoxLayout(self.kart)
        kart_layout.setContentsMargins(50, 50, 50, 50)
        kart_layout.setSpacing(25)

        logo = QLabel("DEMİR CRM")
        logo.setStyleSheet("color: white; font-size: 28px; font-weight: 900; letter-spacing: 5px; border: none;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kart_layout.addWidget(logo)

        # Kullanıcı Adı
        self.u_input = QLineEdit()
        self.u_input.setPlaceholderText("Kullanıcı Adı")
        self.u_input.setStyleSheet("background-color: #121212; border: 1px solid #1F1F1F; border-radius: 12px; padding: 15px; color: white;")
        kart_layout.addWidget(self.u_input)

        # Şifre
        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("Şifre")
        self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.p_input.setStyleSheet(self.u_input.styleSheet())
        
        # --- KRİTİK GÜNCELLEME: ENTER TUŞU DESTEĞİ ---
        self.p_input.returnPressed.connect(self.kontrol_et)
        
        kart_layout.addWidget(self.p_input)

        # Giriş Butonu
        self.btn_giris = QPushButton("SİSTEME GİRİŞ YAP")
        self.btn_giris.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_giris.setStyleSheet("""
            QPushButton { background-color: #00F2FF; color: black; padding: 18px; border-radius: 15px; font-weight: 900; }
            QPushButton:hover { background-color: #00D1DB; }
        """)
        self.btn_giris.clicked.connect(self.kontrol_et)
        kart_layout.addWidget(self.btn_giris)

        layout.addWidget(self.kart)

    def kontrol_et(self):
        u, p = self.u_input.text(), self.p_input.text()
        if u == "admin" and p == "1234": # Şimdilik sabit, db'ye de bağlayabilirsin
            self.giris_basarili.emit()
        else:
            try:
                conn = sqlite3.connect("data/musteri_takip.db")
                res = conn.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (u, p)).fetchone()
                conn.close()
                if res: self.giris_basarili.emit()
                else: QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")
            except:
                QMessageBox.critical(self, "Hata", "Veritabanı bağlantısı yok!")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = LoginEkrani()
    win.show()
    sys.exit(app.exec())