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
    QPushButton { background-color: #8B4513; color: white; border-radius: 8px; padding: 12px; font-weight: bold; min-width: 140px; }
    QPushButton:hover { background-color: #A0522D; }
    QPushButton#btn_delete { background-color: #CD5C5C; }
    QTableWidget { background-color: white; alternate-background-color: #FFFACD; gridline-color: #D2B48C; border: 1px solid #D2B48C; }
    QHeaderView::section { background-color: #DEB887; color: white; padding: 10px; font-weight: bold; }
"""

class AdminFeedbackApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.selected_id = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Golden Stay - Kritik & Saran")
        self.resize(950, 600)
        self.setStyleSheet(STYLE_SHEET)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("💬 KRITIK & SARAN PENGGUNA")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #8B4513; margin: 15px;")
        self.main_layout.addWidget(header)

        # --- Tabel Ulasan ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        # Nama User sekarang menggantikan ID User
        self.table.setHorizontalHeaderLabels(["ID Kritik", "Tanggal", "Nama User", "Kritik / Saran"])
        
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) 
        header_view.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents) 
        header_view.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents) # Nama User
        header_view.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)           
        
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.cellClicked.connect(self.handle_selection)
        self.main_layout.addWidget(self.table)

        # --- Tombol Aksi ---
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("🔄 Refresh Data")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_delete = QtWidgets.QPushButton("🗑️ Hapus Kritik")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.clicked.connect(self.delete_data)

        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_refresh)
        self.btn_layout.addWidget(self.btn_delete)
        self.main_layout.addLayout(self.btn_layout)

    def load_data(self):
        """Memuat ulasan dengan JOIN untuk mendapatkan nama user"""
        self.selected_id = None
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # QUERY JOIN: Menghubungkan tabel ulasan (u) dengan tabel users (s)
                query = """
                    SELECT u.id_ulasan, u.tgl_ulasan, s.nama_user, u.pesan 
                    FROM ulasan u
                    JOIN users s ON u.id_user = s.id_user
                    ORDER BY u.id_ulasan DESC
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                self.table.setRowCount(0)
                
                for r_idx, r_data in enumerate(rows):
                    self.table.insertRow(r_idx)
                    for c_idx, val in enumerate(r_data):
                        item = QtWidgets.QTableWidgetItem(str(val))
                        # Kolom pesan rata kiri, lainnya rata tengah
                        if c_idx == 3:
                            item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                        else:
                            item.setTextAlignment(QtCore.Qt.AlignCenter)
                        self.table.setItem(r_idx, c_idx, item)
                conn.close()
            except Exception as e:
                print(f"Error Database: {e}")

    def handle_selection(self, row, col):
        self.selected_id = self.table.item(row, 0).text()

    def delete_data(self):
        if not self.selected_id:
            QtWidgets.QMessageBox.warning(self, "Pilih Data", "Pilih baris kritik yang ingin dihapus!")
            return

        reply = QtWidgets.QMessageBox.question(self, "Konfirmasi", 
                 f"Hapus kritik ID {self.selected_id}?", 
                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM ulasan WHERE id_ulasan = %s", (self.selected_id,))
                    conn.commit()
                    conn.close()
                    self.load_data()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminFeedbackApp()
    window.show()
    sys.exit(app.exec_())