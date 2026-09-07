import sqlite3
import os

DB_PATH = "data/musteri_takip.db"

def veritabani_hazirla():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Kullanıcılar
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, kullanici_adi TEXT UNIQUE, sifre TEXT)''')
    
    # Müşteriler
    cursor.execute('''CREATE TABLE IF NOT EXISTS musteriler 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, ad_soyad TEXT, telefon TEXT, adres TEXT)''')

    # Satışlar (Müşteri Kartı Genel)
    cursor.execute('''CREATE TABLE IF NOT EXISTS satislar 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, musteri_id INTEGER, tarih TEXT, 
                       toplam REAL, iskonto REAL, net REAL,
                       FOREIGN KEY (musteri_id) REFERENCES musteriler (id))''')

    # Varsayılan Admin
    cursor.execute("INSERT OR IGNORE INTO kullanicilar (kullanici_adi, sifre) VALUES (?, ?)", ("admin", "1234"))
    
    conn.commit()
    conn.close()
    print("Sıfırdan veritabanı kurulumu tamamlandı.")

if __name__ == "__main__":
    veritabani_hazirla()