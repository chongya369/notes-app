"""
系统托盘管理器
管理程序托盘图标和菜单
"""
import threading
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu
from PyQt6.QtCore import QObject, pyqtSignal


class TraySignalEmitter(QObject):
    """托盘信号发射器 - 用于跨线程通信"""
    show_notes = pyqtSignal()
    hide_notes = pyqtSignal()
    new_note = pyqtSignal()
    note_list = pyqtSignal()
    quit_app = pyqtSignal()


class TrayManager:
    """系统托盘管理器"""
    
    def __init__(self, signal_emitter: TraySignalEmitter):
        """
        初始化托盘管理器
        
        Args:
            signal_emitter: 信号发射器，用于跨线程通信
        """
        self.signal_emitter = signal_emitter
        self.icon = None
        self._is_visible = True
        self._running = False
    
    def create_default_icon(self) -> Image.Image:
        """创建默认托盘图标（便签样式）"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 便签背景（黄色）
        draw.rounded_rectangle(
            [4, 4, size-4, size-4],
            radius=8,
            fill='#FFE4B5',
            outline='#DDD'
        )
        
        # 左上角折角效果
        draw.polygon(
            [(4, 4), (16, 4), (4, 16)],
            fill='#FFD700'
        )
        
        # 横线（表示文字）
        draw.line([(12, 24), (52, 24)], fill='#666', width=2)
        draw.line([(12, 34), (48, 34)], fill='#666', width=2)
        draw.line([(12, 44), (40, 44)], fill='#666', width=2)
        
        return image
    
    def create_menu(self) -> Menu:
        """创建托盘菜单"""
        return Menu(
            MenuItem(
                '显示所有便签',
                self.on_show_notes,
                visible=lambda item: not self._is_visible
            ),
            MenuItem(
                '隐藏所有便签',
                self.on_hide_notes,
                visible=lambda item: self._is_visible
            ),
            Menu.SEPARATOR,
            MenuItem(
                '新建便签',
                self.on_new_note
            ),
            MenuItem(
                '便签列表',
                self.on_note_list
            ),
            Menu.SEPARATOR,
            MenuItem(
                '退出',
                self.on_quit
            )
        )
    
    def on_show_notes(self):
        """显示所有便签"""
        self._is_visible = True
        if self.signal_emitter:
            self.signal_emitter.show_notes.emit()
    
    def on_hide_notes(self):
        """隐藏所有便签"""
        self._is_visible = False
        if self.signal_emitter:
            self.signal_emitter.hide_notes.emit()
    
    def on_new_note(self):
        """新建便签"""
        if self.signal_emitter:
            self.signal_emitter.new_note.emit()
    
    def on_note_list(self):
        """显示便签列表"""
        if self.signal_emitter:
            self.signal_emitter.note_list.emit()
    
    def on_quit(self):
        """退出应用"""
        self._running = False
        if self.icon:
            self.icon.stop()
        if self.signal_emitter:
            self.signal_emitter.quit_app.emit()
    
    def on_double_click(self, icon, button):
        """双击托盘图标"""
        if self._is_visible:
            self.on_hide_notes()
        else:
            self.on_show_notes()
    
    def run(self):
        """启动托盘（在独立线程中运行）"""
        image = self.create_default_icon()
        menu = self.create_menu()
        
        self.icon = pystray.Icon(
            'sticky_notes',
            image,
            '便签小程序',
            menu
        )
        
        self.icon.on_double_click = self.on_double_click
        
        self._running = True
        self.icon.run()
    
    def run_detached(self):
        """在独立线程中启动托盘"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """停止托盘"""
        self._running = False
        if self.icon:
            self.icon.stop()
    
    def set_visible(self, visible: bool):
        """设置便签可见性"""
        self._is_visible = visible
    
    def update_icon(self, image: Image.Image = None):
        """更新托盘图标"""
        if self.icon:
            if image is None:
                image = self.create_default_icon()
            self.icon.icon = image
