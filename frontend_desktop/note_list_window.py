"""
便签列表窗口
显示所有便签的列表，支持切换便签、设置等功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton,
    QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor
from typing import Dict, List


class NoteListWindow(QWidget):
    """便签列表窗口"""
    
    note_selected = pyqtSignal(int)
    create_new_note = pyqtSignal()
    show_settings = pyqtSignal()
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.notes: List[Dict] = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("便签列表")
        self.setMinimumSize(350, 400)
        self.resize(400, 550)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        header = self.create_header()
        layout.addWidget(header)
        
        self.note_list = QListWidget()
        self.note_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 4px;
                alternate-background-color: #f8f8f8;
            }
            QListWidget::item {
                padding: 0;
                margin: 4px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        self.note_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.note_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.note_list)
        
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
    
    def create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("便签列表")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        settings_btn = QPushButton("设置")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
        settings_btn.clicked.connect(self.show_settings.emit)
        layout.addWidget(settings_btn)
        
        header.setLayout(layout)
        return header
    
    def create_footer(self) -> QWidget:
        """创建底部按钮区域"""
        footer = QWidget()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        new_btn = QPushButton("+ 新建便签")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        new_btn.clicked.connect(self.create_new_note.emit)
        layout.addWidget(new_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #666;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        refresh_btn.clicked.connect(self.load_notes)
        layout.addWidget(refresh_btn)
        
        footer.setLayout(layout)
        return footer
    
    def load_notes(self):
        """加载便签列表"""
        if not self.api_client or not self.api_client.token:
            return
        
        self.notes = self.api_client.get_notes()
        self.render_notes()
    
    def render_notes(self):
        """渲染便签列表"""
        self.note_list.clear()
        
        if not self.notes:
            item = QListWidgetItem("暂无便签")
            item.setForeground(QColor("#999"))
            self.note_list.addItem(item)
            return
        
        for note in self.notes:
            item_widget = self.create_note_item(note)
            
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 80))
            item.setData(Qt.ItemDataRole.UserRole, note.get('id'))
            
            self.note_list.addItem(item)
            self.note_list.setItemWidget(item, item_widget)
    
    def create_note_item(self, note: Dict) -> QWidget:
        """创建便签项组件"""
        widget = QWidget()
        color = note.get('color', '#FFE4B5')
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # 时间
        from datetime import datetime
        updated_at = note.get('updated_at', '')
        time_str = ''
        if updated_at:
            try:
                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                time_str = dt.strftime('%m/%d %H:%M')
            except:
                time_str = ''
        
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(time_label)
        
        # 内容预览（前2行）
        content = note.get('content', '')
        preview = content if content else '空白便签'
        
        content_label = QLabel(preview)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #333; font-size: 13px;")
        content_label.setMaximumHeight(48)
        layout.addWidget(content_label)
        
        widget.setLayout(layout)
        return widget
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """双击便签项"""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id:
            self.note_selected.emit(note_id)
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        self.load_notes()
