import sys
import os
import mysql.connector
from PyQt5 import QtWidgets, QtCore, QtGui
from fpdf import FPDF

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
    QGroupBox { font-weight: bold; border: 2px solid #D2B48C; border-radius: 10px; background-color: #FFF8DC; margin-top: 10px; }
    QLabel#stat_val { font-size: 20px; font-weight: bold; color: #8B4513; }
    QPushButton { background-color: #8B4513; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
    QPushButton:hover { background-color: #A0522D; }
    QPushButton#btn_pdf { background-color: #CD5C5C; }
    QTableWidget { background-color: white; gridline-color: #D2B48C; border-radius: 5px; }
    QHeaderView::section { background-color: #DEB887; color: white; font-weight: bold; padding: 5px; }
    QDateEdit { background-color: white; border: 1px solid #D2B48C; padding: 5px; border-radius: 4px; }
"""

class AdminReportApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Golden Stay - Laporan Pendapatan")
        self.resize(1100, 800)
        self.setStyleSheet(STYLE_SHEET)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # --- Filter Periode ---
        filter_box = QtWidgets.QGroupBox("Filter Periode Laporan")
        filter_lay = QtWidgets.QHBoxLayout()
        
        self.date_start = QtWidgets.QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QtCore.QDate.currentDate().addMonths(-1))
        
        self.date_end = QtWidgets.QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QtCore.QDate.currentDate())
        
        self.btn_generate = QtWidgets.QPushButton("📊 Generate Laporan")
        self.btn_generate.clicked.connect(self.load_report_data)
        
        self.btn_export = QtWidgets.QPushButton("📕 Export PDF")
        self.btn_export.setObjectName("btn_pdf")
        self.btn_export.clicked.connect(self.export_to_pdf)

        filter_lay.addWidget(QtWidgets.QLabel("Dari:"))
        filter_lay.addWidget(self.date_start)
        filter_lay.addWidget(QtWidgets.QLabel("Sampai:"))
        filter_lay.addWidget(self.date_end)
        filter_lay.addSpacing(20)
        filter_lay.addWidget(self.btn_generate)
        filter_lay.addWidget(self.btn_export)
        filter_box.setLayout(filter_lay)
        self.main_layout.addWidget(filter_box)

        # --- Ringkasan Statistik (Cards) ---
        stats_layout = QtWidgets.QHBoxLayout()
        self.card_total_order = self.create_stat_card("Total Pesanan", "0")
        self.card_total_income = self.create_stat_card("Total Pendapatan", "Rp 0")
        self.card_best_room = self.create_stat_card("Kamar Terlaris", "-")
        
        stats_layout.addWidget(self.card_total_order)
        stats_layout.addWidget(self.card_total_income)
        stats_layout.addWidget(self.card_best_room)
        self.main_layout.addLayout(stats_layout)

        # --- Tabel Laporan ---
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID Laporan", "ID Booking", "ID User", "ID Room", "Pendapatan"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

    def create_stat_card(self, title, value):
        box = QtWidgets.QGroupBox(title)
        lay = QtWidgets.QVBoxLayout()
        lbl = QtWidgets.QLabel(value)
        lbl.setObjectName("stat_val")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(lbl)
        box.setLayout(lay)
        box.value_label = lbl 
        return box

    def load_report_data(self):
        tgl_mulai = self.date_start.date().toString("yyyy-MM-dd")
        tgl_selesai = self.date_end.date().toString("yyyy-MM-dd")
        
        conn = get_db_connection()
        if not conn: return
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT l.id_laporan, l.id_booking, l.id_user, l.id_room, l.pendapatan 
                FROM laporan l
                JOIN booking b ON l.id_booking = b.id_booking
                WHERE b.tgl_booking BETWEEN %s AND %s
            """
            cursor.execute(query, (tgl_mulai, tgl_selesai))
            rows = cursor.fetchall()
            
            self.table.setRowCount(0)
            total_income = 0
            room_counts = {}

            for r_idx, r_data in enumerate(rows):
                self.table.insertRow(r_idx)
                total_income += float(r_data[4])
                
                # Hitung Kamar Terlaris
                id_room = r_data[3]
                room_counts[id_room] = room_counts.get(id_room, 0) + 1
                
                for c_idx, val in enumerate(r_data):
                    text = f"Rp {val:,.0f}" if c_idx == 4 else str(val)
                    item = QtWidgets.QTableWidgetItem(text)
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table.setItem(r_idx, c_idx, item)

            # Update Stat Cards
            self.card_total_order.value_label.setText(str(len(rows)))
            self.card_total_income.value_label.setText(f"Rp {total_income:,.0f}")
            
            if room_counts:
                best_room = max(room_counts, key=room_counts.get)
                self.card_best_room.value_label.setText(f"Room ID: {best_room}")
            else:
                self.card_best_room.value_label.setText("-")

            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Gagal memuat laporan: {e}")

    def export_to_pdf(self):
        if self.table.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "Peringatan", "Tidak ada data untuk diekspor. Silakan generate laporan terlebih dahulu.")
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Simpan Laporan", "Laporan_Pendapatan.pdf", "PDF Files (*.pdf)")
        if not path: return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            
            # Judul Laporan
            pdf.cell(190, 10, "LAPORAN PENDAPATAN GOLDEN STAY", ln=True, align='C')
            pdf.set_font("Arial", '', 12)
            pdf.cell(190, 10, f"Periode: {self.date_start.date().toString('dd/MM/yyyy')} - {self.date_end.date().toString('dd/MM/yyyy')}", ln=True, align='C')
            pdf.ln(10)

            # Header Tabel
            pdf.set_fill_color(222, 184, 135) # Warna DEB887
            pdf.set_font("Arial", 'B', 10)
            headers = ["ID Lap", "ID Book", "ID User", "ID Room", "Pendapatan"]
            widths = [25, 30, 30, 30, 75]
            
            for i in range(len(headers)):
                pdf.cell(widths[i], 10, headers[i], 1, 0, 'C', True)
            pdf.ln()

            # Data Tabel
            pdf.set_font("Arial", '', 10)
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    val = self.table.item(row, col).text()
                    pdf.cell(widths[col], 10, val, 1, 0, 'C')
                pdf.ln()

            # Ringkasan
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(100, 10, f"Total Pesanan: {self.card_total_order.value_label.text()}")
            pdf.ln(7)
            pdf.cell(100, 10, f"Total Pendapatan: {self.card_total_income.value_label.text()}")

            pdf.output(path)
            QtWidgets.QMessageBox.information(self, "Selesai", f"Laporan berhasil diekspor ke:\n{path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error PDF", f"Gagal mengekspor PDF: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminReportApp()
    window.show()
    sys.exit(app.exec_())