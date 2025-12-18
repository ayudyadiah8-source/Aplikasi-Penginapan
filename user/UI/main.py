import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

try:
    from config.db_connect import get_connection
    print("Berhasil mengimpor koneksi database.")
except ImportError as e:
    print(f"Gagal mengimpor: {e}")

# Sekarang baru panggil import-nya
from config.db_connect import get_connection

import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QMainWindow, QFileDialog, QLabel, QPushButton, QFrame, QHBoxLayout
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6 import QtWidgets

try:
    from config.db_connect import get_connection
except ImportError:
    print("Folder 'config' atau file 'db_connect.py' tidak ditemukan!")

# FIX PATH PROJECT

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.append(BASE_DIR)

from tampilan_awal import Ui_WelcomeForm
from login import Ui_LoginForm
from dashboard_user_ui import Ui_DashboardAdmin
from register import Ui_RegisterForm
from book_deluxe_ui import Ui_MainWindow
from popup_pembayaran_ui import Ui_Pembayaran
from rating import Ui_RatingForm


# =========================
#   TAMPILAN AWAL (WELCOME)
# =========================
class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_WelcomeForm()
        self.ui.setupUi(self)

        self.ui.btnLogin.clicked.connect(self.goToLogin)
        
        # Hubungkan tombol Register jika ada di halaman Welcome
        if hasattr(self.ui, 'btnRegister'):
            self.ui.btnRegister.clicked.connect(self.goToRegister)

    def goToLogin(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()

    # Pastikan fungsi ini ada agar WelcomeScreen bisa pindah ke Register
    def goToRegister(self, event=None):
        self.reg = RegisterWindow()
        self.reg.show()
        self.close()

# =========================
#           LOGIN
# =========================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginForm()
        self.ui.setupUi(self)

        # Menghubungkan tombol login
        self.ui.btnLogin.clicked.connect(self.validateLogin)

        if hasattr(self.ui, 'lblFooter'): 
            self.ui.lblFooter.setCursor(Qt.CursorShape.PointingHandCursor)
            self.ui.lblFooter.mousePressEvent = self.goToRegister

    def validateLogin(self):
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan Password wajib diisi!")
            return

        conn = None 
        cursor = None

        try:
            conn = get_connection()
            if conn.is_connected():
                cursor = conn.cursor()
                
                # Query untuk mencari user
                query = "SELECT id_user FROM users WHERE username = %s AND password = %s"
                cursor.execute(query, (username, password))
                result = cursor.fetchone()

                if result:
                    user_id = result[0] 
                    self.goToDashboard(user_id)
                else:
                    QMessageBox.warning(self, "Login Gagal", "Username atau Password salah!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error Database", f"Koneksi gagal: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def goToDashboard(self, user_id):
        self.dashboard = DashboardWindow(user_id) 
        self.dashboard.show()
        self.close()

    def goToRegister(self, event):
        self.reg = RegisterWindow()
        self.reg.show()
        self.close()


# =========================
#        REGISTRASI
# =========================
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterForm()
        self.ui.setupUi(self)
        
        # Menghubungkan tombol daftar ke fungsi prosesRegister
        self.ui.btnRegister.clicked.connect(self.prosesRegister)
        
        # Link untuk kembali ke login
        self.ui.lblStatus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ui.lblStatus.mousePressEvent = self.goToLogin

    def goToLogin(self, event=None): # Gunakan indentasi 1 tab/4 spasi
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def prosesRegister(self): # Hapus definisi ganda sebelumnya, gunakan yang ini
        username = self.ui.txtUsername.text()
        password = self.ui.txtPassword.text()
        nama = self.ui.txtNama.text()
        email = self.ui.txtEmail.text()
        wa = self.ui.txtWA.text()

        if not username or not password or not nama:
            QMessageBox.warning(self, "Gagal", "Data penting wajib diisi!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Pastikan kolom di database Anda sesuai: username, password, nama, email, no_wa
            query = "INSERT INTO users (username, password, nama, email, no_wa) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (username, password, nama, email, wa))
            conn.commit()
            
            QMessageBox.information(self, "Berhasil", "Registrasi Berhasil! Silakan Login.")
            self.goToLogin()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal Daftar: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()


# =========================
#        DASHBOARD USER
# =========================
class DashboardWindow(QWidget):
    def __init__(self, user_id): 
        super().__init__()
        self.ui = Ui_DashboardAdmin()
        self.ui.setupUi(self)
        self.user_id = user_id 

        # --- KONFIGURASI FOTO PROFIL ---
        self.ui.label_30.setFixedSize(100, 100)
        self.ui.label_30.setScaledContents(True)
        self.ui.label_30.setStyleSheet("border: 2px solid #8A2BE2; background-color: #f0f0f0;")
        self.ui.label_30.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ui.label_30.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ui.label_30.mousePressEvent = self.trigger_upload
        
        self.lbl_info_foto = QLabel("Klik kotak untuk upload", self.ui.tabUsers)
        self.lbl_info_foto.setStyleSheet("font-size: 8pt; color: blue; text-decoration: underline;")
        self.lbl_info_foto.setGeometry(10, 60, 130, 20)
        self.lbl_info_foto.mousePressEvent = self.trigger_upload
        
        self.lbl_hapus_foto = QLabel("| Hapus Foto", self.ui.tabUsers)
        self.lbl_hapus_foto.setStyleSheet("font-size: 8pt; color: red; text-decoration: underline; margin-left: 5px;")
        self.lbl_hapus_foto.setGeometry(140, 60, 80, 20)
        self.lbl_hapus_foto.mousePressEvent = self.hapus_foto

        # --- TAMBAHKAN TOMBOL RATING DI UI ---
        # Membuat tombol Rating secara dinamis di sebelah tombol Simpan Perubahan
        self.btnRating = QPushButton("Rating", self.ui.tabUsers)
        self.btnRating.setMinimumSize(QtCore.QSize(100, 35))
        self.btnRating.setStyleSheet("background-color: #FFFF00; color: black; font-weight: bold; border-radius: 8px;")
        
        # Menambahkan tombol ke layout (asumsi layoutButtonsUsers adalah QHBoxLayout di bawah profil)
        self.ui.layoutButtonsUsers.addWidget(self.btnRating)
        
        # Hubungkan klik tombol ke fungsi
        self.btnRating.clicked.connect(self.openRating)

        # --- KONFIGURASI LOGOUT ---
        self.ui.btnDeleteUser.clicked.connect(self.logout)

        # MUAT DATA PROFIL (PENTING: Sekarang fungsi ini dikenali oleh self)
        self.load_user_data()

        # HUBUNGKAN TOMBOL SIMPAN
        self.ui.btnAddUser.clicked.connect(self.simpan_perubahan)

        # --- KONFIGURASI UPLOAD BUKTI ---
        # Pastikan label_35 (teks biru) bisa merespons klik mouse
        self.ui.label_35.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ui.label_35.mousePressEvent = self.upload_bukti_pembayaran

        # --- TOMBOL PESAN (12 Tombol) ---
        self.tombol_kamar = [
            self.ui.btnPrice2, self.ui.btnPrice2_2, self.ui.btnPrice2_7,
            self.ui.btnPrice2_6, self.ui.btnPrice2_3, self.ui.btnPrice2_5,
            self.ui.btnPrice2_16, self.ui.btnPrice2_11, self.ui.btnPrice2_10,
            self.ui.btnPrice2_9, self.ui.btnPrice2_8, self.ui.btnPrice2_4
        ]

        for index, btn in enumerate(self.tombol_kamar):
            id_kamar_db = index + 1
            btn.setProperty("id_room", id_kamar_db) 
            btn.clicked.connect(self.openBooking)

    # SEMUA FUNGSI DI BAWAH INI HARUS MENJOROK KE DALAM (1 TAB/4 SPASI)
    def load_user_data(self):
        """Mengambil data user dari database dan menampilkannya di profil dashboard"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "SELECT nama, email, no_wa, username, password FROM users WHERE id_user = %s"
            cursor.execute(query, (self.user_id,))
            user = cursor.fetchone()

            if user:
                # Mengisi field input secara otomatis meskipun awalnya kosong di DB
                self.ui.lineEdit.setText(str(user[0]) if user[0] else "")   
                self.ui.lineEdit_2.setText(str(user[1]) if user[1] else "") 
                self.ui.lineEdit_3.setText(str(user[2]) if user[2] else "") 
                self.ui.lineEdit_4.setText(str(user[3]) if user[3] else "") 
                self.ui.lineEdit_5.setText(str(user[4]) if user[4] else "") 
        except Exception as e:
            print(f"Error memuat profil: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def simpan_perubahan(self):
        """Menyimpan pembaruan data profil ke database"""
        nama = self.ui.lineEdit.text()
        email = self.ui.lineEdit_2.text()
        telp = self.ui.lineEdit_3.text()
        username = self.ui.lineEdit_4.text()
        password = self.ui.lineEdit_5.text()

        if not nama or not username or not password:
            QMessageBox.warning(self, "Peringatan", "Nama, Username, dan Password wajib diisi!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = """UPDATE users SET nama=%s, email=%s, no_wa=%s, 
                       username=%s, password=%s WHERE id_user=%s"""
            cursor.execute(query, (nama, email, telp, username, password, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Sukses", "Profil Anda berhasil diperbarui!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def hapus_foto(self, event):
        reply = QMessageBox.question(self, "Hapus Foto", "Hapus foto profil?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.ui.label_30.clear()
            self.ui.label_30.setText("Foto Profil")

    def logout(self):
        reply = QMessageBox.question(self, "Logout", "Yakin ingin keluar?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.welcome = WelcomeScreen()
            self.welcome.show()
            self.close()

    def trigger_upload(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.ui.label_30.setPixmap(QPixmap(file_path))

    def openBooking(self):
        btn = self.sender()
        id_room = btn.property("id_room") 
        if id_room:
            # Kirim id_room DAN user_id ke BookingWindow
            self.booking_window = BookingWindow(id_room, self.user_id) 
            self.booking_window.show()

    # PERBAIKAN: Fungsi ini sekarang masuk ke dalam lingkup class (Indented)
    def openRating(self):
        """Membuka window rating.py sebagai dialog pop-up"""
        self.rating_popup = RatingWindow(self)
        self.rating_popup.exec()
    
    def upload_bukti_pembayaran(self, event):
            """Membuka file dialog dan menampilkan gambar sesuai proporsi aslinya"""
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Pilih Bukti Pembayaran", "", "Image Files (*.png *.jpg *.jpeg)"
            )
            
            if file_path:
                pixmap = QPixmap(file_path)
                
                # Mengatur gambar agar mengikuti ukuran label_33 tapi tetap menjaga proporsi (KeepAspectRatio)
                # Ini mencegah gambar terlihat gepeng seperti pada contoh sebelumnya
                scaled_pixmap = pixmap.scaled(
                    self.ui.label_33.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                
                self.ui.label_33.setPixmap(scaled_pixmap)
                self.ui.label_33.setAlignment(Qt.AlignmentFlag.AlignCenter) # Gambar di tengah kotak
                
                # Sembunyikan instruksi awal
                self.ui.label_35.hide()
                self.ui.label_34.hide()
                
                # Tampilkan tombol navigasi tambahan (Ganti & Hapus)
                self.show_photo_controls()

    def show_photo_controls(self):
        """Menampilkan teks interaktif untuk Ganti dan Hapus foto di bawah gambar"""
        # Cek jika label kontrol sudah ada agar tidak duplikat
        if not hasattr(self, 'lbl_photo_controls'):
            self.lbl_photo_controls = QLabel(self.ui.tab)
            self.lbl_photo_controls.setGeometry(250, 385, 300, 20) # Sesuaikan posisi di bawah label_33
            self.lbl_photo_controls.setStyleSheet("font-size: 9pt; font-weight: bold;")
            self.lbl_photo_controls.setText(
                "<a href='ganti' style='color: blue; text-decoration: none;'>Ganti Foto</a> | "
                "<a href='hapus' style='color: red; text-decoration: none;'>Hapus Foto</a>"
            )
            self.lbl_photo_controls.setOpenExternalLinks(False)
            self.lbl_photo_controls.linkActivated.connect(self.handle_photo_link)
        
        self.lbl_photo_controls.show()

    def handle_photo_link(self, link):
        """Menangani klik pada link Ganti atau Hapus"""
        if link == "ganti":
            self.upload_bukti_pembayaran(None)
        elif link == "hapus":
            reply = QMessageBox.question(self, "Hapus Bukti", "Yakin ingin menghapus bukti ini?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.ui.label_33.clear()
                self.ui.label_33.setPixmap(QPixmap()) # Kosongkan
                self.ui.label_35.show() # Munculkan teks instruksi lagi
                self.ui.label_34.show()
                self.lbl_photo_controls.hide()


# =========================
#    HALAMAN BOOKING
# =========================
class BookingWindow(QMainWindow):
    def __init__(self, id_room, user_id): 
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.id_room = id_room
        self.user_id = user_id 
        
        # PANGGIL FUNGSI UNTUK MENGISI DATA
        self.display_room_details()

        # Hubungkan tombol Lanjutkan Membayar (pushButton)
        self.ui.pushButton.clicked.connect(self.openPayment)
        
        # Hubungkan tombol Kembali (pushButton_2)
        self.ui.pushButton_2.clicked.connect(self.backToDashboard)

    def display_room_details(self):
        """Mengambil data kamar dari database dan menampilkannya di Label UI"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True) # Gunakan dictionary agar mudah akses kolom
            
            # Query untuk mengambil nama tipe kamar dan harga
            query = "SELECT tipe_room, harga_weekday FROM rooms WHERE id_room = %s"
            cursor.execute(query, (self.id_room,))
            room = cursor.fetchone()

            if room:
                # 1. Tampilkan Tipe Kamar di label_10
                self.ui.label_10.setText(f"{room['tipe_room']} (1 Kamar)")
                
                # 2. Tampilkan Harga di label_8 dengan format Rupiah
                harga_format = f"Rp.{room['harga_weekday']:,}".replace(",", ".")
                self.ui.label_8.setText(harga_format)

                # 3. Logika Stok Habis
                if room['stok'] <= 0:
                    # Sembunyikan tombol Lanjutkan Membayar jika stok 0
                    self.ui.pushButton.hide() 
                    # Opsional: Ubah teks harga menjadi 'Stok Habis' agar user tahu
                    self.ui.label_8.setText("STOK HABIS")
                    self.ui.label_8.setStyleSheet("color: red; font-weight: bold; background-color: rgb(170, 170, 127);")
                else:
                    # Pastikan tombol muncul jika stok tersedia
                    self.ui.pushButton.show()
                
        except Exception as e:
            print(f"Gagal memuat detail kamar: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def backToDashboard(self):
        # Membuka Dashboard dengan sesi user_id yang aktif
        self.dashboard = DashboardWindow(self.user_id)
        
        # Mengatur agar dashboard langsung menampilkan Tab "Daftar Kamar" (Index 0)
        self.dashboard.ui.tabAdmin.setCurrentIndex(0)
        
        self.dashboard.show()
        self.close()

    def openPayment(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Simpan booking dengan id_user dan id_room agar tidak error 1452
            query = "INSERT INTO booking (id_user, id_room, status_bayar) VALUES (%s, %s, %s)"
            cursor.execute(query, (self.user_id, self.id_room, "pending")) 
            conn.commit()
            
            booking_id = cursor.lastrowid
            
            # Munculkan Popup Pembayaran
            self.payment_window = PaymentPopup(booking_id)
            self.payment_window.show()
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal memproses pesanan: {e}")


# =========================
#    POPUP PEMBAYARAN
# =========================
class PaymentPopup(QWidget):
    def __init__(self, booking_id): # Menerima booking_id
        super().__init__()
        self.ui = Ui_Pembayaran()
        self.ui.setupUi(self)
        self.booking_id = booking_id
        self.sisa_waktu = 30 * 60  # 30 menit dalam detik

        # Timer Hitung Mundur
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000) # Update setiap 1 detik

        # Timer Cek Verifikasi Admin (Cek database setiap 5 detik)
        self.check_db_timer = QTimer(self)
        self.check_db_timer.timeout.connect(self.check_status_database)
        self.check_db_timer.start(5000) 

        self.ui.btnKembali.clicked.connect(self.close)

    def update_timer(self):
        self.sisa_waktu -= 1
        menit = self.sisa_waktu // 60
        detik = self.sisa_waktu % 60
        
        self.ui.labelTitle.setText(f"Selesaikan Pembayaran: {menit:02d}:{detik:02d}")

        if self.sisa_waktu <= 0:
            self.handle_expired()

    def check_status_database(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Gunakan id_booking sesuai struktur tabel database Anda
            query = "SELECT status_bayar FROM booking WHERE id_booking = %s"
            cursor.execute(query, (self.booking_id,))
            result = cursor.fetchone()

            if result and result[0] == 'lunas':
                self.timer.stop()
                self.check_db_timer.stop()
                QMessageBox.information(self, "Berhasil", "Pembayaran telah diverifikasi admin!")
                self.close()
        except Exception as e:
            print(f"Error cek DB: {e}")


    def handle_expired(self):
        self.timer.stop()
        self.check_db_timer.stop()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            query = "UPDATE booking SET status_bayar = 'expired' WHERE id_booking = %s"
            cursor.execute(query, (self.booking_id,))
            conn.commit()
            QMessageBox.warning(self, "Waktu Habis", "Waktu pembayaran habis, pesanan dibatalkan.")
            self.close()
        except Exception as e:
            print(f"Gagal update expired: {e}")


# =========================
#      WINDOW RATING
# =========================
class RatingWindow(QtWidgets.QDialog):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.ui = Ui_RatingForm()
        self.ui.setupUi(self)
        self.parent_dashboard = parent_dashboard

        # Hubungkan Tombol
        self.ui.btnSubmit.clicked.connect(self.prosesKirim)
        self.ui.btnCancel.clicked.connect(self.prosesBatal)

    def prosesKirim(self):
        # Pop up konfirmasi kirim
        reply = QMessageBox.question(self, "Konfirmasi", "Yakin ingin mengirim rating?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Di sini Anda bisa menambahkan logika simpan ke Database jika diperlukan
            QMessageBox.information(self, "Berhasil", "Selamat, rating telah dikirim!")
            self.accept() # Menutup window rating dan kembali ke dashboard

    def prosesBatal(self):
        # Pop up konfirmasi batal
        reply = QMessageBox.question(self, "Konfirmasi Batal", "Yakin batal? Rating tidak akan disimpan.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.reject() # Menutup window tanpa menyimpan


# =========================
#        MAIN APP
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    welcome = WelcomeScreen()
    welcome.show()

    sys.exit(app.exec())


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
