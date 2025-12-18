import sys
import os
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
    QPushButton#btn_confirm { background-color: #2E7D32; } /* Hijau untuk konfirmasi */
    QPushButton#btn_view { background-color: #DEB887; color: #5D4037; } /* Krem untuk lihat bukti */
    QTableWidget { background-color: white; alternate-background-color: #FFFACD; gridline-color: #D2B48C; border: 1px solid #D2B48C; }
    QHeaderView::section { background-color: #DEB887; color: white; padding: 8px; font-weight: bold; }
"""

class AdminPaymentValidationApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.selected_id = None 
        self.selected_file_path = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Admin Pandawa - Validasi Pembayaran")
        self.resize(1000, 700)
        self.setStyleSheet(STYLE_SHEET)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("💳 VALIDASI PEMBAYARAN Customer")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #8B4513; margin: 15px;")
        self.main_layout.addWidget(header)

        # --- Tabel Data ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID Bayar", "ID Book", "ID VA", "Jumlah", "Waktu Bayar", "Status", "Nama File", "ID Room"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # Agar tidak bisa diedit manual di tabel
        self.table.cellClicked.connect(self.handle_selection)
        self.main_layout.addWidget(self.table)

        # --- Tombol Aksi (Hanya 3 Tombol) ---
        self.btn_layout = QtWidgets.QHBoxLayout()
        
        self.btn_refresh = QtWidgets.QPushButton("🔄 Refresh Data")
        
        self.btn_view_proof = QtWidgets.QPushButton("🖼️ Lihat Bukti Transfer")
        self.btn_view_proof.setObjectName("btn_view")
        
        self.btn_confirm = QtWidgets.QPushButton("✅ Konfirmasi Pembayaran")
        self.btn_confirm.setObjectName("btn_confirm")

        # Hubungkan fungsi
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_view_proof.clicked.connect(self.view_proof)
        self.btn_confirm.clicked.connect(self.confirm_payment)

        self.btn_layout.addWidget(self.btn_refresh)
        self.btn_layout.addWidget(self.btn_view_proof)
        self.btn_layout.addWidget(self.btn_confirm)
        
        self.main_layout.addLayout(self.btn_layout)

    def load_data(self):
        """Memuat data pembayaran dari database"""
        self.selected_id = None
        self.selected_file_path = None
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM valpembayaran") # Pastikan nama tabel benar
                rows = cursor.fetchall()
                self.table.setRowCount(0)
                for r_idx, r_data in enumerate(rows):
                    self.table.insertRow(r_idx)
                    for c_idx, val in enumerate(r_data):
                        item = QtWidgets.QTableWidgetItem(str(val))
                        item.setTextAlignment(QtCore.Qt.AlignCenter)
                        
                        # Beri warna pada status
                        if c_idx == 5: # Kolom Status
                            if str(val).lower() == 'confirmed':
                                item.setForeground(QtGui.QBrush(QtGui.QColor("#2E7D32")))
                                item.setFont(QtGui.QFont("Segoe UI", weight=QtGui.QFont.Bold))
                            elif str(val).lower() == 'pending':
                                item.setForeground(QtGui.QBrush(QtGui.QColor("#F57C00")))

                        self.table.setItem(r_idx, c_idx, item)
                conn.close()
            except Exception as e:
                print(f"Error: {e}")

    def handle_selection(self, row, col):
        """Menyimpan ID dan Path File saat baris diklik"""
        self.selected_id = self.table.item(row, 0).text()
        self.selected_file_path = self.table.item(row, 6).text() # Kolom file_name

    def view_proof(self):
        """Membuka Bukti Transfer dalam jendela baru"""
        if not self.selected_file_path or not os.path.exists(self.selected_file_path):
            QtWidgets.QMessageBox.warning(self, "Gagal", "File bukti tidak ditemukan atau belum dipilih!")
            return

        # Buat jendela popup sederhana untuk gambar
        self.img_dialog = QtWidgets.QDialog(self)
        self.img_dialog.setWindowTitle(f"Bukti Bayar - ID {self.selected_id}")
        lay = QtWidgets.QVBoxLayout()
        lbl = QtWidgets.QLabel()
        px = QtGui.QPixmap(self.selected_file_path)
        lbl.setPixmap(px.scaled(500, 700, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        lay.addWidget(lbl)
        self.img_dialog.setLayout(lay)
        self.img_dialog.exec_()

    def confirm_payment(self):
        """Mengubah status pembayaran menjadi confirmed"""
        if not self.selected_id:
            QtWidgets.QMessageBox.warning(self, "Pilih Data", "Silakan klik baris data yang ingin dikonfirmasi!")
            return

        reply = QtWidgets.QMessageBox.question(self, "Konfirmasi", 
                 f"Apakah Anda yakin ingin mengonfirmasi pembayaran ID {self.selected_id}?", 
                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    sql = "UPDATE valpembayaran SET payment_status = 'confirmed' WHERE id_bayar = %s"
                    cursor.execute(sql, (self.selected_id,))
                    conn.commit()
                    conn.close()
                    QtWidgets.QMessageBox.information(self, "Sukses", "Pembayaran Berhasil Dikonfirmasi!")
                    self.load_data()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminPaymentValidationApp()
    window.show()
    sys.exit(app.exec_())