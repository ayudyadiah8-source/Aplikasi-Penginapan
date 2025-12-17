from PyQt5.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QMessageBox,
)
from admin.UI.UX.dashboard_admin import Ui_DashboardAdmin
from models.usersModel import UserModel
from PyQt5.QtWidgets import QHeaderView


class DashboardAdmin(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = Ui_DashboardAdmin()
        self.ui.setupUi(self)

        self.setup_table_users()
        self.load_users()
        self.connect_signals()

    def setup_table_users(self):
        self.ui.tableUsers.setColumnCount(5)
        self.ui.tableUsers.setHorizontalHeaderLabels([
        "ID", "Username", "Role", "Nama Lengkap", "Email"
        ])

        header = self.ui.tableUsers.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.ui.tableUsers.setEditTriggers(
        self.ui.tableUsers.NoEditTriggers
        )
        self.ui.tableUsers.setSelectionBehavior(
        self.ui.tableUsers.SelectRows
        )

    def load_users(self):
        users = UserModel.get_all_users()
        self.ui.tableUsers.setRowCount(0)

        for row_index, user in enumerate(users):
            self.ui.tableUsers.insertRow(row_index)
            for col_index, value in enumerate(user):
                self.ui.tableUsers.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value) if value else "")
                )

    def connect_signals(self):
        self.ui.btnRefreshUsers.clicked.connect(self.load_users)
        # self.ui.btnDeleteUser.clicked.connect(self.delete_user)
        # self.ui.btnUpdateRole.clicked.connect(self.update_role)

    def get_selected_user_id(self):
        selected_row = self.ui.tableUsers.currentRow()
        if selected_row < 0:
            return None

        item = self.ui.tableUsers.item(selected_row, 0)
        return int(item.text())

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Peringatan", "Pilih user terlebih dahulu")
            return

        confirm = QMessageBox.question(
            self,
            "Konfirmasi",
            "Yakin ingin menghapus user ini?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            UserModel.delete_user(user_id)
            self.load_users()
            QMessageBox.information(self, "Sukses", "User berhasil dihapus")

    def update_role(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Peringatan", "Pilih user terlebih dahulu")
            return

        role = self.ui.cmbRole.currentText()
        UserModel.update_role(user_id, role)
        self.load_users()

        QMessageBox.information(
            self,
            "Sukses",
            "Role user berhasil diperbarui"
        )
