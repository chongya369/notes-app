"""
便签Windows客户端 - 主程序入口
支持多便签窗口、系统托盘、置顶显示等功能
"""
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from typing import Dict, List
import traceback

from api_client import APIClient
from config_manager import ConfigManager
from note_window import NoteWindow
from note_list_window import NoteListWindow
from settings_window import SettingsWindow
from tray_manager import TrayManager, TraySignalEmitter


def setup_font(app):
    """设置全局字体，确保中文正常显示"""
    font_families = [
        "Microsoft YaHei",
        "SimHei",
        "Microsoft JhengHei",
        "SimSun",
        "Arial"
    ]
    
    for font_name in font_families:
        try:
            font = QFont(font_name, 10)
            if font.exactMatch():
                app.setFont(font)
                return
        except:
            continue
    
    app.setFont(QFont("Arial", 10))


class NoteAppController:
    """便签应用控制器"""
    
    def __init__(self):
        """初始化应用控制器"""
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.config_manager = ConfigManager()
        self.api_client = APIClient(self.config_manager.server_url)
        
        self.note_windows: Dict[int, NoteWindow] = {}
        self.note_list_window = None
        self.settings_window = None
        
        # 创建托盘信号发射器（必须在主线程中创建）
        self.tray_signal = TraySignalEmitter()
        self.tray_signal.show_notes.connect(self.show_all_notes)
        self.tray_signal.hide_notes.connect(self.hide_all_notes)
        self.tray_signal.new_note.connect(self.create_new_note)
        self.tray_signal.note_list.connect(self.show_note_list)
        self.tray_signal.quit_app.connect(self.quit_app)
        
        self.tray_manager = TrayManager(self.tray_signal)
        self.is_logged_in = False
    
    def run(self):
        """运行应用"""
        try:
            self.tray_manager.run_detached()
            
            if self.config_manager.auto_login:
                self.auto_login()
            
            if not self.is_logged_in:
                self.show_settings()
            
            return self.app.exec()
        except Exception as e:
            print(f"应用启动失败: {e}")
            traceback.print_exc()
            return 1
    
    def auto_login(self):
        """尝试自动登录"""
        username = self.config_manager.username
        password = self.config_manager.password
        
        if username and password:
            result = self.api_client.login(username, password)
            if result.get("success"):
                self.is_logged_in = True
                self.load_notes()
    
    def load_notes(self):
        """加载便签"""
        if not self.api_client.token:
            return
        
        notes = self.api_client.get_notes()
        
        for note_window in list(self.note_windows.values()):
            note_window.close()
        self.note_windows.clear()
        
        for note in notes:
            self.create_note_window(note)
    
    def create_note_window(self, note: Dict) -> NoteWindow:
        """创建便签窗口"""
        note_id = note.get('id')
        
        if note_id in self.note_windows:
            self.note_windows[note_id].show()
            return self.note_windows[note_id]
        
        note_window = NoteWindow(note, self.api_client)
        note_window.content_changed.connect(self.on_note_changed)
        note_window.note_deleted.connect(self.on_note_deleted)
        note_window.create_new_note.connect(self.create_new_note)
        note_window.show_note_list.connect(self.show_note_list)
        note_window.close_window.connect(self.on_close_window)
        
        self.note_windows[note_id] = note_window
        note_window.show()
        
        return note_window
    
    def on_note_changed(self, note_id: int):
        """便签内容改变"""
        if self.note_list_window and self.note_list_window.isVisible():
            self.note_list_window.load_notes()
    
    def on_note_deleted(self, note_id: int):
        """便签被删除"""
        if note_id in self.note_windows:
            del self.note_windows[note_id]
        
        if self.note_list_window and self.note_list_window.isVisible():
            self.note_list_window.load_notes()
    
    def on_close_window(self, note_id: int):
        """关闭便签窗口（不删除）"""
        if note_id in self.note_windows:
            del self.note_windows[note_id]
    
    def show_all_notes(self):
        """显示所有便签"""
        for note_window in self.note_windows.values():
            note_window.show()
            note_window.activateWindow()
    
    def hide_all_notes(self):
        """隐藏所有便签"""
        for note_window in self.note_windows.values():
            note_window.hide()
        
        if self.note_list_window:
            self.note_list_window.hide()
        
        if self.settings_window:
            self.settings_window.hide()
    
    def create_new_note(self):
        """新建便签"""
        if not self.api_client.token:
            QMessageBox.warning(None, "提示", "请先登录")
            self.show_settings()
            return
        
        result = self.api_client.create_note()
        
        if 'id' in result:
            self.create_note_window(result)
            if self.note_list_window and self.note_list_window.isVisible():
                self.note_list_window.load_notes()
        else:
            QMessageBox.warning(None, "失败", result.get('detail', '创建失败'))
    
    def show_note_list(self):
        """显示便签列表"""
        if not self.note_list_window:
            self.note_list_window = NoteListWindow(self.api_client)
            self.note_list_window.note_selected.connect(self.on_note_selected)
            self.note_list_window.create_new_note.connect(self.create_new_note)
            self.note_list_window.show_settings.connect(self.show_settings)
        
        self.note_list_window.show()
        self.note_list_window.activateWindow()
        self.note_list_window.load_notes()
    
    def on_note_selected(self, note_id: int):
        """选中便签"""
        for note_window in self.note_windows.values():
            if note_window.note_id == note_id:
                note_window.show()
                note_window.activateWindow()
                return
        
        notes = self.api_client.get_notes()
        for note in notes:
            if note.get('id') == note_id:
                self.create_note_window(note)
                break
    
    def show_settings(self):
        """显示设置窗口"""
        if not self.settings_window:
            self.settings_window = SettingsWindow(self.api_client)
            self.settings_window.login_success.connect(self.on_login_success)
            self.settings_window.logout.connect(self.on_logout)
        
        self.settings_window.show()
        self.settings_window.activateWindow()
    
    def on_login_success(self):
        """登录成功"""
        self.is_logged_in = True
        self.load_notes()
        self.show_note_list()
    
    def on_logout(self):
        """登出"""
        self.is_logged_in = False
        
        for note_window in list(self.note_windows.values()):
            note_window.close()
        self.note_windows.clear()
        
        if self.note_list_window:
            self.note_list_window.hide()
    
    def quit_app(self):
        """退出应用"""
        for note_window in self.note_windows.values():
            if note_window._is_content_modified:
                note_window.save_note()
        
        self.tray_manager.stop()
        self.app.quit()


def main():
    """主函数"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    setup_font(app)
    
    controller = NoteAppController()
    sys.exit(controller.run())


if __name__ == "__main__":
    main()
