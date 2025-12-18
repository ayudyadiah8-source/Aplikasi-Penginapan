import sys
import mysql.connector
from PyQt5 import QtWidgets, QtCore, QtGui

# --- 1. KONEKSI DATABASE ---
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  
            database="database_hotel"
        )
    except Exception as e:
        print(f"Gagal koneksi: {e}")
        return None

# --- 2. TEMA DESAIN ---
STYLE_SHEET = """
    QWidget { background-color: #FDF5E6; font-family: 'Segoe UI'; color: #5D4037; }
    QPushButton { background-color: #8B4513; color: white; border-radius: 8px; padding: 12px; font-weight: bold; min-width: 150px; font-size: 14px; }
    QPushButton:hover { background-color: #A0522D; }
    QTableWidget { background-color: white; alternate-background-color: #FFFACD; gridline-color: #D2B48C; border: 1px solid #D2B48C; }
    QHeaderView::section { background-color: #DEB887; color: white; padding: 8px; font-weight: bold; }
    QLineEdit { background-color: white; border: 1px solid #DEB887; border-radius: 5px; padding: 5px; }
"""

class AdminBookingApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Golden Stay - Data Pemesanan")
        self.resize(1100, 700)
        self.setStyleSheet(STYLE_SHEET)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QLabel("📋 DAFTAR RESERVASI KAMAR")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #8B4513; margin: 15px;")
        self.main_layout.addWidget(header)

        # --- Bagian Atas (Pencarian & Tombol) ---
        top_bar = QtWidgets.QHBoxLayout()
        
        self.in_search = QtWidgets.QLineEdit()
        self.in_search.setPlaceholderText("Cari ID Booking atau ID User...")
        self.in_search.textChanged.connect(self.load_data) # Live search saat mengetik
        
        self.btn_refresh = QtWidgets.QPushButton("🔄 Refresh Data")
        self.btn_refresh.clicked.connect(self.load_data)

        top_bar.addWidget(QtWidgets.QLabel("Cari:"))
        top_bar.addWidget(self.in_search)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_refresh)
        
        self.main_layout.addLayout(top_bar)

        # --- Tabel Data ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID Booking", "ID User", "ID Room", "Check-In", 
            "Check-Out", "Jumlah Kamar", "Total Harga", "Tgl Booking", "Status"
        ])
        
        # Pengaturan tampilan tabel
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # Data hanya baca
        self.table.verticalHeader().setVisible(False) # Sembunyikan angka baris samping
        
        self.main_layout.addWidget(self.table)

    def load_data(self):
        """Memuat data booking dari database dengan fitur filter search"""
        search_text = self.in_search.text()
        conn = get_db_connection()
        
        if conn:
            try:
                cursor = conn.cursor()
                # Query pencarian fleksibel
                query = "SELECT * FROM booking"
                if search_text:
                    query += f" WHERE id_booking LIKE '%{search_text}%' OR id_user LIKE '%{search_text}%' OR status LIKE '%{search_text}%'"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                self.table.setRowCount(0)
                for r_idx, r_data in enumerate(rows):
                    self.table.insertRow(r_idx)
                    for c_idx, val in enumerate(r_data):
                        # Format tampilan khusus
                        text = str(val)
                        if c_idx == 6: # Kolom Total Harga
                            text = f"Rp {val:,}"
                        
                        item = QtWidgets.QTableWidgetItem(text)
                        item.setTextAlignment(QtCore.Qt.AlignCenter)
                        
                        # Beri warna berdasarkan status
                        if c_idx == 8: # Kolom Status
                            status = str(val).lower()
                            if status == 'bayar':
                                item.setForeground(QtGui.QBrush(QtGui.QColor("#2E7D32"))) # Hijau
                            elif status == 'batal':
                                item.setForeground(QtGui.QBrush(QtGui.QColor("#CD5C5C"))) # Merah
                            elif status == 'selesai':
                                item.setForeground(QtGui.QBrush(QtGui.QColor("#1976D2"))) # Biru
                            
                        self.table.setItem(r_idx, c_idx, item)
                
                conn.close()
            except Exception as e:
                print(f"Error Database: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminBookingApp()
    window.show()
    sys.exit(app.exec_())