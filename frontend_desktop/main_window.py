from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox,
    QListWidget, QListWidgetItem, QColorDialog, QDialog,
    QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from typing import Dict, List
from api_client import APIClient


class NoteCard(QFrame):
    """便签卡片组件"""

    def __init__(self, note: Dict, parent=None):
        super().__init__(parent)
        self.note = note
        self.parent_widget = parent
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.note.get('color', '#FFE4B5')};
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        self.setMinimumHeight(150)
        self.setMaximumHeight(200)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # 标题
        title = self.note.get('title', '无标题')
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(title_label)

        # 内容
        content = self.note.get('content', '')
        content_label = QLabel(content[:100] + ('...' if len(content) > 100 else ''))
        content_label.setStyleSheet("background: transparent; border: none;")
        content_label.setWordWrap(True)
        layout.addWidget(content_label)

        # 时间和操作按钮
        footer_layout = QHBoxLayout()

        updated_at = self.note.get('updated_at', '')
        if updated_at:
            from datetime import datetime
            dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = ''
        time_label = QLabel(time_str)
        time_label.setStyleSheet("background: transparent; border: none; color: #888; font-size: 10px;")
        footer_layout.addWidget(time_label)

        footer_layout.addStretch()

        # 编辑按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        edit_btn.clicked.connect(lambda: self.parent_widget.edit_note(self.note['id']))
        footer_layout.addWidget(edit_btn)

        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #ee5a5a;
            }
        """)
        delete_btn.clicked.connect(lambda: self.parent_widget.delete_note(self.note['id']))
        footer_layout.addWidget(delete_btn)

        layout.addLayout(footer_layout)
        self.setLayout(layout)


class EditNoteDialog(QDialog):
    """编辑便签对话框"""

    def __init__(self, note: Dict, parent=None):
        super().__init__(parent)
        self.note = note
        self.result_data = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑便签")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题输入
        self.title_input = QLineEdit()
        self.title_input.setText(self.note.get('title', ''))
        self.title_input.setPlaceholderText("便签标题")
        layout.addWidget(QLabel("标题:"))
        layout.addWidget(self.title_input)

        # 内容输入
        self.content_input = QTextEdit()
        self.content_input.setText(self.note.get('content', ''))
        self.content_input.setPlaceholderText("便签内容")
        layout.addWidget(QLabel("内容:"))
        layout.addWidget(self.content_input)

        # 颜色选择
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色:"))

        self.color_btn = QPushButton()
        self.current_color = QColor(self.note.get('color', '#FFE4B5'))
        self.update_color_btn()
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()

        layout.addLayout(color_layout)

        # 按钮
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        save_btn.clicked.connect(self.save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #666;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def update_color_btn(self):
        """更新颜色按钮显示"""
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                border: 1px solid #ddd;
                border-radius: 5px;
                min-width: 60px;
                min-height: 30px;
            }}
        """)

    def choose_color(self):
        """选择颜色"""
        color = QColorDialog.getColor(self.current_color, self, "选择颜色")
        if color.isValid():
            self.current_color = color
            self.update_color_btn()

    def save(self):
        """保存"""
        self.result_data = {
            'title': self.title_input.text().strip(),
            'content': self.content_input.toPlainText().strip(),
            'color': self.current_color.name()
        }
        self.accept()


class MainWindow(QWidget):
    """主窗口"""

    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.notes: List[Dict] = []
        self.init_ui()
        self.load_notes()

        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_notes)
        self.timer.start(30000)  # 30秒刷新一次

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle(f"便签小程序 - {self.api_client.username}")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 顶部区域
        header_layout = QHBoxLayout()

        title_label = QLabel("我的便签")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        user_label = QLabel(f"用户: {self.api_client.username}")
        header_layout.addWidget(user_label)

        logout_btn = QPushButton("退出登录")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #ee5a5a;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)

        layout.addLayout(header_layout)

        # 新建便签区域
        new_note_frame = QFrame()
        new_note_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        new_note_layout = QVBoxLayout()
        new_note_layout.setSpacing(10)

        new_title_layout = QHBoxLayout()
        new_title_layout.addWidget(QLabel("标题:"))
        self.new_title_input = QLineEdit()
        self.new_title_input.setPlaceholderText("便签标题")
        self.new_title_input.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; padding: 8px;")
        new_title_layout.addWidget(self.new_title_input)
        new_note_layout.addLayout(new_title_layout)

        new_note_layout.addWidget(QLabel("内容:"))
        self.new_content_input = QTextEdit()
        self.new_content_input.setPlaceholderText("便签内容")
        self.new_content_input.setMaximumHeight(150)
        self.new_content_input.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        new_note_layout.addWidget(self.new_content_input)

        new_note_footer = QHBoxLayout()
        new_note_footer.addWidget(QLabel("颜色:"))

        self.new_color_btn = QPushButton()
        self.new_color = QColor('#FFE4B5')
        self.update_new_color_btn()
        self.new_color_btn.clicked.connect(self.choose_new_color)
        new_note_footer.addWidget(self.new_color_btn)
        new_note_footer.addStretch()

        create_btn = QPushButton("新建便签")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        create_btn.clicked.connect(self.create_note)
        new_note_footer.addWidget(create_btn)

        new_note_layout.addLayout(new_note_footer)
        new_note_frame.setLayout(new_note_layout)
        layout.addWidget(new_note_frame)

        # 便签列表区域
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        scroll_area.setWidgetResizable(True)

        self.notes_container = QWidget()
        self.notes_layout = QGridLayout()
        self.notes_layout.setSpacing(15)
        self.notes_container.setLayout(self.notes_layout)

        scroll_area.setWidget(self.notes_container)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def update_new_color_btn(self):
        """更新新建便签的颜色按钮"""
        self.new_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.new_color.name()};
                border: 1px solid #ddd;
                border-radius: 5px;
                min-width: 60px;
                min-height: 30px;
            }}
        """)

    def choose_new_color(self):
        """选择新建便签的颜色"""
        color = QColorDialog.getColor(self.new_color, self, "选择颜色")
        if color.isValid():
            self.new_color = color
            self.update_new_color_btn()

    def load_notes(self):
        """加载便签"""
        self.notes = self.api_client.get_notes()
        self.render_notes()

    def render_notes(self):
        """渲染便签"""
        # 清除现有内容
        for i in reversed(range(self.notes_layout.count())):
            self.notes_layout.itemAt(i).widget().deleteLater()

        if not self.notes:
            empty_label = QLabel("暂无便签，请创建第一条便签")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #999; font-size: 14px;")
            self.notes_layout.addWidget(empty_label, 0, 0)
            return

        # 添加便签卡片（网格布局）
        row = 0
        col = 0
        max_cols = 3

        for note in self.notes:
            card = NoteCard(note, self)
            self.notes_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_note(self):
        """创建便签"""
        title = self.new_title_input.text().strip()
        content = self.new_content_input.toPlainText().strip()
        color = self.new_color.name()

        if not title and not content:
            QMessageBox.warning(self, "提示", "请输入便签标题或内容")
            return

        result = self.api_client.create_note(title, content, color)

        if 'id' in result:
            self.new_title_input.clear()
            self.new_content_input.clear()
            self.new_color = QColor('#FFE4B5')
            self.update_new_color_btn()
            self.load_notes()
        else:
            QMessageBox.warning(self, "失败", result.get('detail', '创建失败'))

    def edit_note(self, note_id: int):
        """编辑便签"""
        note = next((n for n in self.notes if n['id'] == note_id), None)
        if not note:
            return

        dialog = EditNoteDialog(note, self)
        if dialog.exec():
            result = self.api_client.update_note(
                note_id,
                dialog.result_data['title'],
                dialog.result_data['content'],
                dialog.result_data['color']
            )

            if 'id' in result:
                self.load_notes()
            else:
                QMessageBox.warning(self, "失败", result.get('detail', '更新失败'))

    def delete_note(self, note_id: int):
        """删除便签"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条便签吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = self.api_client.delete_note(note_id)

            if 'message' in result:
                self.load_notes()
            else:
                QMessageBox.warning(self, "失败", result.get('detail', '删除失败'))

    def logout(self):
        """退出登录"""
        self.timer.stop()
        self.api_client.clear_token()
        self.close()
        self.parent().show_login_window()
