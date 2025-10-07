from Frontend.src.Login.user_interface import LoginWindow
from Frontend.src.Admin.Dashboard.admin_dashboard import AdminDashboard
from Frontend.src.Coordinator.Dashboard.CoordinatorDashboard import CoordinatorDashboard

class AppController:
    def __init__(self):
        self.login_window = LoginWindow(controller=self)
        self.login_window.show()

    def on_login_success(self, user_info):
        role = user_info.get("role")

        self.login_window.close()

        if role == "admin":
            self.dashboard = AdminDashboard(user_info=user_info, controller=self)
        elif role == "coordinator":
            self.dashboard = CoordinatorDashboard(user_info=user_info, controller=self)
        else:
            raise ValueError(f"Bilinmeyen rol: {role}")

        self.dashboard.show()

    def logout(self):
        # Dashboard’ı kapat, yeni login ekranını aç
        self.dashboard.close()
        self.login_window = LoginWindow(controller=self)
        self.login_window.show()
