"""
便签窗口组件
单个便签的独立窗口，支持编辑、颜色更换、置顶等功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QMenu, QColorDialog, QSizePolicy, QLabel
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QCursor, QFont, QIcon
from typing import Dict, Optional
from config_manager import ConfigManager


class NoteWindow(QWidget):
    """便签窗口"""
    
    # 信号：便签内容改变
    content_changed = pyqtSignal(int)
    # 信号：便签删除
    note_deleted = pyqtSignal(int)
    # 信号：请求新建便签
    create_new_note = pyqtSignal()
    # 信号：请求显示便签列表
    show_note_list = pyqtSignal()
    # 信号：关闭窗口（不删除标签）
    close_window = pyqtSignal(int)
    
    # 窗口最小尺寸
    MIN_WIDTH = 200
    MIN_HEIGHT = 150
    
    def __init__(self, note: Dict, api_client, parent=None):
        super().__init__(parent)
        self.note = note
        self.note_id = note.get('id', 0)
        self.api_client = api_client
        self.config_manager = ConfigManager()
        
        # 窗口状态
        self._is_pinned = False
        self._is_content_modified = False
        
        # 初始化界面
        self.init_ui()
        self.setup_auto_save()
        
        # 加载便签内容
        self.load_content()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"便签 - {self.note.get('title', '新便签')}")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(280, 200)
        
        # 无边框窗口，但允许调整大小
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # 设置便签背景颜色
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.note.get('color', '#FFE4B5')};
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }}
        """)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 内容编辑区域
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("在这里输入便签内容...")
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 14px;
                padding: 4px;
            }
            QTextEdit:focus {
                outline: none;
            }
        """)
        self.content_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_edit.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.content_edit)
        
        # Resize handle（右下角）
        self.resize_handle = QLabel("◢")
        self.resize_handle.setStyleSheet("""
            color: rgba(0, 0, 0, 0.2);
            font-size: 10px;
            background: transparent;
        """)
        self.resize_handle.setFixedSize(14, 14)
        self.resize_handle.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.resize_handle, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        
        # 启用窗口大小调整
        self._resizing = False
        self._resize_edge = None
        
        # 设置鼠标跟踪以检测边缘
        self.setMouseTracking(True)
        self.content_edit.setMouseTracking(True)
    
    def create_toolbar(self) -> QWidget:
        """创建工具栏"""
        toolbar = QWidget()
        toolbar.setStyleSheet("background: transparent;")
        toolbar.setFixedHeight(28)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 新建便签按钮（左上角）
        self.new_btn = QPushButton("+")
        self.new_btn.setFixedSize(24, 24)
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.5);
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.new_btn.clicked.connect(self.create_new_note.emit)
        self.new_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.new_btn)
        
        # 拖动区域（中间空白）
        layout.addStretch()
        
        # 菜单按钮（右上角三个点）
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedSize(24, 24)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        self.menu_btn.clicked.connect(self.show_menu)
        self.menu_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.menu_btn)
        
        # 关闭按钮（右上角）
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.2);
                border-radius: 12px;
                color: #ff4444;
            }
        """)
        self.close_btn.clicked.connect(self.close_note_window)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.close_btn)
        
        toolbar.setLayout(layout)
        return toolbar
    
    def close_note_window(self):
        """关闭便签窗口（不删除标签）"""
        self.close_window.emit(self.note_id)
        self.close()
    
    def show_menu(self):
        """显示下拉菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
        """)
        
        # 便签列表
        list_action = menu.addAction("便签列表")
        list_action.triggered.connect(self.show_note_list.emit)
        
        # 分隔线
        menu.addSeparator()
        
        # 更换颜色
        color_menu = menu.addMenu("更换颜色")
        for color in ConfigManager.PRESET_COLORS:
            color_action = color_menu.addAction(self.get_color_name(color))
            color_action.triggered.connect(lambda checked, c=color: self.change_color(c))
        
        # 自定义颜色
        custom_color_action = menu.addAction("自定义颜色...")
        custom_color_action.triggered.connect(self.choose_custom_color)
        
        menu.addSeparator()
        
        # 置顶/取消置顶
        pin_text = "取消置顶" if self._is_pinned else "置顶窗口"
        pin_action = menu.addAction(pin_text)
        pin_action.triggered.connect(self.toggle_pin)
        
        menu.addSeparator()
        
        # 关闭窗口（不删除）
        close_action = menu.addAction("关闭窗口")
        close_action.triggered.connect(self.close_note_window)
        
        # 删除便签
        delete_action = menu.addAction("删除便签")
        delete_action.triggered.connect(self.delete_note)
        
        # 显示菜单
        menu.exec(QCursor.pos())
    
    def get_color_name(self, color: str) -> str:
        """获取颜色的中文名称"""
        color_names = {
            "#FFE4B5": "黄色",
            "#E6F3FF": "蓝色",
            "#E6FFE6": "绿色",
            "#FFE6F3": "粉色",
            "#F3E6FF": "紫色",
            "#FFF0E6": "橙色"
        }
        return color_names.get(color, "颜色")
    
    def change_color(self, color: str):
        """更换便签颜色"""
        self.note['color'] = color
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }}
        """)
        
        # 保存到服务端
        self.save_note()
    
    def choose_custom_color(self):
        """选择自定义颜色"""
        current_color = QColor(self.note.get('color', '#FFE4B5'))
        color = QColorDialog.getColor(current_color, self, "选择颜色")
        if color.isValid():
            self.change_color(color.name())
    
    def toggle_pin(self):
        """切换置顶状态"""
        self._is_pinned = not self._is_pinned
        if self._is_pinned:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
        self.show()
    
    def load_content(self):
        """加载便签内容"""
        content = self.note.get('content', '')
        self.content_edit.setPlainText(content)
        self._is_content_modified = False
    
    def on_text_changed(self):
        """文本改变事件"""
        self._is_content_modified = True
    
    def setup_auto_save(self):
        """设置自动保存"""
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_note)
        
        # 文本改变后3秒自动保存
        self.content_edit.textChanged.connect(
            lambda: self.save_timer.start(3000)
        )
    
    def save_note(self):
        """保存便签到服务端"""
        if not self.api_client or not self.api_client.token:
            return
        
        content = self.content_edit.toPlainText()
        color = self.note.get('color', '#FFE4B5')
        
        try:
            result = self.api_client.update_note(
                self.note_id,
                content=content,
                color=color
            )
            if 'id' in result:
                self._is_content_modified = False
                self.content_changed.emit(self.note_id)
        except Exception as e:
            print(f"保存便签失败: {e}")
    
    def delete_note(self):
        """删除便签"""
        if self.api_client and self.api_client.token:
            try:
                result = self.api_client.delete_note(self.note_id)
                if 'message' in result:
                    self.note_deleted.emit(self.note_id)
                    self.close()
            except Exception as e:
                print(f"删除便签失败: {e}")
    
    def get_resize_edge(self, x, y):
        """检测鼠标位置对应的resize边缘"""
        width, height = self.width(), self.height()
        edge_margin = 8
        
        # 右下角
        if x > width - edge_margin and y > height - edge_margin:
            return 'bottom_right'
        # 右边缘
        elif x > width - edge_margin:
            return 'right'
        # 下边缘
        elif y > height - edge_margin:
            return 'bottom'
        # 左边缘
        elif x < edge_margin:
            return 'left'
        # 左下角
        elif x < edge_margin and y > height - edge_margin:
            return 'bottom_left'
        
        return None
    
    def get_resize_cursor(self, edge):
        """获取对应边缘的光标形状"""
        cursor_map = {
            'right': Qt.CursorShape.SizeHorCursor,
            'left': Qt.CursorShape.SizeHorCursor,
            'bottom': Qt.CursorShape.SizeVerCursor,
            'bottom_right': Qt.CursorShape.SizeFDiagCursor,
            'bottom_left': Qt.CursorShape.SizeBDiagCursor
        }
        return cursor_map.get(edge, Qt.CursorShape.ArrowCursor)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 实现窗口拖动和大小调整"""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            x, y = pos.x(), pos.y()
            
            # 检测是否在边缘（用于调整大小）
            self._resize_edge = self.get_resize_edge(x, y)
            
            if self._resize_edge:
                self._resizing = True
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_size = self.size()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return
            
            # 点击工具栏区域可以拖动窗口
            if y < 40:
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
            else:
                super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 实现窗口拖动和大小调整"""
        pos = event.position()
        x, y = pos.x(), pos.y()
        
        # 如果正在拖动调整大小
        if hasattr(self, '_resizing') and self._resizing and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            new_width = self._resize_start_size.width()
            new_height = self._resize_start_size.height()
            new_x = self._resize_start_geometry.x()
            new_y = self._resize_start_geometry.y()
            
            if self._resize_edge in ['right', 'bottom_right']:
                new_width = max(self.MIN_WIDTH, self._resize_start_size.width() + delta.x())
            if self._resize_edge in ['bottom', 'bottom_right', 'bottom_left']:
                new_height = max(self.MIN_HEIGHT, self._resize_start_size.height() + delta.y())
            if self._resize_edge in ['left', 'bottom_left']:
                new_width = max(self.MIN_WIDTH, self._resize_start_size.width() - delta.x())
                new_x = self._resize_start_geometry.x() + delta.x()
            
            self.setGeometry(new_x, new_y, new_width, new_height)
            event.accept()
            return
        
        # 如果正在拖动窗口
        elif hasattr(self, '_drag_position') and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return
        
        # 鼠标悬停检测 - 改变光标形状
        elif event.buttons() == Qt.MouseButton.NoButton:
            edge = self.get_resize_edge(x, y)
            if edge:
                self.setCursor(self.get_resize_cursor(edge))
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if hasattr(self, '_drag_position'):
            del self._drag_position
        if hasattr(self, '_resizing'):
            self._resizing = False
            self._resize_edge = None
        super().mouseReleaseEvent(event)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果内容有修改，先保存
        if self._is_content_modified:
            self.save_note()
        event.accept()
