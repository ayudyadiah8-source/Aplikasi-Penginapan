import sys
from PyQt5.QtWidgets import QApplication
from admin.Controllers.dashboardAdminController import DashboardAdmin

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardAdmin()
    window.show()
    sys.exit(app.exec_())