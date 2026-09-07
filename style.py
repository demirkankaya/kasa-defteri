# style.py
STIL_QUANTUM = """



    /* style.py içine eklenecek kısım */
    QMessageBox {
        background-color: #0D0D0D;
    }
    QMessageBox QLabel {
        color: #FFFFFF; /* Bembeyaz yazı */
        font-weight: 500;
    }
    QMessageBox QPushButton {
        background-color: #1E293B;
        color: white;
        border-radius: 6px;
        padding: 6px 15px;
    }
    QMainWindow { background-color: #050505; }
    QFrame#Sidebar { background-color: #0D0D0D; border-right: 1px solid #1F1F1F; }
    QStackedWidget#ContentArea { 
        background-color: #121212; 
        border-top-left-radius: 40px; 
        border-left: 1px solid #1F1F1F; 
    }
    QPushButton#MenuBtn {
        background-color: transparent; color: #555555; text-align: left;
        padding: 20px 30px; font-size: 13px; font-weight: 800; border: none;
        letter-spacing: 1px;
    }
    QPushButton#MenuBtn:hover { color: #FFFFFF; background-color: rgba(255, 255, 255, 0.03); }
    QPushButton#MenuBtn:checked { 
        color: #00F2FF; 
        background-color: rgba(0, 242, 255, 0.05); 
        border-left: 4px solid #00F2FF; 
    }
    
    QLineEdit, QTextEdit {
        background-color: #0D0D0D; border: 1px solid #1F1F1F; border-radius: 12px;
        padding: 12px; color: white;
    }
    QLineEdit:focus { border: 1px solid #00F2FF; }
    
    QTableWidget { background-color: transparent; border: none; color: #BBBBBB; gridline-color: #1A1A1A; }
    QHeaderView::section { 
        background-color: transparent; color: #444; padding: 15px; 
        border: none; font-weight: 900; text-transform: uppercase;
    }
    
    QFrame#Kart {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1A1A1A, stop:1 #111111);
        border: 1px solid #252525; border-radius: 20px;
    }
"""