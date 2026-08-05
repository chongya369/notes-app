"""
设置窗口
配置服务端地址、用户名密码等
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QFrame, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from config_manager import ConfigManager


class SettingsWindow(QWidget):
    """设置窗口"""
    
    # 信号：设置已保存
    settings_saved = pyqtSignal()
    # 信号：登录成功
    login_success = pyqtSignal()
    # 信号：登出
    logout = pyqtSignal()
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config_manager = ConfigManager()
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("设置")
        self.setFixedSize(400, 650)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
            QCheckBox {
                font-size: 13px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        title = QLabel("便签设置")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 服务器设置组
        server_group = QGroupBox("服务器设置")
        server_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        server_layout = QVBoxLayout()
        server_layout.setSpacing(12)
        
        # 服务器地址
        server_layout.addWidget(QLabel("服务器地址:"))
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("例如: http://127.0.0.1:8000")
        server_layout.addWidget(self.server_input)
        
        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #666;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        test_btn.clicked.connect(self.test_connection)
        server_layout.addWidget(test_btn)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        # 用户设置组
        user_group = QGroupBox("用户设置")
        user_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        user_layout = QVBoxLayout()
        user_layout.setSpacing(12)
        
        # 用户名
        user_layout.addWidget(QLabel("用户名:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        user_layout.addWidget(self.username_input)
        
        # 密码
        user_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        user_layout.addWidget(self.password_input)
        
        # 记住密码
        self.remember_check = QCheckBox("记住密码")
        user_layout.addWidget(self.remember_check)
        
        # 自动登录
        self.auto_login_check = QCheckBox("自动登录")
        user_layout.addWidget(self.auto_login_check)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # 登录/登出按钮
        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        btn_layout.addWidget(self.login_btn)
        
        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_settings(self):
        """加载设置"""
        self.server_input.setText(self.config_manager.server_url)
        self.username_input.setText(self.config_manager.username)
        
        if self.config_manager.remember_password:
            self.password_input.setText(self.config_manager.password)
        
        self.remember_check.setChecked(self.config_manager.remember_password)
        self.auto_login_check.setChecked(self.config_manager.auto_login)
        
        # 更新登录按钮状态
        self.update_login_button()
    
    def save_settings(self):
        """保存设置"""
        self.config_manager.server_url = self.server_input.text().strip()
        self.config_manager.username = self.username_input.text().strip()
        self.config_manager.remember_password = self.remember_check.isChecked()
        self.config_manager.auto_login = self.auto_login_check.isChecked()
        
        if self.remember_check.isChecked():
            self.config_manager.password = self.password_input.text()
        else:
            self.config_manager.password = ""
        
        # 更新API客户端地址
        self.api_client.base_url = self.config_manager.server_url
        
        self.settings_saved.emit()
        QMessageBox.information(self, "成功", "设置已保存")
    
    def test_connection(self):
        """测试连接"""
        server_url = self.server_input.text().strip()
        if not server_url:
            QMessageBox.warning(self, "提示", "请输入服务器地址")
            return
        
        # 临时设置服务器地址进行测试
        original_url = self.api_client.base_url
        self.api_client.base_url = server_url
        
        if self.api_client.check_health():
            QMessageBox.information(self, "成功", "连接成功")
        else:
            QMessageBox.warning(self, "失败", "连接失败，请检查服务器地址")
        
        # 恢复原地址
        self.api_client.base_url = original_url
    
    def handle_login(self):
        """处理登录"""
        if self.api_client.token:
            # 已登录，执行登出
            self.api_client.clear_token()
            self.update_login_button()
            self.logout.emit()
            QMessageBox.information(self, "成功", "已退出登录")
            return
        
        # 执行登录
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return
        
        # 更新服务器地址
        self.api_client.base_url = self.server_input.text().strip()
        
        result = self.api_client.login(username, password)
        
        if result.get("success"):
            self.update_login_button()
            self.login_success.emit()
            self.hide()
        else:
            QMessageBox.warning(self, "失败", result.get("detail", "登录失败"))
    
    def update_login_button(self):
        """更新登录按钮状态"""
        if self.api_client.token:
            self.login_btn.setText("退出登录")
            self.login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #ee5a5a;
                }
            """)
        else:
            self.login_btn.setText("登录")
            self.login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #667eea;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5a6fd6;
                }
            """)
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        self.update_login_button()
