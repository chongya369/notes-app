from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from api_client import APIClient


class LoginWindow(QWidget):
    """登录窗口"""

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("便签小程序 - 登录")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
            QPushButton {
                padding: 10px;
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #667eea;
                color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title_label = QLabel("便签小程序")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 标签页
        tab_widget = QTabWidget()

        # 登录标签页
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        login_layout.setSpacing(15)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("用户名")
        login_layout.addWidget(self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("密码")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        login_layout.addWidget(self.login_password)

        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(login_btn)

        login_tab.setLayout(login_layout)
        tab_widget.addTab(login_tab, "登录")

        # 注册标签页
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        register_layout.setSpacing(15)

        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("用户名 (至少3位)")
        register_layout.addWidget(self.register_username)

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("密码 (至少6位)")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addWidget(self.register_password)

        self.register_key = QLineEdit()
        self.register_key.setPlaceholderText("注册密钥（如有）")
        register_layout.addWidget(self.register_key)

        register_btn = QPushButton("注册")
        register_btn.clicked.connect(self.handle_register)
        register_layout.addWidget(register_btn)

        register_tab.setLayout(register_layout)
        tab_widget.addTab(register_tab, "注册")

        layout.addWidget(tab_widget)
        self.setLayout(layout)

        # 检查服务器
        if not self.api_client.check_health():
            QMessageBox.warning(
                self,
                "提示",
                "后端服务未启动，请先启动后端服务:\npython backend/main.py"
            )

    def handle_login(self):
        """处理登录"""
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return

        result = self.api_client.login(username, password)

        if result.get("success"):
            QMessageBox.information(self, "成功", "登录成功")
            self.close()
            # 发送登录成功信号（由主窗口处理）
            self.parent().show_main_window()
        else:
            QMessageBox.warning(self, "失败", result.get("detail", "登录失败"))

    def handle_register(self):
        """处理注册"""
        username = self.register_username.text().strip()
        password = self.register_password.text().strip()
        key = self.register_key.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "提示", "用户名至少3位")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "提示", "密码至少6位")
            return

        result = self.api_client.register(username, password, key)

        if "message" in result:
            QMessageBox.information(self, "成功", "注册成功，请登录")
            self.findChild(QTabWidget).setCurrentIndex(0)
            self.login_username.setText(username)
            self.register_username.clear()
            self.register_password.clear()
            self.register_key.clear()
        else:
            QMessageBox.warning(self, "失败", result.get("detail", "注册失败"))
