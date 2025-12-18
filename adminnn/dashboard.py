import sys
import os
import mysql.connector
from PyQt5 import QtWidgets, QtCore, QtGui
from manajemen_kamar import AdminHotelApp
from validasi_pembayaran import AdminPaymentValidationApp
from data_pesanan import AdminBookingApp
from laporan import AdminReportApp
from kritik_saran import AdminFeedbackApp
from data_users import AdminUserManagementApp


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

# --- 2. STYLE CSS
STYLE_SHEET = """
    QWidget { background-color: #FDF5E6; font-family: 'Segoe UI'; color: #5D4037; }
    #sidebar { background-color: #8B4513; min-width: 240px; }
    #sidebar QPushButton { 
        background-color: transparent; border: none; color: white; 
        text-align: left; padding: 15px; font-size: 17px; border-bottom: 1px solid #A0522D;
    }
    #sidebar QPushButton:hover { background-color: #A0522D; }
    #sidebar QPushButton#btn_logout { background-color: #CD5C5C; margin-top: 20px; font-weight: bold; }
    QLabel#header_title { font-size: 24px; font-weight: bold; color: #8B4513; margin-bottom: 15px; }
    QTableWidget { background-color: white; gridline-color: #D2B48C; border-radius: 4px; }
    QHeaderView::section { background-color: #DEB887; color: white; font-weight: bold; padding: 5px; }
    QPushButton#action_btn { background-color: #8B4513; color: white; border-radius: 5px; padding: 10px; font-weight: bold; }
    QPushButton#danger_btn { background-color: #CD5C5C; color: white; border-radius: 5px; padding: 10px; font-weight: bold; }
    QPushButton#success_btn { background-color: #2E7D32; color: white; border-radius: 5px; padding: 10px; font-weight: bold; }
"""

class AdminDashboard(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pandawa Admin Dashboard")
        self.resize(1300, 850)
        self.setStyleSheet(STYLE_SHEET)
        self.selected_id = None

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()
        self.setup_content_stack()

    def setup_sidebar(self):
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setObjectName("sidebar")
        side_lay = QtWidgets.QVBoxLayout(self.sidebar)

        title = QtWidgets.QLabel("🏨 Hotel Pandawa")
        title.setStyleSheet("color: black; font-size: 20px; font-weight: bold; padding: 20px;")
        side_lay.addWidget(title)

        # Nama Sidebar Sesuai Permintaan
        self.menus = [
            ("🛏️ Manajemen Kamar", 0),
            ("💳 Validasi Pembayaran", 1),
            ("📅 Data Pemesanan", 2),
            ("📊 Laporan", 3),
            ("💬 Kritik dan Saran", 4),
            ("👥 Data User", 5)
        ]

        for text, index in self.menus:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(lambda checked, i=index: self.change_page(i))
            side_lay.addWidget(btn)

        side_lay.addStretch()

        btn_logout = QtWidgets.QPushButton("🚪 LOG OUT")
        btn_logout.setObjectName("btn_logout")
        btn_logout.clicked.connect(self.handle_logout)
        side_lay.addWidget(btn_logout)

        self.main_layout.addWidget(self.sidebar)

    def setup_content_stack(self):
        self.stack = QtWidgets.QStackedWidget()
        
        self.page_kamar_widget = AdminHotelApp()
        self.page_validasi_pembayaran = AdminPaymentValidationApp()
        self.page_data_pemesanan = AdminBookingApp()
        self.pages_laporan = AdminReportApp()
        self.page_kritik_saran = AdminFeedbackApp()
        self.page_data_users = AdminUserManagementApp()
        
        self.stack.addWidget(self.page_kamar_widget) # Index 0
        self.stack.addWidget(self.page_validasi_pembayaran) # Index 1
        self.stack.addWidget(self.page_data_pemesanan) # Index 2
        self.stack.addWidget(self.pages_laporan) # Index 3
        self.stack.addWidget(self.page_kritik_saran) # Index 4
        self.stack.addWidget(self.page_data_users) # Index 5
        

        self.main_layout.addWidget(self.stack)

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        self.selected_id = None
        
        if index == 0:
            self.page_kamar_widget.load_data()
        elif index == 1:
            self.page_validasi_pembayaran.load_data()
        elif index == 2:
            self.page_data_pemesanan.load_data()
        elif index == 3:
            self.pages_laporan.load_report_data()
        elif index == 4:
            self.page_kritik_saran.load_data()
        elif index == 5:
            self.page_data_users.load_data()

    # --- 0. MANAJEMEN KAMAR ---
    def page_kamar(self):
        return self.page_kamar_widget

    # --- 1. VALIDASI PEMBAYARAN ---
    def page_pembayaran(self):
        return self.page_validasi_pembayaran

    # --- 2. DATA PEMESANAN ---
    def page_booking(self):
        return self.page_data_pemesanan

    # --- 3. LAPORAN ---
    def page_laporan(self):
        return self.pages_laporan

    # --- 4. KRITIK DAN SARAN ---
    def page_kritik(self):
        return self.page_kritik_saran

    # --- 5. DATA USER ---
    def page_user(self):
        return self.page_data_users

    # --- HELPER FUNCTIONS ---
    def fill_table(self, table, rows):
        table.setRowCount(0)
        for r_idx, r_data in enumerate(rows):
            table.insertRow(r_idx)
            for c_idx, val in enumerate(r_data):
                table.setItem(r_idx, c_idx, QtWidgets.QTableWidgetItem(str(val)))

    def get_id(self, row, table):
        self.selected_id = table.item(row, 0).text()

    def handle_logout(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setText("Apakah anda yakin ingin keluar?")
        btn_logout = msg.addButton("Logout", QtWidgets.QMessageBox.AcceptRole)
        msg.addButton("Batal", QtWidgets.QMessageBox.RejectRole)
        btn_logout.setStyleSheet("background-color: #CD5C5C; color: white;")
        msg.exec_()
        if msg.clickedButton() == btn_logout: self.close()

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Konfirmasi Keluar',
            "Apakah Anda yakin ingin menutup aplikasi?", 
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
            QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept() # Menutup aplikasi
        else:
            event.ignore() # Membatalkan penutupan

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())