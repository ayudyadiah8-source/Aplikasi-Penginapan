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
    QPushButton { background-color: #8B4513; color: white; border-radius: 8px; padding: 10px; font-weight: bold; min-width: 120px; }
    QPushButton:hover { background-color: #A0522D; }
    QPushButton#btn_edit { background-color: #D2B48C; color: #5D4037; }
    QPushButton#btn_delete { background-color: #CD5C5C; }
    QTableWidget { background-color: white; alternate-background-color: #FFFACD; gridline-color: #D2B48C; border: 1px solid #D2B48C; }
    QHeaderView::section { background-color: #DEB887; color: white; padding: 10px; font-weight: bold; }
    QLineEdit, QComboBox { background-color: white; border: 1px solid #DEB887; border-radius: 5px; padding: 5px; }
"""

class EditUserDialog(QtWidgets.QDialog):
    """Jendela Pop-up untuk Edit Data User"""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit User - ID {data['id']}")
        self.setFixedSize(400, 400)
        self.setStyleSheet(STYLE_SHEET)
        
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        
        self.in_user = QtWidgets.QLineEdit(data['username'])
        self.in_nama = QtWidgets.QLineEdit(data['nama'])
        self.in_role = QtWidgets.QComboBox()
        self.in_role.addItems(["user", "admin"])
        self.in_role.setCurrentText(data['role'])
        self.in_email = QtWidgets.QLineEdit(data['email'])
        self.in_wa = QtWidgets.QLineEdit(data['no_wa'])
        
        form.addRow("Username:", self.in_user)
        form.addRow("Nama Lengkap:", self.in_nama)
        form.addRow("Role:", self.in_role)
        form.addRow("Email:", self.in_email)
        form.addRow("No. WA:", self.in_wa)
        
        layout.addLayout(form)
        
        self.btn_save = QtWidgets.QPushButton("Simpan Perubahan")
        self.btn_save.setObjectName("btn_edit")
        self.btn_save.clicked.connect(self.accept)
        layout.addWidget(self.btn_save)

class AdminUserManagementApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.selected_id = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("Golden Stay - Manajemen User")
        self.resize(1000, 600)
        self.setStyleSheet(STYLE_SHEET)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("👥 KELOLA DATA PENGGUNA")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #8B4513; margin: 15px;")
        self.main_layout.addWidget(header)

        # --- Tabel User ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID User", "Username", "Nama", "Role", "Email", "No. WA"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.cellClicked.connect(self.handle_selection)
        self.main_layout.addWidget(self.table)

        # --- Tombol Aksi ---
        self.btn_layout = QtWidgets.QHBoxLayout()
        
        self.btn_edit = QtWidgets.QPushButton("📝 Edit User")
        self.btn_edit.setObjectName("btn_edit")
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        
        self.btn_refresh = QtWidgets.QPushButton("🔄 Refresh Data")
        self.btn_refresh.clicked.connect(self.load_data)
        
        self.btn_delete = QtWidgets.QPushButton("🗑️ Hapus User")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_delete.clicked.connect(self.delete_user)

        self.btn_layout.addWidget(self.btn_edit)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_refresh)
        self.btn_layout.addWidget(self.btn_delete)
        self.main_layout.addLayout(self.btn_layout)

    def load_data(self):
        self.selected_id = None
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id_user, username, nama, role, email, no_wa FROM users")
                rows = cursor.fetchall()
                self.table.setRowCount(0)
                for r_idx, r_data in enumerate(rows):
                    self.table.insertRow(r_idx)
                    for c_idx, val in enumerate(r_data):
                        item = QtWidgets.QTableWidgetItem(str(val))
                        item.setTextAlignment(QtCore.Qt.AlignCenter)
                        self.table.setItem(r_idx, c_idx, item)
                conn.close()
            except Exception as e: print(f"Error: {e}")

    def handle_selection(self, row, col):
        self.selected_id = self.table.item(row, 0).text()

    def open_edit_dialog(self):
        """Mengambil data dari tabel dan membuka dialog edit"""
        if not self.selected_id:
            QtWidgets.QMessageBox.warning(self, "Pilih Data", "Pilih user yang ingin diedit!")
            return
        
        row = self.table.currentRow()
        data = {
            'id': self.table.item(row, 0).text(),
            'username': self.table.item(row, 1).text(),
            'nama': self.table.item(row, 2).text(),
            'role': self.table.item(row, 3).text(),
            'email': self.table.item(row, 4).text(),
            'no_wa': self.table.item(row, 5).text()
        }

        dialog = EditUserDialog(data, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    sql = """UPDATE users SET username=%s, nama=%s, role=%s, email=%s, no_wa=%s 
                             WHERE id_user=%s"""
                    cursor.execute(sql, (
                        dialog.in_user.text(), dialog.in_nama.text(), 
                        dialog.in_role.currentText(), dialog.in_email.text(), 
                        dialog.in_wa.text(), self.selected_id
                    ))
                    conn.commit()
                    conn.close()
                    self.load_data()
                    QtWidgets.QMessageBox.information(self, "Sukses", "Data berhasil diperbarui!")
                except Exception as ex:
                    QtWidgets.QMessageBox.critical(self, "Error", str(ex))

    def delete_user(self):
        if not self.selected_id:
            QtWidgets.QMessageBox.warning(self, "Pilih Data", "Pilih user yang akan dihapus!")
            return
        
        reply = QtWidgets.QMessageBox.question(self, "Hapus", f"Hapus User ID {self.selected_id}?", 
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id_user = %s", (self.selected_id,))
                conn.commit()
                conn.close()
                self.load_data()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminUserManagementApp()
    window.show()
    sys.exit(app.exec_())