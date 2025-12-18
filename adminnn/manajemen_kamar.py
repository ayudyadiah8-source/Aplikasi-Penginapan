import sys
import os
import mysql.connector
from PyQt5 import QtWidgets, QtCore, QtGui
import shutil
import uuid

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

# --- 2. TEMA DESAIN (CREAM & BROWN) ---
STYLE_SHEET = """
    QWidget { background-color: #FDF5E6; font-family: 'Segoe UI'; color: #5D4037; }
    QGroupBox { font-weight: bold; border: 2px solid #D2B48C; border-radius: 10px; margin-top: 15px; background-color: #FFF8DC; }
    QLineEdit, QTextEdit, QSpinBox { background-color: white; border: 1px solid #DEB887; border-radius: 5px; padding: 5px; }
    QPushButton { background-color: #8B4513; color: white; border-radius: 8px; padding: 10px; font-weight: bold; min-width: 100px; }
    QPushButton:hover { background-color: #A0522D; }
    QPushButton#btn_choose { background-color: #DEB887; color: #5D4037; min-width: 80px; padding: 5px; }
    QPushButton#btn_edit { background-color: #D2B48C; color: #5D4037; }
    QPushButton#btn_delete { background-color: #CD5C5C; }
    QTableWidget { background-color: white; alternate-background-color: #FFFACD; gridline-color: #D2B48C; border: 1px solid #D2B48C; }
    QHeaderView::section { background-color: #DEB887; color: white; padding: 5px; font-weight: bold; }
"""

class AdminHotelApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.selected_id = None 
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Dashboard Admin Pandawa - Version 1.1")
        self.resize(1150, 800)
        self.setStyleSheet(STYLE_SHEET)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Header
        header = QtWidgets.QLabel("🏨 MANAGEMENT DATA KAMAR")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #8B4513; margin: 10px;")
        self.main_layout.addWidget(header)

        # --- Layout Atas: Form (Kiri) & Preview (Kanan) ---
        self.top_layout = QtWidgets.QHBoxLayout()

        # Group Form Input
        self.form_box = QtWidgets.QGroupBox("Informasi Kamar")
        self.form_grid = QtWidgets.QGridLayout()

        self.in_room_number = QtWidgets.QLineEdit()
        self.in_tipe_room = QtWidgets.QLineEdit()
        self.in_harga_wd = QtWidgets.QLineEdit()
        self.in_harga_we = QtWidgets.QLineEdit()
        self.in_stok = QtWidgets.QSpinBox()
        self.in_stok.setRange(0, 1000)
        
        self.in_file_name = QtWidgets.QLineEdit()
        self.in_file_name.setReadOnly(True)
        self.btn_browse = QtWidgets.QPushButton("Pilih File")
        self.btn_browse.setObjectName("btn_choose")
        self.btn_browse.clicked.connect(self.choose_file)

        self.in_desc = QtWidgets.QTextEdit()
        self.in_desc.setMaximumHeight(60)

        # Susun widget ke grid
        self.form_grid.addWidget(QtWidgets.QLabel("No. Kamar:"), 0, 0)
        self.form_grid.addWidget(self.in_room_number, 0, 1)
        self.form_grid.addWidget(QtWidgets.QLabel("Tipe Kamar:"), 1, 0)
        self.form_grid.addWidget(self.in_tipe_room, 1, 1)
        self.form_grid.addWidget(QtWidgets.QLabel("Harga Weekday:"), 2, 0)
        self.form_grid.addWidget(self.in_harga_wd, 2, 1)
        self.form_grid.addWidget(QtWidgets.QLabel("Harga Weekend:"), 3, 0)
        self.form_grid.addWidget(self.in_harga_we, 3, 1)
        self.form_grid.addWidget(QtWidgets.QLabel("Stok:"), 4, 0)
        self.form_grid.addWidget(self.in_stok, 4, 1)
        self.form_grid.addWidget(QtWidgets.QLabel("Gambar:"), 5, 0)
        
        file_lay = QtWidgets.QHBoxLayout()
        file_lay.addWidget(self.in_file_name)
        file_lay.addWidget(self.btn_browse)
        self.form_grid.addLayout(file_lay, 5, 1)
        
        self.form_grid.addWidget(QtWidgets.QLabel("Deskripsi:"), 6, 0)
        self.form_grid.addWidget(self.in_desc, 6, 1)
        self.form_box.setLayout(self.form_grid)

        # Preview Image Label
        self.preview_box = QtWidgets.QGroupBox("Preview")
        self.preview_layout = QtWidgets.QVBoxLayout()
        self.lbl_preview = QtWidgets.QLabel("Tidak ada gambar")
        self.lbl_preview.setFixedSize(250, 250)
        self.lbl_preview.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("border: 1px dashed #DEB887; background: white;")
        self.preview_layout.addWidget(self.lbl_preview)
        self.preview_box.setLayout(self.preview_layout)

        self.top_layout.addWidget(self.form_box, 2)
        self.top_layout.addWidget(self.preview_box, 1)
        self.main_layout.addLayout(self.top_layout)

        # --- Tombol Aksi ---
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_add = QtWidgets.QPushButton("➕ Tambah")
        self.btn_update = QtWidgets.QPushButton("💾 Update")
        self.btn_update.setObjectName("btn_edit")
        self.btn_delete = QtWidgets.QPushButton("🗑️ Hapus")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_refresh = QtWidgets.QPushButton("🔄 Refresh")

        self.btn_add.clicked.connect(self.add_room)
        self.btn_update.clicked.connect(self.update_room)
        self.btn_delete.clicked.connect(self.delete_room)
        self.btn_refresh.clicked.connect(self.refresh_action)

        self.btn_layout.addWidget(self.btn_add); self.btn_layout.addWidget(self.btn_update)
        self.btn_layout.addWidget(self.btn_delete); self.btn_layout.addWidget(self.btn_refresh)
        self.main_layout.addLayout(self.btn_layout)

        # --- Tabel ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "No", "Tipe", "Deskripsi", "Harga WD", "Harga WE", "Stok", "Visual"])
        
        # PERBAIKAN ERROR: Menggunakan verticalHeader untuk set tinggi baris
        self.table.setIconSize(QtCore.QSize(70, 70))
        self.table.verticalHeader().setDefaultSectionSize(80) 
        
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.cellClicked.connect(self.get_row_data) 
        self.main_layout.addWidget(self.table)

    def set_preview(self, path):
        if path and os.path.exists(path):
            pixmap = QtGui.QPixmap(path)
            self.lbl_preview.setPixmap(pixmap.scaled(250, 250, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.lbl_preview.setText("Gambar tidak ditemukan")
            self.lbl_preview.setPixmap(QtGui.QPixmap())

    def choose_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Pilih Gambar", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.in_file_name.setText(file_path)
            self.set_preview(file_path)

    def load_data(self):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM rooms")
                rows = cursor.fetchall()
                self.table.setRowCount(0)
                for r_idx, r_data in enumerate(rows):
                    self.table.insertRow(r_idx)
                    for c_idx, val in enumerate(r_data):
                        if c_idx == 7: # Kolom Gambar
                            path = os.path.join("assets", str(val))
                            item = QtWidgets.QTableWidgetItem()
                            if path and os.path.exists(path):
                                item.setIcon(QtGui.QIcon(path))
                            else:
                                item.setText("No Image")
                            self.table.setItem(r_idx, c_idx, item)
                        else:
                            item = QtWidgets.QTableWidgetItem(str(val))
                            item.setTextAlignment(QtCore.Qt.AlignCenter)
                            self.table.setItem(r_idx, c_idx, item)
                conn.close()
            except Exception as e:
                print(f"Error Load: {e}")

    def get_row_data(self, row, column):
        try:
            self.selected_id = self.table.item(row, 0).text()
            self.in_room_number.setText(self.table.item(row, 1).text())
            self.in_tipe_room.setText(self.table.item(row, 2).text())
            self.in_desc.setPlainText(self.table.item(row, 3).text())
            self.in_harga_wd.setText(self.table.item(row, 4).text())
            self.in_harga_we.setText(self.table.item(row, 5).text())
            self.in_stok.setValue(int(self.table.item(row, 6).text()))
            
            # Ambil path dari database untuk akurasi preview
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT file_name FROM rooms WHERE id_room=%s", (self.selected_id,))
            res = cursor.fetchone()
            if res:
                filename = res[0]
                full_path = os.path.join("assets", filename)
                self.in_file_name.setText(full_path) # Opsional: tetapkan path lengkap di teks
                self.set_preview(full_path)
            conn.close()
        except: pass

    def add_room(self):
        try:
            # 1. Ambil path asal dari input
            original_path = self.in_file_name.text()
            
            if not original_path or not os.path.exists(original_path):
                QtWidgets.QMessageBox.warning(self, "Peringatan", "Pilih gambar terlebih dahulu!")
                return

            # 2. Siapkan folder assets
            assets_dir = "assets"
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)

            # 3. Buat nama file random (UUID) tetap menjaga ekstensi aslinya
            file_extension = os.path.splitext(original_path)[1] # mengambil .jpg / .png
            random_filename = f"{uuid.uuid4()}{file_extension}"
            destination_path = os.path.join(assets_dir, random_filename)

            # 4. Salin file ke folder assets
            shutil.copy2(original_path, destination_path)

            # 5. Simpan ke Database (Hanya nama filenya saja)
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = """INSERT INTO rooms (room_number, tipe_room, deskripsi_room, 
                         harga_weekday, harga_weekend, stok, file_name) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                
                # Gunakan random_filename, bukan original_path
                vals = (self.in_room_number.text(), self.in_tipe_room.text(), 
                        self.in_desc.toPlainText(), int(self.in_harga_wd.text()), 
                        int(self.in_harga_we.text()), self.in_stok.value(), random_filename)
                
                cursor.execute(sql, vals)
                conn.commit()
                conn.close()
                
                self.refresh_action()
                QtWidgets.QMessageBox.information(self, "Sukses", "Data dan Gambar berhasil disimpan!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Gagal: {e}")

    def update_room(self):
        if not self.selected_id:
            QtWidgets.QMessageBox.warning(self, "Pilih Data", "Klik baris di tabel dulu!")
            return
            
        try:
            new_path = self.in_file_name.text() # Path baru dari browse
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Cek apakah user memilih gambar baru (path lokal) atau tetap gambar lama
            # Jika path mengandung folder "assets", berarti user tidak mengganti gambar
            if "assets" not in new_path and os.path.exists(new_path):
                # --- PROSES GANTI GAMBAR ---
                
                # 1. Hapus gambar lama
                cursor.execute("SELECT file_name FROM rooms WHERE id_room = %s", (self.selected_id,))
                old_file = cursor.fetchone()[0]
                old_path = os.path.join("assets", old_file)
                if os.path.exists(old_path):
                    os.remove(old_path)

                # 2. Upload gambar baru
                file_ext = os.path.splitext(new_path)[1]
                random_filename = f"{uuid.uuid4()}{file_ext}"
                shutil.copy2(new_path, os.path.join("assets", random_filename))
                final_filename = random_filename
            else:
                # User tidak mengganti gambar, ambil nama file yang lama saja
                cursor.execute("SELECT file_name FROM rooms WHERE id_room = %s", (self.selected_id,))
                final_filename = cursor.fetchone()[0]

            # 3. Update Database
            sql = """UPDATE rooms SET room_number=%s, tipe_room=%s, deskripsi_room=%s, 
                     harga_weekday=%s, harga_weekend=%s, stok=%s, file_name=%s 
                     WHERE id_room=%s"""
            vals = (self.in_room_number.text(), self.in_tipe_room.text(), self.in_desc.toPlainText(), 
                    int(self.in_harga_wd.text()), int(self.in_harga_we.text()), 
                    self.in_stok.value(), final_filename, self.selected_id)
            
            cursor.execute(sql, vals)
            conn.commit()
            conn.close()
            
            self.refresh_action()
            QtWidgets.QMessageBox.information(self, "Sukses", "Data diperbarui!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def delete_room(self):
        if not self.selected_id: return
        
        reply = QtWidgets.QMessageBox.question(self, "Hapus", "Yakin hapus data ini?", 
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # 1. Cari nama file di database sebelum dihapus
                cursor.execute("SELECT file_name FROM rooms WHERE id_room = %s", (self.selected_id,))
                res = cursor.fetchone()
                
                if res:
                    filename = res[0]
                    file_path = os.path.join("assets", filename)
                    
                    # 2. Hapus file fisik jika ada
                    if os.path.exists(file_path):
                        os.remove(file_path)

                # 3. Hapus data dari database
                cursor.execute("DELETE FROM rooms WHERE id_room = %s", (self.selected_id,))
                conn.commit()
                conn.close()
                
                self.refresh_action()
                QtWidgets.QMessageBox.information(self, "Sukses", "Data dan file gambar berhasil dihapus!")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Gagal menghapus: {e}")

    def refresh_action(self):
        self.selected_id = None
        self.in_room_number.clear()
        self.in_tipe_room.clear()
        self.in_harga_wd.clear()
        self.in_harga_we.clear()
        self.in_stok.setValue(0)
        self.in_file_name.clear()
        self.in_desc.clear()
        self.lbl_preview.clear()
        self.lbl_preview.setText("Tidak ada gambar")
        self.load_data()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminHotelApp()
    window.show()
    sys.exit(app.exec_())